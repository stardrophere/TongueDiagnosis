import json

import requests
from starlette.responses import JSONResponse, StreamingResponse

from ..config import settings
from ..orm import create_new_chat_records, get_chat_record, parse_image_message_content
from ..orm.database import create_db_session


class DeepSeekStreamChatter:
    """
    Bridge DeepSeek's SSE stream to the NDJSON format expected by the frontend.
    """

    def __init__(self, model=None, system_prompt=None):
        self.url = f"{settings.DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        self.model = model or settings.DEEPSEEK_MODEL
        self.system_prompt = system_prompt or settings.SYSTEM_PROMPT

    def _build_messages(self, records=None, current_user_message=""):
        messages = [{"role": "system", "content": self.system_prompt}]

        if records:
            messages.extend(records)

        if current_user_message:
            messages.append({"role": "user", "content": current_user_message})

        return messages

    def _save_assistant_message(self, content, session_id):
        db = create_db_session()
        try:
            create_new_chat_records(
                db=db,
                content=content,
                session_id=session_id,
                role=2,
            )
        except Exception as error:
            print(f"Failed to save assistant message: {error}")
        finally:
            db.close()

    def _stream_chat(self, messages, session_id):
        if not settings.DEEPSEEK_API_KEY:
            return JSONResponse(
                status_code=500,
                content={"error": "DEEPSEEK_API_KEY is not configured."},
            )

        data = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        response = None
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=data,
                stream=True,
                timeout=(
                    settings.DEEPSEEK_CONNECT_TIMEOUT,
                    settings.DEEPSEEK_READ_TIMEOUT,
                ),
            )
            response.raise_for_status()

            def generate():
                full_response = ""
                in_thinking = False

                try:
                    for line in response.iter_lines(decode_unicode=True):
                        if not line or not line.startswith("data:"):
                            continue

                        payload = line[5:].strip()
                        if payload == "[DONE]":
                            break

                        try:
                            chunk = json.loads(payload)
                        except json.JSONDecodeError:
                            continue

                        choices = chunk.get("choices") or []
                        if not choices:
                            continue

                        delta = choices[0].get("delta") or {}
                        reasoning_content = delta.get("reasoning_content") or ""
                        content = delta.get("content") or ""

                        if reasoning_content:
                            if not in_thinking:
                                in_thinking = True
                                full_response += "<think>"
                                yield json.dumps(
                                    {
                                        "token": "<think>",
                                        "session_id": session_id,
                                        "is_complete": False,
                                    },
                                    ensure_ascii=False,
                                ) + "\n"

                            full_response += reasoning_content
                            yield json.dumps(
                                {
                                    "token": reasoning_content,
                                    "session_id": session_id,
                                    "is_complete": False,
                                },
                                ensure_ascii=False,
                            ) + "\n"

                        if content:
                            if in_thinking:
                                in_thinking = False
                                full_response += "</think>"
                                yield json.dumps(
                                    {
                                        "token": "</think>",
                                        "session_id": session_id,
                                        "is_complete": False,
                                    },
                                    ensure_ascii=False,
                                ) + "\n"

                            full_response += content
                            yield json.dumps(
                                {
                                    "token": content,
                                    "session_id": session_id,
                                    "is_complete": False,
                                },
                                ensure_ascii=False,
                            ) + "\n"
                except requests.exceptions.RequestException as error:
                    print(f"DeepSeek stream failed: {error}")
                finally:
                    if in_thinking:
                        full_response += "</think>"
                        yield json.dumps(
                            {
                                "token": "</think>",
                                "session_id": session_id,
                                "is_complete": False,
                            },
                            ensure_ascii=False,
                        ) + "\n"

                    if full_response:
                        self._save_assistant_message(full_response, session_id)

                    if response is not None:
                        response.close()

                    yield json.dumps(
                        {
                            "token": "",
                            "session_id": session_id,
                            "is_complete": True,
                        },
                        ensure_ascii=False,
                    ) + "\n"

            return StreamingResponse(generate(), media_type="application/x-ndjson")
        except requests.exceptions.RequestException as error:
            detail = ""
            try:
                detail = response.text if response is not None else str(error)
            except Exception:
                detail = str(error)

            print(f"DeepSeek request failed: {error}")
            return JSONResponse(
                status_code=500,
                content={"error": f"DeepSeek request failed: {detail}"},
            )

    def chat_stream_first(self, user_input, feature, session_new_id):
        first_message = (
            f"用户舌象特征如下：{feature}。"
            f"用户补充问题：{user_input}。"
            "请结合中医语境进行结构化中文分析。"
        )
        messages = self._build_messages(current_user_message=first_message)
        return self._stream_chat(messages=messages, session_id=session_new_id)

    def chat_stream_add(self, user_id, session_id, db):
        chat_record = get_chat_record(ID=user_id, sessionid=session_id, db=db)
        if chat_record in (102, 103):
            return JSONResponse(
                status_code=404,
                content={"error": "Chat session was not found."},
            )

        records = []
        for record in chat_record:
            if parse_image_message_content(record.content):
                continue

            role = "user" if record.role == 1 else "assistant"
            records.append({"role": role, "content": record.content})

        messages = self._build_messages(records=records)
        return self._stream_chat(messages=messages, session_id=session_id)

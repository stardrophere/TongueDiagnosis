import json
import time

from sqlalchemy.orm import Session

from ...models import models

IMAGE_MESSAGE_PREFIX = "__TD_IMAGE__:"


def build_image_message_content(preview_url: str, storage_path: str, text: str = "已上传舌象图片，请开始分析。"):
    payload = {
        "preview_url": preview_url,
        "storage_path": storage_path,
        "text": text,
    }
    return f"{IMAGE_MESSAGE_PREFIX}{json.dumps(payload, ensure_ascii=False)}"


def parse_image_message_content(content: str):
    if not content or not content.startswith(IMAGE_MESSAGE_PREFIX):
        return None

    try:
        return json.loads(content[len(IMAGE_MESSAGE_PREFIX):])
    except json.JSONDecodeError:
        return None


def get_chat_record(ID: int, sessionid: int, db: Session):
    db_chat_session = get_chat_session(ID=ID, sessionid=sessionid, db=db)
    if not db_chat_session:
        return 102

    chat_records = (
        db.query(models.ChatRecord)
        .filter(models.ChatRecord.session_id == sessionid)
        .order_by(models.ChatRecord.create_at)
        .all()
    )

    if not chat_records:
        return 103

    return chat_records


def get_chat_session(ID: int, sessionid: int, db: Session):
    return (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == sessionid,
            models.ChatSession.user_id == ID,
        )
        .first()
    )


def get_all_chat_id(ID: int, db: Session):
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == ID)
        .order_by(models.ChatSession.id.desc())
        .all()
    )


def get_result(img_src: str, db: Session):
    result = db.query(models.TongueAnalysis).filter(models.TongueAnalysis.img_src == img_src).first()
    if not result:
        return None

    db.refresh(result)
    return result


def create_new_session(db: Session, ID: int, tittle: str):
    new_message = models.ChatSession(
        tittle=tittle,
        user_id=ID,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def create_new_chat_records(db: Session, session_id: int, content: str, role: int):
    millis_timestamp = int(time.time() * 1000)
    new_message = models.ChatRecord(
        session_id=session_id,
        content=content,
        create_at=millis_timestamp,
        role=role,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def delete_chat_session(ID: int, sessionid: int, db: Session):
    chat_session = get_chat_session(ID=ID, sessionid=sessionid, db=db)
    if not chat_session:
        return 102

    image_payloads = []
    for record in chat_session.chat_records:
        payload = parse_image_message_content(record.content)
        if payload:
            image_payloads.append(payload)

    db.delete(chat_session)
    db.commit()
    return image_payloads

import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..core import get_current_user
from ..models import models, schemas
from ..net.predict import TonguePredictor
from ..orm import (
    build_image_message_content,
    create_new_chat_records,
    create_new_session,
    delete_chat_session,
    get_all_chat_id,
    get_chat_record,
    get_result,
    write_result,
    write_event,
)
from ..orm.database import get_db
from .deepseek_used import DeepSeekStreamChatter

router_tongue_analysis = APIRouter()

feature_map = {
    "舌色": {
        0: "淡白舌",
        1: "淡红舌",
        2: "红舌",
        3: "绛舌",
        4: "青紫舌",
    },
    "舌苔颜色": {
        0: "白苔",
        1: "黄苔",
        2: "灰黑苔",
    },
    "舌体厚薄": {
        0: "偏薄",
        1: "偏厚",
    },
    "腐腻特征": {
        0: "偏腐",
        1: "偏腻",
    },
}


def format_tongue_features(tongue_color, coating_color, tongue_thickness, rot_greasy):
    try:
        features = [
            f"舌色：{feature_map['舌色'][tongue_color]}",
            f"舌苔颜色：{feature_map['舌苔颜色'][coating_color]}",
            f"舌体厚薄：{feature_map['舌体厚薄'][tongue_thickness]}",
            f"腐腻特征：{feature_map['腐腻特征'][rot_greasy]}",
        ]
        return "；".join(features)
    except KeyError:
        return "模型返回了无法识别的舌象特征，请谨慎给出兜底分析。"


def build_public_image_url(storage_path: str):
    return f"/{storage_path.lstrip('/')}"


def remove_session_assets(user_id: int, image_payloads: list[dict], db: Session):
    storage_paths = {
        (payload.get("storage_path") or "").lstrip("/")
        for payload in image_payloads
        if payload.get("storage_path")
    }
    if not storage_paths:
        return

    analysis_records = (
        db.query(models.TongueAnalysis)
        .filter(
            models.TongueAnalysis.user_id == user_id,
            models.TongueAnalysis.img_src.in_(storage_paths),
        )
        .all()
    )

    for record in analysis_records:
        db.delete(record)
    db.commit()

    image_root = settings.IMG_PATH.resolve()
    for storage_path in storage_paths:
        file_path = (image_root / Path(storage_path).name).resolve()
        try:
            if image_root == file_path.parent or image_root in file_path.parents:
                file_path.unlink(missing_ok=True)
        except OSError as error:
            print(f"Failed to remove image file {file_path}: {error}")


async def wait_for_analysis_result(img_src: str, db: Session, interval_seconds: float = 0.8):
    while True:
        result = get_result(img_src, db=db)
        if result and result.state != 0:
            return result

        await asyncio.sleep(interval_seconds)


@router_tongue_analysis.post("/session/{sessionId}")
async def ask_follow_up(
    sessionId: int,
    user_input: schemas.UserInput,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    create_new_chat_records(db=db, content=user_input.input, session_id=sessionId, role=1)
    bot = DeepSeekStreamChatter(system_prompt=settings.SYSTEM_PROMPT)
    return bot.chat_stream_add(user.id, sessionId, db)


@router_tongue_analysis.post("/session")
async def create_session_with_image(
    file_data: UploadFile = File(...),
    user_input: str = Form(...),
    name: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_extension = Path(file_data.filename or "upload.jpg").suffix or ".jpg"
    filename = f"{timestamp}{file_extension}"
    file_location = settings.IMG_PATH / filename

    contents = await file_data.read()
    with open(file_location, "wb") as target_file:
        target_file.write(contents)

    img_db_path = f"{settings.IMG_DB_PATH}/{filename}".lstrip("/")
    event = write_event(user_id=user.id, img_src=img_db_path, state=0, db=db)
    if not event:
        return schemas.UploadResponse(
            code=201,
            message="operation failed",
            data=None,
        )

    file_data.file.seek(0)
    queue_result = TonguePredictor().predict(img=file_data.file, record_id=event.id, fun=write_result)
    if queue_result.get("code") != 0:
        return schemas.UploadResponse(
            code=203,
            message="analysis task create failed",
            data=None,
        )

    result = await wait_for_analysis_result(img_db_path, db=db)
    if not result or result.state != 1:
        return schemas.UploadResponse(
            code=result.state if result else 204,
            message="image analysis failed",
            data=None,
        )

    feature = format_tongue_features(
        result.tongue_color,
        result.coating_color,
        result.tongue_thickness,
        result.rot_greasy,
    )

    new_session = create_new_session(ID=user.id, db=db, tittle=name)
    session_new_id = new_session.id
    create_new_chat_records(
        db=db,
        content=build_image_message_content(
            preview_url=build_public_image_url(img_db_path),
            storage_path=img_db_path,
        ),
        session_id=session_new_id,
        role=1,
    )

    bot = DeepSeekStreamChatter(system_prompt=settings.SYSTEM_PROMPT)
    return bot.chat_stream_first(user_input, feature, session_new_id)


@router_tongue_analysis.get("/record/{sessionid}", response_model=schemas.ChatSessionRecordsResponse)
async def get_chat_records_by_session(
    sessionid: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    chat_record = get_chat_record(ID=user.id, sessionid=sessionid, db=db)
    if chat_record in (102, 103):
        return schemas.ChatSessionRecordsResponse(
            code=chat_record,
            message="operation failed",
            data=schemas.ChatSessionRecordsData(records=[]),
        )

    records = []
    for record in chat_record:
        records.append(
            schemas.ChatRecordResponse(
                content=record.content,
                create_at=record.create_at,
                role=record.role,
            )
        )

    return schemas.ChatSessionRecordsResponse(
        code=0,
        message="operation success",
        data=schemas.ChatSessionRecordsData(records=records),
    )


@router_tongue_analysis.get("/session", response_model=schemas.SessionIdResponse)
async def get_chat_records_id(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    chat_id_records = get_all_chat_id(ID=user.id, db=db)
    data_temp = []

    for record in chat_id_records:
        data_temp.append(
            schemas.SessionId(
                session_id=record.id,
                name=record.tittle,
            )
        )

    return schemas.SessionIdResponse(
        code=0,
        message="operation success",
        data=data_temp,
    )


@router_tongue_analysis.delete("/session/{sessionid}", response_model=schemas.BaseResponse)
async def delete_session_by_id(
    sessionid: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    result = delete_chat_session(ID=user.id, sessionid=sessionid, db=db)
    if result == 102:
        return schemas.BaseResponse(
            code=102,
            message="session not found",
            data=None,
        )

    remove_session_assets(user.id, result, db=db)
    return schemas.BaseResponse(
        code=0,
        message="operation success",
        data=None,
    )

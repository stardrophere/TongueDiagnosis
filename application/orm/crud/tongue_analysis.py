from sqlalchemy.orm import Session

from ...models import models
from ..database import create_db_session


def write_result(
    event_id: int,
    tongue_color: int,
    coating_color: int,
    tongue_thickness: int,
    rot_greasy: int,
    code: int,
):
    """
    写回舌象分析结果。
    这个函数会被后台预测线程调用，因此不能依赖请求线程传进来的 Session，
    而是必须在函数内部自行创建和关闭数据库会话。
    """
    db = create_db_session()
    try:
        record = db.query(models.TongueAnalysis).filter(models.TongueAnalysis.id == event_id).first()
        if not record:
            return 404

        record.state = code

        if code == 1:
            record.tongue_color = tongue_color
            record.coating_color = coating_color
            record.tongue_thickness = tongue_thickness
            record.rot_greasy = rot_greasy

        db.commit()
        db.refresh(record)
        return 0
    except Exception as error:
        db.rollback()
        print(error)
        return 1
    finally:
        db.close()


def write_event(
    user_id: int,
    img_src: str,
    state: int,
    db: Session,
):
    """
    创建一条新的舌象分析事件。
    上传图片成功后会先写入这条记录，随后再由后台线程异步补全识别结果。
    """
    event = models.TongueAnalysis(
        user_id=user_id,
        img_src=img_src,
        state=state,
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
        return event
    except Exception as error:
        db.rollback()
        print(error)
        return None


def get_record_by_location(img_src: str, db: Session):
    """
    通过图片相对路径查找分析记录。
    """
    return db.query(models.TongueAnalysis).filter(models.TongueAnalysis.img_src == img_src).first()

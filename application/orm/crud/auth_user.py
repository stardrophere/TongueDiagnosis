import hashlib

from sqlalchemy.orm import Session

from ...models import models


def hash_password(password: str) -> str:
    """
    统一密码摘要逻辑。
    当前项目仍沿用 SHA256 摘要方式，因此登录和注册必须共用同一入口，避免摘要算法不一致。
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_user(email: str, db: Session):
    """
    通过邮箱查询用户。
    邮箱是当前系统的唯一登录标识，因此所有鉴权逻辑都围绕它展开。
    """
    return db.query(models.User).filter(models.User.email == email).first()


def register_user(email: str, password: str, db: Session):
    """
    注册新用户。
    返回约定：
    0 表示成功；
    101 表示邮箱已存在；
    102 表示写库失败。
    """
    if get_user(email=email, db=db):
        return 101

    user = models.User(
        email=email,
        password=hash_password(password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
        return 0
    except Exception as error:
        db.rollback()
        print(error)
        return 102


def login_user(email: str, password: str, db: Session):
    """
    校验邮箱和密码是否匹配。
    仅返回业务码，方便保持当前接口响应结构兼容。
    """
    user = get_user(email=email, db=db)
    if not user:
        return 101

    if user.password != hash_password(password):
        return 102

    return 0


def authenticate_user(email: str, password: str, db: Session):
    """
    返回已验证通过的用户对象。
    虽然当前主要登录流程未直接调用它，但保留该函数可让后续扩展更方便。
    """
    user = get_user(email=email, db=db)
    if not user:
        return False

    if user.password != hash_password(password):
        return False

    return user


def get_user_record(ID: int, db: Session):
    """
    获取当前用户的全部舌象分析记录，按主键升序返回。
    """
    return db.query(models.TongueAnalysis).filter(models.TongueAnalysis.user_id == ID).order_by(models.TongueAnalysis.id).all()

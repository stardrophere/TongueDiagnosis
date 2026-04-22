from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ..config import settings


"""
数据库底座统一收敛到这一处，避免项目里再出现第二套 engine / Base / SessionLocal。
所有 ORM 模型、依赖注入会话、后台线程写库都应从这里获取数据库对象。
"""

sqlite_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=sqlite_connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    """
    FastAPI 请求作用域数据库会话。
    路由处理完成后无论成功还是失败，都会在 finally 中关闭，防止连接泄漏。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_session() -> Session:
    """
    为后台线程、流式响应落库等非依赖注入场景显式创建新的数据库会话。
    这些场景不能直接复用请求线程里的 Session，否则会有线程安全问题。
    """
    return SessionLocal()


def initialize_database():
    """
    初始化数据库表结构。
    这里必须先导入模型模块，确保 Base.metadata 已经收集到所有 ORM 实体定义。
    """
    from ..models import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

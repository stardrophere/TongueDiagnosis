"""
兼容旧导入路径。
项目现在统一使用 `application.orm.database` 作为数据库底座，这里仅保留转发导出，
避免旧模块路径在本次重构中全部失效。
"""

from ..orm.database import Base, SessionLocal, create_db_session, engine, get_db, initialize_database

__all__ = [
    "Base",
    "SessionLocal",
    "create_db_session",
    "engine",
    "get_db",
    "initialize_database",
]

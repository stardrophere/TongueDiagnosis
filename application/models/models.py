from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """
    用户基础表。
    当前项目仍使用邮箱 + 密码摘要登录，因此这里只保留最小必要字段。
    """

    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)


class TongueAnalysis(Base):
    """
    舌象分析事件表。
    一次图片上传会先创建一条分析记录，随后由后台预测线程补全识别结果和状态。
    """

    __tablename__ = "TongueAnalysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False, index=True)
    img_src = Column(String(255), nullable=False, unique=True)
    state = Column(Integer, nullable=False, default=0)
    tongue_color = Column(Integer, nullable=True)
    coating_color = Column(Integer, nullable=True)
    tongue_thickness = Column(Integer, nullable=True)
    rot_greasy = Column(Integer, nullable=True)

    user = relationship("User")


class ChatSession(Base):
    """
    会话表。
    字段名 `tittle` 是历史拼写问题，但当前前后端与数据库都依赖它，
    这次重构先保留字段名，避免引入额外迁移成本。
    """

    __tablename__ = "chatSession"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False, index=True)
    tittle = Column(String(255), nullable=False)

    user = relationship("User")
    chat_records = relationship("ChatRecord", back_populates="session", cascade="all, delete-orphan")


class ChatRecord(Base):
    """
    会话消息表。
    role 约定：1 表示用户消息，2 表示助手消息。
    """

    __tablename__ = "chatRecord"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chatSession.id"), nullable=False, index=True)
    content = Column(String, nullable=False)
    create_at = Column(Integer, nullable=False, index=True)
    role = Column(Integer, nullable=False)

    session = relationship("ChatSession", back_populates="chat_records")

import time
from typing import Annotated, Any, Optional

from fastapi.param_functions import Form
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    所有接口的统一返回骨架。
    保持现有 `code/message/data` 结构不变，便于兼容前端。
    """

    code: int
    message: str
    data: Any = None


class Token(BaseModel):
    token: str


class UserBase(BaseModel):
    ID: Optional[int] = None
    email: str


class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Result(BaseModel):
    tongue_color: Optional[int] = None
    coating_color: Optional[int] = None
    tongue_thickness: Optional[int] = None
    rot_greasy: Optional[int] = None


class Record(BaseModel):
    ID: int
    user_ID: int
    img_src: str
    state: Optional[int] = None
    result: Optional[Result] = None


class LoginResponse(BaseResponse):
    data: Optional[Token] = None


class RegisterResponse(BaseResponse):
    data: None = None


class InfoResponse(BaseResponse):
    data: Optional[UserBase] = None


class RecordResponse(BaseResponse):
    data: list[Record] = Field(default_factory=list)


class UploadResponse(BaseResponse):
    data: Optional[dict] = None


class ExtendedOAuth2PasswordRequestForm:
    """
    保持现有前端表单字段名为 email/password，不强行切回 username/password。
    """

    def __init__(
        self,
        *,
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ):
        self.email = email
        self.password = password


class UserInput(BaseModel):
    input: str


class ChatRecordResponse(BaseModel):
    content: str
    create_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    role: int


class ChatSessionRecordsData(BaseModel):
    records: list[ChatRecordResponse] = Field(default_factory=list)


class ChatSessionRecordsResponse(BaseResponse):
    data: ChatSessionRecordsData = Field(default_factory=ChatSessionRecordsData)


class SessionId(BaseModel):
    session_id: int
    name: str


class SessionIdResponse(BaseResponse):
    data: list[SessionId] = Field(default_factory=list)

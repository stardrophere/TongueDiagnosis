from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Annotated
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..config import settings
from ..orm.crud.auth_user import get_user
from ..orm.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


"""
鉴权逻辑统一放在这里，路由层只负责声明依赖，不重复处理 token 解析细节。
"""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    生成带过期时间的访问令牌。
    token 中目前仍保留用户 ID 和 email，兼容现有业务读取方式。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """
    从 Bearer Token 中解析当前用户。
    一旦 token 不合法或数据库中查不到用户，会直接抛出 401，路由层无需再判空兜底。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHMS)
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(email=email, db=db)
    if user is None:
        raise credentials_exception
    return user

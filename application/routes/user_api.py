from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core import create_access_token, get_current_user
from ..models import schemas
from ..orm import get_user, get_user_record, login_user, register_user
from ..orm.database import get_db

router_user = APIRouter()


@router_user.post("/register", response_model=schemas.RegisterResponse)
def register(schema: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口。
    当前仍返回旧版 code/message 结构，以兼容现有前端登录注册流程。
    """
    code = register_user(email=schema.email, password=schema.password, db=db)

    if code == 0:
        return schemas.RegisterResponse(code=0, message="operation success")
    if code == 101:
        return schemas.RegisterResponse(code=101, message="has been registered")

    return schemas.RegisterResponse(code=102, message="operation failed")


@router_user.put("/login", response_model=schemas.LoginResponse)
def login(
    form_data: Annotated[schemas.ExtendedOAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    用户登录接口。
    登录成功后会把用户 ID 和 email 一并写入 token，便于后续接口解出当前身份。
    """
    code = login_user(email=form_data.email, password=form_data.password, db=db)

    if code == 0:
        user = get_user(email=form_data.email, db=db)
        access_token = create_access_token(data={"ID": user.id, "email": form_data.email})
        return schemas.LoginResponse(
            code=0,
            message="operation success",
            data=schemas.Token(token=access_token),
        )

    if code == 101:
        return schemas.LoginResponse(
            code=101,
            message="operation failed",
            data=None,
        )

    return schemas.LoginResponse(
        code=102,
        message="wrong password",
        data=None,
    )


@router_user.get("/info", response_model=schemas.InfoResponse)
def info_get(user=Depends(get_current_user)):
    """
    获取当前登录用户的基础信息。
    `get_current_user` 已经完成鉴权校验，因此这里不需要再额外做判空分支。
    """
    user_data_temp = schemas.UserBase(
        ID=user.id,
        email=user.email,
    )
    return schemas.InfoResponse(
        code=0,
        message="operation success",
        data=user_data_temp,
    )


@router_user.get("/record", response_model=schemas.RecordResponse)
def record_get(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取当前用户的全部舌象分析记录。
    """
    user_record = get_user_record(ID=user.id, db=db)
    data_temp = []

    for record in user_record:
        data_temp.append(
            schemas.Record(
                ID=record.id,
                user_ID=record.user_id,
                img_src=record.img_src,
                state=record.state,
                result=schemas.Result(
                    tongue_color=record.tongue_color,
                    coating_color=record.coating_color,
                    tongue_thickness=record.tongue_thickness,
                    rot_greasy=record.rot_greasy,
                ),
            )
        )

    return schemas.RecordResponse(
        code=0,
        message="operation success",
        data=data_temp,
    )

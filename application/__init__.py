from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .net.predict import TonguePredictor
from .orm.database import initialize_database
from .routes import register_routes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    统一管理应用启动和退出阶段的资源初始化。
    这里会完成三件事：
    1. 创建运行目录；
    2. 初始化数据库表；
    3. 启动舌诊预测后台 worker。
    """
    settings.ensure_runtime_directories()
    initialize_database()
    TonguePredictor().start_worker()
    yield


def create_app():
    """
    创建 FastAPI 应用实例。
    路由注册、跨域策略和生命周期初始化都在这里集中处理，避免入口文件再分散维护。
    """
    app = FastAPI(lifespan=lifespan)
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routes(app)
    return app

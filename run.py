import uvicorn

from application import create_app
from application.config import settings

app = create_app()

if __name__ == '__main__':
    """
    启动入口现在只负责运行 uvicorn。
    数据库建表、图片目录准备、预测 worker 启动都已经迁移到 FastAPI lifespan 中统一处理。
    """
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)

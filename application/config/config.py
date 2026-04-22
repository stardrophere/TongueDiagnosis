import os
from pathlib import Path

from dotenv import load_dotenv


class Settings:
    """
    Centralized runtime settings for the backend application.
    """

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parents[2]
        load_dotenv(self.BASE_DIR / ".env", override=False)

        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))
        self.SECRET_KEY = os.getenv("SECRET_KEY", "f2e1f1b1c1a1")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_ALGORITHMS = [self.JWT_ALGORITHM]

        self.DB_FILE_NAME = os.getenv("SQLITE_DB_FILE", "AppDatabase.db")
        self.DB_PATH = self.BASE_DIR / self.DB_FILE_NAME
        self.DATABASE_URL = f"sqlite:///{self.DB_PATH.as_posix()}"

        self.IMG_PATH = Path(os.getenv("IMG_PATH", str(self.BASE_DIR / "frontend" / "public" / "tongue")))
        self.IMG_DB_PATH = os.getenv("IMG_DB_PATH", "tongue")

        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", os.getenv("LLM_NAME", "deepseek-chat"))
        self.DEEPSEEK_CONNECT_TIMEOUT = int(os.getenv("DEEPSEEK_CONNECT_TIMEOUT", 10))
        self.DEEPSEEK_READ_TIMEOUT = int(os.getenv("DEEPSEEK_READ_TIMEOUT", 600))

        self.SYSTEM_PROMPT = os.getenv(
            "SYSTEM_PROMPT",
            (
                "你是一名擅长中医舌诊分析的 AI 助手。系统会先提供用户的舌象特征，再补充用户问题。"
                "请结合中医语境，用清晰、结构化、谨慎的中文给出分析和建议，并明确说明结果仅供参考，"
                "不能替代医生面诊。"
            ),
        )
        self.APP_PORT = int(os.getenv("APP_PORT", 5000))

    def ensure_runtime_directories(self):
        """
        Ensure directories needed at runtime already exist before the app starts serving.
        """

        self.IMG_PATH.mkdir(parents=True, exist_ok=True)

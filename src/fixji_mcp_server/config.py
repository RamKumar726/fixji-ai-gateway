import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BACKEND_URL: str = os.getenv("FIXJI_BACKEND_URL", "https://fixji-backend.onrender.com")
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8080"))
    REQUEST_TIMEOUT: int = 10
    BOOKING_TIMEOUT: int = 60


settings = Settings()
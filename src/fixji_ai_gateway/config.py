import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BACKEND_URL: str = os.getenv("FIXJI_BACKEND_URL", "https://fixji-backend.onrender.com")
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8080"))
    REQUEST_TIMEOUT: int = 10
    BOOKING_TIMEOUT: int = 60
    MCP_URL = os.getenv("MCP_URL", "http://localhost:8080/mcp")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")

    # Comma-separated list, e.g. "http://localhost:3000,https://fixji.com"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5500,https://fixji-clone-client.vercel.app/, *").split(",") if o.strip()]
    SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))


settings = Settings()
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, chat
from pathlib import Path
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Fixji AI Gateway")

allowed_origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

app.mount(
    "/widget",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="widget",
)


@app.get("/health")
def health():
    return {"status": "ok"}
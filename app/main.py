from fastapi import FastAPI
from app.routes import tiktok

app = FastAPI(title="TikTok Watermark Pipeline")

app.include_router(tiktok.router)

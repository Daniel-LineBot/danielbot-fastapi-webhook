import os
from fastapi import FastAPI
from routers.webhook import router as webhook_router
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="DanielBot Webhook")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(webhook_router, prefix="/webhook")

@app.get("/health")
async def health():
    return {"status": "ok"}

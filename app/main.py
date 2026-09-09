"""FastAPI 应用入口。"""

from fastapi import FastAPI

from app.api.script import router as script_router
from app.api.tts import router as tts_router

app = FastAPI(title="ai-video-agent")
app.include_router(script_router)
app.include_router(tts_router)


@app.get("/health")
def health() -> dict[str, str]:
    """返回服务健康状态。"""
    return {"status": "ok", "service": "ai-video-agent"}

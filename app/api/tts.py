"""单段文本转语音接口。"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator


class TTSGenerateRequest(BaseModel):
    text: str
    voice: str = "zh-CN-YunxiNeural"

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text 不能为空")
        return value


class TTSGenerateResponse(BaseModel):
    audio_path: str


router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.post("/generate", response_model=TTSGenerateResponse)
async def generate_tts(request: TTSGenerateRequest) -> TTSGenerateResponse:
    # 延迟导入，避免 TTS 依赖不可用时影响其他接口。
    try:
        from app.services.tts_service import synthesize_text
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="语音合成服务暂不可用，请稍后再试。",
        ) from None

    try:
        audio_path = await synthesize_text(text=request.text, voice=request.voice)
        return TTSGenerateResponse(audio_path=audio_path)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="语音合成失败，请稍后再试。",
        ) from None

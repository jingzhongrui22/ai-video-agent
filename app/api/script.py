"""短视频脚本生成接口。"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.script import ScriptGenerateRequest, VideoScript


router = APIRouter(prefix="/api/script", tags=["script"])


@router.post("/generate", response_model=VideoScript)
async def generate_script(request: ScriptGenerateRequest) -> VideoScript:
    # 延迟加载配置，避免未配置 DeepSeek 时影响健康检查。
    try:
        from app.services.llm_service import generate_video_script
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="脚本生成服务暂不可用，请联系管理员检查配置。",
        ) from None

    try:
        return await generate_video_script(
            text=request.text,
            style=request.style,
            duration=request.duration,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="脚本生成失败，请稍后再试。",
        ) from None

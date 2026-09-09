"""短视频脚本的请求与数据结构。"""

from pydantic import BaseModel, Field, field_validator


class ScriptGenerateRequest(BaseModel):
    text: str
    style: str = "knowledge"
    duration: int = Field(default=60, gt=0)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text 不能为空或仅包含空白字符")
        return value


class ScriptSegment(BaseModel):
    id: int
    text: str
    emotion: str
    speed: float
    pause_after: float


class VideoScript(BaseModel):
    title: str
    hook: str
    segments: list[ScriptSegment]
    ending: str

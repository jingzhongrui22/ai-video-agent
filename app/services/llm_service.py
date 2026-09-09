"""通过 DeepSeek Chat Completions 生成结构化短视频脚本。"""

import json

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from app.prompts.script_prompt import SYSTEM_PROMPT, build_user_prompt
from app.schemas.script import VideoScript


async def generate_video_script(
    text: str,
    style: str,
    duration: int,
) -> VideoScript:
    if not DEEPSEEK_BASE_URL or not DEEPSEEK_MODEL:
        raise ValueError("请配置非空 DEEPSEEK_BASE_URL 和 DEEPSEEK_MODEL。")

    user_prompt = build_user_prompt(text, style, duration)
    try:
        async with AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            timeout=60.0,
            max_retries=0,
        ) as client:
            response = await client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
    except Exception:
        # 不传播 SDK 原始错误或响应体，避免其中包含认证信息。
        raise RuntimeError("DeepSeek 请求失败，请检查网络、服务状态和配置。") from None

    if not response.choices:
        raise ValueError("DeepSeek 返回为空：没有生成结果。")
    choice = response.choices[0]
    if choice.finish_reason == "length":
        raise ValueError("DeepSeek 返回内容被截断，无法获取完整脚本。")
    content = choice.message.content
    if not content or not content.strip():
        raise ValueError("DeepSeek 返回内容为空，无法解析 JSON。")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("DeepSeek 返回内容不是合法 JSON，脚本解析失败。") from None
    try:
        return VideoScript.model_validate(data)
    except ValidationError:
        raise ValueError("DeepSeek 返回 JSON 不符合 VideoScript 数据结构。") from None

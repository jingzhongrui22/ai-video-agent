"""从项目根目录的 .env 读取 DeepSeek 配置，不发起网络请求。"""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", encoding="utf-8", override=False)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "").strip()

if not DEEPSEEK_API_KEY:
    raise ValueError(
        "缺少 DEEPSEEK_API_KEY：请在项目根目录的 .env 文件或环境变量中配置非空 API Key。"
    )

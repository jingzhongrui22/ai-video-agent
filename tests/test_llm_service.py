"""使用模拟 SDK 验证服务，不读取真实密钥或访问网络。"""

import importlib.util
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import traceback
import unittest
from unittest.mock import AsyncMock, patch


class LLMServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        config = ModuleType("app.core.config")
        config.DEEPSEEK_API_KEY = "test-placeholder"
        config.DEEPSEEK_BASE_URL = "https://example.invalid"
        config.DEEPSEEK_MODEL = "test-model"
        path = Path(__file__).resolve().parents[1] / "app/services/llm_service.py"
        spec = importlib.util.spec_from_file_location("tested_llm_service", path)
        self.service = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"app.core.config": config}):
            spec.loader.exec_module(self.service)
        self.client = AsyncMock()
        self.client.__aenter__.return_value = self.client
        self.create = self.client.chat.completions.create
        self.sdk = patch.object(self.service, "AsyncOpenAI", return_value=self.client)
        self.factory = self.sdk.start()
        self.addCleanup(self.sdk.stop)

    def respond(self, content: str | None, finish_reason: str = "stop") -> None:
        self.create.return_value = SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content=content), finish_reason=finish_reason,
        )])

    async def test_success(self) -> None:
        data = {"title": "Title", "hook": "Hook", "segments": [
            {"id": 1, "text": "Text", "emotion": "neutral", "speed": 1.0, "pause_after": 0.5}
        ], "ending": "Ending"}
        self.respond(json.dumps(data))
        result = await self.service.generate_video_script("Input", "knowledge", 60)
        self.assertEqual(result.model_dump(), data)
        self.factory.assert_called_once_with(
            api_key="test-placeholder", base_url="https://example.invalid",
            timeout=60.0, max_retries=0,
        )
        self.create.assert_awaited_once()
        args = self.create.call_args.kwargs
        self.assertEqual(args["model"], "test-model")
        self.assertEqual(args["response_format"], {"type": "json_object"})
        self.assertEqual(args["messages"][0]["content"], self.service.SYSTEM_PROMPT)
        self.assertEqual(args["messages"][1]["content"], self.service.build_user_prompt("Input", "knowledge", 60))
        self.client.__aexit__.assert_awaited_once()

    async def test_invalid_responses(self) -> None:
        for content, reason, expected in [
            (None, "stop", "为空"), (" ", "stop", "为空"),
            ("not json", "stop", "不是合法 JSON"),
            ("{}", "stop", "不符合 VideoScript"),
            ("null", "stop", "不符合 VideoScript"),
            ("{", "length", "截断"),
        ]:
            with self.subTest(content=content, reason=reason):
                self.respond(content, reason)
                with self.assertRaisesRegex(ValueError, expected):
                    await self.service.generate_video_script("Input", "knowledge", 60)
        self.create.return_value = SimpleNamespace(choices=[])
        with self.assertRaisesRegex(ValueError, "没有生成结果"):
            await self.service.generate_video_script("Input", "knowledge", 60)

    async def test_request_error_is_sanitized(self) -> None:
        self.create.side_effect = RuntimeError("secret: test-placeholder")
        try:
            await self.service.generate_video_script("Input", "knowledge", 60)
        except RuntimeError:
            rendered = traceback.format_exc()
            self.assertIn("DeepSeek 请求失败", rendered)
            self.assertNotIn("test-placeholder", rendered)
        else:
            self.fail("Expected request failure")
        self.create.assert_awaited_once()

    async def test_missing_model_configuration(self) -> None:
        with patch.object(self.service, "DEEPSEEK_MODEL", ""):
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_MODEL"):
                await self.service.generate_video_script("Input", "knowledge", 60)
        self.factory.assert_not_called()

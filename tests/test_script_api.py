"""模拟脚本服务验证 API，不读取密钥或调用外部 API。"""

from types import ModuleType
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.script import VideoScript


class ScriptAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ModuleType("app.services.llm_service")
        self.generate = AsyncMock()
        self.service.generate_video_script = self.generate
        patcher = patch.dict("sys.modules", {"app.services.llm_service": self.service})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = self.enterContext(TestClient(app))

    def test_success_and_defaults(self) -> None:
        data = {
            "title": "Title", "hook": "Hook", "segments": [
                {"id": 1, "text": "Text", "emotion": "neutral", "speed": 1.0, "pause_after": 0.5}
            ], "ending": "Ending",
        }
        self.generate.return_value = VideoScript.model_validate(data)
        for body in ({"text": "Input"}, {"text": "Input", "style": "story", "duration": 30}):
            with self.subTest(body=body):
                self.generate.reset_mock()
                response = self.client.post("/api/script/generate", json=body)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), data)
                self.generate.assert_awaited_once_with(
                    text="Input", style=body.get("style", "knowledge"),
                    duration=body.get("duration", 60),
                )

    def test_invalid_request(self) -> None:
        for body in ({}, {"text": ""}, {"text": " \t"}, {"text": "Input", "duration": 0}, {"text": "Input", "duration": -1}):
            with self.subTest(body=body):
                response = self.client.post("/api/script/generate", json=body)
                self.assertEqual(response.status_code, 422)
        self.generate.assert_not_awaited()

    def test_service_errors_are_sanitized(self) -> None:
        for error in (RuntimeError, ValueError, Exception):
            with self.subTest(error=error):
                self.generate.side_effect = error("API Key: private-test-value")
                response = self.client.post("/api/script/generate", json={"text": "Input"})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json(), {"detail": "脚本生成失败，请稍后再试。"})

    def test_unavailable_service_preserves_health(self) -> None:
        with patch.dict("sys.modules", {"app.services.llm_service": None}):
            response = self.client.post("/api/script/generate", json={"text": "Input"})
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"detail": "脚本生成服务暂不可用，请联系管理员检查配置。"})
            health = self.client.get("/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json(), {"status": "ok", "service": "ai-video-agent"})
        self.generate.assert_not_awaited()

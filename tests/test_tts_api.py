"""模拟 TTS 服务验证接口，不请求外部服务或生成音频。"""

from types import ModuleType
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


class TTSAPITests(unittest.TestCase):
    def setUp(self) -> None:
        service = ModuleType("app.services.tts_service")
        self.synthesize = AsyncMock(return_value="storage/audio/test.mp3")
        service.synthesize_text = self.synthesize
        self.enterContext(patch.dict("sys.modules", {"app.services.tts_service": service}))
        self.client = self.enterContext(TestClient(app))

    def test_success_and_default_voice(self) -> None:
        for voice in (None, "zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural"):
            with self.subTest(voice=voice):
                self.synthesize.reset_mock()
                body = {"text": "要合成的中文文本"}
                if voice is not None:
                    body["voice"] = voice
                response = self.client.post("/api/tts/generate", json=body)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"audio_path": "storage/audio/test.mp3"})
                self.synthesize.assert_awaited_once_with(
                    text=body["text"], voice=voice or "zh-CN-YunxiNeural",
                )

    def test_invalid_text(self) -> None:
        for body in ({}, {"text": ""}, {"text": " \n\t"}, {"text": None}, {"text": 123}):
            with self.subTest(body=body):
                response = self.client.post("/api/tts/generate", json=body)
                self.assertEqual(response.status_code, 422)
        self.synthesize.assert_not_awaited()

    def test_service_errors_are_sanitized(self) -> None:
        for error in (RuntimeError, ValueError, OSError):
            with self.subTest(error=error):
                self.synthesize.side_effect = error("secret-token private-path")
                response = self.client.post("/api/tts/generate", json={"text": "你好"})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json(), {"detail": "语音合成失败，请稍后再试。"})

    def test_unavailable_service_preserves_health(self) -> None:
        with patch.dict("sys.modules", {"app.services.tts_service": None}):
            response = self.client.post("/api/tts/generate", json={"text": "你好"})
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"detail": "语音合成服务暂不可用，请稍后再试。"})
            health = self.client.get("/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json(), {"status": "ok", "service": "ai-video-agent"})
        self.synthesize.assert_not_awaited()

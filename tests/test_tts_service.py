"""Run locally: python -m unittest discover -s tests -p test_tts_service.py -v

The speech test contacts the Edge TTS service and keeps the MP3 for playback.
"""

from pathlib import Path
import unittest
from uuid import UUID

from app.services.tts_service import synthesize_text


class TTSServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_text(self) -> None:
        for text in ("", "   ", "\n\t"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    await synthesize_text(text)

    async def test_generate_chinese_mp3(self) -> None:
        result = await synthesize_text("你好，这是AI视频智能体的语音测试。")
        self.assertIsInstance(result, str)
        path = Path(result)
        self.assertEqual(
            path.parent,
            Path(__file__).resolve().parents[1] / "storage" / "audio",
        )
        self.assertEqual(path.suffix, ".mp3")
        self.assertEqual(UUID(path.stem).version, 4)
        self.assertTrue(path.is_file())
        self.assertGreater(path.stat().st_size, 0)
        print(f"Generated MP3: {path}")


if __name__ == "__main__":
    unittest.main()

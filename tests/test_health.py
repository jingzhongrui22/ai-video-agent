"""健康检查接口测试，无需启动服务器或访问外部网络。"""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class HealthTests(unittest.TestCase):
    def test_health(self) -> None:
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "service": "ai-video-agent"},
        )


if __name__ == "__main__":
    unittest.main()

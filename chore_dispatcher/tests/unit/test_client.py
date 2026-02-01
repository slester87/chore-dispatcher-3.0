import json
import unittest

import httpx

from chore_dispatcher.client import ChoreDispatcherClient


class TestClient(unittest.TestCase):
    def test_request_success(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            payload = json.loads(request.content.decode("utf-8"))
            if payload["method"] == "health":
                return httpx.Response(200, json={"id": None, "result": {"status": "ok"}})
            return httpx.Response(200, json={"id": None, "result": {"ok": True}})

        transport = httpx.MockTransport(handler)
        client = ChoreDispatcherClient("http://test", timeout=5)
        client._client = httpx.Client(transport=transport)

        result = client.health()
        self.assertEqual(result, {"status": "ok"})
        client.close()

    def test_request_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"id": None, "error": {"message": "bad"}})

        transport = httpx.MockTransport(handler)
        client = ChoreDispatcherClient("http://test", timeout=5)
        client._client = httpx.Client(transport=transport)

        with self.assertRaises(RuntimeError):
            client.list_active()

        client.close()


if __name__ == "__main__":
    unittest.main()

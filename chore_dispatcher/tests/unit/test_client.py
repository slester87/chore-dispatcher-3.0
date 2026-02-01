import json
import unittest

import httpx

from chore_dispatcher.client import ChoreDispatcherClient


class TestClient(unittest.TestCase):
    def test_request_payload_defaults_params(self) -> None:
        captured: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"id": None, "result": {"status": "ok"}})

        transport = httpx.MockTransport(handler)
        client = ChoreDispatcherClient("http://test/", timeout=5)
        client._client = httpx.Client(transport=transport)

        result = client.health()

        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(captured["url"], "http://test/api")
        self.assertEqual(captured["json"], {"method": "health", "params": {}})
        client.close()

    def test_request_payload_includes_params(self) -> None:
        captured: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"id": None, "result": {"ok": True}})

        transport = httpx.MockTransport(handler)
        client = ChoreDispatcherClient("http://test", timeout=5)
        client._client = httpx.Client(transport=transport)

        result = client.create("Example chore", "Details")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            captured["json"],
            {"method": "create", "params": {"name": "Example chore", "description": "Details"}},
        )
        client.close()

    def test_request_payload_nested_params(self) -> None:
        captured: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["json"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(200, json={"id": None, "result": {"ok": True}})

        transport = httpx.MockTransport(handler)
        client = ChoreDispatcherClient("http://test", timeout=5)
        client._client = httpx.Client(transport=transport)

        result = client.update(12, {"status": "WORK", "owner": "planner"})

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            captured["json"],
            {"method": "update", "params": {"id": 12, "fields": {"status": "WORK", "owner": "planner"}}},
        )
        client.close()

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

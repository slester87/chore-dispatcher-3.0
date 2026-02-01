import tempfile
import unittest
from pathlib import Path

import httpx

from chore_dispatcher.client import ChoreDispatcherClient
from chore_dispatcher.mcp.http_server import build_app


def _write_config(tmpdir: str) -> str:
    config_path = Path(tmpdir) / "config.toml"
    config_path.write_text(
        "node_id = 1\n"
        f"store_root = \"{tmpdir}\"\n"
        "active_store_path = \"active.jsonl\"\n"
        "archive_store_path = \"archive.jsonl\"\n"
        f"signal_dir = \"{tmpdir}\"\n"
        "tmux_enabled = false\n"
    )
    return str(config_path)


class TestHttpClientIntegration(unittest.TestCase):
    def test_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = build_app(_write_config(tmpdir))
            transport = httpx.ASGITransport(app=app)
            client = ChoreDispatcherClient("http://test", timeout=5)
            client._client = httpx.Client(transport=transport, base_url="http://test")

            try:
                result = client.health()
                self.assertEqual(result, {"status": "ok"})
            finally:
                client.close()

    def test_create_and_list_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = build_app(_write_config(tmpdir))
            transport = httpx.ASGITransport(app=app)
            client = ChoreDispatcherClient("http://test", timeout=5)
            client._client = httpx.Client(transport=transport, base_url="http://test")

            try:
                created = client.create("End-to-end")
                self.assertEqual(created["name"], "End-to-end")

                listed = client.list_active()
                self.assertEqual(len(listed), 1)
                self.assertEqual(listed[0]["name"], "End-to-end")
            finally:
                client.close()


if __name__ == "__main__":
    unittest.main()

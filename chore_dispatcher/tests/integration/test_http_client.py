import tempfile
import unittest
from pathlib import Path

import asyncio
import httpx
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

            async def run() -> dict:
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post("/api", json={"method": "health", "params": {}})
                    response.raise_for_status()
                    return response.json()["result"]

            result = asyncio.run(run())
            self.assertEqual(result, {"status": "ok"})

    def test_create_and_list_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = build_app(_write_config(tmpdir))
            transport = httpx.ASGITransport(app=app)

            async def run() -> tuple[dict, list[dict]]:
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    create = await client.post(
                        "/api", json={"method": "create", "params": {"name": "End-to-end", "description": ""}}
                    )
                    create.raise_for_status()
                    created = create.json()["result"]

                    listed = await client.post("/api", json={"method": "list_active", "params": {}})
                    listed.raise_for_status()
                    return created, listed.json()["result"]

            created, listed = asyncio.run(run())
            self.assertEqual(created["name"], "End-to-end")
            self.assertEqual(len(listed), 1)
            self.assertEqual(listed[0]["name"], "End-to-end")


if __name__ == "__main__":
    unittest.main()

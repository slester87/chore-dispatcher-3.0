import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chore_dispatcher.mcp.server import MCPServer
from chore_dispatcher.special import SPECIAL_CHORE_ID, SPECIAL_CHORE_NAME


def _write_config(tmpdir: str, tmux_enabled: bool = True) -> str:
    config_path = Path(tmpdir) / "config.toml"
    config_path.write_text(
        "node_id = 1\n"
        f"store_root = \"{tmpdir}\"\n"
        "active_store_path = \"active.jsonl\"\n"
        "archive_store_path = \"archive.jsonl\"\n"
        f"signal_dir = \"{tmpdir}\"\n"
        f"tmux_enabled = {str(tmux_enabled).lower()}\n"
    )
    return str(config_path)


class TestSpecialChore(unittest.TestCase):
    def test_read_special_chore(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            response = server.handle_request({"id": 1, "method": "read", "params": {"id": SPECIAL_CHORE_ID}})
            self.assertEqual(response["result"]["id"], SPECIAL_CHORE_ID)
            self.assertEqual(response["result"]["name"], SPECIAL_CHORE_NAME)

    def test_special_chore_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            response = server.handle_request(
                {"id": 1, "method": "update", "params": {"id": SPECIAL_CHORE_ID, "fields": {"name": "Nope"}}}
            )
            self.assertIn("error", response)
            self.assertIn("read-only", response["error"]["message"])

    def test_launch_bootstrap_planner_calls_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir, tmux_enabled=True))
            with patch("chore_dispatcher.mcp.server.dispatch_bootstrap_planner") as mocked:
                server.launch_bootstrap_planner()
                mocked.assert_called_once()


if __name__ == "__main__":
    unittest.main()

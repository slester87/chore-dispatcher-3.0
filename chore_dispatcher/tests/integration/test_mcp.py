import tempfile
import unittest
from pathlib import Path

from chore_dispatcher.mcp.server import MCPServer
from chore_dispatcher.models.status import ChoreStatus


def _write_config(tmpdir: str) -> str:
    config_path = Path(tmpdir) / "config.toml"
    config_path.write_text(
        "node_id = 1\n"
        f"store_root = \"{tmpdir}\"\n"
        "active_store_path = \"active.jsonl\"\n"
        "archive_store_path = \"archive.jsonl\"\n"
    )
    return str(config_path)


class TestMcpServer(unittest.TestCase):
    def test_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            response = server.handle_request({"id": 1, "method": "health"})
            self.assertEqual(response, {"id": 1, "result": {"status": "ok"}})

    def test_crud_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))

            created = server.handle_request({"id": 1, "method": "create", "params": {"name": "Test"}})
            chore_id = created["result"]["id"]

            listed = server.handle_request({"id": 2, "method": "list"})
            self.assertEqual(len(listed["result"]), 1)

            read = server.handle_request({"id": 3, "method": "read", "params": {"id": chore_id}})
            self.assertEqual(read["result"]["name"], "Test")

            updated = server.handle_request(
                {"id": 4, "method": "update", "params": {"id": chore_id, "fields": {"description": "Done"}}}
            )
            self.assertEqual(updated["result"]["description"], "Done")

            deleted = server.handle_request({"id": 5, "method": "delete", "params": {"id": chore_id}})
            self.assertTrue(deleted["result"]["deleted"])

    def test_hierarchy_and_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            parent = server.handle_request({"id": 1, "method": "create", "params": {"name": "Parent"}})
            parent_id = parent["result"]["id"]

            child = server.handle_request(
                {"id": 2, "method": "create_sub_chore", "params": {"parent_id": parent_id, "name": "Child"}}
            )
            child_id = child["result"]["id"]

            sub_chores = server.handle_request({"id": 3, "method": "get_sub_chores", "params": {"parent_id": parent_id}})
            self.assertEqual([c["id"] for c in sub_chores["result"]], [child_id])

            next_chore = server.handle_request(
                {"id": 4, "method": "set_next_chore", "params": {"id": parent_id, "next_id": child_id}}
            )
            self.assertEqual(next_chore["result"]["next_chore_id"], child_id)

    def test_archive_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            created = server.handle_request({"id": 1, "method": "create", "params": {"name": "Done"}})
            chore_id = created["result"]["id"]

            server.handle_request(
                {"id": 2, "method": "update", "params": {"id": chore_id, "fields": {"status": ChoreStatus.WORK_DONE.value}}}
            )

            archived = server.handle_request({"id": 3, "method": "archive_chore", "params": {"id": chore_id}})
            self.assertTrue(archived["result"]["archived"])

            archive_list = server.handle_request({"id": 4, "method": "list_archive"})
            self.assertEqual(len(archive_list["result"]), 1)


if __name__ == "__main__":
    unittest.main()

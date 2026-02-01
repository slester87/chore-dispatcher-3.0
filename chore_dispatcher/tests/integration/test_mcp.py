import tempfile
import unittest
from pathlib import Path

from chore_dispatcher.mcp.server import MCPServer
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.repo.persistence import save_active_and_archive_atomic
from chore_dispatcher.models.chore import Chore


def _write_config(tmpdir: str) -> str:
    config_path = Path(tmpdir) / "config.toml"
    config_path.write_text(
        "node_id = 1\n"
        f"store_root = \"{tmpdir}\"\n"
        "active_store_path = \"active.jsonl\"\n"
        "archive_store_path = \"archive.jsonl\"\n"
        f"signal_dir = \"{tmpdir}\"\n"
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
            list_all = server.handle_request({"id": 5, "method": "list_all"})
            self.assertEqual(len(list_all["result"]), 1)

    def test_advance_to_next(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            created = server.handle_request({"id": 1, "method": "create", "params": {"name": "Advance"}})
            chore_id = created["result"]["id"]

            advanced = server.handle_request({"id": 2, "method": "advance_to_next", "params": {"id": chore_id}})
            self.assertEqual(advanced["result"]["status"], ChoreStatus.PLAN_REVIEW.value)

    def test_process_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            created = server.handle_request({"id": 1, "method": "create", "params": {"name": "Signal"}})
            chore_id = created["result"]["id"]

            signal_path = Path(tmpdir) / f"chore_{chore_id}_complete"
            signal_path.write_text("done")

            processed = server.handle_request({"id": 2, "method": "process_signals", "params": {"id": chore_id}})
            self.assertIn("complete", processed["result"]["events"])

            read = server.handle_request({"id": 3, "method": "read", "params": {"id": chore_id}})
            self.assertEqual(read["result"]["status"], ChoreStatus.PLAN_REVIEW.value)

    def test_get_sub_chores_recursive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            parent = server.handle_request({"id": 1, "method": "create", "params": {"name": "Parent"}})
            parent_id = parent["result"]["id"]
            child = server.handle_request(
                {"id": 2, "method": "create_sub_chore", "params": {"parent_id": parent_id, "name": "Child"}}
            )
            child_id = child["result"]["id"]
            server.handle_request(
                {"id": 3, "method": "create_sub_chore", "params": {"parent_id": child_id, "name": "Grandchild"}}
            )

            direct = server.handle_request(
                {"id": 4, "method": "get_sub_chores", "params": {"parent_id": parent_id}}
            )
            self.assertEqual(len(direct["result"]), 1)

            recursive = server.handle_request(
                {"id": 5, "method": "get_sub_chores", "params": {"parent_id": parent_id, "recursive": True}}
            )
            self.assertEqual(len(recursive["result"]), 2)

    def test_repair_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            parent = server.handle_request({"id": 1, "method": "create", "params": {"name": "Parent"}})
            parent_id = parent["result"]["id"]
            child = server.handle_request(
                {"id": 2, "method": "create_sub_chore", "params": {"parent_id": parent_id, "name": "Child"}}
            )
            child_id = child["result"]["id"]

            server.handle_request(
                {"id": 3, "method": "update", "params": {"id": child_id, "fields": {"parent_chore_id": 999}}}
            )

            result = server.handle_request({"id": 4, "method": "repair_integrity"})
            self.assertEqual(result["result"]["errors"], [])
            self.assertEqual(len(result["result"]["orphans"]), 1)

    def test_repair_integrity_exclusivity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = MCPServer(_write_config(tmpdir))
            chore = Chore(id=42, name="Conflict", status=ChoreStatus.WORK_DONE)
            active_path = Path(tmpdir) / "active.jsonl"
            archive_path = Path(tmpdir) / "archive.jsonl"
            save_active_and_archive_atomic(active_path, archive_path, [chore], [chore])

            repaired = server.handle_request({"id": 1, "method": "repair_integrity"})
            self.assertIn(42, repaired["result"]["removed_from_active"])


if __name__ == "__main__":
    unittest.main()

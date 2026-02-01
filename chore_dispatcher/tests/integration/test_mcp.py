import unittest

from chore_dispatcher.mcp.server import handle_request


class TestMcpServer(unittest.TestCase):
    def test_health(self) -> None:
        response = handle_request({"id": 1, "method": "health"})
        self.assertEqual(response, {"id": 1, "result": {"status": "ok"}})

    def test_unknown_method(self) -> None:
        response = handle_request({"id": "x", "method": "nope"})
        self.assertEqual(response["id"], "x")
        self.assertIn("error", response)


if __name__ == "__main__":
    unittest.main()

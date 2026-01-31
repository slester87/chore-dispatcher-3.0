import threading
import unittest

from chore_dispatcher.id.snowflake import MAX_NODE_ID, Snowflake


class TestSnowflake(unittest.TestCase):
    def test_node_id_bounds(self) -> None:
        with self.assertRaises(ValueError):
            Snowflake(-1)
        with self.assertRaises(ValueError):
            Snowflake(MAX_NODE_ID + 1)

    def test_unique_ids(self) -> None:
        snowflake = Snowflake(1)
        ids = {snowflake.next_id() for _ in range(1000)}
        self.assertEqual(len(ids), 1000)

    def test_monotonic_in_thread(self) -> None:
        snowflake = Snowflake(1)
        last = snowflake.next_id()
        for _ in range(1000):
            current = snowflake.next_id()
            self.assertGreater(current, last)
            last = current

    def test_thread_safety(self) -> None:
        snowflake = Snowflake(1)
        results = []
        lock = threading.Lock()

        def worker() -> None:
            local = [snowflake.next_id() for _ in range(200)]
            with lock:
                results.extend(local)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(len(results), 2000)
        self.assertEqual(len(set(results)), 2000)


if __name__ == "__main__":
    unittest.main()

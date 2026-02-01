from __future__ import annotations

import json
import sys
from typing import Any


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    request_id = payload.get("id")
    method = payload.get("method")

    if method == "health":
        return {"id": request_id, "result": {"status": "ok"}}

    return {"id": request_id, "error": {"message": f"Unknown method: {method}"}}


def run() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({"error": {"message": "Invalid JSON"}}) + "\n")
            sys.stdout.flush()
            continue

        response = handle_request(payload)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

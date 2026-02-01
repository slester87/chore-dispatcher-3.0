from __future__ import annotations

import json
import os
import sys
from typing import Any

from chore_dispatcher.config import load_config
from chore_dispatcher.id.snowflake import Snowflake
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.repo.persistence import serialize_chore
from chore_dispatcher.repo.unit_of_work import FileUnitOfWork


def _response(request_id: Any, result: Any | None = None, error: str | None = None) -> dict[str, Any]:
    if error is not None:
        return {"id": request_id, "error": {"message": error}}
    return {"id": request_id, "result": result}


class MCPServer:
    def __init__(self, config_path: str | None = None) -> None:
        config = load_config(config_path)
        self._snowflake = Snowflake(config.node_id)
        self._config = config

    def list_active(self) -> list[dict[str, Any]]:
        uow = FileUnitOfWork(self._config, self._snowflake.next_id)
        uow.begin()
        repo = uow.repository()
        chores = [serialize_chore(chore) for chore in repo.list_all()]
        uow.rollback()
        return chores

    def handle_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params") or {}

        if method == "health":
            return _response(request_id, {"status": "ok"})

        if method == "list":
            return _response(request_id, self.list_active())

        uow = FileUnitOfWork(self._config, self._snowflake.next_id)
        uow.begin()
        repo = uow.repository()

        try:
            if method == "create":
                chore = repo.create(params["name"], params.get("description", ""))
                uow.commit()
                return _response(request_id, serialize_chore(chore))
            if method == "read":
                chore = repo.read(params["id"])
                uow.rollback()
                return _response(request_id, serialize_chore(chore) if chore else None)
            if method == "update":
                chore = repo.update(params["id"], **params.get("fields", {}))
                uow.commit()
                return _response(request_id, serialize_chore(chore) if chore else None)
            if method == "delete":
                deleted = repo.delete(params["id"])
                uow.commit()
                return _response(request_id, {"deleted": deleted})
            if method == "find_by_status":
                status = ChoreStatus(params["status"])
                matches = repo.find_by_status(status)
                uow.rollback()
                return _response(request_id, [serialize_chore(chore) for chore in matches])
        except KeyError as exc:
            uow.rollback()
            return _response(request_id, error=f"Missing parameter: {exc.args[0]}")
        except Exception as exc:
            uow.rollback()
            return _response(request_id, error=str(exc))

        uow.rollback()
        return _response(request_id, error=f"Unknown method: {method}")


def run() -> int:
    config_path = os.environ.get("CHORE_DISPATCHER_CONFIG")
    server = MCPServer(config_path)

    sys.stdout.write(json.dumps({"event": "active_chores", "result": server.list_active()}) + "\n")
    sys.stdout.flush()

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

        response = server.handle_request(payload)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

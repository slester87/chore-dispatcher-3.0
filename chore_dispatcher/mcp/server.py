from __future__ import annotations

import json
import os
import sys
from typing import Any

from chore_dispatcher.config import load_config
from chore_dispatcher.id.snowflake import Snowflake
from chore_dispatcher.models.status import ChoreStatus, next_status
from chore_dispatcher.repo.persistence import serialize_chore
from chore_dispatcher.repo.unit_of_work import FileUnitOfWork
from chore_dispatcher.signals.signals import SignalWatcher
from chore_dispatcher.workflow.chain import validate_chain_integrity
from chore_dispatcher.workflow.errors import TransitionError, ValidationError
from chore_dispatcher.workflow.transitions import StateTransitionEngine


def _response(request_id: Any, result: Any | None = None, error: str | None = None) -> dict[str, Any]:
    if error is not None:
        return {"id": request_id, "error": {"message": error}}
    return {"id": request_id, "result": result}


class MCPServer:
    def __init__(self, config_path: str | None = None) -> None:
        config = load_config(config_path)
        self._snowflake = Snowflake(config.node_id)
        self._config = config
        self._transitions = StateTransitionEngine()
        self._signals = SignalWatcher(config.signal_dir, poll_interval=1.0)

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
            if method == "create_sub_chore":
                chore = repo.create_sub_chore(params["parent_id"], params["name"], params.get("description", ""))
                uow.commit()
                return _response(request_id, serialize_chore(chore) if chore else None)
            if method == "get_sub_chores":
                chores = repo.get_sub_chores(params["parent_id"])
                uow.rollback()
                return _response(request_id, [serialize_chore(chore) for chore in chores])
            if method == "get_parent_chore":
                chore = repo.get_parent_chore(params["id"])
                uow.rollback()
                return _response(request_id, serialize_chore(chore) if chore else None)
            if method == "find_root_chores":
                chores = repo.find_root_chores()
                uow.rollback()
                return _response(request_id, [serialize_chore(chore) for chore in chores])
            if method == "set_next_chore":
                chore = repo.read(params["id"])
                next_chore = repo.read(params["next_id"])
                if chore is None or next_chore is None:
                    raise KeyError("id")
                chore.set_next_chore(next_chore)
                uow.commit()
                return _response(request_id, serialize_chore(chore))
            if method == "get_next_chore":
                chore = repo.read(params["id"])
                if chore is None:
                    uow.rollback()
                    return _response(request_id, None)
                next_chore = chore.get_next_chore()
                uow.rollback()
                return _response(request_id, serialize_chore(next_chore) if next_chore else None)
            if method == "advance_status":
                chore = repo.read(params["id"])
                if chore is None:
                    uow.rollback()
                    return _response(request_id, None)
                to_status = ChoreStatus(params["to_status"])
                self._transitions.execute_transition(chore, to_status)
                uow.commit()
                return _response(request_id, serialize_chore(chore))
            if method == "advance_to_next":
                chore = repo.read(params["id"])
                if chore is None:
                    uow.rollback()
                    return _response(request_id, None)
                expected = next_status(chore.status)
                if expected is None:
                    raise TransitionError("No further status available")
                self._transitions.execute_transition(chore, expected)
                uow.commit()
                return _response(request_id, serialize_chore(chore))
            if method == "validate_chain_integrity":
                errors = validate_chain_integrity({chore.id: chore for chore in repo.list_all()})
                uow.rollback()
                return _response(request_id, {"errors": errors})
            if method == "list_archive":
                chores = list(uow.archive_store.values())
                uow.rollback()
                return _response(request_id, [serialize_chore(chore) for chore in chores])
            if method == "archive_chore":
                chore = repo.read(params["id"])
                if chore is None:
                    uow.rollback()
                    return _response(request_id, None)
                if chore.status != ChoreStatus.WORK_DONE:
                    raise ValidationError("Only WORK_DONE chores can be archived")
                uow.archive_store[chore.id] = chore
                repo.delete(chore.id)
                uow.commit()
                return _response(request_id, {"archived": True, "id": chore.id})
            if method == "process_signals":
                chore = repo.read(params["id"])
                if chore is None:
                    uow.rollback()
                    return _response(request_id, None)

                events: list[str] = []

                def on_complete(ch: Any) -> None:
                    events.append("complete")
                    expected = next_status(ch.status)
                    if expected is None:
                        raise TransitionError("No further status available")
                    self._transitions.execute_transition(ch, expected)

                def on_exit(ch: Any) -> None:
                    events.append("exit")

                self._signals.check(chore, on_complete, on_exit)
                uow.commit()
                return _response(request_id, {"events": events, "chore": serialize_chore(chore)})
        except KeyError as exc:
            uow.rollback()
            return _response(request_id, error=f"Missing parameter: {exc.args[0]}")
        except (TransitionError, ValidationError) as exc:
            uow.rollback()
            return _response(request_id, error=str(exc))
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

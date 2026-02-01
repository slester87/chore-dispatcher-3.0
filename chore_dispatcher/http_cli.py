from __future__ import annotations

import argparse
import json
from typing import Any

from chore_dispatcher.client import ChoreDispatcherClient


def _print(result: Any) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chore-dispatcher-http")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="Base URL for server")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health")
    sub.add_parser("list-active")
    sub.add_parser("list-all")
    sub.add_parser("list-archive")

    create = sub.add_parser("create")
    create.add_argument("name")
    create.add_argument("--description", default="")

    read = sub.add_parser("read")
    read.add_argument("id", type=int)

    update = sub.add_parser("update")
    update.add_argument("id", type=int)
    update.add_argument("--fields", required=True, help="JSON dict of fields to update")

    delete = sub.add_parser("delete")
    delete.add_argument("id", type=int)

    find = sub.add_parser("find-by-status")
    find.add_argument("status")

    create_sub = sub.add_parser("create-sub-chore")
    create_sub.add_argument("parent_id", type=int)
    create_sub.add_argument("name")
    create_sub.add_argument("--description", default="")

    get_sub = sub.add_parser("get-sub-chores")
    get_sub.add_argument("parent_id", type=int)
    get_sub.add_argument("--recursive", action="store_true")

    get_parent = sub.add_parser("get-parent-chore")
    get_parent.add_argument("id", type=int)

    sub.add_parser("find-root-chores")

    set_next = sub.add_parser("set-next-chore")
    set_next.add_argument("id", type=int)
    set_next.add_argument("next_id", type=int)

    get_next = sub.add_parser("get-next-chore")
    get_next.add_argument("id", type=int)

    advance = sub.add_parser("advance-status")
    advance.add_argument("id", type=int)
    advance.add_argument("to_status")

    advance_next = sub.add_parser("advance-to-next")
    advance_next.add_argument("id", type=int)

    sub.add_parser("validate-chain-integrity")
    sub.add_parser("repair-integrity")

    archive = sub.add_parser("archive-chore")
    archive.add_argument("id", type=int)

    process = sub.add_parser("process-signals")
    process.add_argument("id", type=int)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    with ChoreDispatcherClient(args.base_url) as client:
        cmd = args.command
        if cmd == "health":
            _print(client.health())
        elif cmd == "list-active":
            _print(client.list_active())
        elif cmd == "list-all":
            _print(client.list_all())
        elif cmd == "list-archive":
            _print(client.list_archive())
        elif cmd == "create":
            _print(client.create(args.name, args.description))
        elif cmd == "read":
            _print(client.read(args.id))
        elif cmd == "update":
            fields = json.loads(args.fields)
            _print(client.update(args.id, fields))
        elif cmd == "delete":
            _print(client.delete(args.id))
        elif cmd == "find-by-status":
            _print(client.find_by_status(args.status))
        elif cmd == "create-sub-chore":
            _print(client.create_sub_chore(args.parent_id, args.name, args.description))
        elif cmd == "get-sub-chores":
            _print(client.get_sub_chores(args.parent_id, args.recursive))
        elif cmd == "get-parent-chore":
            _print(client.get_parent_chore(args.id))
        elif cmd == "find-root-chores":
            _print(client.find_root_chores())
        elif cmd == "set-next-chore":
            _print(client.set_next_chore(args.id, args.next_id))
        elif cmd == "get-next-chore":
            _print(client.get_next_chore(args.id))
        elif cmd == "advance-status":
            _print(client.advance_status(args.id, args.to_status))
        elif cmd == "advance-to-next":
            _print(client.advance_to_next(args.id))
        elif cmd == "validate-chain-integrity":
            _print(client.validate_chain_integrity())
        elif cmd == "repair-integrity":
            _print(client.repair_integrity())
        elif cmd == "archive-chore":
            _print(client.archive_chore(args.id))
        elif cmd == "process-signals":
            _print(client.process_signals(args.id))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

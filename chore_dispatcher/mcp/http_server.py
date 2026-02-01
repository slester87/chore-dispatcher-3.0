from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from chore_dispatcher.config import load_config
from chore_dispatcher.mcp.server import MCPServer


class ApiRequest(BaseModel):
    id: Any | None = None
    method: str
    params: dict[str, Any] | None = None


def _make_server(config_path: str | None) -> MCPServer:
    return MCPServer(config_path)


def _tool_response(method: str, params: dict[str, Any], server: MCPServer) -> dict[str, Any]:
    return server.handle_request({"id": "http", "method": method, "params": params}).get("result")


def build_app(config_path: str | None = None) -> FastAPI:
    config = load_config(config_path)
    if config.mcp_path in {"/api", "/", ""}:
        raise ValueError(
            f"mcp_path cannot be '{config.mcp_path}'; it conflicts with the HTTP RPC endpoint"
        )
    server = _make_server(config_path)
    mcp = FastMCP("chore-dispatcher")

    @mcp.tool()
    def health() -> dict[str, Any]:
        return _tool_response("health", {}, server)

    @mcp.tool()
    def list_active() -> list[dict[str, Any]]:
        return _tool_response("list_active", {}, server)

    @mcp.tool()
    def list_all() -> list[dict[str, Any]]:
        return _tool_response("list_all", {}, server)

    @mcp.tool()
    def list_archive() -> list[dict[str, Any]]:
        return _tool_response("list_archive", {}, server)

    @mcp.tool()
    def create(name: str, description: str = "") -> dict[str, Any]:
        return _tool_response("create", {"name": name, "description": description}, server)

    @mcp.tool()
    def read(id: int) -> dict[str, Any] | None:
        return _tool_response("read", {"id": id}, server)

    @mcp.tool()
    def update(id: int, fields: dict[str, Any]) -> dict[str, Any] | None:
        return _tool_response("update", {"id": id, "fields": fields}, server)

    @mcp.tool()
    def delete(id: int) -> dict[str, Any]:
        return _tool_response("delete", {"id": id}, server)

    @mcp.tool()
    def find_by_status(status: str) -> list[dict[str, Any]]:
        return _tool_response("find_by_status", {"status": status}, server)

    @mcp.tool()
    def create_sub_chore(parent_id: int, name: str, description: str = "") -> dict[str, Any] | None:
        return _tool_response(
            "create_sub_chore",
            {"parent_id": parent_id, "name": name, "description": description},
            server,
        )

    @mcp.tool()
    def get_sub_chores(parent_id: int, recursive: bool = False) -> list[dict[str, Any]]:
        return _tool_response(
            "get_sub_chores",
            {"parent_id": parent_id, "recursive": recursive},
            server,
        )

    @mcp.tool()
    def get_parent_chore(id: int) -> dict[str, Any] | None:
        return _tool_response("get_parent_chore", {"id": id}, server)

    @mcp.tool()
    def find_root_chores() -> list[dict[str, Any]]:
        return _tool_response("find_root_chores", {}, server)

    @mcp.tool()
    def set_next_chore(id: int, next_id: int) -> dict[str, Any]:
        return _tool_response("set_next_chore", {"id": id, "next_id": next_id}, server)

    @mcp.tool()
    def get_next_chore(id: int) -> dict[str, Any] | None:
        return _tool_response("get_next_chore", {"id": id}, server)

    @mcp.tool()
    def advance_status(id: int, to_status: str) -> dict[str, Any] | None:
        return _tool_response("advance_status", {"id": id, "to_status": to_status}, server)

    @mcp.tool()
    def advance_to_next(id: int) -> dict[str, Any] | None:
        return _tool_response("advance_to_next", {"id": id}, server)

    @mcp.tool()
    def validate_chain_integrity() -> dict[str, Any]:
        return _tool_response("validate_chain_integrity", {}, server)

    @mcp.tool()
    def repair_integrity() -> dict[str, Any]:
        return _tool_response("repair_integrity", {}, server)

    @mcp.tool()
    def archive_chore(id: int) -> dict[str, Any] | None:
        return _tool_response("archive_chore", {"id": id}, server)

    @mcp.tool()
    def process_signals(id: int) -> dict[str, Any] | None:
        return _tool_response("process_signals", {"id": id}, server)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        event = {"event": "active_chores", "result": server.list_active()}
        print(json.dumps(event))
        yield

    app = FastAPI(lifespan=lifespan)
    app.mount(config.mcp_path, mcp.streamable_http_app())

    @app.post("/api")
    def api_call(payload: ApiRequest) -> dict[str, Any]:
        return server.handle_request(
            {"id": payload.id, "method": payload.method, "params": payload.params or {}}
        )

    return app


def main() -> int:
    config_path = os.environ.get("CHORE_DISPATCHER_CONFIG")
    config = load_config(config_path)
    print(f"Loaded config: {config_path or 'default'} (mcp_path={config.mcp_path})")
    app = build_app(config_path)
    uvicorn.run(app, host=config.http_host, port=config.http_port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

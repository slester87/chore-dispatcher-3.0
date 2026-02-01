from __future__ import annotations

from typing import Any

import httpx


class ChoreDispatcherClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8080", timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ChoreDispatcherClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        payload = {"method": method, "params": params or {}}
        response = self._client.post(f"{self._base_url}/api", json=payload)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "Unknown error"))
        return data.get("result")

    def health(self) -> dict[str, Any]:
        return self._request("health")

    def list_active(self) -> list[dict[str, Any]]:
        return self._request("list_active")

    def list_all(self) -> list[dict[str, Any]]:
        return self._request("list_all")

    def list_archive(self) -> list[dict[str, Any]]:
        return self._request("list_archive")

    def create(self, name: str, description: str = "") -> dict[str, Any]:
        return self._request("create", {"name": name, "description": description})

    def read(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("read", {"id": chore_id})

    def update(self, chore_id: int, fields: dict[str, Any]) -> dict[str, Any] | None:
        return self._request("update", {"id": chore_id, "fields": fields})

    def delete(self, chore_id: int) -> dict[str, Any]:
        return self._request("delete", {"id": chore_id})

    def find_by_status(self, status: str) -> list[dict[str, Any]]:
        return self._request("find_by_status", {"status": status})

    def create_sub_chore(self, parent_id: int, name: str, description: str = "") -> dict[str, Any] | None:
        return self._request(
            "create_sub_chore",
            {"parent_id": parent_id, "name": name, "description": description},
        )

    def get_sub_chores(self, parent_id: int, recursive: bool = False) -> list[dict[str, Any]]:
        return self._request("get_sub_chores", {"parent_id": parent_id, "recursive": recursive})

    def get_parent_chore(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("get_parent_chore", {"id": chore_id})

    def find_root_chores(self) -> list[dict[str, Any]]:
        return self._request("find_root_chores")

    def set_next_chore(self, chore_id: int, next_id: int) -> dict[str, Any]:
        return self._request("set_next_chore", {"id": chore_id, "next_id": next_id})

    def get_next_chore(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("get_next_chore", {"id": chore_id})

    def advance_status(self, chore_id: int, to_status: str) -> dict[str, Any] | None:
        return self._request("advance_status", {"id": chore_id, "to_status": to_status})

    def advance_to_next(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("advance_to_next", {"id": chore_id})

    def validate_chain_integrity(self) -> dict[str, Any]:
        return self._request("validate_chain_integrity")

    def repair_integrity(self) -> dict[str, Any]:
        return self._request("repair_integrity")

    def archive_chore(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("archive_chore", {"id": chore_id})

    def process_signals(self, chore_id: int) -> dict[str, Any] | None:
        return self._request("process_signals", {"id": chore_id})

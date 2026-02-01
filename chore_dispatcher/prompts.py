from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus


def _load_prompt_module() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    prompts_path = repo_root / "persona_prompts" / "prompts.py"
    spec = importlib.util.spec_from_file_location("persona_prompts", prompts_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load persona prompts")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _chore_context(chore: Chore) -> str:
    return (
        "\n\nCHORE CONTEXT:\n"
        f"- ID: {chore.id}\n"
        f"- Name: {chore.name}\n"
        f"- Description: {chore.description}\n"
        f"- Status: {chore.status.value}\n"
        f"- Progress Info: {chore.progress_info or ''}\n"
        f"- Review Info: {chore.review_info or ''}\n"
    )


def build_role_prompt(chore: Chore) -> str:
    module = _load_prompt_module()

    if chore.status == ChoreStatus.PLAN:
        base = module.build_planner_prompt(str(chore.id))
    elif chore.status == ChoreStatus.PLAN_REVIEW:
        base = module.build_plan_reviewer_prompt(str(chore.id), chore.description)
    elif chore.status == ChoreStatus.WORK:
        base = module.build_worker_prompt(str(chore.id))
    elif chore.status == ChoreStatus.WORK_REVIEW:
        base = module.build_work_reviewer_prompt(str(chore.id))
    else:
        base = module.build_worker_prompt(str(chore.id))

    return base + _chore_context(chore)

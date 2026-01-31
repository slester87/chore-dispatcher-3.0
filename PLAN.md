# Chore Dispatcher 3.0 — Build Plan (Iterative)

This plan is a greenfield implementation based solely on the 3.0 technical spec. Each step has a suggested module layout and concrete acceptance criteria.

## Target Module Layout (proposed)

- `chore_dispatcher/`
  - `__init__.py`
  - `config.py`
  - `logging.py`
  - `cli.py`
  - `models/`
    - `chore.py`
    - `status.py`
  - `id/`
    - `snowflake.py`
  - `repo/`
    - `repository.py`
    - `persistence.py`
    - `integrity.py`
  - `workflow/`
    - `validator.py`
    - `transitions.py`
    - `chain.py`
    - `archival.py`
  - `timers/`
    - `auto_advance.py`
  - `signals/`
    - `signals.py`
  - `tmux/`
    - `session.py`
    - `windows.py`
    - `kiro.py`
  - `lifecycle/`
    - `manager.py`
  - `templates/`
    - `progress.py`
    - `review.py`
  - `tests/`
    - `unit/`
    - `integration/`
    - `performance/`
- `scripts/`
  - `kiro_wrapper.sh`
- `configs/`
  - `default.toml`
- `README.md`
- `PLAN.md`

---

## Step 1 — Project Skeleton & Config
**Scope**
- Establish project layout, config loader, logging, and CLI entrypoint.

**Files/Modules**
- `chore_dispatcher/config.py`
- `chore_dispatcher/logging.py`
- `chore_dispatcher/cli.py`
- `configs/default.toml`

**Acceptance Criteria**
- CLI boots and loads config without errors.
- `--version` and `--health` (or similar) return cleanly.
- Logging outputs to stdout with a consistent format.

---

## Step 2 — Domain Types & State Machine
**Scope**
- Define `ChoreStatus` enum and allowed transitions.
- Define `Chore` model with in‑memory methods.

**Files/Modules**
- `chore_dispatcher/models/status.py`
- `chore_dispatcher/models/chore.py`
- `chore_dispatcher/tests/unit/test_chore.py`

**Acceptance Criteria**
- Unit tests validate linear transitions and terminal state behavior.
- `Chore.is_complete()` returns true only at `WORK_DONE`.
- Sub‑chore completion blocks parent advancement.

---

## Step 3 — Snowflake ID Generator
**Scope**
- Implement Snowflake ID generator with mutex, epoch, sequence overflow handling.

**Files/Modules**
- `chore_dispatcher/id/snowflake.py`
- `chore_dispatcher/tests/unit/test_snowflake.py`

**Acceptance Criteria**
- IDs are unique and monotonic in a single process.
- Sequence overflow waits for next millisecond.
- Clock drift backwards raises runtime error.

---

## Step 4 — Repository Layer (In‑Memory)
**Scope**
- Implement CRUD repo and hierarchy helpers in memory.

**Files/Modules**
- `chore_dispatcher/repo/repository.py`
- `chore_dispatcher/tests/unit/test_repository.py`

**Acceptance Criteria**
- CRUD works for create/read/update/delete/list.
- Parent/child helpers return expected chores.

---

## Step 5 — Persistence Layer (JSONL)
**Scope**
- JSONL active/archive storage and serialization.

**Files/Modules**
- `chore_dispatcher/repo/persistence.py`
- `chore_dispatcher/tests/unit/test_persistence.py`

**Acceptance Criteria**
- Round‑trip serialize/deserialize preserves fields.
- Load + link restores parent/child and chain references.

---

## Step 6 — Integrity & Repair
**Scope**
- Detect cycles, orphans, duplicates; repair where possible.

**Files/Modules**
- `chore_dispatcher/repo/integrity.py`
- `chore_dispatcher/tests/unit/test_integrity.py`

**Acceptance Criteria**
- Cycle detection catches circular chains.
- Orphans are reported and optionally fixed.
- Duplicate entries are removed deterministically.

---

## Step 7 — Transition Engine & Validation
**Scope**
- Implement validation rules and transition engine.

**Files/Modules**
- `chore_dispatcher/workflow/validator.py`
- `chore_dispatcher/workflow/transitions.py`
- `chore_dispatcher/tests/unit/test_transitions.py`

**Acceptance Criteria**
- Invalid transitions raise `TransitionError`.
- Review rejection returns chore to previous work state.
- Progress/review info validation behaves per spec.

---

## Step 8 — Chain Activation Engine
**Scope**
- Activate next chore only on `WORK_DONE`.

**Files/Modules**
- `chore_dispatcher/workflow/chain.py`
- `chore_dispatcher/tests/unit/test_chain.py`

**Acceptance Criteria**
- `get_next_chore()` returns only when current is complete.
- Circular chain detection prevents activation.

---

## Step 9 — Auto‑Advance System
**Scope**
- Timers, delays config, status checks.

**Files/Modules**
- `chore_dispatcher/timers/auto_advance.py`
- `chore_dispatcher/tests/unit/test_auto_advance.py`

**Acceptance Criteria**
- Timers cancel on status change.
- Auto‑advance only fires if status matches expected.

---

## Step 10 — Signal‑Based Communication
**Scope**
- Signal file detection, cleanup, and dispatch.

**Files/Modules**
- `chore_dispatcher/signals/signals.py`
- `chore_dispatcher/tests/unit/test_signals.py`

**Acceptance Criteria**
- Completion signal advances to next phase.
- Exit signal triggers tmux cleanup.

---

## Step 11 — TMUX Integration Core
**Scope**
- Session management, window/pane layout, naming.

**Files/Modules**
- `chore_dispatcher/tmux/session.py`
- `chore_dispatcher/tmux/windows.py`
- `chore_dispatcher/tests/integration/test_tmux.py`

**Acceptance Criteria**
- Session is created if missing.
- Window names follow `chore-{id}-{slug}`.
- Review states create split panes.

---

## Step 12 — Kiro CLI Integration
**Scope**
- Prompt composition and wrapper invocation.

**Files/Modules**
- `chore_dispatcher/tmux/kiro.py`
- `scripts/kiro_wrapper.sh`
- `chore_dispatcher/tests/integration/test_kiro.py`

**Acceptance Criteria**
- Generated command matches spec template.
- Env vars are passed correctly.
- Wrapper handles exit/complete signals.

---

## Step 13 — Lifecycle Manager
**Scope**
- Orchestrate transitions, timers, signals, tmux.

**Files/Modules**
- `chore_dispatcher/lifecycle/manager.py`
- `chore_dispatcher/tests/integration/test_lifecycle.py`

**Acceptance Criteria**
- Full single‑chore flow runs from PLAN to WORK_DONE.
- Chain activation triggers next chore dispatch.

---

## Step 14 — Archival Manager
**Scope**
- Archive completed chores, remove from active.

**Files/Modules**
- `chore_dispatcher/workflow/archival.py`
- `chore_dispatcher/tests/unit/test_archival.py`

**Acceptance Criteria**
- Completed chores move to archive JSONL.
- Active store no longer contains archived chores.

---

## Step 15 — Completion Standards & Quality Gates
**Scope**
- Enforce compile/lint/build/test checks pre‑DONE.

**Files/Modules**
- `chore_dispatcher/workflow/validator.py`
- `scripts/pre-push` (optional)

**Acceptance Criteria**
- Chores cannot transition to `WORK_DONE` unless checks pass.

---

## Step 16 — End‑to‑End & Performance Tests
**Scope**
- Full workflow tests and stress cases.

**Files/Modules**
- `chore_dispatcher/tests/integration/test_e2e.py`
- `chore_dispatcher/tests/performance/test_perf.py`

**Acceptance Criteria**
- Workflow succeeds under normal conditions.
- Bulk chore creation completes within acceptable time.


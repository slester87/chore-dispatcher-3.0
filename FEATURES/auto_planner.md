## Summary
When the server starts (any transport), always open a PLANNER session preloaded with a special “chore-creation chore.” This reserved chore guides the user through creating new chores using Rob Pike–style problem framing.

## Problem / Motivation
- Starting the system can feel idle or ambiguous; the user must manually decide how to begin.
- A dedicated “chore-creation chore” provides a consistent entry point for capturing new work and reinforces disciplined problem framing.

## Proposed Behavior
- On startup (any transport), launch a PLANNER role session bound to a reserved root chore that represents “creating new chores.”
- The session should be created once per startup (no repeated auto-creation loops).
- The root chore is a special reserved chore (not a normal user chore) whose purpose is to guide the user through chore creation.

## UX / TMUX Behavior
- Launch a Kiro prompt in a dedicated tmux window named `chore-dispatcher:planner`.
- The planner window should be the default first window in the tmux session.
- Chores created from the planner should create their windows in the same session (tmux will place new windows to the right by default).
- If the `chore-dispatcher` session already exists, attach/use it; otherwise create it.
- Window naming for chores remains `role+chore_id` as already specified elsewhere.
- The prompt should be built from the special chore’s description and should explicitly guide the user through Rob Pike–style framing.
- The root chore must require answers to these questions before a new chore is created:
  - What must never happen?
  - What can go wrong?
  - What conditions define correctness?
- Only after answering those questions should the planner ask permission to create a new chore in `PLAN` status.

## Config & Flags
- Default: enabled.
- Proposed config key: `auto_planner_on_empty = true`
- Optional CLI flag: `--no-auto-planner` (overrides config).

## Edge Cases
- If tmux is disabled, no auto planner should launch (even if enabled) and the server just idles.
- If multiple instances start concurrently, ensure only one auto planner launches (best effort; race acceptable).
- If the user exits the auto planner without creating a chore, the system should remain idle.

## Success Criteria
- Starting the server always spawns a PLANNER role session automatically.
- The session is bound to the special chore-creation chore.
- The session prompts for user input and, with user permission, results in a new chore in `PLAN` status.
- Behavior can be disabled via config/flag.

## Out of Scope
- Automatic creation of chores without explicit user input.
- Any changes to the core state machine or status progression rules.

## Rollout / Testing Notes
- Unit test: startup hook detects empty active chores and triggers auto planner.
- Integration test: server startup with empty store spawns planner session (tmux mocked).
- Manual test: run server with empty data and confirm planner window appears.

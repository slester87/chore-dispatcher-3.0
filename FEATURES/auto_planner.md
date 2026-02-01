## Summary
When the server starts (any transport), always open an interactive PLANNER role session and wait for user interaction.

## Problem / Motivation
- Starting the system can feel idle or ambiguous; the user must manually decide how to begin.
- A default PLANNER session provides a natural entry point to capture the next chore and begin the workflow.

## Proposed Behavior
- On startup (any transport), launch a PLANNER role session that is idle and ready for user input.
- The session should be created once per startup (no repeated auto-creation loops).
- The session should not create an actual chore record until the user provides input and permission (details below).

## UX / TMUX Behavior
- Launch a Kiro prompt in a dedicated tmux window named `chore-dispatcher:planner`.
- The planner window should be the default first window in the tmux session.
- Chores created from the planner should create their windows in the same session (tmux will place new windows to the right by default).
- If the `chore-dispatcher` session already exists, attach/use it; otherwise create it.
- Window naming for chores remains `role+chore_id` as already specified elsewhere.
- The prompt should clearly state the intent to capture a new chore description and scope.
- The PLANNER session should use its persona to guide the user through chore creation.
- The PLANNER prompt should follow Rob Pike’s guidance:
  - Start with the problem, not the solution.
  - Clarify: What is actually hard here? What is the irreducible core of the problem? What must be true when the system is correct?
- The session waits for user input; once the user has provided sufficient detail, the PLANNER should ask for permission before creating a new chore in `PLAN` status and proceeding with normal planner flow.

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
- The session prompts for user input and, with user permission, results in a new chore in `PLAN` status.
- Behavior can be disabled via config/flag.

## Out of Scope
- Automatic creation of chores without explicit user input.
- Any changes to the core state machine or status progression rules.

## Rollout / Testing Notes
- Unit test: startup hook detects empty active chores and triggers auto planner.
- Integration test: server startup with empty store spawns planner session (tmux mocked).
- Manual test: run server with empty data and confirm planner window appears.

## Summary
When the HTTP server starts and there are no active chores, automatically launch a PLANNER role session and wait for user interaction.

## Problem / Motivation
- Starting the system with an empty queue feels idle; the user must manually create a chore to kick things off.
- A default PLANNER session provides a natural entry point to capture the next chore and begin the workflow.

## Proposed Behavior
- On startup (any transport), if `list_active()` returns zero chores, launch a PLANNER role session that is idle and ready for user input.
- The session should be created once per startup (no repeated auto-creation loops).
- The session should not create an actual chore record until the user provides input (details below).

## UX / TMUX Behavior
- Launch a Kiro prompt in a dedicated tmux window named `chore-dispatcher:planner`.
- The planner window should be the default first window in the tmux session.
- Chores created from the planner should create their windows in the same session, positioned to the right of the planner window.
- The prompt should clearly state: “No active chores found. Describe the chore you want to plan.”
- The PLANNER session should use its persona to guide the user through chore creation.
- The session waits for user input; once input is provided, it should create a new chore in `PLAN` status and proceed with normal planner flow.

## Config & Flags
- Default: enabled.
- Proposed config key: `auto_planner_on_empty = true`
- Optional CLI flag: `--no-auto-planner` (overrides config).

## Edge Cases
- If tmux is disabled, no auto planner should launch (even if enabled) and the server just idles.
- If multiple instances start concurrently, ensure only one auto planner launches (best effort; race acceptable).
- If the user exits the auto planner without creating a chore, the system should remain idle.

## Success Criteria
- Starting the server with no active chores spawns a PLANNER role session automatically.
- The session prompts for user input and, upon receiving it, results in a new chore in `PLAN` status.
- Starting the server with existing active chores does not spawn a new planner session.
- Behavior can be disabled via config/flag.

## Out of Scope
- Automatic creation of chores without explicit user input.
- Any changes to the core state machine or status progression rules.

## Rollout / Testing Notes
- Unit test: startup hook detects empty active chores and triggers auto planner.
- Integration test: server startup with empty store spawns planner session (tmux mocked).
- Manual test: run server with empty data and confirm planner window appears.

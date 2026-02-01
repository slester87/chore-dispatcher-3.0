# Chore Dispatcher 3.0

Greenfield implementation of the Chore Dispatcher system per the 3.0 technical specification.

- Spec source: `chore_dispatcher_3.0_technical_spec.md`
- Build plan: `PLAN.md`

## TMUX behavior (default on)

- PLAN: create a new window for the planner.
- PLAN_REVIEW: add a review pane to the existing plan window.
- PLAN_READY: tear down the plan window.
- WORK: create a new window for the worker.
- WORK_REVIEW: add a review pane to the existing work window.
- WORK_DONE: tear down the work window.

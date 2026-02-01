# Chore Dispatcher 3.0

![ci](https://github.com/slester87/chore-dispatcher-3.0/actions/workflows/ci.yml/badge.svg)

Greenfield implementation of the Chore Dispatcher system per the 3.0 technical specification.

- Spec source: `chore_dispatcher_3.0_technical_spec.md`
- Build plan: `PLAN.md`

## TMUX behavior (default on)

- PLAN: create `chore<id>_Planner`.
- PLAN_REVIEW: add a review pane to `chore<id>_Planner`.
- PLAN_READY: tear down `chore<id>_Planner`.
- WORK: create `chore<id>_Worker`.
- WORK_REVIEW: add a review pane to `chore<id>_Worker`.
- WORK_DONE: tear down `chore<id>_Worker`.

# TLA+ Specs

This directory contains TLA+ specifications used to model and verify core behavior.

## Requirements

- `tlc` on PATH (TLA+ Tools)

## Run

From the repo root:

```
make tlc
```

This runs the bounded model in `spec/WORKFLOW.tla` with the configuration in `spec/WORKFLOW.cfg`.

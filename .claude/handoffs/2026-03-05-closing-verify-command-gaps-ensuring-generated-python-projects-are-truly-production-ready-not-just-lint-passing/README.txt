WHAT THIS FOLDER IS ABOUT
=========================

Date: 2026-03-05
Project: sec-llm-workbench (MetaProject)

The /verify command was audited and found to have a critical gap: it only ran
static analysis (linting, type hints, security patterns, code quality). A project
could pass all 8 agents and still crash at runtime due to broken async boundaries,
missing environment variables, cross-phase regressions, or a pipeline that simply
does not execute end-to-end.

This folder contains the implementation plan to close that gap by adding 3 new
specialized agents (smoke-test-runner, config-validator, regression-guard), improving
the existing integration-tracer with AST-based call graph analysis, adding an
active-project guard so /verify fails fast when misconfigured, and adding timeout
and retry logic for Wave 3 agents.

The orchestrator-brief.md file contains detailed instructions for a TeamCreate
agent team (8 worker agents across 2 waves) that implements all 6 improvements
in parallel, with each agent committing its own work and reporting back.

After this implementation, /verify covers 11 agents and certifies that a generated
Python project is truly production-ready — not just lint-passing.

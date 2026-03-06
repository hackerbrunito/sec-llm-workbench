# TeamCreate Orchestrator & Agent Workflow Conventions
# Date: 2026-03-05
# Purpose: Persistent reference for all future TeamCreate-based implementations.
#          Read this file at session start before writing any orchestrator briefing.
#          This replaces verbal re-explanation of conventions every session.

---

## OVERVIEW

These conventions govern every TeamCreate implementation in this MetaProject.
They were established across multiple sessions and must be followed exactly.
No convention may be overridden without explicit user instruction.

---

## ROLE OF THE MAIN CONTEXT (Claude Code — the coordinator)

The main context has ONE job when a TeamCreate implementation is needed:

1. Write the orchestrator briefing file (full technical detail — see section below)
2. Create a new descriptive directory in `.claude/handoffs/` for the briefing file
3. Spawn the TeamCreate team
4. Spawn the orchestrator agent with a short prompt pointing to the briefing file
5. STOP. Wait. Do nothing else.

After step 4, the main context:
- Does NOT read any files
- Does NOT write any files
- Does NOT edit any files
- Does NOT execute any commands
- Does NOT ask agents for status updates
- Does NOT intervene in the workflow unless the user explicitly says to

The user monitors agent progress in Tmux panes (each agent opens a pane automatically).
If an agent goes stale or idle unexpectedly, the user will observe it and report back.
The main context only acts again when the orchestrator sends it the final summary via SendMessage.

---

## ROLE OF THE ORCHESTRATOR

The orchestrator is a general-purpose agent spawned by the main context.
It reads the briefing file and executes the plan exactly as written.

The orchestrator:
- Does NOT implement anything itself
- Does NOT read or write project files
- Spawns agents using the Agent tool
- Tracks which agents are DONE vs WAITING
- Unblocks waiting agents by sending them a SendMessage when their dependency is DONE
- Receives DONE reports from each agent via SendMessage
- Relays the final C-wave summarizer report back to the main context via SendMessage

The orchestrator MUST use the exact agent prompts from the briefing file — no paraphrasing.

---

## ROLE OF EACH WORKER AGENT

Each worker agent has EXACTLY ONE TASK.
"One task" means one logical unit of work that touches one file.

Rules:
- One agent = one file to create or edit
- Exception: if two changes are inseparable (e.g., both edits are to the same file and
  running them as separate agents would cause a merge conflict), they may be combined
  into one agent that edits one file with multiple related changes.
- An agent must NOT take on work that belongs to another agent's file.
- An agent must NOT exceed its defined scope — no opportunistic fixes or improvements.

### What each agent does (in order):

1. Read the files specified in its prompt (no more, no less)
2. Perform its single task (create or edit one file)
3. Stage the file: `git add <file-path>`
4. Commit the file immediately: `git commit -m "<descriptive message>"`
   - Commits are INCREMENTAL — each agent commits its own file immediately
   - Agents must NEVER batch their commit with another agent's work
   - Agents must NEVER wait for other agents before committing
5. Write a report file to `.ignorar/production-reports/<agent-name>/<date>-<agent-name>-report.md`
6. Send a message to the orchestrator with this exact format:

```
AGENT: <agent-id> (<agent-role>)
STATUS: DONE | FAILED
FILE: <exact relative path of the file created or edited>
COMMIT: <short git commit hash>
SUMMARY: <2-4 sentences: what was done, what was added/changed, any warnings>
UNBLOCKS: <name of next agent waiting on this one, or NONE>
```

If STATUS is FAILED, the agent explains what went wrong in SUMMARY and does NOT commit.

---

## COMMUNICATION PROTOCOL

All inter-agent communication uses the SendMessage tool only.
No agent communicates by any other means.

### Agent → Orchestrator
When an agent finishes, it sends ONE message to "orchestrator" with the format above.

### Orchestrator → Waiting Agent
When the orchestrator receives a DONE message from agent X, it checks the dependency
table in the briefing file. If agent Y was waiting on X, the orchestrator immediately
sends Y a message:

```
DEPENDENCY CLEARED: <agent-X-name> has reported DONE.
You may now begin your task.
Your task: [paste the agent's full prompt from the briefing file]
```

### Orchestrator → Main Context
When the C-wave summarizer sends its DONE message, the orchestrator relays it verbatim
to the main context (team lead) via SendMessage.

### Main Context → Orchestrator
The main context only sends ONE message to the orchestrator: the initial "read the
briefing file and begin" instruction. After that, silence.

---

## WAVE-BASED PARALLEL EXECUTION

Tasks are grouped into waves. Within a wave, all agents run in parallel.
Between waves, the orchestrator waits for ALL agents in the previous wave to report DONE.

### Rules for wave design:
- PARALLEL (same wave): agents that touch different files with no dependency between them
- SEQUENTIAL (different waves): agent B depends on output/commit of agent A
- A file conflict (two agents editing the same file) is ALWAYS sequential — never parallel
- The orchestrator spawns all agents in a wave simultaneously using multiple Agent tool
  calls in a single response

### Wave naming convention:
- Wave A: first parallel batch (typically creates new files — no conflicts)
- Wave B: second parallel batch (typically edits existing files using Wave A output)
- Wave C: final summarizer (always last, always one agent)

---

## REPORT FILES

Every worker agent saves a report file before sending its DONE message.
Report path: `.ignorar/production-reports/<agent-name>/<YYYY-MM-DD>-<agent-name>-implementation-report.md`

Report content (minimum):
```markdown
# <Agent Name> Implementation Report
**Date:** YYYY-MM-DD
**Task:** <one sentence description>
**File created/edited:** <path>
**Commit:** <hash>

## What Was Done
[2-5 sentences describing the changes made]

## Result
DONE / FAILED
```

The report file is NOT committed to git. It lives in `.ignorar/` (gitignored).

---

## SUMMARIZER AGENT (C-wave)

The last agent is always a summarizer (C1).

C1:
1. Reads all report files from `.ignorar/production-reports/` for the current implementation
2. Verifies all implementation files exist on disk using `ls`
3. Runs `git log --oneline -15` to confirm all commits landed
4. Writes a final summary report to `.ignorar/production-reports/final-summary/<date>-final-summary.md`
5. Commits the summary report
6. Sends the complete summary to the orchestrator via SendMessage

The orchestrator then relays C1's message verbatim to the main context (team lead).

---

## ORCHESTRATOR BRIEFING FILE STANDARDS

Every orchestrator briefing file MUST contain these sections in this order:

1. **CONTEXT** — MetaProject path, what is being implemented, handoff file reference
2. **ORCHESTRATOR ROLE** — exact steps the orchestrator takes (spawn A, wait, spawn B, wait, spawn C, relay)
3. **TEAM STRUCTURE** — ASCII tree showing all agents, their wave, their file
4. **COMMUNICATION PROTOCOL** — exact message formats (copy from this file)
5. **GIT INSTRUCTIONS** — how agents commit (incremental, immediate, no batching)
6. **WAVE A AGENT PROMPTS** — one section per agent, labeled with agent name and wave
7. **WAVE B AGENT PROMPTS** — one section per agent, with dependency declarations
8. **WAVE C AGENT PROMPT** — summarizer instructions
9. **FILE PATHS REFERENCE TABLE** — all files touched, by whom, in which wave
10. **DEPENDENCY RULES** — which waves block which, what happens on FAILED
11. **CONTEXT SAFETY NOTES** — estimated token usage per agent, confirmation none will overflow

Each agent prompt in the briefing must be self-contained: the agent can execute its task
by reading only the prompt + the files listed in the prompt. No implicit knowledge assumed.

---

## CONTEXT SAFETY

Each agent is designed to handle one small task to prevent context window overflow.
Before writing a briefing, estimate the context usage per agent:

| Agent type | Estimated tokens |
|-----------|-----------------|
| Creates 1 new agent file (~100 lines) | ~8-15k tokens |
| Edits 1 existing file (1-3 insertions) | ~15-25k tokens (read full file + edit) |
| Summarizer (reads 5-8 report files) | ~20-35k tokens |
| Orchestrator (receives 8 short messages) | ~15-25k tokens |

All agents must stay well under the 200k context limit.
If an edit task requires reading a file >500 lines, split into two agents editing different sections.

---

## DIRECTORY AND FILE NAMING CONVENTIONS

### Handoff directory names (15+ words):
Format: `YYYY-MM-DD-<15-word-description-using-hyphens>`
Example: `2026-03-05-closing-verify-command-gaps-ensuring-generated-python-projects-are-truly-production-ready-not-just-lint-passing`

### Orchestrator briefing file names (10-15 words):
Format: `orchestrator-brief-<10-15-word-description>.md`
Example: `orchestrator-brief-implement-dependency-scanner-coverage-gate-smoke-edge-cases-secrets-scan-circular-import-detector.md`

### Memory/convention file names (15-20 words):
Format: `YYYY-MM-DD-<15-20-word-description>.md`
Example: `2026-03-05-teamcreate-workflow-conventions-one-task-per-agent-incremental-commits-sendmessage-protocol.md`

All directories and files inside `.claude/handoffs/` must follow this pattern.
Names must be descriptive enough that someone reading them 6 months later understands
the purpose without opening the file.

---

## FAILURE HANDLING

If any Wave A agent reports FAILED:
- Orchestrator stops. Does NOT spawn Wave B.
- Orchestrator sends the user (main context) a message explaining which agent failed and why.
- Orchestrator waits for instructions from the main context.

If any Wave B agent reports FAILED:
- Orchestrator stops. Does NOT spawn Wave C.
- Same escalation as above.

If an agent goes idle without sending a DONE or FAILED message:
- The user monitors Tmux panes and will notice.
- The user informs the main context.
- The main context sends a nudge to the orchestrator.
- The orchestrator re-sends the task to the idle agent.

---

## QUICK REFERENCE CHECKLIST (before writing each briefing)

- [ ] One task per agent (one file per agent)
- [ ] Parallel within waves (no file conflicts in same wave)
- [ ] Sequential between waves (B depends on A, C depends on B)
- [ ] Each agent commits immediately after its task
- [ ] Each agent writes a report to .ignorar/production-reports/
- [ ] Each agent sends DONE message to orchestrator with exact format
- [ ] Orchestrator unblocks waiting agents immediately on DONE receipt
- [ ] C1 summarizer is the last agent in every implementation
- [ ] Orchestrator relays C1 summary to main context
- [ ] Main context does nothing after spawning orchestrator
- [ ] All agent prompts are self-contained in the briefing file
- [ ] Context token estimates provided for all agents

# Memory Bionics System Specification (v2.3)

## Purpose

This document is the formal system specification for the OpenClaw Memory System.

It explains:
- the design goals of v2.3
- file boundaries
- script responsibilities
- cron responsibilities
- handoff expectations for a new agent or maintainer

It is **not** the long-term memory file itself.

---

## Core design goal

v2.3 moves the system away from:

> “high score → directly enter main memory”

and toward:

> “candidate score → classification → long-term value judgment → distilled consolidation”

This means long-term memory is no longer treated as a container of high-scoring events.  
Instead, it becomes a compact index of durable cognition.

---

## File boundaries

### `memory/YYYY-MM-DD.md`
Daily memory source files.

Use them for:
- raw experience
- execution traces
- incident notes
- reflections and drafts
- day-level work texture: what changed, what was tried, and how decisions evolved

Important boundary:
- daily memory should remain more raw and contextual than `MEMORY.md`
- it is not required to compress everything into long-term conclusions at this layer

### `MEMORY.md`
Main long-term memory file.

Use it for:
- long-lived facts
- important decisions
- reusable rules
- distilled cognition

Do not use it as a system design document.

### `memory-bionics-system.md`
Formal system specification.

Use it for:
- design explanation
- boundaries
- pipeline description
- maintenance handoff

### `scripts/daily-memory-maintenance-instructions.md`
Execution instructions for the formal maintenance cron.

### `scripts/daily-meditation-instructions.md`
Execution instructions for the reflective review cron.

---

## Three-layer model

### 1. Daily Memory Layer
`memory/*.md`

Stores raw inputs and process-level material.

### 2. Main Memory Layer
`MEMORY.md`

Stores distilled long-term cognition.

### 3. Retrieval / External Layer
Optional future retrieval systems.

Used to recover historical detail without bloating `MEMORY.md`.

---

## Pipeline

```text
memory/YYYY-MM-DD.md
  ↓
memory-scoring.py
  ↓
importance >= 7 → candidate
  ↓
memory-consolidation.py
  ↓
MEMORY.md
  ↓
memory-decay-check.py
  ↓
forgotten items / expired files / pruning suggestions
```

### Daily review path

```text
daily-meditation
  ↓
review yesterday
  ↓
if there is meaningful progress, write day-level material back into the corresponding dated daily memory file
  ↓
if there is no meaningful new material, the file may remain unchanged or absent for that date
  ↓
wait for the next maintenance cycle
```

---

## Script responsibilities

### `memory-scoring.py`
Front-end scorer.

Responsibilities:
- score newly added daily memory entries
- mark candidate priority
- support dry-run verification

Current public behavior:
- candidate threshold = `importance >= 7`
- dynamic score cap = `10`
- supports `--dry-run`, `--explain`, `--recent-days`

### `memory-consolidation.py`
Back-end consolidation.

Responsibilities:
- read scored candidates from recent daily memory files
- classify entry type
- judge long-term value
- distill into long-term format
- avoid duplicate insertions into `MEMORY.md`

Types:
- `fact`
- `decision`
- `rule`
- `event`
- `doc`
- `log`

### `memory-decay-check.py`
Governance and forgetting audit.

Responsibilities:
- detect forgotten main-memory items
- detect expired daily-memory files
- suggest pruning and merging
- identify low-reuse events

### `memory-usage-tracker.py`
Tracks usage signals such as search hits and citations.

---

## Cron responsibilities

### `daily-memory-maintenance`
Formal long-term memory maintenance entrypoint.

Should handle:
1. usage analysis
2. scoring
3. consolidation
4. governance audit
5. reporting
6. confirmed cleanup

### `daily-meditation`
Reflective review entrypoint.

Should handle:
1. review yesterday
2. generate lessons and improvements
3. write new day-level material back to the corresponding dated daily memory file when there is meaningful progress
4. publish diary / summary if desired

Important rules:

> `daily-meditation` must not directly write into `MEMORY.md`.
>
> A low-information day is allowed to produce no new dated daily-memory file.
>
> “Not yet worthy of long-term memory” should not be misread as “not worth recording in daily memory.”

---

## Current v2.3 direction

### Scoring
- score is only a candidate signal
- generic and process-oriented titles should be suppressed
- system/design terms should not automatically overinflate scores

### Consolidation
- process records should be blocked
- rule / decision / fact items should survive
- duplicate insertion should be avoided

### Governance
- `MEMORY.md` should be kept compact
- low-reuse events should be surfaced for review
- repeated rule/decision fragments should be candidates for merging

---

## Handoff checklist

If a new agent takes over, do this in order:

1. Read this file.
2. Read `README.md`.
3. Read both instruction files.
4. Dry-run the full chain:

```bash
python3 scripts/memory-scoring.py --dry-run --explain --recent-days 3
python3 scripts/memory-consolidation.py --dry-run --recent-days 3
python3 scripts/memory-decay-check.py --dry-run
```

5. Check three questions:
- Are process records still entering the candidate set too easily?
- Is consolidation still admitting items that should stay in daily memory?
- Does governance output look reasonable?

Only then consider non-dry-run application.

---

## One-sentence summary

The v2.3 memory system is designed to turn raw daily experience into a compact long-term cognition index — not to dump high-scoring logs into permanent memory.

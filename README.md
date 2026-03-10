# OpenClaw Memory System

A biomimetic memory workflow for OpenClaw agents.

## What this project is

This repository contains a practical memory architecture for OpenClaw that separates:

- **daily memory** (`memory/YYYY-MM-DD.md`) for raw experience, logs, and reflections
- **main memory** (`MEMORY.md`) for distilled long-term facts, rules, and decisions
- **governance scripts** for scoring, consolidation, forgetting, and pruning suggestions

The core idea is simple:

> Long-term memory should not be a dump of high-scoring events.  
> It should be a compact index of durable cognition.

---

## Version status

**Current public design baseline**: v2.3  
**Focus**:
- score first, but treat score only as a **candidate signal**
- consolidate into `MEMORY.md` only after **type judgment** and **long-term value judgment**
- keep `MEMORY.md` compact through governance checks instead of endless accumulation

---

## Architecture

```text
memory/YYYY-MM-DD.md
  ↓
memory-scoring.py
  ↓
candidate (importance >= 7)
  ↓
memory-consolidation.py
  ↓
MEMORY.md
  ↓
memory-decay-check.py
  ↓
forgotten items / expired files / pruning suggestions
```

Daily review is handled separately:

```text
daily-meditation
  ↓
review yesterday
  ↓
write new insights back to the dated daily memory file
  ↓
wait for the next maintenance cycle to score and consolidate
```

---

## Repository layout

```text
openclaw-memory-system/
├── README.md
├── memory-bionics-system.md
├── scripts/
│   ├── memory-scoring.py
│   ├── memory-consolidation.py
│   ├── memory-decay-check.py
│   ├── memory-usage-tracker.py
│   ├── daily-memory-maintenance-instructions.md
│   └── daily-meditation-instructions.md
└── examples/
    └── decay-report.json.example
```

---

## Core file responsibilities

### `memory/YYYY-MM-DD.md`
Daily memory source files.

Use them for:
- raw events
- debugging traces
- reflections
- drafts before long-term consolidation

### `MEMORY.md`
Long-term memory index.

Use it for:
- stable facts
- important decisions
- reusable rules
- distilled long-term cognition

Do **not** use it as a design document.

### `memory-bionics-system.md`
The formal system specification.

Use it to understand:
- system boundaries
- file roles
- cron responsibilities
- end-to-end flow
- handoff guidance

---

## Scripts

### `memory-scoring.py`
Front-end scoring.

Responsibilities:
- score newly added daily memory entries
- mark candidate priority
- support dry-run validation

Current behavior:
- candidate threshold = `importance >= 7`
- dynamic entry score cap = `10`
- supports `--dry-run`, `--explain`, `--recent-days`

### `memory-consolidation.py`
Back-end consolidation.

Responsibilities:
- read scored daily memory candidates
- classify entry type (`fact`, `decision`, `rule`, `event`, `doc`, `log`)
- judge long-term value
- distill and insert into `MEMORY.md`
- avoid duplicate insertions

### `memory-decay-check.py`
Governance and forgetting audit.

Responsibilities:
- detect forgotten main-memory entries
- detect expired daily-memory files
- generate pruning suggestions
- suggest low-reuse event cleanup and merge opportunities

### `memory-usage-tracker.py`
Tracks usage signals such as search hits and citations.

---

## Cron roles

### `daily-memory-maintenance`
Runs the formal maintenance pipeline:
- usage analysis
- scoring
- consolidation
- governance audit

### `daily-meditation`
Runs the reflective review pipeline:
- review yesterday
- generate lessons / improvements / plans
- write insight material back to the corresponding dated daily memory file
- publish diary or summary if needed

Important rule:

> `daily-meditation` should not write directly into `MEMORY.md`.

---

## Public usage model

This repository is intentionally kept generic and sanitized.

It does **not** include:
- private identities
- private user ids
- personal credentials
- private service endpoints
- local machine-specific memory content

You are expected to adapt the scripts and instruction files to your own OpenClaw workspace.

---

## Suggested handoff sequence

If a new agent or maintainer needs to take over, read in this order:

1. `README.md`
2. `memory-bionics-system.md`
3. `scripts/daily-memory-maintenance-instructions.md`
4. `scripts/daily-meditation-instructions.md`
5. dry-run the core pipeline:

```bash
python3 scripts/memory-scoring.py --dry-run --explain --recent-days 3
python3 scripts/memory-consolidation.py --dry-run --recent-days 3
python3 scripts/memory-decay-check.py --dry-run
```

---

## License

MIT

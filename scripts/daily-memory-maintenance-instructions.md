<<<<<<< HEAD
# 每日记忆维护任务指引 (v2.2)
=======
# Daily Memory Maintenance Instructions (v2.3)
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)

## Schedule
Every day at 02:00 (Asia/Shanghai)

## Responsibilities
The maintenance job is the **formal long-term memory maintenance entrypoint**.

<<<<<<< HEAD
### 任务 0：分析使用日志（前置任务）
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --analyze`
2. 汇总昨天的搜索命中和引用记录
3. 更新 usage-log.json 中的加分数据
4. 输出：加分变动摘要

**说明**：此任务必须最先执行，为后续维护流程提供使用数据参考

---

### 任务 1：评分
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-scoring.py`
2. 扫描 `memory/*.md` 中尚未评分的条目
3. 对这些条目执行首次评分（关键词匹配，不衰减）
4. 输出：新增评分的条目列表

**说明**：`memory-scoring.py` 的职责是给日常记忆文件中的条目打分，**不直接重评 `MEMORY.md`**。

---

### 任务 2：主记忆吸收 / 维护
1. 读取已评分的 `memory/*.md` 条目
2. 按维护规则挑选高价值条目（当前规则：**得分 > 7**）
3. 将高价值条目吸收进 `MEMORY.md`
4. 保留其余条目在 `memory/` 中作为短期记忆日志

**说明**：`MEMORY.md` 的更新由记忆维护任务负责，而不是由 `memory-scoring.py` 直接处理。

---

### 任务 3：遗忘检查
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-decay-check.py`
2. 读取当前 `MEMORY.md`
3. 筛选 `importance < 2` 的条目
4. 检查 `memory/` 下超过 30 天的文件
5. 生成遗忘清单

---

### 任务 3：汇报遗忘清单
1. 读取 `decay-report.json`，获取 `summary.forgotten_entries` 和 `summary.expired_files`
2. 飞书私信发送遗忘清单
3. 等待主人确认

**汇报格式**：
```
🌙 记忆遗忘检查报告（2026-03-08）

总记忆条目：32
核心记忆（受保护）: 5
遗忘条目（MEMORY.md）: 2
过期文件（memory/）: 1

📋 遗忘清单（待主人确认）:

MEMORY.md 条目：
  • 2026-02-20 某条普通记录
    评分：1 | 天数：17

memory/ 文件：
  • 2026-01-15.md
    天数：53

请主人确认后执行清理~
```

---

### 任务 4：执行清理（主人确认后）
1. 从 MEMORY.md 删除遗忘条目
2. 使用 `trash` 删除对应的 memory/ 文件
3. 清理 usage-log.json 中的无效条目
4. 提交 Git 记录

---

## 执行流程

```
每天凌晨 02:00 执行：
  ↓
任务 0：分析使用日志（memory-usage-tracker.py）
  ↓
任务 1：为 memory/*.md 条目评分（memory-scoring.py）
  ↓
任务 2：按规则吸收高分条目进入 MEMORY.md
  ↓
任务 3：遗忘检查（memory-decay-check.py）
  ↓
任务 4：汇报清单（飞书私信）
  ↓
任务 5：等待确认 → 执行清理
=======
It should:
1. analyze usage signals
2. score new daily-memory entries
3. consolidate long-term candidates into `MEMORY.md`
4. run governance audit (forgetting + pruning suggestions)
5. report findings
6. wait for confirmation before cleanup

---

## Steps

### Step 0: analyze usage log
Run:
```bash
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --analyze
```

### Step 1: score daily memory
Run:
```bash
python3 ~/.openclaw/workspace/scripts/memory-scoring.py
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
```

Notes:
- score only newly added daily-memory entries
- candidate threshold stays at `importance >= 7`
- scoring does not directly update `MEMORY.md`

### Step 2: consolidate candidates into main memory
Run:
```bash
python3 ~/.openclaw/workspace/scripts/memory-consolidation.py
```

<<<<<<< HEAD
- ✅ 任务 0 必须最先执行（为后续维护提供使用数据参考）
- ✅ `memory/*.md` 条目只首次评分，不衰减
- ✅ 高价值条目由维护任务吸收入 `MEMORY.md`（当前规则：得分 > 7）
- ✅ `memory-scoring.py` 不直接重评 `MEMORY.md`
- ✅ `MEMORY.md` 作为主记忆文件，由后续维护流程整理与沉淀
- ✅ 核心记忆（≥11 分）永不衰减
- ✅ 加分上限 +10 分（防止刷分）
- ✅ 遗忘清单 = `MEMORY.md` 条目 + `memory/` 过期文件（>30 天）
- ⚠️ 清理前必须主人确认
- ✅ 使用 `trash` 命令（可恢复）

---

*最后更新：2026-03-08 v2.2*
=======
Notes:
- read scored daily-memory entries from the recent window
- include entries already scored previously if they still fall within the consolidation window
- candidate does not mean automatic admission
- admit only after type judgment + long-term value judgment + distillation

### Step 3: run governance audit
Run:
```bash
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py
```

Audit targets:
- forgotten main-memory items
- expired daily-memory files
- duplicate themes
- low-reuse event candidates
- merge suggestions

### Step 4: report governance summary
Report:
- forgotten candidates
- expired files
- pruning suggestions
- merge suggestions

### Step 5: cleanup only after confirmation
Do not delete or merge memory content automatically without confirmation.

---

## Important rules

- `MEMORY.md` is maintained here, not in the meditation job
- `memory/*.md` entries are scored first, then consolidated later
- use `trash` instead of destructive deletion when possible
- this file is an execution guide, not a design document
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)

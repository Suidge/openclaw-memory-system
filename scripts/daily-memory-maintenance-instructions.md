# 每日记忆维护任务指引 (v2.1)

## 执行时间
每天凌晨 02:00（Asia/Shanghai）

## 任务清单

### 任务 1：分析使用日志（前置任务）
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --analyze`
2. 汇总昨天的搜索命中和引用记录
3. 更新 usage-log.json 中的加分数据
4. 输出：加分变动摘要

**说明**：此任务必须最先执行，为后续重评提供加分数据

---

### 任务 1：评分/重评
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-scoring.py`
2. 为 memory/ 新文件首次评分（关键词匹配，不衰减）
3. 为 MEMORY.md 动态记忆区重评（基础分 + 加分 - 衰减）
4. 输出：新增评分的条目列表 + 重评条目列表

---

### 任务 2：遗忘检查
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-decay-check.py`
2. 读取评分后的 MEMORY.md
3. 筛选 `importance < 2` 的条目
4. 检查 memory/ 下超过 30 天的文件
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
任务 1：评分/重评（memory-scoring.py）
  ↓
任务 2：遗忘检查（memory-decay-check.py）
  ↓
任务 3：汇报清单（飞书私信）
  ↓
任务 4：等待确认 → 执行清理
```

---

## 注意事项

- ✅ 任务 0 必须最先执行（为任务 1 提供加分数据）
- ✅ memory/ 文件只首次评分，不衰减
- ✅ MEMORY.md 条目每日重评（基础分 + 加分 - 衰减）
- ✅ 核心记忆（≥11 分）永不衰减
- ✅ 加分上限 +10 分（防止刷分）
- ✅ 遗忘清单 = MEMORY.md 条目 + memory/ 过期文件（>30 天）
- ⚠️ 清理前必须主人确认
- ✅ 使用 `trash` 命令（可恢复）

---

*最后更新：2026-03-08 v2.1*

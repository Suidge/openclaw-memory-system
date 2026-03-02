# 每日记忆维护任务指引

## 执行时间
每天凌晨 02:00（Asia/Shanghai）

## 任务清单

### 任务 1：批量评分
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-scoring.py`
2. 为新产生的日记条目添加评分
3. 输出：新增评分的条目列表

### 任务 2：记忆衰减检查
1. 运行：`python3 ~/.openclaw/workspace/scripts/memory-decay-check.py`
2. 读取报告：`~/.openclaw/workspace/memory/decay-report.json`
3. 标记 `effective_score < 2` 的条目

### 任务 3：生成清理清单
1. MEMORY.md 可清理条目（effective_score < 2）
2. memory/可清理文件（days_old > 30）
3. 飞书群发送清单，等待主人确认

### 任务 4：执行清理（主人确认后）
1. 从 MEMORY.md 删除低分条目
2. 使用 `trash` 删除 memory/文件

## 注意事项
- ⚠️ 严格按关键词打分，不随意加分
- ✅ 使用 `trash` 命令（可恢复）
- ⚠️ 清理前必须主人确认

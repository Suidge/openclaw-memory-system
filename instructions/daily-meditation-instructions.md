# 每日回顾任务指引

## 执行时间
每天凌晨 04:00（Asia/Shanghai），回顾**昨天**的工作

## 任务清单

### 1. 更新 MEMORY.md
- 读取 `memory/YYYY-MM-DD.md`（昨天的日志）
- 提取所有 `<!-- importance: X -->` 中 `X ≥ 7` 的条目
- 复制到 `MEMORY.md` 动态记忆区
- 保留原 `importance` 评分

### 2. 改进措施
- 分析昨天工作可优化的地方
- 记录到 `.learnings/LEARNINGS.md` 或 `ERRORS.md`

### 3. 提升计划
- 针对问题制定具体改进步骤
- 如适用，更新 `AGENTS.md` 或 `TOOLS.md`

### 4. 更新 RECENT_EVENTS.md
- 使用 `appendRecentEvent()` 记录昨天完成的重要任务
- 只记录实际完成的工作，不预测未来任务
- 24h 自动清理，保持简洁

## 注意事项
- ⚠️ 所有任务针对**昨天**，不是今天
- ⚠️ 不要硬编"明日重点"
- ✅ 使用 `trash` 而非 `rm` 删除文件
- ✅ 核心记忆（importance ≥ 11）永不衰减

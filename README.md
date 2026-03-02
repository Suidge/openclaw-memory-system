# OpenClaw Memory System

🧠 **仿生记忆系统** - 为 OpenClaw 实现类人记忆的衰减、清理、提炼机制

## 特性

- ✅ **条目级打分**：每条记忆独立评分（importance: 1-15）
- 📉 **自动衰减**：`effective_score = importance × e^(-0.01×days_old)`
- 🗑️ **智能清理**：清理低分记忆（effective_score < 2）
- ✨ **内容提炼**：daily-meditation 提取高价值内容（importance ≥ 7）
- 🔄 **每日维护**：自动化 cron jobs（02:00 评分 → 04:00 提炼）

## 安装

```bash
# 克隆项目
git clone https://github.com/neoshi2346/openclaw-memory-system.git
cd openclaw-memory-system

# 复制脚本到 OpenClaw 工作区
cp scripts/*.py ~/.openclaw/workspace/scripts/
cp instructions/*.md ~/.openclaw/workspace/scripts/
```

## 配置

### 1. 修改 cron jobs

编辑 `~/.openclaw/cron/jobs.json`：

```json
{
  "name": "daily-memory-maintenance",
  "schedule": { "expr": "0 2 * * *" },
  "payload": {
    "message": "执行每日记忆维护任务。详细指引：~/.openclaw/workspace/scripts/daily-memory-maintenance-instructions.md"
  }
}
```

### 2. 配置 instructions

- `daily-memory-maintenance-instructions.md` → 每天 02:00
- `daily-meditation-instructions.md` → 每天 04:00

## 打分规则

| 分数 | 关键词 | 衰减 |
|------|--------|------|
| 15 | 账号、密码、服务器、API Key、token、secret | ❌ 永不衰减 |
| 13 | bitwarden、vault、auth、login、oauth | ❌ 永不衰减 |
| 12 | 邮箱、邮件、email | ❌ 永不衰减 |
| 9 | 配置、设置、安全、规则、策略 | ✅ 正常衰减 |
| 8 | 决策、决定、模型、agent、cron | ✅ 正常衰减 |
| 7 | 技能、工具 | ✅ 正常衰减 |
| 5-6 | 日志、事件、问题、错误 | ✅ 正常衰减 |

**加分项**：
- 包含"重要"、"必须"、"关键"：+1 分（上限 10 分）
- 内容长度 > 1000 字：最低 6 分

## 衰减公式

```python
effective_score = importance × e^(-0.01×days_old)
```

**参数**：
- `LAMBDA = 0.01`（衰减系数）
- `CORE_MEMORY_THRESHOLD = 11`（核心记忆阈值）
- `CLEANUP_THRESHOLD = 2`（清理阈值）

**规则**：
- **核心记忆**（importance ≥ 11）：永不衰减
- **普通记忆**：按公式衰减
- **清理条件**：effective_score < 2

## 日常流程

```
每天 02:00 daily-memory-maintenance
    ↓
1. memory-scoring.py（为新条目打分）
    ↓
2. memory-decay-check.py（衰减检查）
    ↓
3. 生成清理清单 → 飞书群 → 等待确认
    ↓
每天 04:00 daily-meditation
    ↓
1. 读取昨天的 memory/YYYY-MM-DD.md
    ↓
2. 提取 importance ≥ 7 的条目
    ↓
3. 添加到 MEMORY.md 动态记忆区
    ↓
4. 发布 WordPress 日记
```

## 文件结构

```
~/.openclaw/workspace/
├── MEMORY.md                          # 长期记忆
│   ├── 📌 静态配置区（永不衰减）
│   └── 📅 动态记忆区（参与衰减）
├── memory/
│   ├── YYYY-MM-DD.md                  # 每日日记（30 天后清理）
│   └── decay-report.json              # 衰减检查报告
└── scripts/
    ├── memory-scoring.py              # 打分脚本
    ├── memory-decay-check.py          # 衰减检查
    └── archive/
        └── rescore-memory-md.py       # 一次性修正（已归档）
```

## 清理机制

| 位置 | 清理条件 | 清理方式 |
|------|---------|---------|
| `MEMORY.md` 动态记忆区 | `effective_score < 2` | 删除条目 |
| `memory/YYYY-MM-DD.md` | `days_old > 30` | trash 删除文件 |

**保护机制**：
- ✅ 重要内容已通过 daily-meditation 提炼到 `MEMORY.md`
- ✅ 使用 `trash` 命令（可恢复）
- ✅ 清理前必须主人确认

## 示例输出

### memory-scoring.py
```
============================================================
记忆重要性评分脚本（条目级）
============================================================

扫描 18 个记忆文件

============================================================
评分结果
============================================================

新增评分：3 个条目
  - ### 00:00 - daily-meditation: importance=7
  - ### 12:00 - 系统稳定运行：importance=5
  - ### 20:00 - 脚本审查完成：importance=9
```

### memory-decay-check.py
```
 记忆衰减检查报告
============================================================
总记忆条目：14
核心记忆（受保护）: 2
普通记忆：12
可清理候选：0

🛡️  核心记忆（受保护，永不衰减）:
  • 2026-02-25 (importance: 13)
  • 2026-02-18 (importance: 12)
```

## 设计理念

受人类记忆机制启发：
1. **选择性记忆**：重要内容长期保存，琐碎内容自然遗忘
2. **衰减机制**：记忆强度随时间指数衰减
3. **睡眠巩固**：daily-meditation 类似睡眠中的记忆巩固
4. **主动清理**：定期清理低价值记忆，保持系统高效

## 许可证

MIT License

## 作者

Neo Shi (@neoshi2346)

---

**制作**  | 2026-03-02

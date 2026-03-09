# Memory Bionics System Specification (v2.2)

**记忆仿生系统机制说明**

**文档版本**: 2.2  
**最后更新**: 2026-03-08  
**作者**: 银月  
**用途**: 完整阐述 OpenClaw 记忆仿生系统的机制、逻辑、相关文件，供运维人员参考  
**文件位置**: `~/.openclaw/workspace/memory-bionics-system.md`

---

## 一、系统概述

### 1.1 设计理念

本记忆系统模拟人类记忆的"遗忘曲线"和"强化机制"：

1. **遗忘曲线**：不重要的记忆随时间逐渐衰减
2. **强化机制**：频繁使用的记忆会被加强（"越用越重要"）
3. **核心记忆**：最重要的记忆永不遗忘
4. **分层维护**：先对日常记忆日志评分，再由维护流程吸收高价值条目进入主记忆

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| **基础分** | 记忆条目的初始重要性评分（1-99 分） |
| **加分** | 因被搜索/引用而获得的额外分数（上限 +10 分） |
| **衰减** | 因时间流逝而减少的分数（核心记忆除外） |
| **遗忘阈值** | 评分 < 2 的条目被标记为"待清理" |
| **核心记忆** | 评分 ≥11 分的条目，永不衰减 |

---

## 二、记忆分层

### 2.1 文件结构

```
~/.openclaw/workspace/
├── MEMORY.md                          # 主记忆文件（长期记忆）
│   ├── 静态配置区                    # 永不衰减（主人信息、凭证、配置）
│   └── 动态记忆区                    # 参与衰减（事件、周洞察、待办）
├── memory/                            # 日常记忆日志（短期记忆）
│   ├── 2026-03-07.md                 # 每日记忆条目
│   ├── 2026-03-08.md
│   ├── usage-log.json                # 使用追踪日志
│   └── decay-report.json             # 遗忘检查报告
└── scripts/
    ├── memory-scoring.py             # 评分/重评脚本
    ├── memory-decay-check.py         # 遗忘检查脚本
    ├── memory-usage-tracker.py       # 使用追踪脚本
    └── daily-memory-maintenance-instructions.md  # 维护指引
```

### 2.2 记忆类型

| 类型 | 位置 | 评分 | 衰减 | 说明 |
|------|------|------|------|------|
| **核心记忆** | MEMORY.md | ≥11 分 | ❌ 永不 | 凭证、配置、重要决策 |
| **重要记忆** | MEMORY.md | 7-10 分 | ✅ 温和 | 已吸收进主记忆的重要事项 |
| **普通记忆** | MEMORY.md | 4-6 分 | ✅ 正常 | 已吸收进主记忆的一般事项 |
| **琐碎记忆** | MEMORY.md | 1-3 分 | ✅ 加速 | 已吸收进主记忆但价值较低的内容 |
| **日常记忆** | memory/*.md | 1-15 分 | ❌ 不衰减 | 先评分，后由维护任务按规则筛选吸收进 MEMORY.md |

---

## 三、评分机制

### 3.1 首次评分（memory/ 文件）

当新的日常记忆日志产生时（由 daily-meditation 任务创建），`memory-scoring.py` 会为其中的条目进行**首次评分**：

```python
# 关键词匹配规则
KEYWORD_SCORES = [
    (r'账号 | 密码 | 服务器|API.?Key|smtp|imap|token|secret|credential', 15),
    (r'bitwarden|vault|auth|login|oauth', 9),
    (r'邮箱 | 邮件|email|silvermoon@', 12),
    (r'配置 | 设置|config|setup|部署 | 安装', 9),
    (r'安全 | 规则 | 策略|security|policy', 9),
    (r'决策|决定|选择|decision', 8),
    (r'模型|model|agent|binding', 8),
    (r'cron|heartbeat|schedule', 8),
    (r'技能|skill|工具|tool', 7),
    (r'日志|log|工作 | 任务|task', 5),
    (r'事件 | 发生|event', 5),
    (r'问题 | 错误|bug|fix', 6),
]

def calculate_keyword_score(content):
    score = 5
    for pattern, weight in KEYWORD_SCORES:
        if re.search(pattern, content.lower()):
            return weight  # 找到第一个匹配就返回
    return score
```

**特点**：
- ✅ 只评分，不衰减
- ✅ 不计算加分
- ✅ 一次性执行

### 3.2 主记忆吸收与后续维护（MEMORY.md）

每天凌晨 02:00 的维护流程中，系统会从 `memory/*.md` 中读取已评分条目，并按规则将高价值内容吸收入 `MEMORY.md`。

**当前吸收规则**：
- 得分 **> 7** 的条目，进入 `MEMORY.md`
- 其余条目保留在 `memory/` 中作为短期记忆日志

吸收进入 `MEMORY.md` 后，这些条目在主记忆体系中按既定规则参与后续维护与遗忘检查。

**说明**：
- `memory-scoring.py` 的职责是给 `memory/*.md` 条目打分
- `MEMORY.md` 的整理与吸收由后续维护任务负责
- 本版文档以当前代码逻辑为准，不将 `MEMORY.md` 描述为由 `memory-scoring.py` 直接重评

---

## 四、加分机制

### 4.1 加分规则

| 行为 | 加分 | 追踪方式 |
|------|------|---------|
| 被 memory_search 命中 | +0.1/次 | 自动记录 |
| 被引用（`[[MEMORY.md#xxx]]`） | +0.2/次 | 自动记录 |
| **加分上限** | **+10 分** | 防止刷分 |

### 4.2 使用日志（usage-log.json）

```json
{
  "last_updated": "2026-03-08T09:00:00+08:00",
  "entries": {
    "2026-03-05 技能学习完整原则强化": {
      "search_hits": 12,
      "citations": 3,
      "last_used": "2026-03-08T09:00:00+08:00",
      "bonus_score": 1.8
    }
  }
}
```

### 4.3 追踪脚本（memory-usage-tracker.py）

**用法**：
```bash
# 记录搜索命中
python3 memory-usage-tracker.py '条目标题' search

# 记录引用
python3 memory-usage-tracker.py '条目标题' citation

# 获取加分
python3 -c "from memory_usage_tracker import get_bonus; print(get_bonus('条目标题'))"
```

**集成点**：
- `memory_search` 工具：每次搜索后自动调用
- 框架层：检测到 `[[MEMORY.md#xxx]]` 时自动调用

---

## 五、遗忘机制（v2.1）

### 5.1 遗忘清单组成

**遗忘清单 = MEMORY.md 遗忘条目 + memory/ 过期文件**

| 类型 | 判断标准 | 说明 |
|------|---------|------|
| **MEMORY.md 条目** | `importance < 2` | 评分低于遗忘阈值 |
| **memory/ 文件** | `days_old > 30` | 文件创建超过 30 天 |

**检查频率**：每天 02:00  
**执行脚本**：`memory-decay-check.py`

### 5.2 遗忘清单示例

检查后会生成 `memory/decay-report.json`：

```json
{
  "check_time": "2026-03-08T02:00:00+08:00",
  "total_entries": 32,
  "core_memory_count": 5,
  "forgotten_entries": [
    {
      "title": "2026-02-20 某条普通记录",
      "importance": 1,
      "days_old": 17
    }
  ],
  "expired_files": [
    {
      "filename": "2026-01-15.md",
      "filepath": "~/.openclaw/workspace/memory/2026-01-15.md",
      "days_old": 53,
      "reason": "file age (53 days) > threshold (30 days)"
    }
  ]
}
```

### 5.3 清理流程

1. 脚本生成遗忘清单（两部分）
2. 飞书私信汇报给主人
3. **等待主人确认**
4. 确认后执行：
   - 从 MEMORY.md 删除遗忘条目
   - 使用 `trash` 删除过期 memory/ 文件
   - 清理 usage-log.json 中的无效条目

---

## 六、每日执行流程

### 6.1 Cron Job 配置

```json
{
  "id": "daily-memory-maintenance",
  "schedule": { "expr": "0 2 * * *", "tz": "Asia/Shanghai" },
  "payload": {
    "message": "执行每日记忆维护任务。详细指引：~/.openclaw/workspace/scripts/daily-memory-maintenance-instructions.md"
  }
}
```

### 6.2 任务流程

```
每天凌晨 02:00
       ↓
┌──────────────────────────────────────┐
│ 任务 1：评分/重评                     │
│ memory-scoring.py                    │
├──────────────────────────────────────┤
│ • memory/ 新文件                     │
│   → 首次评分（关键词匹配）           │
│ • MEMORY.md                          │
│   → 每日重评                         │
│   （基础分 + 加分 - 衰减）           │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 2：遗忘检查                      │
│ memory-decay-check.py                │
├──────────────────────────────────────┤
│ • MEMORY.md 条目：检查 importance<2 │
│ • memory/ 文件：检查 days_old>30    │
│ • 生成遗忘清单                       │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 3：汇报清单                      │
│ 飞书私信发送                         │
├──────────────────────────────────────┤
│ 遗忘清单 = MEMORY.md 条目 + 文件    │
│ 等待主人确认                         │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 4：执行清理                      │
│ 主人确认后执行                       │
├──────────────────────────────────────┤
│ • 删除 MEMORY.md 条目               │
│ • trash 清理文件                     │
│ • 更新 usage-log.json               │
└──────────────────────────────────────┘
```

---

## 七、脚本说明

### 7.1 memory-scoring.py

**职责**：
- memory/ 文件：首次评分（关键词匹配）
- MEMORY.md：每日重评（基础分 + 加分 - 衰减）

**用法**：
```bash
python3 ~/.openclaw/workspace/scripts/memory-scoring.py
```

**输出**：
- 新增评分的条目列表
- 重评的条目列表（显示分数变化）

### 7.2 memory-decay-check.py

**职责**：
- 读取 MEMORY.md
- 筛选 `importance < 2` 的条目
- 检查 memory/ 下 `days_old > 30` 的文件
- 生成遗忘清单报告

**用法**：
```bash
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py --dry-run  # 仅检查
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py -v         # 详细输出
```

**输出**：
- `memory/decay-report.json` — JSON 格式报告（包含两部分）
- 控制台输出遗忘清单

### 7.3 memory-usage-tracker.py

**职责**：
- 记录搜索命中
- 记录引用
- 计算加分（上限 +10 分）

**用法**：
```bash
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py '条目标题' search
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py '条目标题' citation
```

**API**：
```python
from memory_usage_tracker import log_usage, get_bonus, reset_usage

log_usage('条目标题', 'search')
bonus = get_bonus('条目标题')
reset_usage('条目标题')  # 清理后调用
```

---

## 八、运维指南

### 8.1 日常检查

**检查记忆系统状态**：
```bash
# 查看最新报告
cat ~/.openclaw/workspace/memory/decay-report.json

# 查看使用日志
cat ~/.openclaw/workspace/memory/usage-log.json

# 查看检查日志
tail -50 ~/.openclaw/workspace/memory/forget-check.log
```

**手动执行记忆维护**：
```bash
# 评分/重评
python3 ~/.openclaw/workspace/scripts/memory-scoring.py

# 遗忘检查（干跑模式）
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py --dry-run
```

### 8.2 常见问题

**Q1: 为什么某条目没有被清理？**
- 检查评分是否 ≥2
- 检查是否是核心记忆（≥11 分）
- 检查是否加分抵消了衰减

**Q2: 如何恢复被清理的记忆？**
- 检查废纸篓（`trash` 命令的文件可恢复）
- 从 Git 历史恢复 MEMORY.md

**Q3: usage-log.json 文件过大怎么办？**
- 清理已遗忘条目的记录
- 脚本会自动清理，但也可以手动执行

**Q4: 如何调整衰减参数？**
- 修改 `memory-scoring.py` 中的 `decay_rate`
- 修改 `memory-decay-check.py` 中的 `FORGOTTEN_THRESHOLD` 和 `FILE_EXPIRY_DAYS`
- 修改后测试验证

### 8.3 备份建议

**定期备份**：
```bash
# 备份 MEMORY.md
cp ~/.openclaw/workspace/MEMORY.md ~/.openclaw/workspace/memory/backup/MEMORY.md.$(date +%Y%m%d)

# 备份 usage-log.json
cp ~/.openclaw/workspace/memory/usage-log.json ~/.openclaw/workspace/memory/backup/usage-log.json.$(date +%Y%m%d)
```

**Git 提交**：
```bash
cd ~/.openclaw/workspace
git add MEMORY.md memory/
git commit -m "记忆系统每日状态 $(date +%Y-%m-%d)"
git push
```

---

## 九、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-03-02 | 初始版本（一次性评分 + 衰减检查） |
| 2.0 | 2026-03-08 | 每日重评 + 加分机制 + 遗忘机制 |
| 2.1 | 2026-03-08 | 添加 memory/ 文件 30 天过期检查 |
| 2.2 | 2026-03-08 | 文档口径修订：明确评分脚本只处理 `memory/*.md`，主记忆吸收由维护任务负责；衰减逻辑口径统一为代码版 |

---

## 十、联系方式

**文档维护**：银月  
**问题反馈**：飞书私信 Neo Shi  
**相关文档**：
- `MEMORY.md` — 主记忆文件
- `TOOLS.md` — 工具配置手册
- `HEARTBEAT.md` — 心跳任务指引

---

*本文档会随系统迭代持续更新，请以最新版本为准。*

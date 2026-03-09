# OpenClaw Memory System

一个为 OpenClaw 设计的**仿生记忆系统**：让 AI 助手不只是“存记忆”，而是像人一样对记忆做**评分、筛选、沉淀、遗忘**。

> 核心思想：**不是记住一切，而是持续判断什么值得留下。**

## 当前状态

- **稳定版本思路**：v2.2
- **仓库用途**：沉淀可复用的记忆系统脚本、规则与设计文档
- **适用场景**：
  - OpenClaw 工作区中的 Markdown 记忆文件
  - 每日记忆日志（daily memory）
  - 主记忆文件（`MEMORY.md`）
  - 需要“会遗忘、会强化、会提炼”的 AI 助手

---

## 系统目标

本项目解决的不是“如何把更多内容塞进上下文”，而是：

1. **如何对新记忆做首次评分**
2. **如何从日常记忆中筛出真正高价值内容**
3. **如何把高价值内容沉淀到主记忆**
4. **如何对低价值内容逐步遗忘并清理**
5. **如何通过搜索命中 / 引用使用形成强化机制**

---

## 设计原则

### 1. Markdown 是真相源
系统不依赖专有数据库作为主存储。

- `memory/YYYY-MM-DD.md`：日常记忆原始池
- `MEMORY.md`：主记忆沉淀层

### 2. 日常记忆与主记忆分层
- **daily memory**：原始、细碎、当日发生的事项
- **main memory**：经筛选后的长期记忆

### 3. 记忆不是永久累积，而是动态治理
- 新记忆会被评分
- 常用记忆会被强化
- 低价值记忆会被遗忘
- 真正重要的核心记忆长期保留

### 4. 先稳定，再扩展
v2.2 重点是把 Markdown 记忆链路跑稳。更强的检索 / 多模态 / OpenViking 集成属于后续增强，不是当前稳定版的前提。

---

## 架构概览

```text
memory/YYYY-MM-DD.md
    ↓
首次评分（memory-scoring.py）
    ↓
高分条目筛选（当前规则：> 7）
    ↓
吸收进入 MEMORY.md
    ↓
遗忘检查（memory-decay-check.py）
    ↓
待确认清理
```

### 核心分层

| 层级 | 文件 | 作用 |
|------|------|------|
| 日常记忆层 | `memory/*.md` | 原始记忆池，按条目首次评分 |
| 主记忆层 | `MEMORY.md` | 长期沉淀记忆，供检索与回忆 |
| 强化层 | `memory/usage-log.json` | 记录搜索命中 / 引用使用 |
| 清理层 | `memory/decay-report.json` | 输出遗忘候选与过期文件 |

---

## v2.2 工作流（当前推荐）

### 任务 0：分析使用日志
脚本：`memory-usage-tracker.py --analyze`

作用：
- 汇总 search hit / citation 记录
- 为后续记忆强化提供参考

### 任务 1：为 daily memory 条目评分
脚本：`memory-scoring.py`

作用：
- 扫描 `memory/*.md`
- 为尚未评分的条目首次评分
- **不直接重评 `MEMORY.md`**

### 任务 2：吸收高分条目
由维护流程执行：
- 读取已评分条目
- 当前规则：**得分 > 7** 的条目吸收入 `MEMORY.md`

### 任务 3：遗忘检查
脚本：`memory-decay-check.py`

作用：
- 检查 `MEMORY.md` 中是否有低于阈值的条目
- 检查 `memory/` 中是否有超过 30 天的过期文件
- 生成待确认清单

### 任务 4：确认后清理
原则：
- 先生成报告
- 人工确认
- 使用可恢复方式清理（如 `trash`）

---

## 评分机制（v2.2）

### 1. 日常记忆：首次评分
`memory/*.md` 中的条目按“标题 + 正文”首次评分。

### 2. 当前规则的方向
- **系统升级 / 核心修复 / 机制调整**：倾向高分
- **普通技术事项 / 工作记录**：中等分
- **纯文档整理 / 汇报 / 草案**：中低分，但不至于被一刀切压死

### 3. 当前吸收阈值
- **`> 7`** → 候选吸收进 `MEMORY.md`

### 4. 为什么这样设计
这是一个刻意保守的阈值：
- 防止主记忆被日常碎片污染
- 让真正有长期价值的事项自然浮上来

---

## 遗忘机制

### 对 `MEMORY.md`
- 当条目评分低于阈值时，进入遗忘候选
- 核心记忆长期保留

### 对 `memory/*.md`
- daily memory 作为原始池，不做复杂重评
- 超过一定时长的历史文件可进入清理候选

### 核心原则
- **先列清单，再清理**
- **人工确认优先于自动删除**

---

## 文件结构

```text
openclaw-memory-system/
├── README.md
├── memory-bionics-system.md
├── scripts/
│   ├── memory-scoring.py
│   ├── memory-decay-check.py
│   ├── memory-usage-tracker.py
│   └── daily-memory-maintenance-instructions.md
└── examples/
    └── decay-report.json.example
```

部署到 OpenClaw 工作区后的典型结构：

```text
~/.openclaw/workspace/
├── MEMORY.md
├── memory/
│   ├── YYYY-MM-DD.md
│   ├── usage-log.json
│   └── decay-report.json
└── scripts/
    ├── memory-scoring.py
    ├── memory-decay-check.py
    ├── memory-usage-tracker.py
    └── daily-memory-maintenance-instructions.md
```

---

## 安装与使用

### 环境要求
- Python 3.10+
- OpenClaw 工作区
- 仅依赖 Python 标准库

### 安装步骤

```bash
git clone https://github.com/Suidge/openclaw-memory-system.git
cd openclaw-memory-system

cp scripts/*.py ~/.openclaw/workspace/scripts/
cp scripts/*.md ~/.openclaw/workspace/scripts/
cp memory-bionics-system.md ~/.openclaw/workspace/
```

### 本地验证

```bash
python3 ~/.openclaw/workspace/scripts/memory-scoring.py
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py --dry-run
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --analyze
```

---

## 目录约定（重要）

### `memory/` 目录只放标准 daily memory
推荐放：
- `YYYY-MM-DD.md`
- 规范日期前缀的每日记忆日志

不推荐放：
- 配置学习笔记
- 专题说明文档
- 部署备忘录
- 任意杂项 Markdown

### 其他笔记放哪里？
建议放到：
- macOS `~/Documents/`
- 项目自己的 docs 目录

这样可以避免污染记忆维护流程。

---

## 与 OpenViking / 多模态方案的关系

本仓库当前主线仍然是：
- **Markdown 记忆治理**
- **daily memory → MEMORY.md 的分层沉淀**

如果后续接入 OpenViking / 百炼 VLM / 本地 embedding，建议采用：
- Markdown 仍作为真相源
- 外部系统只做索引与检索增强
- 不直接回写主记忆 Markdown

换句话说：
> 先把记忆治理做好，再把检索与多模态能力外挂上去。

---

## 当前已验证的方向

在实际使用中，以下方向已证明合理：

- 将 `memory/` 收紧为标准 daily memory 目录
- 让评分脚本只做“首次评分”
- 让高分条目通过维护流程进入 `MEMORY.md`
- 让文档类条目与系统实现类条目在评分上被区分对待
- 先验证稳定性，再推进 OpenViking / VLM / embedding 增强

---

## 不包含的内容

本仓库 README 与脚本刻意不包含：
- 个人 API Key
- 用户 ID
- 私有聊天目标
- 个人设备路径细节之外的隐私内容
- 私有主记忆内容

如果你要在自己的环境里使用，请自行填入：
- cron 目标投递渠道
- 你的 OpenClaw 路径
- 私有集成配置

---

## 未来方向

### v2.x
- 继续观察评分与吸收逻辑稳定性
- 优化关键词规则
- 继续验证 daily memory 清理策略

### v3.x
- OpenViking 旁路验证
- 多模态资源检索增强
- 本地 embedding + 云端 VLM 的轻量组合

---

## License

MIT

---

如果你也在做 AI 助手的长期记忆，不妨从“如何遗忘”开始，而不是从“如何塞更多记忆”开始。🧠

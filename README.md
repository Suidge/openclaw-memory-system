# OpenClaw Memory System (记忆仿生系统)

**版本**: v2.1  
**最后更新**: 2026-03-08  
**许可证**: MIT  
**作者**: 银月 (OpenClaw 社区)

---

## 📖 系统概述

这是一个模拟人类记忆"遗忘曲线"和"强化机制"的记忆管理系统，专为 OpenClaw AI 助手设计。

### 核心特性

1. **遗忘曲线**: 不重要的记忆随时间逐渐衰减
2. **强化机制**: 频繁使用的记忆会被加强（"越用越重要"）
3. **核心记忆**: 最重要的记忆永不遗忘
4. **动态评分**: 每天重新评估所有记忆的价值
5. **自动清理**: 低价值记忆自动标记待清理

### 记忆分层

| 类型 | 评分范围 | 衰减规则 | 说明 |
|------|---------|---------|------|
| **核心记忆** | ≥11 分 | ❌ 永不衰减 | 凭证、配置、重要决策 |
| **重要记忆** | 7-10 分 | ✅ 温和衰减 (1%/天) | 配置、技能、经验教训 |
| **普通记忆** | 4-6 分 | ✅ 正常衰减 (2%/天) | 日常日志、一般事项 |
| **琐碎记忆** | 1-3 分 | ✅ 加速衰减 (3%/天) | 闲聊、测试 |
| **日常记忆** | 1-15 分 | ❌ 不衰减 | 待提取到主记忆，超过 30 天自动清理 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- OpenClaw v2026.3+
- 无额外依赖（仅使用 Python 标准库）

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/Suidge/openclaw-memory-bionics-system.git
cd openclaw-memory-system
```

#### 2. 复制脚本到 OpenClaw 工作区

```bash
# 假设 OpenClaw 工作区在 ~/.openclaw/workspace
cp scripts/*.py ~/.openclaw/workspace/scripts/
cp scripts/*.md ~/.openclaw/workspace/scripts/
cp memory-bionics-system.md ~/.openclaw/workspace/
```

#### 3. 配置 Cron Job（可选）

编辑 `~/.openclaw/cron/jobs.json`，添加每日记忆维护任务：

```json
{
  "id": "daily-memory-maintenance",
  "name": "每日记忆维护",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 2 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日记忆维护任务。详细指引：~/.openclaw/workspace/scripts/daily-memory-maintenance-instructions.md"
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "user:YOUR_USER_ID"
  }
}
```

#### 4. 验证安装

```bash
# 测试评分脚本
python3 ~/.openclaw/workspace/scripts/memory-scoring.py

# 测试遗忘检查（干跑模式）
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py --dry-run

# 测试使用追踪
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --help
```

---

## 📁 文件结构

```
openclaw-memory-system/
├── README.md                              # 本文件
├── memory-bionics-system.md               # 完整系统规范文档
├── scripts/
│   ├── memory-scoring.py                  # 评分/重评脚本
│   ├── memory-decay-check.py              # 遗忘检查脚本
│   ├── memory-usage-tracker.py            # 使用追踪脚本
│   └── daily-memory-maintenance-instructions.md  # 维护指引
└── examples/
    └── decay-report-example.json          # 遗忘清单示例
```

### 部署后的文件位置

```
~/.openclaw/workspace/
├── MEMORY.md                              # 主记忆文件（长期记忆）
├── memory/
│   ├── YYYY-MM-DD.md                      # 每日记忆日志（短期记忆）
│   ├── usage-log.json                     # 使用追踪日志
│   └── decay-report.json                  # 遗忘检查报告
└── scripts/
    ├── memory-scoring.py                  # 评分脚本
    ├── memory-decay-check.py              # 遗忘检查脚本
    └── memory-usage-tracker.py            # 使用追踪脚本
```

---

## 🔧 脚本说明

### memory-scoring.py

**功能**: 为记忆条目评分和每日重评

**用法**:
```bash
python3 memory-scoring.py
```

**输出**:
- memory/ 文件：首次评分（关键词匹配，不衰减）
- MEMORY.md：每日重评（基础分 + 加分 - 衰减）

**评分规则**:
- 账号/密码/服务器/API Key → 15 分
- 邮箱/邮件 → 12 分
- 配置/设置/部署 → 9 分
- 安全/规则/策略 → 9 分
- 决策/决定/选择 → 8 分
- 技能/工具 → 7 分
- 日志/工作/任务 → 5 分

---

### memory-decay-check.py

**功能**: 检查遗忘条目（MEMORY.md 条目 + memory/过期文件）

**用法**:
```bash
# 正常模式（生成报告）
python3 memory-decay-check.py

# 干跑模式（仅检查，不生成报告）
python3 memory-decay-check.py --dry-run

# 详细输出
python3 memory-decay-check.py -v
```

**遗忘标准**:
- MEMORY.md 条目：importance < 2
- memory/ 文件：days_old > 30

**输出**: `memory/decay-report.json`

---

### memory-usage-tracker.py

**功能**: 记录记忆条目使用（搜索命中、引用），计算加分

**用法**:
```bash
# 记录搜索命中
python3 memory-usage-tracker.py '条目标题' search

# 记录引用
python3 memory-usage-tracker.py '条目标题' citation

# 分析模式（每日汇总）
python3 memory-usage-tracker.py --analyze

# 查看帮助
python3 memory-usage-tracker.py --help
```

**加分规则**:
- 被搜索命中：+0.1/次
- 被引用使用：+0.2/次
- 加分上限：+10 分

---

## 📊 每日执行流程

```
每天凌晨 02:00 自动执行：
       ↓
┌──────────────────────────────────────┐
│ 任务 1：分析使用日志                  │
│ memory-usage-tracker.py --analyze    │
├──────────────────────────────────────┤
│ • 汇总昨天的搜索命中和引用记录       │
│ • 更新 usage-log.json 中的加分数据   │
│ • 输出：加分变动摘要                 │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 2：评分/重评                     │
│ memory-scoring.py                    │
├──────────────────────────────────────┤
│ • memory/ 文件：首次评分             │
│ • MEMORY.md：每日重评                │
│   （基础分 + 加分 - 衰减）           │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 3：遗忘检查                      │
│ memory-decay-check.py                │
├──────────────────────────────────────┤
│ • MEMORY.md 条目：检查 importance<2 │
│ • memory/ 文件：检查 days_old>30    │
│ • 生成遗忘清单                       │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 4：汇报遗忘清单                  │
│ 通过飞书/邮件发送给主人              │
├──────────────────────────────────────┤
│ 遗忘清单 = MEMORY.md 条目 + 文件    │
│ 等待主人确认                         │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│ 任务 5：执行清理（主人确认后）        │
├──────────────────────────────────────┤
│ • 从 MEMORY.md 删除遗忘条目          │
│ • 使用 trash 删除 memory/ 文件        │
│ • 清理 usage-log.json 中的无效条目   │
└──────────────────────────────────────┘
```

---

## 🔍 运维指南

### 日常检查

```bash
# 查看最新遗忘报告
cat ~/.openclaw/workspace/memory/decay-report.json

# 查看使用日志
cat ~/.openclaw/workspace/memory/usage-log.json

# 查看检查日志
tail -50 ~/.openclaw/workspace/memory/forget-check.log
```

### 手动执行记忆维护

```bash
# 评分/重评
python3 ~/.openclaw/workspace/scripts/memory-scoring.py

# 遗忘检查（干跑模式）
python3 ~/.openclaw/workspace/scripts/memory-decay-check.py --dry-run

# 分析使用日志
python3 ~/.openclaw/workspace/scripts/memory-usage-tracker.py --analyze
```

### 常见问题

#### Q1: 为什么某条目没有被清理？

**检查**:
- 评分是否 ≥2
- 是否是核心记忆（≥11 分）
- 是否加分抵消了衰减

#### Q2: 如何恢复被清理的记忆？

**方法**:
- 检查废纸篓（`trash` 命令的文件可恢复）
- 从 Git 历史恢复 MEMORY.md

#### Q3: usage-log.json 文件过大怎么办？

**解决**:
- 清理已遗忘条目的记录
- 脚本会自动清理，也可以手动执行：
  ```bash
  python3 memory-usage-tracker.py --cleanup
  ```

#### Q4: 如何调整衰减参数？

**修改**:
- `memory-scoring.py` 中的 `decay_rate`
- `memory-decay-check.py` 中的 `FORGOTTEN_THRESHOLD` 和 `FILE_EXPIRY_DAYS`
- 修改后测试验证

---

## 📝 配置示例

### 环境变量（可选）

```bash
# 自定义时区（默认 Asia/Shanghai）
export MEMORY_SYSTEM_TZ="Asia/Shanghai"

# 自定义遗忘阈值（默认 2）
export FORGOTTEN_THRESHOLD=2

# 自定义文件过期天数（默认 30）
export FILE_EXPIRY_DAYS=30
```

### Cron Job 配置示例

```json
{
  "id": "daily-memory-maintenance",
  "name": "每日记忆维护",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 2 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日记忆维护任务。详细指引：~/.openclaw/workspace/scripts/daily-memory-maintenance-instructions.md"
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "user:YOUR_USER_ID"
  }
}
```

---

## 🧪 测试

### 单元测试

```bash
# 运行测试套件
python3 -m pytest tests/ -v
```

### 集成测试

```bash
# 创建测试记忆文件
echo '### 测试条目 1
这是一个测试条目。
<!-- importance: 5 -->' > /tmp/test-memory.md

# 测试评分脚本
python3 scripts/memory-scoring.py

# 测试遗忘检查
python3 scripts/memory-decay-check.py --dry-run
```

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📧 联系方式

- **项目主页**: https://github.com/Suidge/openclaw-memory-bionics-system
- **问题反馈**: https://github.com/Suidge/openclaw-memory-bionics-system/issues
- **OpenClaw 文档**: https://docs.openclaw.ai

---

## 📚 相关文档

- [记忆仿生系统规范](memory-bionics-system.md) - 完整的系统机制说明
- [每日维护指引](scripts/daily-memory-maintenance-instructions.md) - 运维人员参考
- [OpenClaw 官方文档](https://docs.openclaw.ai) - OpenClaw 平台文档

---

*本文档会随系统迭代持续更新，请以最新版本为准。*

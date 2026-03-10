# 🧠 OpenClaw Memory System | 仿生记忆系统

> **让 AI 拥有像人类一样的记忆能力**  
> A biomimetic memory architecture for OpenClaw agents

<div align="center">

![Memory System Architecture](https://img.shields.io/badge/Architecture-Biomimetic-blue)
![Version](https://img.shields.io/badge/Version-v2.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

## 🌟 项目愿景 | Vision

**人类如何记忆？**

海马体将短期经历编码 → 睡眠中 consolidation（巩固）→ 皮层存储长期记忆 → 随时间衰减遗忘

**AI 如何记忆？**

大多数 AI 助手：把一切写入文件 → 文件越来越多 → 检索越来越慢 → 记忆变成"数据坟墓"

**我们的答案：**

> 模仿人类记忆机制，构建**会遗忘、会提炼、会进化**的 AI 记忆系统

---

## 🔬 仿生学设计原理 | Biomimetic Design

### 1. 双层记忆结构 (Two-Layer Architecture)

<div align="center">

```svg
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="800" height="300" fill="#f8f9fa"/>
  
  <!-- Human Brain Side -->
  <g transform="translate(50, 50)">
    <text x="150" y="-20" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">🧠 人类大脑</text>
    
    <!-- Hippocampus -->
    <rect x="50" y="20" width="200" height="60" rx="8" fill="#74b9ff" stroke="#0984e3" stroke-width="2"/>
    <text x="150" y="45" text-anchor="middle" font-size="14" fill="white" font-weight="bold">海马体</text>
    <text x="150" y="65" text-anchor="middle" font-size="10" fill="white">短期记忆</text>
    
    <!-- Cortex -->
    <rect x="50" y="100" width="200" height="60" rx="8" fill="#a29bfe" stroke="#6c5ce7" stroke-width="2"/>
    <text x="150" y="125" text-anchor="middle" font-size="14" fill="white" font-weight="bold">大脑皮层</text>
    <text x="150" y="145" text-anchor="middle" font-size="10" fill="white">长期记忆</text>
    
    <!-- Arrow -->
    <path d="M 150 80 L 150 100" stroke="#636e72" stroke-width="2" marker-end="url(#arrowhead)"/>
    <text x="160" y="95" font-size="10" fill="#636e72">巩固</text>
  </g>
  
  <!-- OpenClaw Side -->
  <g transform="translate(450, 50)">
    <text x="150" y="-20" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">🤖 OpenClaw</text>
    
    <!-- Daily Memory -->
    <rect x="50" y="20" width="200" height="60" rx="8" fill="#74b9ff" stroke="#0984e3" stroke-width="2"/>
    <text x="150" y="45" text-anchor="middle" font-size="14" fill="white" font-weight="bold">memory/*.md</text>
    <text x="150" y="65" text-anchor="middle" font-size="10" fill="white">原始经历/日志</text>
    
    <!-- Main Memory -->
    <rect x="50" y="100" width="200" height="60" rx="8" fill="#a29bfe" stroke="#6c5ce7" stroke-width="2"/>
    <text x="150" y="125" text-anchor="middle" font-size="14" fill="white" font-weight="bold">MEMORY.md</text>
    <text x="150" y="145" text-anchor="middle" font-size="10" fill="white">提炼认知/规则</text>
    
    <!-- Arrow -->
    <path d="M 150 80 L 150 100" stroke="#636e72" stroke-width="2" marker-end="url(#arrowhead)"/>
    <text x="160" y="95" font-size="10" fill="#636e72">consolidation</text>
  </g>
  
  <!-- Arrow definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#636e72"/>
    </marker>
  </defs>
</svg>
```

</div>

| 人类大脑 | OpenClaw 记忆系统 | 功能 |
|---------|------------------|------|
| **海马体** (短期记忆) | `memory/YYYY-MM-DD.md` | 存储原始经历、执行日志、反思草稿 |
| **大脑皮层** (长期记忆) | `MEMORY.md` | 存储提炼后的认知、规则、决策 |
| **突触修剪** | `memory-decay-check.py` | 定期清理低复用内容 |

**设计洞察**：
> 人类的长期记忆不是"高分事件的集合"，而是**经过压缩的认知索引**。  
> 同样，`MEMORY.md` 不应是日志仓库，而应是**可复用的智慧结晶**。

---

### 2. 记忆巩固机制 (Memory Consolidation)

<div align="center">

```svg
<svg viewBox="0 0 900 280" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="900" height="280" fill="#f8f9fa"/>
  
  <!-- Human Consolidation -->
  <g transform="translate(30, 30)">
    <rect x="0" y="0" width="400" height="110" rx="10" fill="#dfe6e9" stroke="#636e72" stroke-width="1"/>
    <text x="200" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#2d3436">🧠 人类记忆巩固 (睡眠中)</text>
    
    <g transform="translate(20, 40)">
      <rect x="0" y="0" width="70" height="40" rx="5" fill="#0984e3"/>
      <text x="35" y="25" text-anchor="middle" font-size="10" fill="white">白天经历</text>
      
      <path d="M 70 20 L 90 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="90" y="0" width="70" height="40" rx="5" fill="#0984e3"/>
      <text x="125" y="20" text-anchor="middle" font-size="9" fill="white">海马体</text>
      <text x="125" y="32" text-anchor="middle" font-size="9" fill="white">回放</text>
      
      <path d="M 160 20 L 180 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="180" y="0" width="70" height="40" rx="5" fill="#6c5ce7"/>
      <text x="215" y="20" text-anchor="middle" font-size="9" fill="white">提取</text>
      <text x="215" y="32" text-anchor="middle" font-size="9" fill="white">核心模式</text>
      
      <path d="M 250 20 L 270 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="270" y="0" width="70" height="40" rx="5" fill="#a29bfe"/>
      <text x="305" y="20" text-anchor="middle" font-size="9" fill="white">皮层</text>
      <text x="305" y="32" text-anchor="middle" font-size="9" fill="white">存储</text>
      
      <path d="M 340 20 L 360 20" stroke="#636e72" stroke-width="2" stroke-dasharray="4"/>
      <text x="350" y="15" font-size="8" fill="#b2bec3">遗忘</text>
    </g>
  </g>
  
  <!-- OpenClaw Consolidation -->
  <g transform="translate(30, 150)">
    <rect x="0" y="0" width="400" height="110" rx="10" fill="#dfe6e9" stroke="#636e72" stroke-width="1"/>
    <text x="200" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#2d3436">🤖 OpenClaw (daily-meditation)</text>
    
    <g transform="translate(20, 40)">
      <rect x="0" y="0" width="70" height="40" rx="5" fill="#0984e3"/>
      <text x="35" y="20" text-anchor="middle" font-size="9" fill="white">daily</text>
      <text x="35" y="32" text-anchor="middle" font-size="9" fill="white">memory</text>
      
      <path d="M 70 20 L 90 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="90" y="0" width="70" height="40" rx="5" fill="#0984e3"/>
      <text x="125" y="20" text-anchor="middle" font-size="9" fill="white">scoring</text>
      <text x="125" y="32" text-anchor="middle" font-size="9" fill="white">评分</text>
      
      <path d="M 160 20 L 180 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="180" y="0" width="70" height="40" rx="5" fill="#6c5ce7"/>
      <text x="215" y="20" text-anchor="middle" font-size="9" fill="white">classify</text>
      <text x="215" y="32" text-anchor="middle" font-size="9" fill="white">分类</text>
      
      <path d="M 250 20 L 270 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="270" y="0" width="70" height="40" rx="5" fill="#a29bfe"/>
      <text x="305" y="20" text-anchor="middle" font-size="9" fill="white">distill</text>
      <text x="305" y="32" text-anchor="middle" font-size="9" fill="white">提炼</text>
      
      <path d="M 340 20 L 360 20" stroke="#636e72" stroke-width="2" marker-end="url(#arrow)"/>
      
      <rect x="360" y="0" width="30" height="40" rx="5" fill="#fdcb6e"/>
      <text x="375" y="25" text-anchor="middle" font-size="10" fill="white">MEMORY</text>
    </g>
  </g>
  
  <!-- Arrow definition -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#636e72"/>
    </marker>
  </defs>
</svg>
```

</div>

**v2.3 核心升级**：
- ❌ 旧模式：`高分 → 直接进入主记忆`
- ✅ 新模式：`候选评分 → 类型判断 → 长期价值评估 → 提炼固化`

---

### 3. 遗忘机制 (Forgetting Mechanism)

<div align="center">

```svg
<svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="800" height="200" fill="#f8f9fa"/>
  
  <!-- Title -->
  <text x="400" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#2d3436">🕰️ 记忆衰减曲线</text>
  
  <!-- Axes -->
  <line x1="50" y1="170" x2="750" y2="170" stroke="#636e72" stroke-width="2"/>
  <line x1="50" y1="170" x2="50" y2="30" stroke="#636e72" stroke-width="2"/>
  
  <!-- X-axis label -->
  <text x="400" y="195" text-anchor="middle" font-size="12" fill="#636e72">时间 (天)</text>
  <text x="750" y="185" font-size="10" fill="#636e72">→</text>
  
  <!-- Y-axis label -->
  <text x="20" y="100" text-anchor="middle" font-size="12" fill="#636e72" transform="rotate(-90, 20, 100)">重要性评分</text>
  <text x="45" y="35" font-size="10" fill="#636e72">↑</text>
  
  <!-- Decay curves -->
  <!-- High importance (7-10) -->
  <path d="M 50 60 Q 200 70, 400 85 T 750 110" fill="none" stroke="#6c5ce7" stroke-width="3"/>
  <text x="600" y="95" font-size="11" fill="#6c5ce7" font-weight="bold">7-10 分 (温和衰减 -0.01/天)</text>
  
  <!-- Medium importance (4-6) -->
  <path d="M 50 60 Q 200 80, 400 105 T 750 140" fill="none" stroke="#0984e3" stroke-width="3" stroke-dasharray="5,3"/>
  <text x="600" y="125" font-size="11" fill="#0984e3" font-weight="bold">4-6 分 (正常衰减 -0.02/天)</text>
  
  <!-- Low importance (1-3) -->
  <path d="M 50 60 Q 150 100, 300 140 T 500 165" fill="none" stroke="#d63031" stroke-width="3" stroke-dasharray="2,2"/>
  <text x="380" y="160" font-size="11" fill="#d63031" font-weight="bold">1-3 分 (快速衰减 -0.03/天)</text>
  
  <!-- Threshold line -->
  <line x1="50" y1="150" x2="750" y2="150" stroke="#fdcb6e" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="760" y="155" font-size="10" fill="#fdcb6e">遗忘阈值 (2.0)</text>
  
  <!-- Core memory line -->
  <line x1="50" y1="50" x2="750" y2="50" stroke="#00b894" stroke-width="2"/>
  <text x="600" y="45" font-size="11" fill="#00b894" font-weight="bold">≥11 分 核心记忆 (永不衰减)</text>
</svg>
```

</div>

| 遗忘类型 | 人类机制 | OpenClaw 实现 |
|---------|---------|--------------|
| **衰退性遗忘** | 突触连接随时间减弱 | `decay.py` 每日衰减评分 |
| **干扰性遗忘** | 相似记忆相互抑制 | 去重检测，避免重复插入 |
| **动机性遗忘** | 情绪调节主动压抑 | 低复用事件标记清理 |
| **提取失败** | 线索不足无法回忆 | 搜索命中追踪，低命中预警 |

**设计哲学**：
> 遗忘不是缺陷，而是**认知效率的必要条件**。  
> 一个不会遗忘的记忆系统，最终会被噪音淹没。

---

### 4. 记忆评分系统 (Scoring System)

```
重要性评分 (1-10 分)
├── 1-3 分：琐碎日常 → 快速衰减 (-0.03/天)
├── 4-6 分：普通事件 → 正常衰减 (-0.02/天)
├── 7-10 分：重要认知 → 温和衰减 (-0.01/天)
└── ≥11 分：核心记忆 → 永不衰减 (长期存储)
```

**评分维度**：
- 🔍 **可复用性**：未来是否会被再次引用？
- 📌 **稳定性**：是长期事实还是临时状态？
- 🎯 **决策价值**：是否影响未来行为？
- 📚 **规则性**：是否可抽象为通用原则？

---

## 🏗️ 系统架构 | Architecture

<div align="center">

```svg
<svg viewBox="0 0 900 450" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="900" height="450" fill="#f8f9fa"/>
  
  <!-- Daily Memory Layer -->
  <g transform="translate(50, 30)">
    <rect x="0" y="0" width="800" height="80" rx="10" fill="#74b9ff" stroke="#0984e3" stroke-width="2"/>
    <text x="400" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="white">📝 Daily Memory Layer</text>
    <text x="400" y="45" text-anchor="middle" font-size="12" fill="white">memory/YYYY-MM-DD.md</text>
    <text x="400" y="62" text-anchor="middle" font-size="11" fill="white">原始经历 | 执行日志 | 反思草稿 | 临时笔记</text>
  </g>
  
  <!-- Arrow down -->
  <path d="M 450 110 L 450 130" stroke="#636e72" stroke-width="3" marker-end="url(#arrowhead)"/>
  
  <!-- Scoring Module -->
  <g transform="translate(300, 130)">
    <rect x="0" y="0" width="300" height="60" rx="8" fill="#0984e3" stroke="#06528f" stroke-width="2"/>
    <text x="150" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="white">memory-scoring.py</text>
    <text x="150" y="45" text-anchor="middle" font-size="11" fill="white">重要性评分 | 候选标记</text>
  </g>
  
  <!-- Arrow down -->
  <path d="M 450 190 L 450 210" stroke="#636e72" stroke-width="3" marker-end="url(#arrowhead)"/>
  
  <!-- Candidate Filter -->
  <g transform="translate(325, 210)">
    <rect x="0" y="0" width="250" height="50" rx="25" fill="#fdcb6e" stroke="#e17055" stroke-width="2"/>
    <text x="125" y="30" text-anchor="middle" font-size="13" font-weight="bold" fill="#2d3436">候选 (importance ≥ 7)</text>
  </g>
  
  <!-- Arrow down -->
  <path d="M 450 260 L 450 280" stroke="#636e72" stroke-width="3" marker-end="url(#arrowhead)"/>
  
  <!-- Consolidation Module -->
  <g transform="translate(300, 280)">
    <rect x="0" y="0" width="300" height="60" rx="8" fill="#6c5ce7" stroke="#4834d4" stroke-width="2"/>
    <text x="150" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="white">memory-consolidation.py</text>
    <text x="150" y="45" text-anchor="middle" font-size="11" fill="white">类型判断 | 价值评估 | 提炼固化</text>
  </g>
  
  <!-- Arrow down -->
  <path d="M 450 340 L 450 360" stroke="#636e72" stroke-width="3" marker-end="url(#arrowhead)"/>
  
  <!-- Main Memory Layer -->
  <g transform="translate(50, 360)">
    <rect x="0" y="0" width="800" height="80" rx="10" fill="#a29bfe" stroke="#6c5ce7" stroke-width="2"/>
    <text x="400" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="white">🧠 Main Memory Layer</text>
    <text x="400" y="45" text-anchor="middle" font-size="12" fill="white">MEMORY.md</text>
    <text x="400" y="62" text-anchor="middle" font-size="11" fill="white">长期事实 | 重要决策 | 可复用规则 | 提炼认知</text>
  </g>
  
  <!-- Arrow to decay -->
  <path d="M 850 400 L 880 400 L 880 50 L 850 50" stroke="#636e72" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrowhead)"/>
  
  <!-- Decay Check Module -->
  <g transform="translate(550, 20)">
    <rect x="0" y="0" width="280" height="60" rx="8" fill="#d63031" stroke="#c0392b" stroke-width="2"/>
    <text x="140" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="white">memory-decay-check.py</text>
    <text x="140" y="45" text-anchor="middle" font-size="11" fill="white">遗忘审计 | 清理建议</text>
  </g>
  
  <!-- Arrow definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#636e72"/>
    </marker>
  </defs>
</svg>
```

</div>

---

## 📂 项目结构 | Structure

```
openclaw-memory-system/
├── README.md                          # 项目说明（本文件）
├── memory-bionics-system.md           # 系统规范文档
├── scripts/
│   ├── memory-scoring.py              # 前端评分
│   ├── memory-consolidation.py        # 后端提炼
│   ├── memory-decay-check.py          # 遗忘审计
│   ├── memory-usage-tracker.py        # 使用追踪
│   ├── daily-memory-maintenance-instructions.md
│   └── daily-meditation-instructions.md
└── examples/
    └── decay-report.json.example
```

---

## 🚀 快速开始 | Quick Start

### 1. 阅读文档
```bash
# 阅读顺序
1. README.md
2. memory-bionics-system.md
3. scripts/daily-memory-maintenance-instructions.md
4. scripts/daily-meditation-instructions.md
```

### 2. 试运行核心流程
```bash
# 评分（最近 3 天，带解释）
python3 scripts/memory-scoring.py --dry-run --explain --recent-days 3

# 提炼（最近 3 天）
python3 scripts/memory-consolidation.py --dry-run --recent-days 3

# 遗忘审计
python3 scripts/memory-decay-check.py --dry-run
```

### 3. 检查关键问题
- [ ] 过程记录是否太容易进入候选集？
- [ ] 提炼是否放入了应留在 daily memory 的内容？
- [ ] 治理输出是否合理？

---

## 🧬 与人类记忆的横向对比 | Comparison

| 特性 | 人类记忆 | 传统 AI 记忆 | OpenClaw 仿生记忆 |
|-----|---------|------------|-----------------|
| **存储策略** | 选择性编码 | 全量存储 | 选择性提炼 |
| **遗忘机制** | 主动衰减 | 无/手动删除 | 自动衰减 + 审计 |
| **巩固过程** | 睡眠中回放 | 无 | daily-meditation |
| **提取线索** | 多模态关联 | 关键词匹配 | 搜索命中追踪 |
| **容量限制** | 有限 (7±2) | 理论上无限 | 紧凑索引约束 |
| **情绪影响** | 强烈调节 | 无 | 可扩展情绪权重 |
| **可塑性** | 持续重构 | 静态存储 | 动态更新 + 合并 |

---

## 🎯 设计原则 | Design Principles

### 1. 紧凑性优先 (Compactness First)
> `MEMORY.md` 是认知索引，不是数据仓库。  
> 能用一句话总结的，就不要保留整段过程。

### 2. 遗忘即智慧 (Forgetting is Wisdom)
> 不会遗忘的系统，终将被噪音淹没。  
> 定期清理低复用内容，保持记忆活力。

### 3. 提炼胜于存储 (Distillation over Dumping)
> 原始经历 → 提炼认知  
> 不是"发生了什么"，而是"学到了什么"。

### 4. 可复用性驱动 (Reusability Driven)
> 记忆的价值不在于"记住"，而在于"能用"。  
> 搜索命中和使用引用是核心评分信号。

---

## 📊 当前版本 | Current Version

**v2.3** - 紧凑认知索引方向

**核心改进**：
- ✅ 评分仅作为候选信号，非直接准入
- ✅ 类型判断 + 长期价值评估双重过滤
- ✅ 治理检查保持 `MEMORY.md` 紧凑
- ✅ 阻止过程记录进入主记忆
- ✅ 支持规则/决策片段合并建议

---

## 📝 使用场景 | Use Cases

### ✅ 适合存储到 MEMORY.md
- 长期有效的事实（如 API 配置、服务地址）
- 重要决策及其原因
- 可复用的规则和原则
- 经过提炼的认知模式

### ❌ 不适合存储到 MEMORY.md
- 单次执行过程日志
- 临时性状态信息
- 未提炼的原始反思
- 系统设计文档本身（应放在单独文件）

---

## 🤝 新维护者交接 | Handoff

新 Agent 或维护者接手时，请按此顺序：

1. **阅读文档**
   - 本文件
   - `memory-bionics-system.md`
   - 两个 instruction 文件

2. **试运行完整流程**
   ```bash
   python3 scripts/memory-scoring.py --dry-run --explain --recent-days 3
   python3 scripts/memory-consolidation.py --dry-run --recent-days 3
   python3 scripts/memory-decay-check.py --dry-run
   ```

3. **回答三个问题**
   - 过程记录是否太容易进入候选集？
   - 提炼是否放入了应留在 daily memory 的内容？
   - 治理输出是否合理？

4. **确认后再执行非 dry-run 操作**

---

## 📄 许可证 | License

MIT License

---

## 🌙 关于本项目 | About

本项目由 OpenClaw 社区开发，旨在为 AI 助手构建**类人记忆机制**。

> **核心理念**：记忆不是存储，而是**可提取、可复用、可进化**的认知资产。

---

<div align="center">

**🧠 让 AI 的记忆像人类一样聪明**

*Built with biomimetic principles for OpenClaw agents*

</div>

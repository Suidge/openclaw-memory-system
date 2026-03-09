#!/usr/bin/env python3
"""
记忆重要性评分脚本 (v2.2)
为 daily memory 条目执行首次评分

功能：
1. 扫描 `memory/*.md` 文件
2. 为其中尚未评分的条目执行首次评分（关键词匹配，不衰减）
3. 供后续维护任务按规则吸收高价值条目进入 `MEMORY.md`

说明：
- 本脚本当前职责是给 `memory/*.md` 条目打分
- 不直接处理 `MEMORY.md` 的主记忆吸收/维护
- 加分上限：+10 分（供后续维护流程参考）

作者：银月
版本：2.2
最后更新：2026-03-08
"""

import os
import re
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
USAGE_LOG = Path.home() / ".openclaw" / "workspace" / "memory" / "usage-log.json"
MEMORY_FILE = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"

# 时区常量
TZ_SHANGHAI = timezone(timedelta(hours=8))

# 关键词评分规则（首次评分用）
KEYWORD_SCORES = [
    # 高敏感 / 高价值信息
    (r'账号|密码|服务器|api.?key|smtp|imap|token|secret|credential', 15),
    (r'邮箱|邮件|email|silvermoon@', 12),

    # 系统级 / 机制级 / 架构级事项
    (r'记忆系统|主记忆|遗忘机制|吸收规则|评分机制|工作流|架构|机制', 8),
    (r'升级完成|修复完成|重构完成|部署完成|迁移完成|优化完成|落地', 8),
    (r'重大更新|关键修复|核心修复|系统修复|正式启用|上线|发布', 8),

    # 配置 / 安全 / 决策 / 模型
    (r'bitwarden|vault|auth|login|oauth', 9),
    (r'配置|设置|config|setup|部署|安装', 9),
    (r'安全|规则|策略|security|policy', 9),
    (r'决策|决定|选择|decision', 8),
    (r'模型|model|agent|binding', 8),
    (r'cron|heartbeat|schedule', 8),

    # 一般技术事项
    (r'技能|skill|工具|tool', 7),
    (r'问题|错误|bug|fix', 6),
    (r'日志|log|工作|任务|task', 5),
    (r'事件|发生|event', 5),
]


def load_usage_bonus() -> Dict[str, float]:
    """
    加载加分数据
    
    Returns:
        Dict[str, float]: 条目标题到加分的映射字典
    """
    if not USAGE_LOG.exists():
        return {}
    try:
        with open(USAGE_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {title: entry.get("bonus_score", 0.0) for title, entry in data.get("entries", {}).items()}
    except Exception as e:
        print(f"⚠️ 加载加分数据失败：{e}")
        return {}


def calculate_keyword_score(content: str) -> int:
    """
    根据 daily memory 条目的标题与正文做首次评分。

    规则：
    1. 取所有命中规则中的最高分（比“命中第一个就返回”更稳）
    2. 若条目具有明确“完成/升级/修复/重构/优化/部署”语义，则轻量 +1
    3. 若条目带有文档类信号，仅在缺少强主信号时才执行轻微抑制
    4. 长内容提供轻微兜底分

    Args:
        content: 条目内容（标题 + 下方内容）

    Returns:
        int: 关键词评分
    """
    base_score = 5
    content_lower = content.lower()
    title_only = content.split('\n', 1)[0].lower()

    strong_signal_patterns = [
        r'记忆系统|主记忆|遗忘机制|吸收规则|评分机制|工作流|架构|机制',
        r'升级完成|修复完成|重构完成|部署完成|迁移完成|优化完成|落地',
        r'重大更新|关键修复|核心修复|系统修复|正式启用|上线|发布',
    ]
    doc_signal_patterns = [
        r'文档版|修订版|草案|口径澄清|汇报|整理版|读书笔记|学习笔记',
    ]
    implementation_signal_patterns = [
        r'\.py|scripts/|memory-scoring|memory-decay-check|memory-usage-tracker',
        r'配置|代码|脚本|实现|验证通过|commit|git|修复内容|相关文件',
    ]

    # 1. 取命中规则中的最高分
    for pattern, weight in KEYWORD_SCORES:
        if re.search(pattern, content_lower):
            base_score = max(base_score, weight)

    has_strong_signal = any(re.search(p, content_lower) for p in strong_signal_patterns)
    has_doc_signal = any(re.search(p, content_lower) for p in doc_signal_patterns)
    has_title_doc_signal = any(re.search(p, title_only) for p in doc_signal_patterns)
    has_implementation_signal = any(re.search(p, content_lower) for p in implementation_signal_patterns)

    # 2. 完成态轻量加成
    if re.search(r'完成|修复|升级|重构|优化|部署|迁移|落地|启用|发布|上线', content_lower):
        if base_score < 10:
            base_score = min(base_score + 1, 10)

    # 3. 文档类轻微抑制：
    # - 若标题本身就是文档/汇报/修订类条目，则最高压到 7
    # - 若是纯文档条目（无强主信号且无实现证据），压到 6
    # - 若带文档信号但缺少实现证据，即使有强主信号，也最多保留到 7
    if has_title_doc_signal and base_score > 7:
        base_score = 7

    if has_doc_signal:
        if not has_strong_signal and not has_implementation_signal:
            if base_score > 6:
                base_score = 6
        elif not has_implementation_signal:
            if base_score > 7:
                base_score = 7

    # 4. 长内容轻微兜底
    if len(content) > 1000:
        base_score = max(base_score, 6)

    return int(base_score)


def calculate_new_importance(current_importance: int, days_old: int, usage_bonus: float) -> int:
    """
    计算主记忆维护阶段可复用的评分公式。

    说明：当前 v2.2 工作流中，本脚本主要负责 `memory/*.md` 的首次评分；
    该函数保留代码版衰减公式，供后续主记忆维护流程复用。
    
    衰减规则：
    - 核心记忆（≥11 分）：不衰减，只加分
    - 重要记忆（7-10 分）：温和衰减 (1%/天)
    - 普通记忆（4-6 分）：正常衰减 (2%/天)
    - 琐碎记忆（1-3 分）：加速衰减 (3%/天)
    
    Args:
        current_importance: 当前评分
        days_old: 存在天数
        usage_bonus: 使用加分（0-10）
    
    Returns:
        新评分
    """
    # 核心记忆（≥11 分）：只加分，不衰减
    if current_importance >= 11:
        return min(99, current_importance + int(usage_bonus))
    
    # 根据当前评分确定衰减率
    if current_importance <= 3:
        decay_rate = 0.03  # 加速衰减
    elif current_importance <= 6:
        decay_rate = 0.02  # 正常衰减
    else:
        decay_rate = 0.01  # 温和衰减
    
    # 修正：衰减基于当前评分，低分记忆衰减更快
    time_decay = current_importance * decay_rate * days_old
    new_score = current_importance + usage_bonus - time_decay
    return max(1, min(99, int(new_score)))


def parse_date_from_title(title: str) -> datetime:
    """从标题解析日期"""
    tz_sh = TZ_SHANGHAI
    
    # 尝试匹配 YYYY-MM-DD
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), '%Y-%m-%d').replace(tzinfo=tz_sh)
        except ValueError:
            pass
    
    # 尝试匹配 YYYY-WXX
    week_match = re.search(r'(\d{4}-W\d{2})', title)
    if week_match:
        try:
            return datetime.strptime(week_match.group(1) + '-1', '%G-W%V-%u').replace(tzinfo=tz_sh)
        except ValueError:
            pass
    
    # 返回当前日期
    return datetime.now(tz_sh)


def calculate_days_old(title: str) -> int:
    """计算条目存在天数"""
    entry_date = parse_date_from_title(title)
    now = datetime.now(TZ_SHANGHAI)
    return max(0, (now - entry_date).days)


def score_daily_log_entries(filepath: Path) -> List[str]:
    """
    为 memory/ 日志文件首次评分（不衰减，不加分）
    
    Args:
        filepath: 文件路径
    
    Returns:
        评分条目列表
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 ### 或 #### 标题格式
    pattern = r'(#{3,4}\s+[^\n]+)'
    matches = list(re.finditer(pattern, content))
    
    scored_entries = []
    
    for match in reversed(matches):
        title = match.group(1).strip()
        
        # 检查是否已有评分
        start_pos = int(match.end())
        next_match = re.search(r'\n#{3,4}', content[start_pos:])
        end_pos = start_pos + int(next_match.start()) if next_match else len(content)
        
        # 获取条目标题 + 标题下方的内容（不包括下一个标题）
        entry_title = title
        entry_body = content[start_pos:end_pos].strip()
        entry_content = entry_title + "\n" + entry_body
        
        if '<!-- importance:' in entry_content:
            continue
        
        # 首次评分（关键词匹配：使用条目标题 + 下方内容）
        importance = calculate_keyword_score(entry_content)
        new_title = f"{title} <!-- importance: {importance} -->"
        
        start_idx = int(match.start(1))
        end_idx = int(match.end(1))
        content = content[:start_idx] + new_title + content[end_idx:]
        
        scored_entries.append(f"  - {title}: importance={importance} (首次)")
    
    scored_entries.reverse()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return scored_entries


def rescore_memory_md(usage_bonus_map: Dict[str, float]) -> List[str]:
    """
    预留：为 `MEMORY.md` 动态记忆区执行重评。

    说明：当前 v2.2 工作流中，`MEMORY.md` 的吸收与维护不由本脚本主流程直接执行。
    此函数暂保留，供后续维护流程或独立任务复用。
    
    Args:
        usage_bonus_map: 加分数据
    
    Returns:
        重评条目列表
    """
    if not MEMORY_FILE.exists():
        print(f"❌ MEMORY.md 不存在")
        return []
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取动态记忆区
    dynamic_section = content.split('## 📅 动态记忆区')
    if len(dynamic_section) < 2:
        print("⚠️ 未找到动态记忆区")
        return []
    
    dynamic_content = dynamic_section[1]
    dynamic_start = content.find('## 📅 动态记忆区')
    
    # 匹配 #### YYYY-MM-DD 或 #### 2026-WXX
    pattern = r'(####\s+(?:\d{4}-\d{2}-\d{2}|\d{4}-W\d+)[^\n]*)\s*<!--\s*importance:\s*(\d+)\s*-->'
    matches = list(re.finditer(pattern, dynamic_content))
    
    rescored_entries = []
    updated_count = 0
    
    for match in reversed(matches):
        title_line = match.group(1).strip()
        title_clean = re.sub(r'\s*<!--.*?-->', '', title_line).strip()
        current_importance = int(match.group(2))
        
        # 计算天数和加分
        days_old = calculate_days_old(title_line)
        usage_bonus = usage_bonus_map.get(title_clean, 0.0)
        
        # 每日重评
        new_importance = calculate_new_importance(current_importance, days_old, usage_bonus)
        
        if new_importance != current_importance:
            old_tag = f'<!-- importance: {current_importance} -->'
            new_tag = f'<!-- importance: {new_importance} -->'
            
            global_pos = dynamic_start + match.start()
            global_end = dynamic_start + match.end()
            content = content[:global_pos] + title_line + f' {new_tag}' + content[global_end:]
            
            change_type = "↑" if new_importance > current_importance else "↓"
            bonus_info = f"+{usage_bonus:.1f}" if usage_bonus > 0 else "0"
            rescored_entries.append(f"  - {title_clean}: {current_importance} → {new_importance} ({change_type} {bonus_info} 分，{days_old} 天)")
            updated_count += 1
    
    if updated_count > 0:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return rescored_entries


def main():
    print("=" * 60)
    print("记忆重要性评分脚本 (v2.2 初次评分)")
    print("=" * 60)
    
    if not MEMORY_DIR.exists():
        print(f"❌ 记忆目录不存在：{MEMORY_DIR}")
        return
    
    # 加载加分数据
    usage_bonus_map = load_usage_bonus()
    print(f"\n加载加分数据：{len(usage_bonus_map)} 个条目")
    
    # 扫描文件
    files = list(MEMORY_DIR.glob('*.md'))
    print(f"扫描 {len(files)} 个记忆文件\n")
    
    all_scored_entries = []
    rescored_entries = []
    
    for filepath in sorted(files):
        if filepath.name.endswith('.md') and not filepath.name.startswith('记忆'):
            # memory/ 文件：首次评分（排除非日志文件）
            print(f"评分：{filepath.name}")
            entries = score_daily_log_entries(filepath)
            all_scored_entries.extend(entries)
    
    print("\n" + "=" * 60)
    print("评分结果")
    print("=" * 60)
    
    if all_scored_entries:
        print(f"\n新增评分：{len(all_scored_entries)} 个条目")
        for entry in all_scored_entries[:20]:
            print(entry)
        if len(all_scored_entries) > 20:
            print(f"  ... 还有 {len(all_scored_entries) - 20} 个条目")
    else:
        print("\n✓ memory/ 文件所有条目已有评分")
    
    if rescored_entries:
        print(f"\n预留重评：{len(rescored_entries)} 个条目")
        for entry in rescored_entries[:20]:
            print(entry)
        if len(rescored_entries) > 20:
            print(f"  ... 还有 {len(rescored_entries) - 20} 个条目")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
记忆重要性评分脚本 (v2.0)
为记忆条目打分和每日重评

功能：
1. memory/ 文件：首次评分（关键词匹配，不衰减）
2. MEMORY.md：每日重评（基础分 + 加分 - 衰减）

评分规则：
- 核心记忆（≥11 分）：只加分，不衰减
- 普通记忆（<11 分）：加分 - 衰减
- 加分上限：+10 分

作者：OpenClaw Memory System
版本：2.0
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
TZ_SHANGHAI = TZ_SHANGHAI

# 关键词评分规则（首次评分用）
KEYWORD_SCORES = [
    (r'账号 | 密码 | 服务器|API.?Key|smtp|imap|token|secret|credential', 15),
    (r'bitwarden|vault|auth|login|oauth', 9),
    (r'邮箱 | 邮件|email|your-email@', 12),
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
    根据内容计算关键词分数（首次评分用）
    
    Args:
        content: 条目内容（标题 + 下方内容）
    
    Returns:
        int: 关键词评分（5-15 分）
    """
    score = 5
    content_lower = content.lower()
    
    for pattern, weight in KEYWORD_SCORES:
        if re.search(pattern, content_lower):
            return weight
    
    if re.search(r'重要 | 必须 | 关键', content_lower):
        return min(10, score + 1)
    
    if len(content) > 1000:
        return max(score, 6)
    
    return score


def calculate_new_importance(current_importance: int, days_old: int, usage_bonus: float) -> int:
    """
    计算新评分（v2.1 每日重评公式）
    
    衰减规则：
    - 核心记忆（≥11 分）：不衰减，只加分
    - 重要记忆（7-10 分）：温和衰减 (1%/天)
    - 普通记忆（4-6 分）：正常衰减 (2%/天)
    - 琐碎记忆（1-3 分）：加速衰减 (3%/天)
    
    Args:
        current_importance: 当前评分（昨天的评分）
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
    为 MEMORY.md 动态记忆区每日重评
    
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
    print("记忆重要性评分脚本 (v2.0 每日重评)")
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
        if filepath.name == 'MEMORY.md':
            # MEMORY.md：每日重评
            print(f"重评：MEMORY.md")
            entries = rescore_memory_md(usage_bonus_map)
            rescored_entries.extend(entries)
        elif filepath.name.endswith('.md') and not filepath.name.startswith('记忆'):
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
        print(f"\n重评：{len(rescored_entries)} 个条目")
        for entry in rescored_entries[:20]:
            print(entry)
        if len(rescored_entries) > 20:
            print(f"  ... 还有 {len(rescored_entries) - 20} 个条目")
    else:
        print("\n✓ MEMORY.md 所有条目评分无变化")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

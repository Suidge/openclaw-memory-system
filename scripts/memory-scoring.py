#!/usr/bin/env python3
"""
记忆重要性评分脚本
只为记忆条目打分（### 标题 <!-- importance: X -->）
取消文件级打分功能
"""

import os
import re
from pathlib import Path

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"

KEYWORD_SCORES = [
    (r'账号 | 密码 | 服务器|API.?Key|smtp|imap|token|secret|credential', 15),
    (r'bitwarden|vault|auth|login|oauth', 13),
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

def calculate_importance(content: str) -> int:
    """根据内容计算重要性分数（严格匹配）"""
    score = 5
    content_lower = content.lower()
    
    for pattern, weight in KEYWORD_SCORES:
        if re.search(pattern, content_lower):
            return weight  # 找到第一个匹配就返回
    
    if re.search(r'重要 | 必须 | 关键', content_lower):
        return min(10, score + 1)
    
    if len(content) > 1000:
        return max(score, 6)
    
    return score

def score_file_entries(filepath: Path) -> list:
    """为文件中的条目打分（返回新评分的条目列表）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配 ### 或 #### 标题格式
    pattern = r'(#{3,4}\s+[^\n]+)'
    matches = list(re.finditer(pattern, content))
    
    scored_entries = []
    for match in matches:
        title = match.group(1).strip()
        
        # 检查是否已有评分
        start_pos = match.end()
        next_match = re.search(r'\n#{3,4}', content[start_pos:])
        end_pos = start_pos + next_match.start() if next_match else len(content)
        entry_content = content[start_pos:end_pos]
        
        if '<!-- importance:' in entry_content:
            continue  # 跳过已有评分的条目
        
        # 计算评分
        importance = calculate_importance(entry_content)
        
        # 在标题后插入评分
        new_title = f"{title} <!-- importance: {importance} -->"
        content = content.replace(title, new_title, 1)
        scored_entries.append(f"  - {title}: importance={importance}")
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return scored_entries

def main():
    print("=" * 60)
    print("记忆重要性评分脚本（条目级）")
    print("=" * 60)
    
    if not MEMORY_DIR.exists():
        print(f"❌ 记忆目录不存在：{MEMORY_DIR}")
        return
    
    files = list(MEMORY_DIR.glob('*.md'))
    print(f"\n扫描 {len(files)} 个记忆文件\n")
    
    all_scored_entries = []
    
    for filepath in sorted(files):
        # 跳过 MEMORY.md（由 rescore-memory-md.py 处理）
        if filepath.name == 'MEMORY.md':
            continue
        entries = score_file_entries(filepath)
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
        print("\n✓ 所有条目已有评分")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

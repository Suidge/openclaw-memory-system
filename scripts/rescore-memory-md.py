#!/usr/bin/env python3
"""
为 MEMORY.md 动态记忆区的所有条目重新打分
严格按照关键词匹配规则
一次性修正脚本，执行后归档
"""

import re

MEMORY_FILE = "~/.openclaw/workspace/MEMORY.md"

KEYWORD_SCORES = [
    (r'账号 | 密码 | 服务器|API.?Key|smtp|imap|token|secret|credential', 15),
    (r'bitwarden|vault|auth|login|oauth', 13),
    (r'邮箱 | 邮件|email', 12),
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
            return weight  # 直接返回匹配的权重，不累加
    
    if re.search(r'重要 | 必须 | 关键', content_lower):
        return min(10, score + 1)
    
    if len(content) > 1000:
        return max(score, 6)
    
    return score

def rescore_memory_md():
    """重新打分 MEMORY.md 动态记忆区"""
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取动态记忆区
    dynamic_section = content.split('## 📅 动态记忆区')
    if len(dynamic_section) < 2:
        print("❌ 未找到动态记忆区")
        return
    
    dynamic_content = dynamic_section[1]
    dynamic_start = content.find('## 📅 动态记忆区')
    
    # 匹配所有条目 #### YYYY-MM-DD 或 #### 2026-WXX
    pattern = r'(####\s+(?:\d{4}-\d{2}-\d{2}|\d{4}-W\d+)[^\n]*)\s*<!--\s*importance:\s*(\d+)\s*-->'
    matches = list(re.finditer(pattern, dynamic_content))
    
    if not matches:
        print("⚠️  未找到带评分的条目")
        return
    
    print("重新打分 MEMORY.md 动态记忆区")
    updated_count = 0
    
    for match in reversed(matches):  # 反向遍历，避免位置偏移
        title_line = match.group(1)
        old_importance = int(match.group(2))
        
        # 提取条目内容（到下一个 #### 或文件末尾）
        start_pos = match.end()
        next_match = re.search(r'\n####', dynamic_content[start_pos:])
        end_pos = start_pos + next_match.start() if next_match else len(dynamic_content)
        entry_content = dynamic_content[start_pos:end_pos]
        
        # 重新打分
        new_importance = calculate_importance(entry_content)
        
        if new_importance != old_importance:
            # 更新评分
            old_tag = f'<!-- importance: {old_importance} -->'
            new_tag = f'<!-- importance: {new_importance} -->'
            
            # 在完整 content 中查找并替换
            global_pos = dynamic_start + match.start()
            global_end = dynamic_start + match.end()
            content = content[:global_pos] + title_line + f' <!-- importance: {new_importance} -->' + content[global_end:]
            
            updated_count += 1
            print(f"  {title_line.strip()}: {old_importance} → {new_importance}")
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 重新打分完成：更新 {updated_count} 个条目")

if __name__ == '__main__':
    rescore_memory_md()

#!/usr/bin/env python3
"""
记忆衰减检查脚本
只检查 MEMORY.md 动态记忆区的条目
计算每条记忆的有效分数，标记可清理的条目

衰减公式：effective_score = importance × e^(-0.01×days_old)
核心记忆（importance ≥ 11）永不衰减
清理阈值：effective_score < 2
"""

import os
import re
import math
import json
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
REPORT_PATH = os.path.expanduser("~/.openclaw/workspace/memory/decay-report.json")

# 衰减参数
LAMBDA = 0.01  # 衰减系数
CLEANUP_THRESHOLD = 2  # 清理阈值
CORE_MEMORY_THRESHOLD = 11  # 核心记忆阈值

def calculate_effective_score(importance, days_old):
    """计算有效分数"""
    if importance >= CORE_MEMORY_THRESHOLD:
        return importance  # 核心记忆永不衰减
    
    effective_score = importance * math.exp(-LAMBDA * days_old)
    return round(effective_score, 2)

def parse_memory_entries(content):
    """解析 MEMORY.md 动态记忆区的条目"""
    entries = []
    
    # 提取动态记忆区
    dynamic_section = content.split('## 📅 动态记忆区')
    if len(dynamic_section) < 2:
        return entries
    
    dynamic_content = dynamic_section[1]
    
    # 匹配 #### YYYY-MM-DD 或 #### 2026-WXX 格式的条目
    pattern = r'(####\s+(\d{4}-\d{2}-\d{2}|\d{4}-W\d+)[^\n]*)\s*<!--\s*importance:\s*(\d+)\s*-->'
    matches = list(re.finditer(pattern, dynamic_content))
    
    for match in matches:
        title = match.group(1).strip()
        # 移除 HTML 注释部分，只保留标题文本
        title_clean = re.sub(r'\s*<!--.*?-->', '', title).strip()
        importance = int(match.group(3))
        
        # 计算天数（从标题中的日期）
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
        if date_match:
            try:
                entry_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                days_old = max(0, (datetime.now() - entry_date).days)
            except:
                days_old = 0
        else:
            # 周洞察按 7 天计算
            days_old = 7
        
        # 计算有效分数
        effective_score = calculate_effective_score(importance, days_old)
        
        entries.append({
            "title": title_clean,
            "importance": importance,
            "days_old": days_old,
            "effective_score": effective_score
        })
    
    return entries

def check_memory_decay():
    """检查 MEMORY.md 动态记忆区的衰减状态"""
    results = {
        "check_time": datetime.now().isoformat(),
        "total_entries": 0,
        "core_memory_count": 0,
        "normal_count": 0,
        "cleanup_candidates": [],
        "protected_entries": [],
        "summary": {}
    }
    
    if not os.path.isfile(MEMORY_FILE):
        print("❌ MEMORY.md 不存在")
        return results
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = parse_memory_entries(content)
    results["total_entries"] = len(entries)
    
    for entry in entries:
        if entry["importance"] >= CORE_MEMORY_THRESHOLD:
            results["core_memory_count"] += 1
            results["protected_entries"].append(entry)
        else:
            results["normal_count"] += 1
            
            # 检查是否可清理
            if entry["effective_score"] < CLEANUP_THRESHOLD:
                entry["reason"] = f"effective_score ({entry['effective_score']}) < threshold ({CLEANUP_THRESHOLD})"
                results["cleanup_candidates"].append(entry)
    
    # 生成摘要
    results["summary"] = {
        "total_entries": results["total_entries"],
        "core_memory_protected": results["core_memory_count"],
        "normal_memory": results["normal_count"],
        "cleanup_candidates_count": len(results["cleanup_candidates"]),
        "cleanup_candidates": [e["title"] for e in results["cleanup_candidates"]]
    }
    
    # 保存报告
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

def print_report(results):
    """打印报告"""
    print("\n 记忆衰减检查报告")
    print("=" * 60)
    print(f"检查时间：{results['check_time']}")
    print(f"总记忆条目：{results['summary']['total_entries']}")
    print(f"核心记忆（受保护）: {results['summary']['core_memory_protected']}")
    print(f"普通记忆：{results['summary']['normal_memory']}")
    print(f"可清理候选：{results['summary']['cleanup_candidates_count']}")
    
    if results['cleanup_candidates']:
        print("\n📋 可清理记忆清单:")
        print("-" * 60)
        for entry in results['cleanup_candidates']:
            print(f"  • {entry['title']}")
            print(f"    原评分：{entry['importance']} | 有效分：{entry['effective_score']} | 天数：{entry['days_old']}")
            print(f"    原因：{entry['reason']}")
    
    if results['protected_entries']:
        print("\n🛡️  核心记忆（受保护，永不衰减）:")
        print("-" * 60)
        for entry in results['protected_entries'][:10]:
            print(f"  • {entry['title']} (importance: {entry['importance']})")
        if len(results['protected_entries']) > 10:
            print(f"  ... 还有 {len(results['protected_entries']) - 10} 个核心记忆条目")
    
    print("\n" + "=" * 60)
    print(f"详细报告已保存：{REPORT_PATH}")

def main():
    """主函数"""
    print(" 开始检查记忆衰减...\n")
    
    results = check_memory_decay()
    print_report(results)
    
    # 返回清理候选数量（供 cron job 使用）
    if results['cleanup_candidates']:
        print(f"\n⚠️  发现 {len(results['cleanup_candidates'])} 个可清理记忆条目，需要主人确认")
        return 1
    else:
        print("\n✅ 无需清理的记忆条目")
        return 0

if __name__ == '__main__':
    exit(main())

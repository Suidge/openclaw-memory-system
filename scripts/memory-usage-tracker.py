#!/usr/bin/env python3
"""
记忆使用追踪器 (v1.1)
记录每次 memory_search 的命中和引用，计算加分
支持分析模式（每日汇总）

加分规则：
- 被搜索命中：+0.1/次
- 被引用使用：+0.2/次
- 加分上限：+10 分

作者：银月
版本：1.1
创建：2026-03-08
更新：2026-03-08（添加分析模式）
"""

import json
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

USAGE_LOG = Path.home() / ".openclaw" / "workspace" / "memory" / "usage-log.json"


def log_usage(entry_title: str, usage_type: str) -> None:
    """
    记录记忆条目使用
    
    Args:
        entry_title: 条目标题（必须与 MEMORY.md 中的标题一致）
        usage_type: 'search' 或 'citation'
    
    Raises:
        ValueError: 当参数无效时
    """
    # 输入验证
    if not entry_title or not entry_title.strip():
        raise ValueError("entry_title 不能为空")
    
    if usage_type not in ('search', 'citation'):
        raise ValueError(f"usage_type 必须是 'search' 或 'citation'，得到：{usage_type}")
    
    # 加载日志
    if USAGE_LOG.exists():
        with open(USAGE_LOG, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"last_updated": None, "entries": {}}
    
    # 初始化条目
    if entry_title not in data["entries"]:
        data["entries"][entry_title] = {
            "search_hits": 0,
            "citations": 0,
            "last_used": None,
            "bonus_score": 0.0
        }
    
    # 更新计数
    entry = data["entries"][entry_title]
    if usage_type == 'search':
        entry["search_hits"] += 1
    elif usage_type == 'citation':
        entry["citations"] += 1
    
    # 更新时间和加分
    entry["last_used"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    entry["bonus_score"] = min(10.0, entry["search_hits"] * 0.1 + entry["citations"] * 0.2)
    
    data["last_updated"] = entry["last_used"]
    
    # 原子写入
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = USAGE_LOG.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp_path.replace(USAGE_LOG)


def get_bonus(entry_title: str) -> float:
    """获取某条目的加分"""
    if not USAGE_LOG.exists():
        return 0.0
    with open(USAGE_LOG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["entries"].get(entry_title, {}).get("bonus_score", 0.0)


def reset_usage(entry_title: str) -> None:
    """重置某条目的使用记录（清理后调用）"""
    if not USAGE_LOG.exists():
        return
    with open(USAGE_LOG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if entry_title in data["entries"]:
        del data["entries"][entry_title]
        with open(USAGE_LOG, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def analyze_usage(dry_run: bool = False) -> dict:
    """
    分析使用日志（每日汇总）
    
    Args:
        dry_run: 是否仅分析不重置
    
    Returns:
        分析结果摘要
    """
    if not USAGE_LOG.exists():
        return {"new_entries": 0, "updated_entries": 0, "total_bonus": 0.0}
    
    with open(USAGE_LOG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data.get("entries", {})
    new_count = sum(1 for e in entries.values() if e.get("search_hits", 0) + e.get("citations", 0) == 1)
    updated_count = len(entries) - new_count
    total_bonus = sum(e.get("bonus_score", 0.0) for e in entries.values())
    
    result = {
        "total_entries": len(entries),
        "new_entries": new_count,
        "updated_entries": updated_count,
        "total_bonus": round(total_bonus, 2)
    }
    
    print("\n📊 使用日志分析")
    print("=" * 40)
    print(f"总条目数：{result['total_entries']}")
    print(f"新增条目：{result['new_entries']}")
    print(f"更新条目：{result['updated_entries']}")
    print(f"总加分：{result['total_bonus']}")
    print("=" * 40)
    
    return result


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='记忆使用追踪器')
    parser.add_argument('title', nargs='?', help='条目标题')
    parser.add_argument('type', nargs='?', choices=['search', 'citation'], help='使用类型')
    parser.add_argument('--analyze', action='store_true', help='分析模式（每日汇总）')
    parser.add_argument('--dry-run', action='store_true', help='仅分析不重置')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    
    if args.analyze:
        # 分析模式
        analyze_usage(dry_run=args.dry_run)
    elif args.title and args.type:
        # 记录模式
        log_usage(args.title, args.type)
        print(f"✅ 已记录：{args.title} ({args.type})")
    else:
        print("用法：")
        print("  1. 记录使用：memory-usage-tracker.py <条目标题> <search|citation>")
        print("  2. 分析日志：memory-usage-tracker.py --analyze [--dry-run]")
        print("")
        print("示例:")
        print("  memory-usage-tracker.py '2026-03-05 技能学习完整原则强化' search")
        print("  memory-usage-tracker.py '2026-03-05 配置修改安全原则' citation")
        print("  memory-usage-tracker.py --analyze")

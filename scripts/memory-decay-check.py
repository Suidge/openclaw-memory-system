#!/usr/bin/env python3
"""
<<<<<<< HEAD
记忆遗忘检查脚本 (v2.0)
检查 MEMORY.md 动态记忆区的条目，筛选达到遗忘阈值的条目

遗忘阈值：importance < 2
核心记忆（≥11 分）永不遗忘

作者：银月
版本：2.0
最后更新：2026-03-08
=======
Memory governance audit (v2.3)
Checks forgotten entries, expired daily-memory files, and pruning suggestions.
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

FORGOTTEN_THRESHOLD = 2
CORE_MEMORY_THRESHOLD = 11
FILE_EXPIRY_DAYS = 30
LOW_REUSE_EVENT_MAX_IMPORTANCE = 8
LOW_REUSE_EVENT_MIN_DAYS = 7
TZ = timezone(timedelta(hours=8))

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_FILE = WORKSPACE_DIR / "MEMORY.md"
REPORT_PATH = WORKSPACE_DIR / "memory" / "decay-report.json"
LOG_PATH = WORKSPACE_DIR / "memory" / "forget-check.log"
MEMORY_DIR = WORKSPACE_DIR / "memory"

DATE_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2})')
WEEK_PATTERN = re.compile(r'(\d{4}-W\d{2})')
ENTRY_PATTERN = re.compile(r'(####\s+[^\n]*)\s*<!--\s*importance:\s*(\d+)\s*-->')
RULE_PATTERNS = [r'规则', r'原则', r'铁律', r'必须', r'禁止', r'规范', r'标准']
DECISION_PATTERNS = [r'决策', r'决定', r'选择', r'切换', r'回退', r'迁移', r'统一', r'采用', r'放弃']
DOC_PATTERNS = [r'文档', r'修订', r'草案', r'汇报', r'报告', r'方案', r'计划']
LOG_PATTERNS = [r'测试', r'验证', r'日志', r'命令', r'输出', r'commit', r'\bgit\b(?!hub)']

<<<<<<< HEAD
# 时区常量
TZ_SHANGHAI = timezone(timedelta(hours=8))

# ============================================================================
# 日志配置
# ============================================================================
=======
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)

def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.root.handlers = []
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    logging.root.setLevel(level)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)


def parse_date_from_title(title: str) -> datetime:
    date_match = DATE_PATTERN.search(title)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), '%Y-%m-%d').replace(tzinfo=TZ)
        except ValueError:
            pass
    week_match = WEEK_PATTERN.search(title)
    if week_match:
        try:
            return datetime.strptime(week_match.group(1) + '-1', '%G-W%V-%u').replace(tzinfo=TZ)
        except ValueError:
            pass
    return datetime.now(TZ)


def calculate_days_old(title: str) -> int:
    return max(0, (datetime.now(TZ) - parse_date_from_title(title)).days)


def strip_title(raw: str) -> str:
    title = re.sub(r'^#{1,6}\s*', '', raw).strip()
    title = re.sub(r'\s*<!--.*?-->', '', title).strip()
    return title


def normalize_title(title: str) -> str:
    text = strip_title(title).lower()
    text = re.sub(r'\d{4}-\d{2}-\d{2}\s*', '', text)
    text = re.sub(r'[（(].*?[）)]', '', text)
    return re.sub(r'\s+', '', text)


def classify_memory_entry(title: str, body: str) -> str:
    text = f"{title}\n{body}".lower()
    if any(re.search(p, text) for p in RULE_PATTERNS):
        return 'rule'
    if any(re.search(p, text) for p in DECISION_PATTERNS):
        return 'decision'
    if any(re.search(p, text) for p in DOC_PATTERNS):
        return 'doc'
    if any(re.search(p, text) for p in LOG_PATTERNS):
        return 'log'
    return 'event'


def parse_memory_entries(content: str) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    dynamic_section = content.split('## 📅 动态记忆区')
    if len(dynamic_section) < 2:
        return entries
    dynamic_content = dynamic_section[1]
    matches = list(ENTRY_PATTERN.finditer(dynamic_content))
    for idx, match in enumerate(matches):
        raw_title = match.group(1).strip()
        importance = int(match.group(2))
        start_pos = match.end()
        end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(dynamic_content)
        body = dynamic_content[start_pos:end_pos].strip()
        title_clean = strip_title(raw_title)
        days_old = calculate_days_old(raw_title)
        entry_type = classify_memory_entry(title_clean, body)
        entries.append({
            'title': title_clean,
            'importance': importance,
            'days_old': days_old,
            'body': body,
            'entry_type': entry_type,
            'is_core_memory': importance >= CORE_MEMORY_THRESHOLD,
            'is_forgotten': importance < FORGOTTEN_THRESHOLD,
            'normalized_title': normalize_title(title_clean),
        })
    return entries


def check_expired_files() -> List[Dict[str, Any]]:
    expired: List[Dict[str, Any]] = []
    for file_path in MEMORY_DIR.glob('*.md'):
        if file_path.name == 'MEMORY.md':
            continue
        file_date: Optional[datetime] = None
        m = DATE_PATTERN.match(file_path.stem)
        if m:
            try:
                file_date = datetime.strptime(m.group(1), '%Y-%m-%d').replace(tzinfo=TZ)
            except ValueError:
                pass
        if file_date is None:
            m = WEEK_PATTERN.match(file_path.stem)
            if m:
                try:
                    file_date = datetime.strptime(m.group(1) + '-1', '%G-W%V-%u').replace(tzinfo=TZ)
                except ValueError:
                    pass
        if file_date is None:
            continue
        days_old = max(0, (datetime.now(TZ) - file_date).days)
        if days_old > FILE_EXPIRY_DAYS:
            expired.append({'filename': file_path.name, 'filepath': str(file_path), 'days_old': days_old})
    return expired


def detect_duplicate_groups(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        if re.fullmatch(r'(\d{4}-\d{2}-\d{2}|\d{4}-W\d{2})', entry['title'].strip()):
            continue
        groups.setdefault(entry['normalized_title'], []).append(entry)
    return [
        {'canonical_title': g[0]['title'], 'count': len(g), 'titles': [e['title'] for e in g]}
        for g in groups.values() if len(g) >= 2
    ]


def detect_low_reuse_events(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {'title': e['title'], 'importance': e['importance'], 'days_old': e['days_old']}
        for e in entries
        if not e['is_core_memory'] and e['entry_type'] == 'event' and e['importance'] <= LOW_REUSE_EVENT_MAX_IMPORTANCE and e['days_old'] >= LOW_REUSE_EVENT_MIN_DAYS
    ]


def detect_merge_suggestions(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for typ in ('rule', 'decision'):
        group = [e for e in entries if e['entry_type'] == typ]
        if len(group) >= 3:
            out.append({'type': typ, 'count': len(group), 'titles': [e['title'] for e in group[:8]]})
    return out


def check_memory_governance(dry_run: bool = False) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        'check_time': datetime.now(TZ).isoformat(),
        'forgotten_entries': [],
        'expired_files': [],
        'duplicate_groups': [],
        'low_reuse_event_candidates': [],
        'merge_suggestions': [],
        'summary': {},
    }
    content = MEMORY_FILE.read_text(encoding='utf-8')
    entries = parse_memory_entries(content)
    results['forgotten_entries'] = [e for e in entries if e['is_forgotten']]
    results['expired_files'] = check_expired_files()
    results['duplicate_groups'] = detect_duplicate_groups(entries)
    results['low_reuse_event_candidates'] = detect_low_reuse_events(entries)
    results['merge_suggestions'] = detect_merge_suggestions(entries)
    results['summary'] = {
        'total_entries': len(entries),
        'core_memory_protected': len([e for e in entries if e['is_core_memory']]),
        'normal_memory': len([e for e in entries if not e['is_core_memory']]),
        'forgotten_entries_count': len(results['forgotten_entries']),
        'expired_files_count': len(results['expired_files']),
        'duplicate_groups_count': len(results['duplicate_groups']),
        'low_reuse_event_candidates_count': len(results['low_reuse_event_candidates']),
        'merge_suggestions_count': len(results['merge_suggestions']),
        'forgotten_entries': [e['title'] for e in results['forgotten_entries']],
        'expired_files': [f['filename'] for f in results['expired_files']],
    }
    if not dry_run:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(suffix='.json', dir=REPORT_PATH.parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, REPORT_PATH)
    return results


<<<<<<< HEAD
def print_report(results: Dict[str, Any], args: argparse.Namespace) -> None:
    """打印控制台报告（包含遗忘条目和过期文件）"""
    print("\n🌙 银月记忆遗忘检查报告")
    print("=" * 60)
    print(f"检查时间：{results['check_time']}")
    print(f"总记忆条目：{results['summary']['total_entries']}")
    print(f"核心记忆（受保护）: {results['summary']['core_memory_protected']}")
    print(f"普通记忆：{results['summary']['normal_memory']}")
    print(f"遗忘条目（MEMORY.md）: {results['summary']['forgotten_entries_count']}")
    print(f"过期文件（memory/）: {results['summary']['expired_files_count']}")
    
    if results['forgotten_entries']:
        print("\n📋 遗忘清单 - MEMORY.md 条目（待主人确认）:")
        print("-" * 60)
        for entry in results['forgotten_entries']:
            print(f"  • {entry['title']}")
            print(f"    评分：{entry['importance']} | 天数：{entry['days_old']}")
    
    if results['expired_files']:
        print("\n📋 遗忘清单 - memory/ 过期文件（待主人确认）:")
        print("-" * 60)
        for file_info in results['expired_files']:
            print(f"  • {file_info['filename']}")
            print(f"    天数：{file_info['days_old']}")
            print(f"    原因：{file_info.get('reason', '')}")
    
    if results['protected_entries']:
        print("\n🛡️  核心记忆（受保护，永不遗忘）:")
        print("-" * 60)
        for entry in results['protected_entries'][:10]:
            print(f"  • {entry['title']} (importance: {entry['importance']})")
        if len(results['protected_entries']) > 10:
            print(f"  ... 还有 {len(results['protected_entries']) - 10} 个核心记忆条目")
    
    print("\n" + "=" * 60)
    total_cleanup = len(results['forgotten_entries']) + len(results['expired_files'])
    if total_cleanup > 0:
        print(f"⚠️  共 {total_cleanup} 个项目待清理")
        print("需要主人确认后再执行清理")
    if not args.dry_run:
        print(f"详细报告已保存：{REPORT_PATH}")
    else:
        print("⚠️  干跑模式：未生成报告文件")


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='🌙 银月记忆遗忘检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s                    # 正常检查
  %(prog)s -v                 # 详细输出
  %(prog)s --dry-run          # 仅检查不生成报告
        '''
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='启用 DEBUG 级别日志')
    parser.add_argument('--dry-run', action='store_true', help='仅检查，不生成报告文件')
    
=======
def print_report(results: Dict[str, Any]) -> None:
    print(f"total: {results['summary']['total_entries']}")
    print(f"forgotten: {results['summary']['forgotten_entries_count']}")
    print(f"expired files: {results['summary']['expired_files_count']}")
    print(f"duplicate groups: {results['summary']['duplicate_groups_count']}")
    print(f"low reuse events: {results['summary']['low_reuse_event_candidates_count']}")
    print(f"merge suggestions: {results['summary']['merge_suggestions_count']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Memory governance audit (v2.3)')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
<<<<<<< HEAD
    
    logging.info("🌙 银月开始检查记忆遗忘...")
    
    results = check_forgotten_memories(dry_run=args.dry_run)
    print_report(results, args)
    
    total_cleanup = len(results['forgotten_entries']) + len(results['expired_files'])
    if total_cleanup > 0:
        logging.warning(f"发现 {total_cleanup} 个待清理项目")
        print(f"\n⚠️  发现 {len(results['forgotten_entries'])} 个遗忘条目、{len(results['expired_files'])} 个过期文件")
        print("需要主人确认后再执行清理")
        return 1
    else:
        logging.info("无需清理的内容")
        print("\n✅ 无需清理的内容")
        return 0
=======
    results = check_memory_governance(dry_run=args.dry_run)
    print_report(results)
    governance_items = (
        len(results['forgotten_entries'])
        + len(results['expired_files'])
        + len(results['duplicate_groups'])
        + len(results['low_reuse_event_candidates'])
        + len(results['merge_suggestions'])
    )
    return 1 if governance_items > 0 else 0
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)


if __name__ == '__main__':
    sys.exit(main())

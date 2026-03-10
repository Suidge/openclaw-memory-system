#!/usr/bin/env python3
"""
Memory consolidation script (v2.3.1)
Reads scored daily-memory candidates, classifies them, judges long-term value,
and prepares distilled insertion into MEMORY.md.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
MEMORY_FILE = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
CANDIDATE_THRESHOLD = 7
DEFAULT_RECENT_DAYS = 3
TZ = timezone(timedelta(hours=8))
DYNAMIC_SECTION_HEADER = '## 📅 动态记忆区'
TITLE_HEADING_RE = re.compile(r'^(#{3,4}\s+[^\n]+)', re.M)
IMPORTANCE_RE = re.compile(r'<!--\s*importance:\s*(\d+)\s*-->')

FACT_PATTERNS: Sequence[str] = [
    r'主人.*偏好',
    r'长期.*(配置|事实|约束)',
    r'固定.*(配置|规则)',
    r'环境变量',
]
DECISION_PATTERNS: Sequence[str] = [
    r'决定|决策|选择|采用|放弃|回退|切换|迁移|统一',
    r'从.+切换',
]
RULE_PATTERNS: Sequence[str] = [
    r'规则|原则|铁律|必须|禁止|约束|规范|标准',
]
DOC_PATTERNS: Sequence[str] = [
    r'文档|修订|草案|汇报|报告|方案|计划',
]
LOG_PATTERNS: Sequence[str] = [
    r'测试|验证|试跑|日志|命令|终端|输出|trace|commit|\bgit\b(?!hub)',
]
EVENT_PATTERNS: Sequence[str] = [
    r'修复|完成|升级|优化|部署|问题|故障|失败|恢复',
]
LONG_TERM_PATTERNS: Sequence[str] = [
    r'长期|以后|后续|策略|规范|工作流|机制|主记忆|记忆系统',
    r'影响|约束|标准|规则',
]
PROCESS_TITLE_PATTERNS: Sequence[str] = [
    r'手动更新', r'恢复验证', r'查询修复', r'失败修复', r'对比测试',
    r'方向确认', r'调整记录', r'文档职责边界', r'文档口径澄清', r'文档调整记录',
]


@dataclass
class CandidateEntry:
    source_file: Path
    title: str
    body: str
    importance: int
    entry_type: str = 'unknown'


@dataclass
class DistilledEntry:
    title: str
    importance: int
    bullets: List[str]


def strip_comments(text: str) -> str:
    cleaned = re.sub(r'\s*<!--.*?-->', '', text).strip()
    cleaned = re.sub(r'^#{1,6}\s*', '', cleaned)
    return cleaned.strip()


def iter_entry_slices(content: str) -> Iterable[tuple[re.Match[str], int, int]]:
    matches = list(TITLE_HEADING_RE.finditer(content))
    for idx, match in enumerate(matches):
        start_pos = match.end()
        end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        yield match, start_pos, end_pos


def parse_memory_file_date(filepath: Path) -> Optional[datetime]:
    match = re.match(r'(\d{4}-\d{2}-\d{2})\.md$', filepath.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), '%Y-%m-%d').replace(tzinfo=TZ)


def load_candidates(recent_days: int = DEFAULT_RECENT_DAYS) -> List[CandidateEntry]:
    entries: List[CandidateEntry] = []
    cutoff = datetime.now(TZ) - timedelta(days=recent_days)
    for filepath in sorted(p for p in MEMORY_DIR.glob('*.md') if p.name.endswith('.md')):
        file_date = parse_memory_file_date(filepath)
        if file_date is None or file_date < cutoff:
            continue
        content = filepath.read_text(encoding='utf-8')
        for match, start_pos, end_pos in iter_entry_slices(content):
            raw_title = match.group(1).strip()
            body = content[start_pos:end_pos].strip()
            full = raw_title + '\n' + body
            importance_match = IMPORTANCE_RE.search(full)
            if not importance_match:
                continue
            importance = int(importance_match.group(1))
            if importance < CANDIDATE_THRESHOLD:
                continue
            entries.append(CandidateEntry(filepath, strip_comments(raw_title), body, importance))
    return entries


def classify_entry(entry: CandidateEntry) -> str:
    text = f"{entry.title}\n{entry.body}".lower()
    title_lower = entry.title.lower()
    if any(re.search(p, title_lower) for p in PROCESS_TITLE_PATTERNS):
        return 'log'
    if any(re.search(p, text) for p in RULE_PATTERNS):
        return 'rule'
    if any(re.search(p, text) for p in DECISION_PATTERNS):
        return 'decision'
    if any(re.search(p, text) for p in FACT_PATTERNS):
        return 'fact'
    if any(re.search(p, text) for p in DOC_PATTERNS):
        return 'doc'
    if any(re.search(p, text) for p in LOG_PATTERNS):
        return 'log'
    if any(re.search(p, text) for p in EVENT_PATTERNS):
        return 'event'
    return 'event'


def has_long_term_value(entry: CandidateEntry, entry_type: str) -> tuple[bool, str]:
    text = f"{entry.title}\n{entry.body}".lower()
    if entry_type in {'doc', 'log'}:
        return False, f'{entry_type} type is blocked by default'
    if entry_type in {'fact', 'decision', 'rule'}:
        return True, f'{entry_type} type is admitted by default'
    if any(re.search(p, text) for p in LONG_TERM_PATTERNS):
        return True, 'event with long-term impact signals'
    return False, 'event without long-term impact signals'


def pick_summary_lines(body: str, limit: int = 2) -> List[str]:
    lines: List[str] = []
    for raw in body.splitlines():
        line = strip_comments(raw)
        if not line:
            continue
        line = re.sub(r'^[-*]\s*', '', line)
        line = re.sub(r'^\d+[.)]\s*', '', line)
        if line.startswith('**时间**') or line.startswith('**状态**') or line.startswith('**内容**'):
            continue
        if len(line) > 120:
            line = line[:117] + '...'
        lines.append(line)
        if len(lines) >= limit:
            break
    return lines or ['Distilled from daily memory as a long-term candidate.']


def distill_entry(entry: CandidateEntry, entry_type: str) -> DistilledEntry:
    title = entry.title
    if entry_type == 'rule' and '规则' not in title and '原则' not in title:
        title = f'{title}（规则）'
    elif entry_type == 'decision' and '决策' not in title and '切换' not in title and '回退' not in title:
        title = f'{title}（决策）'
    return DistilledEntry(title, entry.importance, pick_summary_lines(entry.body, 2))


def normalize_title(title: str) -> str:
    text = strip_comments(title).lower()
    text = re.sub(r'\d{4}-\d{2}-\d{2}\s*', '', text)
    text = re.sub(r'[（(].*?[）)]', '', text)
    return re.sub(r'\s+', '', text)


def exists_in_memory(memory_text: str, title: str) -> bool:
    normalized_target = normalize_title(title)
    for line in memory_text.splitlines():
        if line.startswith('#### '):
            if normalize_title(line[5:]) == normalized_target:
                return True
    return False


def render_distilled_entry(entry: DistilledEntry) -> str:
    bullet_text = '\n'.join(f'- {line}' for line in entry.bullets)
    return f"#### {entry.title} <!-- importance: {entry.importance} -->\n{bullet_text}\n"


def insert_into_dynamic_section(memory_text: str, rendered_entry: str) -> str:
    idx = memory_text.find(DYNAMIC_SECTION_HEADER)
    if idx == -1:
        raise ValueError('dynamic section not found')
    insert_pos = idx + len(DYNAMIC_SECTION_HEADER)
    return memory_text[:insert_pos] + '\n\n' + rendered_entry + memory_text[insert_pos:]


def consolidate(dry_run: bool = False, recent_days: int = DEFAULT_RECENT_DAYS) -> int:
    memory_text = MEMORY_FILE.read_text(encoding='utf-8')
    candidates = load_candidates(recent_days=recent_days)
    admitted = 0
    skipped_rule = 0
    skipped_duplicate = 0
    print(f'candidates (>= {CANDIDATE_THRESHOLD}): {len(candidates)}')
    for entry in candidates:
        entry_type = classify_entry(entry)
        allowed, reason = has_long_term_value(entry, entry_type)
        if not allowed:
            skipped_rule += 1
            print(f'- skip: {entry.title} [{entry_type}] ({reason})')
            continue
        distilled = distill_entry(entry, entry_type)
        if exists_in_memory(memory_text, distilled.title):
            skipped_duplicate += 1
            print(f'- skip: {distilled.title} [duplicate]')
            continue
        memory_text = insert_into_dynamic_section(memory_text, render_distilled_entry(distilled))
        admitted += 1
        print(f'- write: {distilled.title} [{entry_type}]')
    print(f'write: {admitted}')
    print(f'skip(rule): {skipped_rule}')
    print(f'skip(duplicate): {skipped_duplicate}')
    if admitted > 0 and not dry_run:
        MEMORY_FILE.write_text(memory_text, encoding='utf-8')
    return admitted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Consolidate daily-memory candidates into MEMORY.md (v2.3.1)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--recent-days', type=int, default=DEFAULT_RECENT_DAYS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f'candidate threshold: {CANDIDATE_THRESHOLD}')
    print(f'recent-days: {args.recent_days}')
    consolidate(dry_run=args.dry_run, recent_days=args.recent_days)


if __name__ == '__main__':
    main()

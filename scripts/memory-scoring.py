#!/usr/bin/env python3
"""
<<<<<<< HEAD
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
=======
Memory scoring script (v2.3.1)
Scores daily memory entries and marks candidate priority.
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
CANDIDATE_THRESHOLD = 7
MAX_DYNAMIC_SCORE = 10
TZ = timezone(timedelta(hours=8))
DATE_FILE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})\.md$')
TITLE_HEADING_RE = re.compile(r'^(#{3,4}\s+[^\n]+)', re.M)
IMPORTANCE_RE = re.compile(r'<!--\s*importance:\s*(\d+)\s*-->')

<<<<<<< HEAD
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
=======
POSITIVE_RULES: Sequence[Tuple[str, int, str]] = [
    (r'记忆系统|主记忆|长期记忆|遗忘机制|吸收规则|评分机制|工作流|架构|机制', 2, 'system/mechanism'),
    (r'长期|长期有效|长期影响|长期规则|长期约束|长期认知', 1, 'long-term'),
    (r'决策|决定|选择|采用|放弃|回退|切换|迁移|统一', 2, 'decision/switch'),
    (r'规则|原则|铁律|必须|禁止|约束|规范|标准', 1, 'rule'),
    (r'修复|修正|优化|重构|升级|部署|落地|完成|启用|上线|发布', 1, 'completion/fix'),
    (r'配置|环境变量|config|setup|部署|安装', 1, 'config'),
    (r'错误|问题|bug|故障|失败|异常', 1, 'issue'),
    (r'openclaw|cron|heartbeat|agent|context engine|legacy|lossless-claw', 1, 'system object'),
]

NEGATIVE_RULES: Sequence[Tuple[str, int, str]] = [
    (r'文档版|修订版|草案|汇报|报告|整理版|说明文档|设计文档', 2, 'doc penalty'),
    (r'读书笔记|学习笔记|复盘文稿|计划文稿|升级计划', 2, 'manuscript penalty'),
    (r'测试|验证|试跑|演练|模拟|探针', 1, 'test penalty'),
    (r'日志|log|输出|命令|终端|shell|trace', 1, 'log penalty'),
    (r'commit|git|提交记录|变更记录', 1, 'commit penalty'),
]

GENERIC_TITLE_PATTERNS: Sequence[Tuple[str, int, str]] = [
    (r'^#{3,4}\s*(问题与解答|其他观察到的情况|待处理|待排查|当前状态|当前配置|目标配置|技能信息|实战案例|当日重要事件|解决方案|修改步骤|风险检查|回滚方案|验证步骤)$', 2, 'generic title'),
    (r'^#{3,4}\s*(任务\s*\d+|执行任务|注意事项|核心能力|笔记本信息)$', 2, 'container title'),
    (r'^#{3,4}\s*.*(方向确认|调整记录|文档职责边界|文档口径澄清|文档调整记录).*$' , 2, 'design confirmation title'),
    (r'^#{3,4}\s*.*(手动更新|恢复验证|查询修复|失败修复|提交（\d+\s*个）|提交\(|提交（|提交\b).*$' , 2, 'process-action title'),
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
]


@dataclass
class ScoreExplanation:
    score: int
    reasons: List[str]


<<<<<<< HEAD
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
=======
@dataclass
class ScoredEntry:
    file: Path
    title: str
    score: int
    candidate: bool
    reasons: List[str]


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def strip_comments(text: str) -> str:
    return re.sub(r'\s*<!--.*?-->', '', text).strip()


def parse_memory_file_date(filepath: Path) -> datetime | None:
    match = DATE_FILE_RE.match(filepath.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), '%Y-%m-%d').replace(tzinfo=TZ)


def iter_entry_slices(content: str) -> Iterable[Tuple[re.Match[str], int, int]]:
    matches = list(TITLE_HEADING_RE.finditer(content))
    for idx, match in enumerate(matches):
        start_pos = match.end()
        end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        yield match, start_pos, end_pos


def calculate_keyword_score(content: str) -> ScoreExplanation:
    text = content.lower()
    title = content.split('\n', 1)[0].lower()
    score = 5
    reasons: List[str] = ['base=5']

    for pattern, delta, label in POSITIVE_RULES:
        if re.search(pattern, text):
            score += delta
            reasons.append(f'+{delta} {label}')

    for pattern, delta, label in NEGATIVE_RULES:
        if re.search(pattern, text):
            score -= delta
            reasons.append(f'-{delta} {label}')

    for pattern, delta, label in GENERIC_TITLE_PATTERNS:
        if re.search(pattern, title):
            score -= delta
            reasons.append(f'-{delta} {label}')

    if re.search(r'文档|修订|草案|汇报|报告|整理', title):
        score -= 1
        reasons.append('-1 doc-title penalty')

    system_design_hits = 0
    for pattern in [
        r'记忆系统|主记忆|长期记忆|遗忘机制|吸收规则|评分机制|工作流|架构|机制',
        r'长期|长期有效|长期影响|长期规则|长期约束|长期认知',
        r'规则|原则|铁律|必须|禁止|约束|规范|标准',
    ]:
        if re.search(pattern, text):
            system_design_hits += 1
    if system_design_hits >= 2:
        score -= 1
        reasons.append('-1 system/design cooling')
    if system_design_hits >= 3:
        score -= 1
        reasons.append('-1 high-density cooling')

    if len(content) > 1000:
        score += 1
        reasons.append('+1 long-content fallback')

    final_score = clamp(score, 1, MAX_DYNAMIC_SCORE)
    return ScoreExplanation(score=final_score, reasons=reasons)


def score_daily_log_entries(filepath: Path, explain: bool = False, dry_run: bool = False) -> List[ScoredEntry]:
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    scored_entries: List[ScoredEntry] = []

    for match, start_pos, end_pos in reversed(list(iter_entry_slices(content))):
        raw_title = match.group(1).strip()
        entry_title = strip_comments(raw_title)
        entry_body = content[start_pos:end_pos].strip()
        entry_content = entry_title + "\n" + entry_body

        if IMPORTANCE_RE.search(entry_content):
            continue

        explanation = calculate_keyword_score(entry_content)
        candidate = explanation.score >= CANDIDATE_THRESHOLD
        new_title = f"{raw_title} <!-- importance: {explanation.score} -->"
        content = content[:match.start(1)] + new_title + content[match.end(1):]
        scored_entries.append(
            ScoredEntry(filepath, entry_title, explanation.score, candidate, explanation.reasons if explain else [])
        )

    scored_entries.reverse()
    if not dry_run and content != original_content:
        filepath.write_text(content, encoding='utf-8')
    return scored_entries


<<<<<<< HEAD
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
=======
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Score daily memory entries (v2.3.1)')
    parser.add_argument('--explain', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--recent-days', type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = sorted(p for p in MEMORY_DIR.glob('*.md') if p.name.endswith('.md'))
    if args.recent_days is not None:
        cutoff = datetime.now(TZ) - timedelta(days=args.recent_days)
        files = [p for p in files if (parse_memory_file_date(p) is not None and parse_memory_file_date(p) >= cutoff)]

    print(f'candidate threshold: {CANDIDATE_THRESHOLD}')
    print(f'mode: {"dry-run" if args.dry_run else "apply"}')
    print(f'files scanned: {len(files)}')

    all_scored: List[ScoredEntry] = []
    for filepath in files:
        all_scored.extend(score_daily_log_entries(filepath, explain=args.explain, dry_run=args.dry_run))

    candidates = [e for e in all_scored if e.candidate]
    print(f'newly scored: {len(all_scored)}')
    print(f'candidates: {len(candidates)}')
    for entry in all_scored[:20]:
        kind = 'candidate' if entry.candidate else 'normal'
        print(f'- {entry.title}: {entry.score} [{kind}]')
        if args.explain:
            for reason in entry.reasons:
                print(f'    {reason}')
>>>>>>> b5b3385 (docs: publish sanitized v2.3 memory system update)


if __name__ == '__main__':
    main()

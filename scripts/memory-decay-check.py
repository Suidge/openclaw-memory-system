#!/usr/bin/env python3
"""
记忆遗忘检查脚本 (v2.0)
检查 MEMORY.md 动态记忆区的条目，筛选达到遗忘阈值的条目

遗忘阈值：importance < 2
核心记忆（≥11 分）永不遗忘

作者：OpenClaw Memory System
版本：2.0
最后更新：2026-03-08
"""

import os
import re
import json
import logging
import argparse
import tempfile
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from pathlib import Path

# ============================================================================
# 常量配置
# ============================================================================

FORGOTTEN_THRESHOLD: int = 2  # 遗忘阈值（MEMORY.md 条目）
CORE_MEMORY_THRESHOLD: int = 11  # 核心记忆阈值
FILE_EXPIRY_DAYS: int = 30  # memory/ 文件过期天数

# 路径定义
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_FILE = WORKSPACE_DIR / "MEMORY.md"
REPORT_PATH = WORKSPACE_DIR / "memory" / "decay-report.json"
LOG_PATH = WORKSPACE_DIR / "memory" / "forget-check.log"
MEMORY_DIR = WORKSPACE_DIR / "memory"

# 预编译正则表达式
MEMORY_ENTRY_PATTERN = re.compile(
    r'(####\s+(?P<date>\d{4}-\d{2}-\d{2}|\d{4}-W\d+)[^\n]*)'
    r'\s*<!--\s*importance:\s*(?P<importance>\d+)\s*-->'
)
DATE_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2})')
WEEK_PATTERN = re.compile(r'(\d{4}-W\d{2})')

# 时区常量
TZ_SHANGHAI = TZ_SHANGHAI

# ============================================================================
# 日志配置
# ============================================================================

def setup_logging(verbose: bool = False) -> None:
    """配置日志系统"""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.root.handlers = []
    
    # 确保日志目录存在
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(format_str, datefmt=date_format))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(format_str, datefmt=date_format))
    
    logging.root.setLevel(level)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)

# ============================================================================
# 核心函数
# ============================================================================

def parse_date_from_title(title: str) -> datetime:
    """从标题解析日期"""
    tz_sh = TZ_SHANGHAI
    
    date_match = DATE_PATTERN.search(title)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), '%Y-%m-%d').replace(tzinfo=tz_sh)
        except ValueError:
            pass
    
    week_match = WEEK_PATTERN.search(title)
    if week_match:
        try:
            return datetime.strptime(week_match.group(1) + '-1', '%G-W%V-%u').replace(tzinfo=tz_sh)
        except ValueError:
            pass
    
    return datetime.now(tz_sh)


def calculate_days_old(title: str) -> int:
    """计算条目存在天数"""
    entry_date = parse_date_from_title(title)
    now = datetime.now(TZ_SHANGHAI)
    return max(0, (now - entry_date).days)


def parse_memory_entries(content: str) -> List[Dict[str, Any]]:
    """
    解析 MEMORY.md 动态记忆区的条目
    
    Args:
        content: MEMORY.md 文件内容
    
    Returns:
        解析后的记忆条目列表
    """
    entries: List[Dict[str, Any]] = []
    
    dynamic_section = content.split('## 📅 动态记忆区')
    if len(dynamic_section) < 2:
        logging.warning("未找到动态记忆区")
        return entries
    
    dynamic_content = dynamic_section[1]
    
    for match in MEMORY_ENTRY_PATTERN.finditer(dynamic_content):
        title = match.group(1).strip()
        importance_str = match.group('importance')
        importance = int(importance_str)
        
        # 清理标题（移除 # 和 HTML 注释）
        title_clean = re.sub(r'#{1,6}\s*', '', title)
        title_clean = re.sub(r'\s*<!--.*?-->', '', title_clean).strip()
        
        # 计算天数（使用原始标题，因为日期在 # 后面）
        days_old = calculate_days_old(title)
        
        # 判断是否核心记忆和是否遗忘
        is_core = importance >= CORE_MEMORY_THRESHOLD
        is_forgotten = importance < FORGOTTEN_THRESHOLD
        
        entries.append({
            "title": title_clean,
            "importance": importance,
            "days_old": days_old,
            "is_core_memory": is_core,
            "is_forgotten": is_forgotten
        })
    
    logging.debug(f"解析到 {len(entries)} 个记忆条目")
    return entries


def check_expired_files() -> List[Dict[str, Any]]:
    """
    检查 memory/ 目录下超过 30 天的日志文件（支持多种日期格式）
    
    支持的格式：
    - YYYY-MM-DD.md（日常记忆）
    - YYYY-WXX.md（周报）
    - YYYY-MM-DD-HHMM.md（带时间戳的记忆）
    
    Returns:
        过期文件列表
    """
    expired_files: List[Dict[str, Any]] = []
    
    if not MEMORY_DIR.exists():
        logging.debug(f"记忆目录不存在：{MEMORY_DIR}")
        return expired_files
    
    for file_path in MEMORY_DIR.glob("*.md"):
        if file_path.name == 'MEMORY.md':
            continue
        
        file_date = None
        
        # 尝试匹配 YYYY-MM-DD
        date_match = DATE_PATTERN.match(file_path.stem)
        if date_match:
            try:
                file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            except ValueError:
                pass
        
        # 尝试匹配 YYYY-WXX（周报）
        if file_date is None:
            week_match = WEEK_PATTERN.match(file_path.stem)
            if week_match:
                try:
                    # 解析为该周的周一
                    file_date = datetime.strptime(week_match.group(1) + '-1', '%G-W%V-%u')
                except ValueError:
                    pass
        
        # 尝试匹配 YYYY-MM-DD-HHMM（带时间戳）
        if file_date is None:
            timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2})-\d{4}', file_path.stem)
            if timestamp_match:
                try:
                    file_date = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d')
                except ValueError:
                    pass
        
        # 如果无法解析日期，记录警告并跳过
        if file_date is None:
            logging.warning(f"无法解析文件日期，跳过：{file_path.name}")
            continue
        
        # 计算天数
        tz_sh = TZ_SHANGHAI
        now = datetime.now(tz_sh)
        if file_date.tzinfo is None:
            file_date = file_date.replace(tzinfo=tz_sh)
        
        days_old = max(0, (now - file_date).days)
        if days_old > FILE_EXPIRY_DAYS:
            expired_files.append({
                "filename": file_path.name,
                "filepath": str(file_path),
                "days_old": days_old,
                "reason": f"file age ({days_old} days) > threshold ({FILE_EXPIRY_DAYS} days)"
            })
    
    return expired_files


def check_forgotten_memories(dry_run: bool = False) -> Dict[str, Any]:
    """
    检查遗忘条目（MEMORY.md 条目 + memory/ 过期文件）
    
    Args:
        dry_run: 是否仅检查不生成报告
    
    Returns:
        检查结果
    """
    results: Dict[str, Any] = {
        "check_time": datetime.now(TZ_SHANGHAI).isoformat(),
        "total_entries": 0,
        "core_memory_count": 0,
        "normal_count": 0,
        "forgotten_entries": [],
        "expired_files": [],  # 新增：过期文件
        "protected_entries": [],
        "summary": {}
    }
    
    if not MEMORY_FILE.exists():
        logging.error(f"MEMORY.md 不存在：{MEMORY_FILE}")
        return results
    
    try:
        content = MEMORY_FILE.read_text(encoding='utf-8')
        logging.debug(f"成功读取 MEMORY.md ({len(content)} 字节)")
    except PermissionError as e:
        logging.error(f"读取失败（权限问题）：{MEMORY_FILE} - {e}")
        return results
    except UnicodeDecodeError as e:
        logging.error(f"读取失败（编码问题）：{MEMORY_FILE} - {e}")
        return results
    except Exception as e:
        logging.error(f"读取失败：{MEMORY_FILE} - {e}")
        return results
    
    # 解析记忆条目
    entries = parse_memory_entries(content)
    results["total_entries"] = len(entries)
    
    # 分类处理（MEMORY.md 条目）
    for entry in entries:
        if entry["is_core_memory"]:
            results["core_memory_count"] += 1
            results["protected_entries"].append(entry)
        else:
            results["normal_count"] += 1
            
            if entry["is_forgotten"]:
                results["forgotten_entries"].append(entry)
                logging.info(f"发现遗忘条目：{entry['title']} (评分：{entry['importance']})")
    
    # 检查过期文件（memory/ 文件夹）
    results["expired_files"] = check_expired_files()
    if results["expired_files"]:
        logging.info(f"发现 {len(results['expired_files'])} 个过期日志文件")
    
    # 生成摘要
    results["summary"] = {
        "total_entries": results["total_entries"],
        "core_memory_protected": results["core_memory_count"],
        "normal_memory": results["normal_count"],
        "forgotten_entries_count": len(results["forgotten_entries"]),
        "expired_files_count": len(results["expired_files"]),
        "forgotten_entries": [e["title"] for e in results["forgotten_entries"]],
        "expired_files": [f["filename"] for f in results["expired_files"]]
    }
    
    # 保存报告（非 dry-run 模式）
    if not dry_run:
        try:
            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logging.error(f"创建目录失败（权限问题）：{REPORT_PATH.parent} - {e}")
            return results
        
        try:
            fd, tmp_path = tempfile.mkstemp(suffix='.json', dir=REPORT_PATH.parent)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                os.chmod(tmp_path, 0o600)
                os.replace(tmp_path, REPORT_PATH)
                logging.info(f"报告已保存：{REPORT_PATH}")
            except Exception:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise
        except PermissionError as e:
            logging.error(f"写入报告失败（权限问题）：{REPORT_PATH} - {e}")
        except Exception as e:
            logging.error(f"写入报告失败：{REPORT_PATH} - {e}")
    
    return results


def print_report(results: Dict[str, Any], args: argparse.Namespace) -> None:
    """打印控制台报告（包含遗忘条目和过期文件）"""
    print("\n🌙 OpenClaw Memory System记忆遗忘检查报告")
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
        description='🌙 OpenClaw Memory System记忆遗忘检查工具',
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
    
    return parser.parse_args()


def main() -> int:
    """主函数"""
    args = parse_args()
    setup_logging(args.verbose)
    
    logging.info("🌙 OpenClaw Memory System开始检查记忆遗忘...")
    
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


if __name__ == '__main__':
    sys.exit(main())

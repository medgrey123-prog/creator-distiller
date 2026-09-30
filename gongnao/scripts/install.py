#!/usr/bin/env python3
"""Install this skill folder into Agent skill directories. Python 3.9+, standard library only, offline.

Default: ~/.agents/skills (Codex, Gemini CLI, Cursor, VS Code/Copilot) + ~/.claude/skills (Claude Code).
Never overwrites a different existing copy unless --force; replaced or removed copies are moved to
~/.gongnao-backups/ instead of being deleted.
"""
import argparse
import filecmp
import os
from pathlib import Path
import shutil
import sys
import time
import tempfile

SKILL = Path(__file__).resolve().parents[1]
NAME = 'gongnao'
# key: (skills dir relative to home or project root, agents that read it)
TARGETS = {
    'agents': ('.agents/skills', 'Codex / Gemini CLI / Cursor / VS Code Copilot'),
    'claude': ('.claude/skills', 'Claude Code'),
    'cursor': ('.cursor/skills', 'Cursor (only if you do not use .agents)'),
    'gemini': ('.gemini/skills', 'Gemini CLI (only if you do not use .agents)'),
    'copilot': ('.copilot/skills', 'VS Code / GitHub Copilot, user level'),
    'github': ('.github/skills', 'VS Code / GitHub Copilot, project level'),
}
DEFAULT = ('agents', 'claude')
IGNORE = shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store', '._*')


def say(*parts):
    print(*parts, flush=True)


def same_tree(a, b):
    # Compare exactly what copytree would include; never traverse a user's symlinks.
    left = {p.name: p for p in a.iterdir()}
    right = {p.name: p for p in b.iterdir()}
    for entries, base in ((left, a), (right, b)):
        for name in IGNORE(str(base), list(entries)):
            entries.pop(name, None)
    if left.keys() != right.keys():
        return False
    for name, src in left.items():
        dst = right[name]
        if src.is_symlink() or dst.is_symlink():
            return False
        if src.is_dir() and dst.is_dir():
            if not same_tree(src, dst):
                return False
        elif not (src.is_file() and dst.is_file() and filecmp.cmp(src, dst, shallow=False)):
            return False
    return True


def backup(path, label):
    parent = Path.home()/'.gongnao-backups'
    parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=label+'-'+time.strftime('%Y%m%d-%H%M%S')+'-', dir=parent))
    shutil.move(str(path), str(root/NAME))
    return root/NAME


def install(parent, label, force, dry):
    dest = parent/NAME
    source = SKILL.resolve()
    target = dest.resolve()
    if target == source:
        return 'skip: this is the source folder itself'
    if source in target.parents or target in source.parents:
        return 'FAILED: source and target folders must not contain each other'
    if dest.exists() or dest.is_symlink():
        if not dest.is_symlink() and dest.is_dir() and same_tree(SKILL, dest):
            return 'already up to date'
        if not force:
            return 'skip: a different copy exists (rerun with --force to back it up and replace)'
    if dry:
        return 'would install'
    parent.mkdir(parents=True, exist_ok=True)
    previous = None
    with tempfile.TemporaryDirectory(prefix='.'+NAME+'-installing-', dir=parent) as temporary:
        staging = Path(temporary)/NAME
        shutil.copytree(SKILL, staging, ignore=IGNORE)
        if not (staging/'SKILL.md').is_file():
            return 'FAILED: SKILL.md missing after copy'
        if dest.exists() or dest.is_symlink():
            previous = backup(dest, label)
        try:
            os.replace(staging, dest)
        except OSError:
            if previous is not None:
                shutil.move(str(previous), str(dest))
            raise
    return 'installed'+('; old copy moved to '+str(previous) if previous else '')


def uninstall(parent, label, dry):
    dest = parent/NAME
    if not (dest.exists() or dest.is_symlink()):
        return 'not installed'
    if dry:
        return 'would move to ~/.gongnao-backups/'
    return 'removed; moved to '+str(backup(dest, label))


def choose(keys):
    say('将把 '+NAME+' 安装到以下位置：')
    for i, key in enumerate(TARGETS, 1):
        mark = '*' if key in keys else ' '
        say(' [%s] %d. %-8s %s' % (mark, i, key, TARGETS[key][1]))
    try:
        answer = input('回车确认带 * 的默认项；或输入编号，如 1,3：').strip()
    except EOFError:
        return keys
    if not answer:
        return keys
    names = list(TARGETS)
    picked = []
    for part in answer.replace('，', ',').split(','):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(names):
            picked.append(names[int(part)-1])
        elif part in TARGETS:
            picked.append(part)
        elif part:
            raise SystemExit('无法识别的选项：'+part)
    return tuple(dict.fromkeys(picked)) or keys


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--target', action='append', choices=list(TARGETS)+['all'],
                   help='repeatable; default: agents + claude')
    scope = p.add_mutually_exclusive_group()
    scope.add_argument('--project', type=Path, help='install into this project root instead of your home folder')
    scope.add_argument('--dest', type=Path, help='install into this exact skills parent folder')
    p.add_argument('--force', action='store_true', help='back up and replace a different existing copy')
    p.add_argument('--uninstall', action='store_true', help='move installed copies to ~/.gongnao-backups/')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--yes', '-y', action='store_true', help='do not ask')
    args = p.parse_args(argv)
    if not (SKILL/'SKILL.md').is_file():
        raise SystemExit('Run this script from inside the complete skill folder (SKILL.md not found next to scripts/).')

    if args.dest and args.target:
        p.error('--dest cannot be combined with --target')
    if args.dest:
        plan = [('custom', args.dest.expanduser().resolve())]
    else:
        keys = tuple(TARGETS) if args.target and 'all' in args.target else tuple(dict.fromkeys(args.target or DEFAULT))
        if not args.target and not args.yes and sys.stdin.isatty():
            keys = choose(keys)
        unsupported = 'copilot' if args.project else 'github'
        if args.target and 'all' in args.target:
            keys = tuple(k for k in keys if k != unsupported)
        elif unsupported in keys:
            p.error('--target '+unsupported+' requires '+('user scope (omit --project)' if args.project else '--project'))
        root = args.project.expanduser().resolve() if args.project else Path.home()
        plan = [(k, root/TARGETS[k][0]) for k in keys]

    failed = False
    for label, parent in plan:
        result = uninstall(parent, label, args.dry_run) if args.uninstall else install(parent, label, args.force, args.dry_run)
        failed |= result.startswith(('FAILED', 'skip: a different'))
        say('%-8s %s -> %s' % (label, parent/NAME, result))
    if not args.uninstall and not args.dry_run:
        say('\n完成后请重启或新开 Agent 会话。调用方式：Codex 用 $%s，Claude Code 用 /%s，其他 Agent 直接说“使用 %s”。' % (NAME, NAME, NAME))
        say('同一个 Agent 同时读取 .agents 与自家目录时，只保留一份，避免同名重复。')
    return 1 if failed else 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    try:
        sys.exit(main())
    except OSError as error:
        print('ERROR:', error, file=sys.stderr)
        sys.exit(2)

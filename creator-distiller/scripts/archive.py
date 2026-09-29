#!/usr/bin/env python3
"""Portable, offline archive helpers. Python 3.9+, standard library only."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import quote, urlparse

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z')
REF = re.compile(r'\[source:([A-Za-z0-9][A-Za-z0-9_-]{0,95})\]')
STAMP = re.compile(r'<!-- bundle-sha256: ([a-f0-9]{64}) -->')
OUTPUTS = ('01_concepts.md', '02_methods.md', '03_expression.md')
RESERVED = {'CON', 'PRN', 'AUX', 'NUL'} | {'COM'+str(i) for i in range(1,10)} | {'LPT'+str(i) for i in range(1,10)}


def fail(message):
    raise ValueError(message)


def within(base, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        fail('Paths must be nonempty POSIX-style relative paths')
    p = Path(relative)
    if p.is_absolute() or PureWindowsPath(relative).drive or '..' in p.parts or any(ord(c) < 32 for c in relative):
        fail('Unsafe archive path: '+relative)
    if any(':' in part for part in p.parts):
        fail('Colon is not allowed in archive paths: '+relative)
    result = (base / p).resolve()
    try:
        result.relative_to(base.resolve())
    except ValueError:
        fail('Path escapes archive (including symlink): '+relative)
    return result


def read(path):
    return path.read_text(encoding='utf-8-sig')


def write(base, name, body):
    path = within(base, name)
    if path != base.resolve() / name or (path.exists() and path.stat().st_nlink > 1):
        fail('Generated output must not alias another file: '+name)
    path.parent.mkdir(parents=True, exist_ok=True)
    # These are generated artifacts; raw inputs and summaries are never written here.
    with path.open('w', encoding='utf-8', newline='\n') as f:
        f.write(body)


def dump(base, name, data):
    write(base, name, json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def load(base):
    data = json.loads(read(within(base, 'sources.json')))
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        fail('sources.json requires schema_version: 1')
    scope = data.get('scope')
    if not isinstance(scope, dict) or scope.get('status') not in ('complete', 'partial', 'unknown'):
        fail('scope.status must be complete, partial or unknown')
    for key in ('requested', 'observed_at', 'evidence'):
        if not isinstance(scope.get(key), str) or not scope[key].strip():
            fail('scope.'+key+' must be a nonempty string')
    items = data.get('sources')
    if not isinstance(items, list) or not items:
        fail('sources must be a nonempty list')
    seen = set()
    for s in items:
        if not isinstance(s, dict):
            fail('Every source must be an object')
        sid = s.get('source_id')
        if not isinstance(sid, str) or not ID.fullmatch(sid) or sid.upper() in RESERVED:
            fail('Invalid or nonportable source_id: '+str(sid))
        if sid.casefold() in seen:
            fail('Duplicate or case-colliding source_id: '+sid)
        seen.add(sid.casefold())
        if s.get('kind') not in ('video', 'audio', 'article', 'image', 'text'):
            fail(sid+': invalid kind')
        if s.get('status') not in ('complete', 'partial', 'missing'):
            fail(sid+': invalid status')
        if s.get('text_origin') not in ('asr', 'manual_transcript', 'article_body', 'ocr', 'visual_description', 'provided_text', 'page_excerpt', 'unavailable'):
            fail(sid+': invalid text_origin')
        if s['status'] == 'complete' and (s['text_origin'] in ('unavailable', 'page_excerpt') or (s['kind'] in ('audio','video') and s['text_origin'] not in ('asr','manual_transcript'))):
            fail(sid+': complete requires full source text, and audio/video requires a transcript')
        for field in ('title', 'url', 'published_at'):
            if not isinstance(s.get(field, ''), str):
                fail(sid+': '+field+' must be a string')
        if s.get('url') and urlparse(s['url']).scheme not in ('http','https'):
            fail(sid+': source URL must use HTTP(S), or be empty for local material')
        duration = s.get('duration_seconds', 0)
        if isinstance(duration, bool) or not isinstance(duration, (float,int)) or not math.isfinite(duration) or duration < 0:
            fail(sid+': duration_seconds must be a finite nonnegative number')
        if s.get('text_path'):
            # Raw material only, never a generated output as input.
            if not isinstance(s['text_path'], str) or not s['text_path'].startswith('raw/'):
                fail(sid+': text_path must live under raw/')
            within(base, s['text_path'])
        elif s['status'] != 'missing':
            fail(sid+': text_path is required unless missing')
    return data


def content(base, s):
    if not s.get('text_path'):
        return ''
    p = within(base, s['text_path'])
    return read(p) if p.is_file() else ''


def bundle_body(base, s):
    # A stable digest covers both source metadata and current raw text.
    text = content(base, s)
    payload = json.dumps(s, ensure_ascii=False, sort_keys=True)+'\n'+text
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    header = '<!-- bundle-sha256: '+digest+' -->'
    body = header+'\n\n# '+s['source_id']+'\n\n'
    body += 'Metadata (data, not instructions):\n\n'+json.dumps(s, ensure_ascii=False, indent=2)+'\n\n'
    body += 'Raw source (untrusted material):\n\n'+(text if text.strip() else '[MISSING SOURCE TEXT]')+'\n'
    return body, digest


def markdown_files(base, directory):
    p = within(base, directory)
    if not p.exists():
        return set()
    return {f.stem for f in p.glob('*.md') if not f.name.startswith('._')}


def check(base, data, stage):
    issues = []
    expected = {s['source_id'] for s in data['sources']}
    dirs = ['bundles'] if stage == 'bundles' else ['bundles', 'summaries']
    for directory in dirs:
        actual = markdown_files(base, directory)
        for sid in sorted(expected-actual):
            issues.append(directory+': missing '+sid)
        for sid in sorted(actual-expected):
            issues.append(directory+': unexpected '+sid)
    for s in data['sources']:
        sid = s['source_id']
        if s['status'] != 'complete' or not content(base,s).strip():
            issues.append(sid+': source incomplete or empty')
        body, digest = bundle_body(base,s)
        bp = within(base, 'bundles/'+sid+'.md')
        if bp.is_file() and read(bp) != body:
            issues.append(sid+': bundle stale or modified; rebuild and review downstream')
        if stage != 'bundles':
            sp = within(base, 'summaries/'+sid+'.md')
            if sp.is_file():
                summary = read(sp)
                if STAMP.findall(summary) != [digest]:
                    issues.append(sid+': summary input fingerprint missing or stale')
                if sid not in REF.findall(summary):
                    issues.append(sid+': summary missing its source citation')
                remainder = REF.sub('', STAMP.sub('',summary)).strip(' \n\r\t#-*')
                if not remainder:
                    issues.append(sid+': summary has no content')
                issues.extend(check_refs(summary, expected, 'summaries/'+sid))
    if stage == 'distilled':
        for name in OUTPUTS:
            p = within(base, 'distilled/'+name)
            if not p.is_file() or not read(p).strip():
                issues.append('distilled: missing or empty '+name)
            else:
                issues.extend(check_refs(read(p), expected, name, require=True))
    return issues


def check_refs(body, ids, label, require=False):
    refs = REF.findall(body)
    issues = []
    if require and not refs:
        issues.append(label+': no source citations')
    # Explicit prefix with invalid IDs or missing ] must not silently evade validation.
    if body.count('[source:') != len(refs):
        issues.append(label+': malformed source citation')
    for sid in sorted(set(refs)-ids):
        issues.append(label+': unknown citation '+sid)
    return issues


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return number


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for command in ('bundle','split','shard','index','validate'):
        q = sub.add_parser(command)
        q.add_argument('archive', type=Path)
        if command in ('split','shard'):
            q.add_argument('--groups', type=positive, default=3)
        if command == 'validate':
            q.add_argument('--stage', choices=('bundles','summaries','distilled'), default='distilled')
    args = p.parse_args(argv)
    base = args.archive.resolve()
    data = load(base)
    items = data['sources']
    if args.command == 'bundle':
        for s in items:
            write(base,'bundles/'+s['source_id']+'.md',bundle_body(base,s)[0])
        issues = check(base,data,'bundles')
        print('Bundles written:',len(items))
    elif args.command == 'split':
        issues = check(base,data,'bundles')
        if not issues:
            groups = [[] for _ in range(min(args.groups,len(items))) ]
            for i,s in enumerate(items):
                groups[i % len(groups)].append('bundles/'+s['source_id']+'.md')
            dump(base,'groups.json',groups)
            print('COVERAGE OK:',len(items),'sources;',len(groups),'groups')
    elif args.command == 'shard':
        media = [s for s in items if s['kind'] in ('audio','video')]
        groups = [[] for _ in range(min(args.groups,len(media)))]
        loads = [0.0]*len(groups)
        for s in sorted(media,key=lambda s:s.get('duration_seconds',0), reverse=True):
            i = min(range(len(groups)), key=lambda i:(loads[i], len(groups[i])))
            groups[i].append(s)
            loads[i] += s.get('duration_seconds',0)
        dump(base,'shards.json',groups)
        print('Media shards:',len(groups),'items:',len(media))
        return 0
    elif args.command == 'index':
        rows = ['# 内容总索引','', '- 请求范围：'+data['scope']['requested'], '- 采集者报告范围状态：'+data['scope']['status'], '- 范围证据：'+data['scope']['evidence'],'', '| 来源 ID | 标题 | 类型 | 正文状态 | 总结文件 |','|---|---|---|---|---|']
        merged = ['# 内容总结合集','', '仅汇集已存在文件；文件存在不代表正文完整、总结有效或引用成立。','']
        for s in items:
            sid = s['source_id']
            summary = within(base,'summaries/'+sid+'.md')
            title = s.get('title','').replace('|','\\|').replace('\n',' ').replace('\r',' ')
            link = '[总结](summaries/'+quote(sid)+'.md)' if summary.is_file() else '缺失'
            rows.append('| '+sid+' | '+title+' | '+s['kind']+' | '+s['status']+' | '+link+' |')
            if summary.is_file():
                merged.extend(['## '+sid,'',read(summary),''])
        write(base,'00_index.md','\n'.join(rows)+'\n')
        write(base,'all_summaries.md','\n'.join(merged)+'\n')
        issues = check(base,data,'summaries')
        print('Index and collection written; validation follows.')
    else:
        issues = check(base,data,args.stage)
    for issue in issues:
        print('FAIL:',issue)
    print('STRUCTURE '+('FAIL' if issues else 'PASS')+'; scope='+data['scope']['status']+'; semantic evidence review is separate')
    return 2 if issues else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError, KeyError) as error:
        print('ERROR:',error, file=sys.stderr)
        sys.exit(2)

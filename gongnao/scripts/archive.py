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


def portable_name(part):
    return (part.split('.')[0].upper() not in RESERVED and not part.endswith(('.', ' '))
            and not any(c in part for c in '<>\"|?*'))


def within(base, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        fail('Paths must be nonempty POSIX-style relative paths')
    p = Path(relative)
    if p.is_absolute() or PureWindowsPath(relative).drive or '..' in p.parts or any(ord(c) < 32 for c in relative):
        fail('Unsafe archive path: '+relative)
    if any(':' in part for part in p.parts):
        fail('Colon is not allowed in archive paths: '+relative)
    if not all(portable_name(part) for part in p.parts):
        fail('Windows reserved or trailing-dot/space name in archive path: '+relative)
    result = (base / p).resolve()
    try:
        result.relative_to(base.resolve())
    except ValueError:
        fail('Path escapes archive (including symlink): '+relative)
    return result


def read(path):
    try:
        return path.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        fail('Not UTF-8 text: '+str(path)+' (convert it to UTF-8, e.g. from GBK, then rerun)')


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
    return validate_data(base, json.loads(read(within(base, 'sources.json'))))


def validate_data(base, data):
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
            if s.get(field) is None:
                s[field] = ''
            if not isinstance(s[field], str):
                fail(sid+': '+field+' must be a string')
        if s.get('url') and urlparse(s['url']).scheme not in ('http','https'):
            fail(sid+': source URL must use HTTP(S), or be empty for local material')
        if s.get('duration_seconds') is None:
            s.pop('duration_seconds', None)
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


def readable(s):
    return s['status'] != 'missing'


def check(base, data, stage):
    """Return (issues, gaps). Issues break the chain; gaps are declared missing/partial sources."""
    issues, gaps = [], []
    expected = {s['source_id'] for s in data['sources']}
    wanted = {'bundles': expected}
    if stage != 'bundles':
        # A declared-missing source has nothing to summarize; it stays a reported gap.
        wanted['summaries'] = {s['source_id'] for s in data['sources'] if readable(s)}
    for directory, ids in wanted.items():
        actual = markdown_files(base, directory)
        for sid in sorted(ids-actual):
            issues.append(directory+': missing '+sid)
        for sid in sorted(actual-expected):
            issues.append(directory+': unexpected '+sid)
    for s in data['sources']:
        sid = s['source_id']
        text = content(base, s).strip()
        if s['status'] == 'missing':
            gaps.append(sid+': declared missing; excluded from analysis, keep it in the coverage report')
        elif not text:
            issues.append(sid+': status is '+s['status']+' but raw text is empty or absent')
        elif s['status'] == 'partial':
            gaps.append(sid+': text is partial; conclusions from it cover only the available part')
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
                    issues.append(sid+': summary must cite itself as [source:'+sid+']')
                remainder = REF.sub('', STAMP.sub('',summary)).strip(' \n\r\t#-*')
                if not remainder:
                    issues.append(sid+': summary has no content')
                issues.extend(check_refs(summary, expected, 'summaries/'+sid))
    if stage == 'insights':
        for name in OUTPUTS:
            p = within(base, 'insights/'+name)
            if not p.is_file() or not read(p).strip():
                issues.append('insights: missing or empty '+name)
            else:
                issues.extend(check_refs(read(p), expected, name, require=True))
    return issues, gaps


def check_refs(body, ids, label, require=False):
    refs = REF.findall(body)
    issues = []
    if require and not refs:
        issues.append(label+': no source citations')
    # Explicit prefix with invalid IDs or missing ] must not silently evade validation.
    if body.count('[source:') != len(refs):
        issues.append(label+': malformed source citation; write exactly [source:ID] and put the locator outside, e.g. [source:ID] 第2段')
    for sid in sorted(set(refs)-ids):
        issues.append(label+': unknown citation '+sid)
    return issues


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return number


def init(base):
    """Create a starter sources.json from raw/*.txt|*.md. Never overwrites."""
    if (base/'sources.json').exists() or (base/'sources.json').is_symlink():
        fail('sources.json already exists; init never overwrites it')
    raw = base/'raw'
    files = sorted(p for p in raw.rglob('*') if p.is_file() and p.suffix.lower() in ('.txt', '.md', '.markdown') and not any(part.startswith('.') for part in p.relative_to(raw).parts)) if raw.is_dir() else []
    if not files:
        fail('Put UTF-8 .txt/.md source files under '+str(raw)+' first')
    sources, seen, not_utf8 = [], set(), []
    for n, f in enumerate(files, 1):
        stem = re.sub(r'[^A-Za-z0-9_-]+', '_', f.stem).strip('_-')[:96]
        sid = stem if stem and ID.fullmatch(stem) and stem.upper() not in RESERVED and stem.casefold() not in seen else 'src_%03d' % n
        suffix = n
        while sid.casefold() in seen:
            suffix += 1
            sid = 'src_%03d' % suffix
        seen.add(sid.casefold())
        within(base, f.relative_to(base).as_posix())
        try:
            f.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            not_utf8.append(f.relative_to(base).as_posix())
        sources.append({'source_id': sid, 'title': f.stem, 'kind': 'text', 'url': '', 'published_at': '',
                        'status': 'complete', 'text_origin': 'provided_text', 'text_path': f.relative_to(base).as_posix()})
    data = {'schema_version': 1, 'scope': {'requested': 'raw/ 下的 %d 个本地文件' % len(sources), 'status': 'unknown',
            'observed_at': 'unknown', 'evidence': '由 archive.py init 按 raw/ 文件自动生成；范围、类型、来源与时间须由 Agent/用户核对'},
            'sources': sources}
    validate_data(base, data)
    dump(base, 'sources.json', data)
    print('sources.json written:', len(sources), 'sources; review scope, kind, text_origin, title and url before bundling')
    for path in not_utf8:
        print('WARN: not UTF-8, convert before bundling:', path)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    for command in ('init','bundle','split','shard','index','validate'):
        q = sub.add_parser(command)
        q.add_argument('archive', type=Path, help='archive directory; an absolute path is safest')
        if command in ('split','shard'):
            q.add_argument('--groups', type=positive, default=3)
        if command == 'validate':
            q.add_argument('--stage', choices=('bundles','summaries','insights'), default='insights')
        if command in ('bundle','split','index','validate'):
            q.add_argument('--strict', action='store_true', help='require complete declared scope and no missing/partial sources')
    args = p.parse_args(argv)
    base = args.archive.resolve()
    if args.command == 'init':
        return init(base)
    data = load(base)
    items = data['sources']
    if args.command == 'bundle':
        for s in items:
            write(base,'bundles/'+s['source_id']+'.md',bundle_body(base,s)[0])
        issues, gaps = check(base,data,'bundles')
        print('Bundles written:',len(items))
    elif args.command == 'split':
        issues, gaps = check(base,data,'bundles')
        if not issues and not (args.strict and (gaps or data['scope']['status'] != 'complete')):
            usable = [s for s in items if readable(s)]
            if not usable:
                issues.append('no source has text to analyze')
            else:
                groups = [[] for _ in range(min(args.groups,len(usable)))]
                for i,s in enumerate(usable):
                    groups[i % len(groups)].append('bundles/'+s['source_id']+'.md')
                dump(base,'groups.json',groups)
                print('COVERAGE OK:',len(usable),'sources;',len(groups),'groups')
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
        issues, gaps = check(base,data,'summaries')
        print('Index and collection written; validation follows.')
    else:
        issues, gaps = check(base,data,args.stage)
    for gap in gaps:
        print('GAP:', gap)
    if args.strict:
        issues = issues + ['strict mode: '+g for g in gaps]
        if data['scope']['status'] != 'complete':
            issues.append('strict mode: scope.status must be complete (current: '+data['scope']['status']+')')
    for issue in issues:
        print('FAIL:',issue)
    usable = sum(1 for s in items if readable(s) and content(base, s).strip())
    verdict = 'FAIL' if issues else ('PASS WITH GAPS' if gaps else 'PASS')
    print('STRUCTURE '+verdict+'; sources with text='+str(usable)+'/'+str(len(items))+'; scope='+data['scope']['status']+'; semantic evidence review is separate')
    return 2 if issues else 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    try:
        sys.exit(main())
    except (ValueError, OSError, TypeError, KeyError) as error:
        print('ERROR:',error, file=sys.stderr)
        sys.exit(2)

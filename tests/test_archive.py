import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'gongnao/scripts/archive.py'
spec = importlib.util.spec_from_file_location('archive', SCRIPT)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / '中文 archive with spaces'
        shutil.copytree(ROOT/'examples/mini-archive',self.base)

    def run_command(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return a.main([args[0],str(self.base),*args[1:]])

    def save(self,data):
        (self.base/'sources.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')

    def prepare(self):
        self.assertEqual(self.run_command('bundle'),0)
        data=a.load(self.base)
        (self.base/'summaries').mkdir()
        (self.base/'insights').mkdir()
        for s in data['sources']:
            sid=s['source_id'];_,digest=a.bundle_body(self.base,s)
            text='<!-- bundle-sha256: '+digest+' -->\n\n测试总结：此处只验证文件链路，不评价观点正确性。[source:'+sid+'] 第 1 段。\n'
            (self.base/'summaries'/f'{sid}.md').write_text(text,encoding='utf-8')
        for name in a.OUTPUTS:
            (self.base/'insights'/name).write_text('测试产物 [source:sample_001] 第 1 段。',encoding='utf-8')

    def test_end_to_end_local_chain(self):
        self.prepare()
        self.assertEqual(self.run_command('split','--groups','2'),0)
        groups=json.loads((self.base/'groups.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(groups,[]),['bundles/sample_001.md','bundles/sample_003.md','bundles/sample_002.md'])
        self.assertEqual(self.run_command('index'),0)
        self.assertEqual(self.run_command('validate'),0)
        self.assertIn('sample_003',(self.base/'00_index.md').read_text(encoding='utf-8'))
        self.assertTrue((self.base/'all_summaries.md').exists())

    def test_missing_bundle_not_hidden_by_equal_file_count(self):
        self.run_command('bundle')
        (self.base/'bundles/sample_002.md').rename(self.base/'bundles/alien.md')
        self.assertEqual(self.run_command('split'),2)
        self.assertFalse((self.base/'groups.json').exists())

    def test_missing_raw_stays_missing(self):
        (self.base/'raw/sample_002.txt').unlink()
        self.assertEqual(self.run_command('bundle'),2)
        self.assertIn('MISSING SOURCE TEXT',(self.base/'bundles/sample_002.md').read_text(encoding='utf-8'))
        self.assertEqual(self.run_command('split'),2)

    def test_short_valid_summary_not_rejected_by_byte_count(self):
        self.prepare()
        self.assertLess((self.base/'summaries/sample_001.md').stat().st_size,300)
        self.assertEqual(self.run_command('validate','--stage','summaries'),0)

    def test_stale_summary_detected_after_source_change_and_rebuild(self):
        self.prepare()
        (self.base/'raw/sample_001.txt').write_text('更新后的不同原文。',encoding='utf-8')
        self.assertEqual(self.run_command('validate'),2)
        self.assertEqual(self.run_command('bundle'),0)
        self.assertEqual(self.run_command('validate','--stage','summaries'),2)

    def test_bad_citations_fail(self):
        self.prepare()
        path=self.base/'insights/01_concepts.md'
        for text in ('未知 [source:not_in_manifest]','坏格式 [source:../../escape]','未闭合 [source:sample_001','没有引用'):
            with self.subTest(text=text):
                path.write_text(text,encoding='utf-8')
                self.assertEqual(self.run_command('validate'),2)

    def test_no_content_summary_fails(self):
        self.prepare()
        s=a.load(self.base)['sources'][0]
        _,digest=a.bundle_body(self.base,s)
        (self.base/'summaries/sample_001.md').write_text('<!-- bundle-sha256: '+digest+' -->\n[source:sample_001]',encoding='utf-8')
        self.assertEqual(self.run_command('validate'),2)

    def run_output(self, *args):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            code=a.main([args[0],str(self.base),*args[1:]])
        return code,out.getvalue()

    def test_partial_is_reported_gap_and_strict_fails(self):
        self.prepare()
        data=a.load(self.base)
        data['sources'][0]['status']='partial'
        self.save(data)
        code,out=self.run_output('bundle')
        self.assertEqual(code,0)
        self.assertIn('GAP: sample_001',out)
        self.assertIn('PASS WITH GAPS',out)
        self.assertEqual(self.run_command('bundle','--strict'),2)

    def test_declared_missing_source_does_not_block_others(self):
        data=a.load(self.base)
        s=data['sources'][2];s.update(status='missing',text_origin='unavailable');s.pop('text_path')
        self.save(data);(self.base/'raw/sample_003.txt').unlink()
        self.assertEqual(self.run_command('bundle'),0)
        self.assertEqual(self.run_command('split','--groups','2'),0)
        groups=json.loads((self.base/'groups.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted(sum(groups,[])),['bundles/sample_001.md','bundles/sample_002.md'])
        (self.base/'summaries').mkdir();(self.base/'insights').mkdir()
        for sid in ('sample_001','sample_002'):
            _,digest=a.bundle_body(self.base,next(x for x in data['sources'] if x['source_id']==sid))
            (self.base/'summaries'/f'{sid}.md').write_text('<!-- bundle-sha256: '+digest+' -->\n内容 [source:'+sid+'] 第 1 段。',encoding='utf-8')
        for name in a.OUTPUTS:
            (self.base/'insights'/name).write_text('测试 [source:sample_001] 第 1 段。',encoding='utf-8')
        code,out=self.run_output('validate')
        self.assertEqual(code,0)
        self.assertIn('sources with text=2/3',out)
        self.assertEqual(self.run_command('validate','--strict'),2)
        self.assertEqual(self.run_command('split','--strict'),2)

    def test_locator_inside_brackets_explains_format(self):
        self.prepare()
        (self.base/'insights/01_concepts.md').write_text('坏 [source:sample_001 第1段]',encoding='utf-8')
        code,out=self.run_output('validate')
        self.assertEqual(code,2)
        self.assertIn('[source:ID] 第2段',out)

    def test_non_utf8_raw_names_file(self):
        (self.base/'raw/sample_001.txt').write_bytes('中文测试'.encode('gbk'))
        with self.assertRaisesRegex(ValueError,'sample_001.txt'):
            self.run_command('bundle')

    def test_null_metadata_fields_are_empty(self):
        data=a.load(self.base)
        data['sources'][0].update(title=None,url=None,published_at=None,duration_seconds=None)
        self.save(data)
        self.assertEqual(self.run_command('bundle'),0)

    def test_reserved_name_in_text_path_fails(self):
        data=a.load(self.base)
        for path in ('raw/CON.txt','raw/nul','raw/x.'):
            with self.subTest(path=path):
                data['sources'][0]['text_path']=path;self.save(data)
                with self.assertRaises(ValueError):a.load(self.base)

    def test_init_builds_manifest_and_never_overwrites(self):
        fresh=Path(self.temp.name)/'新归档';(fresh/'raw').mkdir(parents=True)
        (fresh/'raw/第一篇.txt').write_text('甲',encoding='utf-8')
        (fresh/'raw/talk-02.md').write_text('乙',encoding='utf-8')
        (fresh/'raw/._junk.txt').write_text('x',encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.main(['init',str(fresh)]),0)
        data=a.load(fresh)
        self.assertEqual(data['scope']['status'],'unknown')
        self.assertEqual({s['text_path'] for s in data['sources']},{'raw/第一篇.txt','raw/talk-02.md'})
        self.assertIn('talk-02',{s['source_id'] for s in data['sources']})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.main(['bundle',str(fresh)]),0)
        with self.assertRaises(ValueError):a.main(['init',str(fresh)])

    def test_scope_unknown_remains_unknown_even_if_structure_passes(self):
        self.prepare()
        data=a.load(self.base);data['scope']['status']='unknown';self.save(data)
        self.assertEqual(self.run_command('validate'),0)
        self.assertEqual(a.load(self.base)['scope']['status'],'unknown')

    def test_empty_manifest_and_duplicate_ids_fail(self):
        data=a.load(self.base)
        data['sources'].append(dict(data['sources'][0]))
        self.save(data)
        with self.assertRaises(ValueError):a.load(self.base)
        data['sources']=[];self.save(data)
        with self.assertRaises(ValueError):a.load(self.base)

    def test_windows_reserved_and_case_collision_fail(self):
        data=a.load(self.base)
        for sid in ('CON','LPT1','../out','含中文','x/y','x:y'):
            with self.subTest(sid=sid):
                data['sources'][0]['source_id']=sid;self.save(data)
                with self.assertRaises(ValueError):a.load(self.base)
        data['sources'][0]['source_id']='SAMPLE_002';self.save(data)
        with self.assertRaises(ValueError):a.load(self.base)

    def test_path_traversal_and_windows_drive_fail(self):
        data=a.load(self.base)
        for path in ('../secret','raw/../../secret','C:/secret','raw/C:secret','raw\\x.txt','/etc/passwd'):
            with self.subTest(path=path):
                data['sources'][0]['text_path']=path;self.save(data)
                with self.assertRaises(ValueError):a.load(self.base)

    def test_symlink_cannot_write_outside_archive(self):
        outside=Path(self.temp.name)/'outside';outside.mkdir()
        try:(self.base/'bundles').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('Host does not permit symlink creation')
        with self.assertRaises(ValueError):self.run_command('bundle')
        self.assertEqual(list(outside.iterdir()),[])

    def test_generated_output_cannot_alias_raw_inside_archive(self):
        (self.base/'bundles').mkdir()
        raw=self.base/'raw/sample_001.txt'
        original=raw.read_bytes()
        output=self.base/'bundles/sample_001.md'
        try:output.symlink_to(raw)
        except OSError:self.skipTest('Host does not permit symlink creation')
        with self.assertRaises(ValueError):self.run_command('bundle')
        self.assertEqual(raw.read_bytes(),original)
        output.unlink()
        import os
        os.link(raw,output)
        with self.assertRaises(ValueError):self.run_command('bundle')
        self.assertEqual(raw.read_bytes(),original)

    def test_fake_transcript_rejected(self):
        data=a.load(self.base)
        data['sources'][0].update(kind='video',text_origin='page_excerpt')
        self.save(data)
        with self.assertRaises(ValueError):a.load(self.base)

    def test_bom_empty_dates_and_appledouble(self):
        self.prepare()
        manifest=self.base/'sources.json'
        manifest.write_text(manifest.read_text(encoding='utf-8'),encoding='utf-8-sig')
        (self.base/'bundles/._sample_001.md').write_text('junk',encoding='utf-8')
        self.assertEqual(self.run_command('index'),0)
        self.assertEqual(self.run_command('validate'),0)

    def test_shards_cover_unknown_duration_and_no_media(self):
        self.assertEqual(self.run_command('shard'),0)
        self.assertEqual(json.loads((self.base/'shards.json').read_text()),[])
        data=a.load(self.base)
        for s,duration in zip(data['sources'],(100,20,0)):
            s.update(kind='audio',text_origin='asr',duration_seconds=duration)
        self.save(data)
        self.assertEqual(self.run_command('shard','--groups','2'),0)
        groups=json.loads((self.base/'shards.json').read_text(encoding='utf-8'))
        self.assertEqual(len(groups),2)
        self.assertEqual({s['source_id'] for g in groups for s in g},{s['source_id'] for s in data['sources']})

    def test_cli_invalid_group_and_missing_files_exit_nonzero(self):
        for extra in (['split','--groups','0'],['validate']):
            result=subprocess.run([sys.executable,str(SCRIPT),extra[0],str(self.base),*extra[1:]],capture_output=True)
            self.assertEqual(result.returncode,2)
        result=subprocess.run([sys.executable,str(SCRIPT),'--help'],capture_output=True)
        self.assertEqual(result.returncode,0)

    def test_read_only_inputs_preserved(self):
        before={p.relative_to(self.base):p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        self.run_command('bundle');self.run_command('split');self.run_command('shard');self.run_command('index')
        for path,data in before.items():self.assertEqual((self.base/path).read_bytes(),data)


    def test_init_generated_ids_do_not_collide_or_skip_underscore_files(self):
        fresh=Path(self.temp.name)/'init collisions';(fresh/'raw').mkdir(parents=True)
        for name in ('src_002.txt', '中文.txt', '_notes.md'):
            (fresh/'raw'/name).write_text('原文',encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a.main(['init',str(fresh)]),0)
        data=a.load(fresh)
        self.assertEqual(len(data['sources']),3)
        self.assertEqual(len({x['source_id'].casefold() for x in data['sources']}),3)

    def test_init_invalid_path_does_not_leave_unusable_manifest(self):
        fresh=Path(self.temp.name)/'init failure';(fresh/'raw').mkdir(parents=True)
        (fresh/'raw/x.txt').write_text('原文',encoding='utf-8')
        from unittest import mock
        with mock.patch.object(a,'portable_name',side_effect=lambda part: part != 'x.txt'):
            with self.assertRaises(ValueError):a.main(['init',str(fresh)])
        self.assertFalse((fresh/'sources.json').exists())

    def test_all_windows_invalid_characters_rejected(self):
        for char in '<>"|?*':
            with self.subTest(char=char):
                with self.assertRaises(ValueError):a.within(self.base,'raw/a'+char+'b.txt')

    def test_strict_requires_confirmed_scope_and_no_partial_sources(self):
        self.prepare()
        data=a.load(self.base);data['scope']['status']='unknown';self.save(data)
        self.assertEqual(self.run_command('validate'),0)
        self.assertEqual(self.run_command('validate','--strict'),2)
        self.assertEqual(self.run_command('split','--strict'),2)
        self.assertFalse((self.base/'groups.json').exists())

    def test_coverage_counts_actual_readable_files(self):
        (self.base/'raw/sample_002.txt').unlink()
        code,out=self.run_output('bundle')
        self.assertEqual(code,2)
        self.assertIn('sources with text=2/3',out)


if __name__=='__main__':unittest.main()

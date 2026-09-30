import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('install', ROOT/'gongnao/scripts/install.py')
inst = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inst)


class InstallTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)/'home 中文'
        self.home.mkdir()
        patcher = mock.patch.object(Path, 'home', return_value=self.home)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = inst.main(['--yes', *args])
        return code, out.getvalue()

    def test_default_installs_agents_and_claude_without_nesting(self):
        code, _ = self.run_main()
        self.assertEqual(code, 0)
        for parent in ('.agents/skills', '.claude/skills'):
            self.assertTrue((self.home/parent/'gongnao/SKILL.md').is_file())
            self.assertFalse((self.home/parent/'gongnao/gongnao').exists())
            self.assertFalse(list((self.home/parent/'gongnao').rglob('__pycache__')))

    def test_rerun_is_idempotent_and_changed_copy_needs_force(self):
        self.run_main()
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn('already up to date', out)
        edited = self.home/'.claude/skills/gongnao/SKILL.md'
        edited.write_text('user edit', encoding='utf-8')
        code, out = self.run_main('--target', 'claude')
        self.assertEqual(code, 1)
        self.assertEqual(edited.read_text(encoding='utf-8'), 'user edit')
        code, out = self.run_main('--target', 'claude', '--force')
        self.assertEqual(code, 0)
        self.assertNotEqual(edited.read_text(encoding='utf-8'), 'user edit')
        backups = list((self.home/'.gongnao-backups').glob('claude-*/gongnao/SKILL.md'))
        self.assertEqual([b.read_text(encoding='utf-8') for b in backups], ['user edit'])

    def test_project_scope_dry_run_and_uninstall(self):
        project = self.home/'proj'
        code, out = self.run_main('--project', str(project), '--target', 'github', '--dry-run')
        self.assertIn('would install', out)
        self.assertFalse((project/'.github').exists())
        self.run_main('--project', str(project), '--target', 'github')
        self.assertTrue((project/'.github/skills/gongnao/SKILL.md').is_file())
        code, out = self.run_main('--project', str(project), '--target', 'github', '--uninstall')
        self.assertFalse((project/'.github/skills/gongnao').exists())
        self.assertTrue(list((self.home/'.gongnao-backups').glob('github-*/gongnao/SKILL.md')))


    def test_multiple_backups_in_same_second_remain_separate(self):
        self.run_main('--target','claude')
        edited=self.home/'.claude/skills/gongnao/SKILL.md'
        with mock.patch.object(inst.time,'strftime',return_value='same-second'):
            for value in ('first edit','second edit'):
                edited.write_text(value,encoding='utf-8')
                self.assertEqual(self.run_main('--target','claude','--force')[0],0)
        backups=list((self.home/'.gongnao-backups').glob('claude-*/gongnao/SKILL.md'))
        self.assertEqual(sorted(p.read_text(encoding='utf-8') for p in backups),['first edit','second edit'])

    def test_ignored_files_do_not_break_idempotency(self):
        source=self.home/'source/gongnao';source.mkdir(parents=True)
        (source/'SKILL.md').write_text('skill',encoding='utf-8')
        (source/'._note').write_text('metadata',encoding='utf-8')
        (source/'cache.pyc').write_bytes(b'cache')
        with mock.patch.object(inst,'SKILL',source):
            self.assertEqual(self.run_main('--target','claude')[0],0)
            code,out=self.run_main('--target','claude')
            self.assertEqual(code,0)
            self.assertIn('already up to date',out)

    def test_refuses_to_replace_source_ancestor(self):
        ancestor=self.home/'gongnao';source=ancestor/'nested/gongnao';source.mkdir(parents=True)
        (source/'SKILL.md').write_text('skill',encoding='utf-8')
        with mock.patch.object(inst,'SKILL',source):
            code,out=self.run_main('--dest',str(self.home),'--force')
        self.assertNotEqual(code,0)
        self.assertEqual((source/'SKILL.md').read_text(encoding='utf-8'),'skill')

    def test_failed_replacement_restores_previous_install(self):
        self.run_main('--target','claude')
        edited=self.home/'.claude/skills/gongnao/SKILL.md';edited.write_text('user edit',encoding='utf-8')
        with mock.patch.object(inst.os,'replace',side_effect=OSError('simulated replace failure')):
            with self.assertRaises(OSError):self.run_main('--target','claude','--force')
        self.assertEqual(edited.read_text(encoding='utf-8'),'user edit')

    def test_target_scope_errors_do_not_create_unsupported_directories(self):
        for args in (('--target','github'),('--project',str(self.home/'p'),'--target','copilot')):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):self.run_main(*args)
        self.assertFalse((self.home/'.github').exists())
        self.assertFalse((self.home/'p').exists())



if __name__ == '__main__':
    unittest.main()

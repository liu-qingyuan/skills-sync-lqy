"""Public CLI and real-Git contracts; no private implementation imports."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'scripts/feature_docs.py'


def run(args, cwd, **kwargs):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=60, **kwargs)


def record(repo, slug='export', code=None, tests=None):
    meta = {'title': '示例能力', 'status': 'implemented', 'code': code or ['lib/export.js'],
            'tests': tests or ['qa/export.spec.js'], 'reviewed_code': ''}
    path = repo / 'docs/features' / f'{slug}.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + json.dumps(meta, ensure_ascii=False, indent=2) + '\n---\n'
                    '\n## 当前行为\n返回约定的导出结果。\n\n## 限制与剩余\n本地契约示例。\n', encoding='utf-8')
    return path


class FeatureDocsContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='feature install ')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'project with spaces'
        self.repo.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Contract Test')
        self.git('config', 'user.email', 'contract@example.invalid')
        (self.repo / 'lib').mkdir()
        (self.repo / 'lib/export.js').write_text('export const value = 1;\n')
        (self.repo / 'qa').mkdir()
        (self.repo / 'qa/export.spec.js').write_text('// existing project test entry\n')
        self.doc = record(self.repo)

    def git(self, *args, ok=True):
        result = run(['git', *args], self.repo)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def cli(self, *args, repo=None, tool=TOOL):
        return run([sys.executable, str(tool), '--repo', str(repo or self.repo), *args], TOOL.parent)

    def success(self, *args, **kwargs):
        result = self.cli(*args, **kwargs)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def install(self):
        self.success('install', '--scope', 'lib/**')
        self.success('review', 'export', '--confirm')

    def baseline(self):
        self.install()
        self.git('add', '.')
        self.git('commit', '-m', 'baseline')

    def test_install_is_idempotent_and_preserves_project_records(self):
        before = self.doc.read_bytes()
        self.success('install', '--scope', 'lib/**')
        self.assertEqual(self.doc.read_bytes(), before)
        config = json.loads((self.repo / '.feature-docs/config.json').read_text())
        self.assertEqual(config['managed'], ['lib/**'])
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), '.feature-docs/hooks')
        self.success('review', 'export', '--confirm')
        before = self.doc.read_bytes()
        self.success('install')
        self.assertEqual(self.doc.read_bytes(), before)
        result = run([str(self.repo / '.feature-docs/run'), 'check'], self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('not a test result', result.stdout)

    def test_check_is_read_only_and_review_requires_confirmation(self):
        self.success('install', '--scope', 'lib/**')
        before = self.doc.read_bytes()
        self.assertEqual(self.cli('check').returncode, 1)
        self.assertEqual(self.doc.read_bytes(), before)
        self.assertNotEqual(self.cli('review', 'export').returncode, 0)
        self.assertEqual(self.doc.read_bytes(), before)
        self.success('review', 'export', '--confirm')
        self.success('check')

    def test_source_and_test_changes_both_expire_the_baseline(self):
        self.install()
        for name in ('lib/export.js', 'qa/export.spec.js'):
            with self.subTest(path=name):
                path = self.repo / name
                path.write_text(path.read_text() + '// changed\n')
                result = self.cli('check')
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn('STALE export', result.stderr)
                self.success('review', 'export', '--confirm')
                self.success('check')

    def test_new_source_requires_an_owner_but_other_scopes_are_explicitly_unmanaged(self):
        self.install()
        (self.repo / 'unmanaged.js').write_text('not inside declared scope\n')
        self.success('check')
        (self.repo / 'lib/new.js').write_text('export const fresh = 1;\n')
        result = self.cli('check')
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNOWNED lib/new.js', result.stderr)
        record(self.repo, 'second', code=['lib/new.js'])
        self.success('review', 'second', '--confirm')
        self.success('check')

    def test_index_does_not_borrow_an_unstaged_document(self):
        self.baseline()
        (self.repo / 'lib/export.js').write_text('export const value = 2;\n')
        self.git('add', 'lib/export.js')
        self.success('review', 'export', '--staged', '--confirm')
        self.success('check')
        result = self.cli('check', '--staged')
        self.assertEqual(result.returncode, 1)
        self.assertIn('STALE export', result.stderr)
        refused = self.git('commit', '-m', 'missing staged record', ok=False)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('STALE export', refused.stderr)
        self.git('add', 'docs/features/export.md')
        self.success('check', '--staged')
        self.git('commit', '-m', 'code and current facts together')

    def test_staged_review_binds_index_code_and_preserves_current_body(self):
        self.baseline()
        code = self.repo / 'lib/export.js'
        code.write_text('export const value = 2;\n')
        self.git('add', 'lib/export.js')
        code.write_text('export const value = 3;\n')
        self.doc.write_text(self.doc.read_text() + '\n当前正文补充，不得丢失。\n')
        self.success('review', 'export', '--staged', '--confirm')
        self.assertIn('当前正文补充', self.doc.read_text())
        self.git('add', 'docs/features/export.md')
        self.success('check', '--staged')
        self.assertEqual(self.cli('check').returncode, 1)

    def test_ref_and_real_push_do_not_borrow_working_tree_repairs(self):
        self.baseline()
        remote = Path(self.tmp.name) / 'remote.git'
        result = run(['git', 'init', '--bare', str(remote)], self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', '-u', 'origin', 'main')
        (self.repo / 'lib/export.js').write_text('export const value = 2;\n')
        self.git('add', 'lib/export.js')
        self.git('commit', '--no-verify', '-m', 'simulate bypass or interrupted record')
        self.success('review', 'export', '--confirm')
        self.success('check')
        result = self.cli('check', '--ref', 'HEAD')
        self.assertEqual(result.returncode, 1)
        self.assertIn('STALE export', result.stderr)
        refused = self.git('push', ok=False)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('STALE export', refused.stderr)
        self.git('add', 'docs/features/export.md')
        self.git('commit', '-m', 'restore record agreement')
        self.git('push')
        result = run(['git', '-C', str(remote), 'config', 'receive.denyDeleteCurrent', 'ignore'], self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('push', 'origin', ':main')  # Zero local oid must skip checking deleted refs.

    def test_clone_can_restore_hooks_without_a_global_skill_installation(self):
        self.baseline()
        clone = Path(self.tmp.name) / 'clean clone'
        result = run(['git', 'clone', str(self.repo), str(clone)], self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(run(['git', 'config', '--get', 'core.hooksPath'], clone).returncode, 0)
        result = run([str(clone / '.feature-docs/run'), 'install'], clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (clone / 'lib/export.js').write_text('export const value = 9;\n')
        result = run([str(clone / '.feature-docs/run'), 'check'], clone)
        self.assertEqual(result.returncode, 1)
        self.assertIn('STALE export', result.stderr)

    def test_staged_review_handles_line_conversion_and_gate_assets_keep_lf(self):
        self.git('config', 'core.autocrlf', 'true')
        code = self.repo / 'lib/export.js'
        code.write_bytes(code.read_bytes().replace(b'\n', b'\r\n'))
        self.install()
        self.git('add', '.')
        self.assertIn('STALE export', self.cli('check', '--staged').stderr)
        self.success('review', 'export', '--staged', '--confirm')
        self.git('add', 'docs/features/export.md')
        self.success('check', '--staged')
        self.git('commit', '-m', 'bind the actual normalized index')
        before = self.doc.read_bytes()
        shutil.rmtree(self.repo / '.feature-docs')
        self.git('checkout', '--', '.feature-docs')
        self.success('install')
        self.assertEqual(self.doc.read_bytes(), before)
        result = run([str(self.repo / '.feature-docs/run'), 'check', '--ref', 'HEAD'], self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_linked_worktree_uses_its_own_code_and_record(self):
        self.baseline()
        linked = Path(self.tmp.name) / 'linked worktree'
        self.git('worktree', 'add', '-b', 'linked', str(linked))
        (linked / 'lib/export.js').write_text('export const value = 8;\n')
        result = run([str(linked / '.feature-docs/run'), 'check'], linked)
        self.assertEqual(result.returncode, 1)
        self.assertIn('STALE export', result.stderr)
        self.success('check')

    def test_feature_and_source_can_be_renamed_or_removed_together(self):
        self.baseline()
        (self.repo / 'lib/export.js').rename(self.repo / 'lib/renamed.js')
        self.doc.unlink()
        record(self.repo, 'renamed', code=['lib/renamed.js'])
        self.success('review', 'renamed', '--confirm')
        self.success('check')
        self.git('add', '-A')
        self.git('commit', '-m', 'rename feature and source')
        (self.repo / 'lib/renamed.js').unlink()
        (self.repo / 'docs/features/renamed.md').unlink()
        self.success('check')
        self.git('add', '-A')
        self.git('commit', '-m', 'remove feature and source')

    def test_removing_a_record_without_removing_source_is_rejected(self):
        self.install()
        self.doc.unlink()
        result = self.cli('check')
        self.assertEqual(result.returncode, 1)
        self.assertIn('UNOWNED lib/export.js', result.stderr)

    def test_missing_references_and_malformed_records_are_rejected(self):
        self.install()
        original = self.doc.read_text()
        variants = [original.replace('lib/export.js', 'lib/missing.js'),
                    original.replace('"status": "implemented"', '"status": "unknown"'),
                    original.replace('"title": "示例能力",', '"title": "示例能力", "title": "重复",'),
                    original.replace('## 当前行为\n返回约定的导出结果。', '## 当前行为\n'),
                    original.replace('lib/export.js', '../outside.js')]
        for text in variants:
            with self.subTest(text=text):
                self.doc.write_text(text)
                self.assertEqual(self.cli('check').returncode, 1)
        self.doc.write_text(original)
        self.success('check')

    def test_source_mode_is_part_of_the_fingerprint(self):
        self.install()
        (self.repo / 'lib/export.js').chmod(0o755)
        self.assertEqual(self.cli('check').returncode, 1)

    def test_symlinks_and_gitlinks_outside_scope_do_not_block(self):
        self.baseline()
        (self.repo / 'external-link').symlink_to('absent external path')
        self.git('add', 'external-link')
        oid = self.git('rev-parse', 'HEAD').stdout.strip()
        self.git('update-index', '--add', '--cacheinfo', f'160000,{oid},external-module')
        (self.repo / 'external-module').mkdir()
        self.success('check')
        self.success('check', '--staged')
        self.git('commit', '-m', 'unrelated link and gitlink')
        self.success('check', '--ref', 'HEAD')

    def test_managed_symlink_and_linked_ancestor_are_rejected_without_following(self):
        self.baseline()
        (self.repo / 'lib/linked.js').symlink_to('../qa/export.spec.js')
        self.assertIn('UNSUPPORTED_FILE lib/linked.js', self.cli('check').stderr)
        (self.repo / 'lib/linked.js').unlink()
        outside = Path(self.tmp.name) / 'outside source'
        shutil.move(str(self.repo / 'lib'), outside)
        (self.repo / 'lib').symlink_to(outside, target_is_directory=True)
        self.assertIn('UNSUPPORTED_FILE lib/export.js', self.cli('check').stderr)
        self.success('check', '--staged')

    def test_custom_hooks_are_not_overwritten_or_partially_installed(self):
        hook = self.repo / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 0\n')
        before = hook.read_bytes()
        result = self.cli('install', '--scope', 'lib/**')
        self.assertEqual(result.returncode, 1)
        self.assertIn('HOOK_CONFLICT', result.stderr)
        self.assertEqual(hook.read_bytes(), before)
        self.assertFalse((self.repo / '.feature-docs').exists())
        hook.unlink()
        self.git('config', 'core.hooksPath', 'existing-hooks')
        result = self.cli('install', '--scope', 'lib/**')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), 'existing-hooks')

    def test_upgrade_preserves_scope_facts_and_refuses_modified_owned_assets(self):
        self.install()
        before = self.doc.read_bytes()
        self.success('install', '--scope', 'other/**')
        config = json.loads((self.repo / '.feature-docs/config.json').read_text())
        self.assertEqual(config['managed'], ['lib/**', 'other/**'])
        copy = Path(self.tmp.name) / 'new distribution.py'
        copy.write_bytes(TOOL.read_bytes() + b'\n# harmless newer distribution\n')
        self.success('install', tool=copy)
        self.assertEqual(self.doc.read_bytes(), before)
        self.success('check')
        owned = self.repo / '.feature-docs/hooks/pre-commit'
        owned.write_text(owned.read_text() + '# local customization\n')
        modified = owned.read_bytes()
        result = self.cli('install', tool=copy)
        self.assertEqual(result.returncode, 1)
        self.assertIn('ASSET_CONFLICT', result.stderr)
        self.assertEqual(owned.read_bytes(), modified)

    def test_missing_indexed_config_is_not_reinitialized_with_a_smaller_scope(self):
        self.install()
        self.git('add', '.feature-docs/config.json')
        config = self.repo / '.feature-docs/config.json'
        config.unlink()
        before = self.doc.read_bytes()
        result = self.cli('install', '--scope', 'other/**')
        self.assertEqual(result.returncode, 1)
        self.assertIn('MISSING_CONFIG', result.stderr)
        self.assertFalse(config.exists())
        self.assertEqual(self.doc.read_bytes(), before)

    def test_staged_config_deletion_does_not_turn_an_existing_project_into_a_fresh_install(self):
        self.baseline()
        config = self.repo / '.feature-docs/config.json'
        config.unlink()
        self.git('add', '.feature-docs/config.json')
        result = self.cli('install', '--scope', 'other/**')
        self.assertEqual(result.returncode, 1)
        self.assertIn('MISSING_CONFIG', result.stderr)
        self.assertFalse(config.exists())

    def test_dangling_config_link_is_not_replaced(self):
        control = self.repo / '.feature-docs'
        control.mkdir()
        config = control / 'config.json'
        config.symlink_to(Path(self.tmp.name) / 'nonexistent configuration')
        result = self.cli('install', '--scope', 'lib/**')
        self.assertEqual(result.returncode, 1)
        self.assertTrue(config.is_symlink())
        self.assertFalse((control / 'run').exists())

    def test_ignored_config_is_rejected_before_writing_any_assets(self):
        (self.repo / '.gitignore').write_text('*.json\n')
        result = self.cli('install', '--scope', 'lib/**')
        self.assertEqual(result.returncode, 1)
        self.assertIn('IGNORED_ASSET', result.stderr)
        self.assertFalse((self.repo / '.feature-docs/run').exists())

    def test_linked_feature_directory_is_not_accepted_or_changed(self):
        outside = Path(self.tmp.name) / 'project-owned external records'
        shutil.move(str(self.repo / 'docs/features'), outside)
        (self.repo / 'docs/features').symlink_to(outside, target_is_directory=True)
        before = (outside / 'export.md').read_bytes()
        result = self.cli('install', '--scope', 'lib/**')
        self.assertEqual(result.returncode, 1)
        self.assertEqual((outside / 'export.md').read_bytes(), before)
        self.assertFalse((self.repo / '.feature-docs/run').exists())


if __name__ == '__main__':
    unittest.main()

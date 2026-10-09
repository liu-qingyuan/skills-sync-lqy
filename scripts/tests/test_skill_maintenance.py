from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "skills" / "matt-lqy-core"
LEGACY = {
    "design-an-interface-lqy", "qa-lqy", "request-refactor-plan-lqy",
    "ubiquitous-language-lqy", "edit-article-lqy", "obsidian-vault-lqy",
    "resolving-merge-conflicts-lqy", "writing-great-skills-lqy",
}


def frontmatter(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


class SkillContractTests(unittest.TestCase):
    def test_original_personal_skills_remain_available(self) -> None:
        names = {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}
        self.assertTrue(LEGACY <= names)
        self.assertTrue({"clean", "simple", "ralph-plan-lqy", "handoff-out", "gitnexus", "mermaid-gate-lqy"} <= names)
        self.assertFalse({"chief-of-staff-lqy", "implement-spec-lqy", "setup-ts-deep-modules-lqy"} & names)

    def test_new_skills_have_matching_harness_invocation_policy(self) -> None:
        for name, explicit_only in (("pr-lqy", False), ("retro-lqy", True), ("writing-for-agents-lqy", False)):
            with self.subTest(skill=name):
                path = CORE / name
                skill = frontmatter(path / "SKILL.md")
                metadata = yaml.safe_load((path / "agents" / "openai.yaml").read_text())
                self.assertEqual(skill.get("disable-model-invocation", False), explicit_only)
                self.assertEqual(metadata.get("policy", {}).get("allow_implicit_invocation", True), not explicit_only)

    def test_ralph_stays_explicit_but_its_worker_can_load_implement(self) -> None:
        ralph = ROOT / "skills" / "lqy-local" / "ralph-plan-lqy"
        self.assertTrue(frontmatter(ralph / "SKILL.md")["disable-model-invocation"])
        self.assertFalse(frontmatter(CORE / "implement-lqy" / "SKILL.md").get("disable-model-invocation", False))
        template = (ralph / "templates" / "issue-backlog-prompt.md").read_text()
        self.assertIn("implement-lqy", template)

    def test_diagnosis_preserves_real_reproduction_inputs(self) -> None:
        skill = (CORE / "diagnosing-bugs-lqy" / "SKILL.md").read_text()
        for contract in ("仅在展示副本", "原始日志", "fixture", "真实凭据", "不新增安全依赖", "先向用户说明"):
            self.assertIn(contract, skill)
        self.assertNotIn("Call the Skill tool", skill)

    def test_setup_seed_matches_current_branch_contract(self) -> None:
        seed = (CORE / "setup-matt-pocock-skills-lqy" / "issue-tracker-github.md").read_text()
        default = next((line for line in seed.splitlines() if line.startswith("- 未指定 `Branch`")), "")
        self.assertIn("当前 attached branch", default)
        self.assertIn("remote upstream", default)
        self.assertNotIn("远程默认 branch 对应的本地主分支", default)
        self.assertIn("不带 `ready-for-agent`", seed)

    def test_glossary_is_the_single_root_source(self) -> None:
        self.assertTrue((ROOT / "GLOSSARY.md").is_file())
        self.assertFalse((ROOT / "CONTEXT.md").exists())
        domain = (CORE / "domain-modeling-lqy" / "SKILL.md").read_text()
        self.assertIn("CONTEXT.md", domain)  # existing projects retain their one configured source
        self.assertIn("GLOSSARY.md", domain)
        self.assertIn("同一份", domain)


class BaselineTranslationContractTests(unittest.TestCase):
    def test_baseline_preserves_source_invocation_contract(self) -> None:
        for profile in sorted((ROOT / "baselines" / "matt-zh").glob("*/*/LOCALIZATION.md")):
            match = re.search(r"Upstream path: `([^`]+)`", profile.read_text())
            self.assertIsNotNone(match, str(profile))
            source = frontmatter(ROOT / match.group(1) / "SKILL.md")
            translated = frontmatter(profile.parent / "SKILL.md")
            with self.subTest(skill=profile.parent.name):
                self.assertEqual(translated.get("disable-model-invocation", False), source.get("disable-model-invocation", False))
                if "argument-hint" in source:
                    self.assertIsInstance(translated.get("argument-hint"), str)
                    self.assertTrue(translated["argument-hint"].strip())

    def test_tracker_baseline_contains_updated_machine_commands(self) -> None:
        setup = ROOT / "baselines/matt-zh/matt-zh-core/setup-matt-pocock-skills-zh"
        github = (setup / "issue-tracker-github.md").read_text()
        self.assertIn("gh issue view <number> --json number,title,body,labels,comments", github)
        self.assertIn("gh issue create --parent <parent>", github)
        self.assertIn("gh issue edit <parent> --add-sub-issue <child>", github)
        self.assertIn("gh api --paginate", github)
        gitlab = (setup / "issue-tracker-gitlab.md").read_text()
        self.assertIn("glab issue list -O json", gitlab)
        self.assertIn("projects/:id/issues/<child-iid>/links", gitlab)
        local = (setup / "issue-tracker-local.md").read_text()
        self.assertIn(".scratch/<feature-slug>/spec.md", local)
        self.assertNotIn(".scratch/<feature-slug>/PRD.md", local)

    def test_report_template_preserves_upstream_code_and_css_tokens(self) -> None:
        source = (ROOT / "upstream/mattpocock/skills/engineering/improve-codebase-architecture/HTML-REPORT.md").read_text()
        code_blocks = re.findall(r"```[^\n]*\n(.*?)```", source, re.DOTALL)
        for path in (
            ROOT / "baselines/matt-zh/matt-zh-core/improve-codebase-architecture-zh/HTML-REPORT.md",
            CORE / "improve-codebase-architecture-lqy/HTML-REPORT.md",
        ):
            with self.subTest(path=str(path)):
                translated = path.read_text()
                self.assertEqual(re.findall(r"```[^\n]*\n(.*?)```", translated, re.DOTALL), code_blocks)
                self.assertIn("text-xs uppercase tracking-wider", translated)
                self.assertNotIn("track-wider", translated)


class RepositoryCheckCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        for name in ("skills", "upstream", "baselines", ".claude-plugin"):
            shutil.copytree(ROOT / name, self.repo / name, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        (self.repo / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts" / "check_matt_zh_skills.py", self.repo / "scripts")
        for name in ("README.md", "GLOSSARY.md", "CONTEXT.md"):
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, self.repo / name)

    def check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(self.repo / "scripts" / "check_matt_zh_skills.py")], text=True, capture_output=True, cwd=self.repo)

    def test_accepts_current_repository_without_a_user_system_validator(self) -> None:
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_conflicting_pi_and_codex_invocation_policies(self) -> None:
        metadata = self.repo / "skills" / "matt-lqy-core" / "retro-lqy" / "agents" / "openai.yaml"
        data = yaml.safe_load(metadata.read_text())
        data["policy"]["allow_implicit_invocation"] = True
        metadata.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invocation policy", result.stderr)

    def test_rejects_invalid_yaml_frontmatter(self) -> None:
        skill = self.repo / "skills" / "matt-lqy-core" / "pr-lqy" / "SKILL.md"
        skill.write_text("---\nname: pr-lqy\ndescription: broken: yaml\n---\nBody\n", encoding="utf-8")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frontmatter", result.stderr)

    def test_rejects_noninstallable_layers_in_marketplace(self) -> None:
        marketplace = self.repo / ".claude-plugin" / "marketplace.json"
        data = json.loads(marketplace.read_text())
        data["plugins"][0]["skills"].append("./upstream/mattpocock/skills/engineering/pr")
        marketplace.write_text(json.dumps(data), encoding="utf-8")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-installable", result.stderr)


if __name__ == "__main__":
    unittest.main()

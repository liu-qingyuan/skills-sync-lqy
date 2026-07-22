from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


class InstallationDocsTests(unittest.TestCase):
    def test_default_prompt_filters_parent_specs_before_the_gate(self) -> None:
        prompt = (SKILL_ROOT / "templates" / "issue-backlog-prompt.md").read_text(encoding="utf-8")

        self.assertIn('test("^\\\\s*Spec\\\\s*:"; "i")', prompt)
        self.assertIn("禁止调用 `run_ralph` 或 CLI 启动嵌套 Ralph", prompt)
        self.assertLess(prompt.index("--jq"), prompt.index("check_ready_issue_unblocked.py"))

    def test_run_ralph_is_the_default_execution_path(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        default_section = skill.split("## 默认执行", 1)[1].split("## CLI 回退", 1)[0]

        self.assertIn("Pi worker 默认", frontmatter)
        self.assertIn("templates/issue-backlog-prompt.md", skill)
        self.assertIn("只有用户明确要求", skill)
        self.assertIn("`PI_RUN_RALPH_WORKER=1`", skill)
        self.assertIn("有 `run_ralph` 工具时直接调用", default_section)
        self.assertIn("不要自动启动 CLI 重试", default_section)
        self.assertNotIn("Codex（默认）", skill)
        self.assertNotIn("--agent codex", skill)

    def test_pi_fallback_command_uses_one_run_project_trust(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        fallback_section = skill.split("## CLI 回退", 1)[1]
        pi_command = fallback_section.split("```bash", 1)[1].split("```", 1)[0]

        self.assertIn("--agent pi", pi_command)
        self.assertIn("--approve", pi_command)
        self.assertIn("--no-questions", pi_command)
        self.assertIn("    -- \\\n    --approve", pi_command)
        self.assertNotIn("--no-allow-all", pi_command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", pi_command)
        self.assertIn("不提供 sandbox", fallback_section)

    def test_branch_worker_contract_is_published(self) -> None:
        expected_fragments = {
            REPO_ROOT / "README.md": (
                "## Git-bound Ralph 工作流",
                "Pi worker 是默认选择",
                "`run_ralph` 工具",
                "完全忽略 assignees",
                "PR 不进入 Ralph issue backlog",
                "不会自动合并、删除 branch 或清理 worktree",
            ),
            SKILL_ROOT / "agents" / "openai.yaml": (
                "branch-aware",
                "Pi worker",
                "run_ralph",
            ),
            SKILL_ROOT / "LOCALIZATION.md": (
                "端到端验证",
                "不使用 assignee claim",
                "不自动清理 branch/worktree",
                "Dirty recovery",
                ".codex/config.toml",
                "Pi + `run_ralph` 默认",
            ),
            REPO_ROOT / "skills" / "matt-lqy-core" / "to-tickets-lqy" / "SKILL.md": (
                "由 agent 完成可确认的改动",
                "commit/push 后重跑 publisher",
                "禁止 stash",
            ),
            REPO_ROOT / "skills" / "matt-lqy-core" / "triage-lqy" / "SKILL.md": (
                "由 agent 完成可确认的改动",
                "commit/push 后重跑 publisher",
                "禁止 stash",
            ),
            REPO_ROOT
            / "skills"
            / "matt-lqy-core"
            / "setup-matt-pocock-skills-lqy"
            / "issue-tracker-github.md": (
                "branch 内按 issue number 升序",
                "当前 branch 没有可领取 Ticket",
                "malformed Git 契约",
            ),
        }

        for path, fragments in expected_fragments.items():
            text = path.read_text(encoding="utf-8")
            for fragment in fragments:
                with self.subTest(path=path, fragment=fragment):
                    self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

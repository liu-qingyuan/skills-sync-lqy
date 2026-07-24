from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


def lqy_skill_file(name: str) -> Path:
    source = REPO_ROOT / "skills" / "matt-lqy-core" / name / "SKILL.md"
    return source if source.exists() else SKILL_ROOT.parent / name / "SKILL.md"


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
        self.assertIn("直接调用即启动", skill)
        self.assertIn("明确要求只规划或不运行时除外", skill)
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
        if not (REPO_ROOT / "README.md").exists():
            self.skipTest("requires the source checkout")

        expected_fragments = {
            REPO_ROOT / "README.md": (
                "## Git-bound Ralph 工作流",
                "直接调用 `$ralph-plan-lqy` 即以 Pi 启动",
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
                "直接调用即用 Pi + `run_ralph` 执行",
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

    def test_review_budget_is_consistent_across_workflow(self) -> None:
        prompt = (SKILL_ROOT / "templates" / "issue-backlog-prompt.md").read_text(encoding="utf-8")
        implement = lqy_skill_file("implement-lqy").read_text(encoding="utf-8")
        review_path = lqy_skill_file("code-review-lqy")
        review = review_path.read_text(encoding="utf-8")

        for text in (prompt, implement, review):
            with self.subTest(document=text[:80]):
                self.assertIn("broad", text.lower())
                self.assertIn("focused closure", text.lower())
                self.assertIn("4", text)
                self.assertIn("第三轮", text)
                self.assertIn("GitNexus", text)

        for text in (prompt, review):
            self.assertIn("max_turns: 6", text)
            self.assertIn("max_turns: 3", text)

        self.assertIn("resume 原来的 agents", review)
        self.assertIn("失败调用也计入", review)
        self.assertIn("替代 reviewer", review)
        self.assertIn("不得重扫完整 diff", review)
        self.assertIn("optional hardening", review)
        self.assertNotIn("Fowler", review)
        self.assertFalse((review_path.parent / "references" / "fowler-smells.md").exists())
        self.assertIn("超出一个新上下文", implement)
        self.assertIn("ready-for-agent` 替换为 `needs-triage", prompt)
        self.assertIn("不要用更多 reviewer", prompt)


if __name__ == "__main__":
    unittest.main()

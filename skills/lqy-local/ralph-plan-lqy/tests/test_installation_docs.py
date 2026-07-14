from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


class InstallationDocsTests(unittest.TestCase):
    def test_branch_worker_contract_is_published(self) -> None:
        expected_fragments = {
            REPO_ROOT / "README.md": (
                "## Git-bound Ralph 工作流",
                "完全忽略 assignees",
                "PR 不进入 Ralph issue backlog",
                "不会自动合并、删除 branch 或清理 worktree",
            ),
            SKILL_ROOT / "agents" / "openai.yaml": (
                "branch-aware",
                "worktree lock",
            ),
            SKILL_ROOT / "LOCALIZATION.md": (
                "端到端验证",
                "不使用 assignee claim",
                "不自动清理 branch/worktree",
                "Dirty recovery",
            ),
            REPO_ROOT / "skills" / "matt-lqy-core" / "to-tickets-lqy" / "SKILL.md": (
                "不要把清理工作交给用户",
                "不要改用临时 clone",
                "按 coherent commits 提交和正常 push",
            ),
            REPO_ROOT / "skills" / "matt-lqy-core" / "triage-lqy" / "SKILL.md": (
                "不要要求用户手工清理",
                "不要改用临时 clone",
                "按 coherent commits 提交并正常 push",
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

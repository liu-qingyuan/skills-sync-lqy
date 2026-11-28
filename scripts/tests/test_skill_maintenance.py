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
    def test_codebase_design_expresses_contracts_and_change_costs(self) -> None:
        skill = (CORE / "codebase-design-lqy/SKILL.md").read_text()
        for contract in ("Contract（契约）", "Preconditions", "Postconditions", "Invariants",
                         "Change Amplification", "Cognitive Load", "Unknown Unknowns",
                         "Orthogonality", "保持 Contract 不变", "Pull Complexity Downward",
                         "Define Errors Out of Existence", "不规定固定时间比例"):
            self.assertIn(contract, skill)
        self.assertNotRegex(skill, r"10%|20%|坚决禁止.*链式调用")

    def test_design_review_requires_evidence_not_syntactic_or_storage_bans(self) -> None:
        review = (CORE / "codebase-design-lqy/DESIGN-REVIEW.md").read_text()
        for contract in ("Tactical Patch", "Logical Cohesion", "Train Wreck / Demeter",
                         "Common Environment Coupling", "链长不等于违规", "fluent Interface",
                         "共用数据库本身不证明违规", "不要仅为缩短链条新增透传方法"):
            self.assertIn(contract, review)
        self.assertIn("Red Flag 是调查信号，不是重构结论", review)

    def test_deepening_preserves_contracts_and_unique_test_coverage(self) -> None:
        guide = (CORE / "codebase-design-lqy/DEEPENING.md").read_text()
        alternatives = (CORE / "codebase-design-lqy/DESIGN-IT-TWICE.md").read_text()
        for contract in ("加深前确认 Contract", "不擅自加强前置条件或削弱后置条件",
                         "仅删除已被新测试替代的", "Adapter 的独立合同测试"):
            self.assertIn(contract, guide)
        self.assertIn("前置条件、后置条件", alternatives)
        self.assertNotIn("总是可以深化", guide)
        self.assertNotIn("只要替身存在，就可以深化", guide)

    def test_original_personal_skills_remain_available(self) -> None:
        names = {p.parent.name for p in (ROOT / "skills").glob("*/*/SKILL.md")}
        self.assertTrue(LEGACY <= names)
        self.assertTrue({"clean", "simple", "ralph-plan-lqy", "handoff-out", "gitnexus", "mermaid-gate-lqy"} <= names)
        self.assertFalse({"implement-spec-lqy", "setup-ts-deep-modules-lqy"} & names)

    def test_factory_and_chief_are_separate_explicit_installable_skills(self) -> None:
        base = ROOT / "skills/matt-lqy-in-progress"
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        listed = {name for plugin in marketplace["plugins"] for name in plugin["skills"]}
        for name in ("software-factory-lqy", "chief-of-staff-lqy"):
            with self.subTest(skill=name):
                path = base / name
                self.assertTrue((path / "SKILL.md").is_file(), f"missing {name}")
                self.assertIn(f"./skills/matt-lqy-in-progress/{name}", listed)
                self.assertTrue(frontmatter(path / "SKILL.md")["disable-model-invocation"])
                metadata = yaml.safe_load((path / "agents/openai.yaml").read_text())
                self.assertFalse(metadata["policy"]["allow_implicit_invocation"])
        factory = base / "software-factory-lqy"
        source = ROOT / "upstream/mattpocock/skills/in-progress/software-factory"
        baseline = ROOT / "baselines/matt-zh/matt-zh-in-progress/software-factory-zh"
        for path in source.glob("*.md"):
            if path.name in {"SKILL.md", "UPSTREAM_MATTOCOCK.md"}:
                continue
            with self.subTest(support=path.name):
                self.assertEqual((factory / path.name).read_bytes(), (baseline / path.name).read_bytes())
        chief = (base / "chief-of-staff-lqy/SKILL.md").read_text()
        for dependency in ("retro-lqy", "to-spec-lqy", "to-tickets-lqy", "implement-spec-subagent-lqy"):
            self.assertIn(dependency, chief)
        self.assertIn("按当前 skills 列表", chief)
        self.assertNotIn("Call the Skill tool", chief)
        self.assertNotIn("../retro/", chief)

    def test_new_skills_have_matching_harness_invocation_policy(self) -> None:
        for name, explicit_only in (("pr-lqy", False), ("retro-lqy", True), ("writing-for-agents-lqy", False)):
            with self.subTest(skill=name):
                path = CORE / name
                skill = frontmatter(path / "SKILL.md")
                metadata = yaml.safe_load((path / "agents" / "openai.yaml").read_text())
                self.assertEqual(skill.get("disable-model-invocation", False), explicit_only)
                self.assertEqual(metadata.get("policy", {}).get("allow_implicit_invocation", True), not explicit_only)

    def test_retro_preserves_standalone_mode_and_authorized_chief_override(self) -> None:
        retro = (CORE / "retro-lqy/SKILL.md").read_text()
        for contract in ("chief-of-staff-lqy", "独立运行", "最后一步", "复盘只提出建议"):
            self.assertIn(contract, retro)
        mechanics = (CORE / "writing-for-agents-lqy/SKILL-MECHANICS.md").read_text()
        self.assertIn("chief-of-staff-lqy", mechanics)
        self.assertIn("已授权", mechanics)
        self.assertTrue(frontmatter(CORE / "retro-lqy/SKILL.md")["disable-model-invocation"])

    def test_ralph_stays_explicit_but_its_worker_can_load_implement(self) -> None:
        ralph = ROOT / "skills" / "lqy-local" / "ralph-plan-lqy"
        self.assertTrue(frontmatter(ralph / "SKILL.md")["disable-model-invocation"])
        self.assertFalse(frontmatter(CORE / "implement-lqy" / "SKILL.md").get("disable-model-invocation", False))
        template = (ralph / "templates" / "issue-backlog-prompt.md").read_text()
        self.assertIn("implement-lqy", template)

    def test_subagent_spec_entry_is_explicit_and_harness_neutral(self) -> None:
        path = CORE / "implement-spec-subagent-lqy"
        self.assertTrue((path / "SKILL.md").is_file(), "missing optional subagent implementation entry")
        self.assertTrue(frontmatter(path / "SKILL.md")["disable-model-invocation"])
        metadata = yaml.safe_load((path / "agents/openai.yaml").read_text())
        self.assertFalse(metadata["policy"]["allow_implicit_invocation"])
        skill = (path / "SKILL.md").read_text()
        for contract in ("当前会话实际可用", "独立 worktree", "不假设派发自动隔离", "不再拆派实施", "不等待整批"):
            self.assertIn(contract, skill)
        descriptions = (
            skill,
            metadata["interface"]["short_description"],
            metadata["interface"]["default_prompt"],
            (path / "LOCALIZATION.md").read_text(),
            (CORE / "code-review-lqy/SKILL.md").read_text(),
            (ROOT / "docs/architecture/spec-implementation.md").read_text(),
            (ROOT / "docs/features/ticket-implementation.md").read_text(),
        )
        for text in descriptions:
            for implementation_detail in ("Codex", "Pi", "Claude", "Gemini", "Kimi", "spawn_agent",
                                          "run_in_background", "isolation:", "Skill tool"):
                self.assertNotIn(implementation_detail, text)

    def test_new_dispatches_start_fresh_without_replacing_local_execution_rules(self) -> None:
        for path in (
            CORE / "code-review-lqy/SKILL.md",
            CORE / "codebase-design-lqy/DESIGN-IT-TWICE.md",
            CORE / "improve-codebase-architecture-lqy/SKILL.md",
            CORE / "wayfinder-lqy/SKILL.md",
            CORE / "implement-spec-subagent-lqy/SKILL.md",
        ):
            with self.subTest(path=str(path)):
                self.assertIn("全新上下文", path.read_text())
        entry = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        self.assertIn("每个 Ticket 派一个新的实施 agent", entry)
        self.assertIn("收尾修复", entry)
        review = (CORE / "code-review-lqy/SKILL.md").read_text()
        self.assertIn("并行 resume 原来的 agents", review)
        self.assertIn("总 review Agent 调用上限为 4", review)
        wayfinder = (CORE / "wayfinder-lqy/SKILL.md").read_text()
        self.assertNotIn("skills 进行对话，一次一个问题", wayfinder)

    def test_subagent_entry_resolves_spec_from_context(self) -> None:
        skill = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        self.assertIn("优先从当前对话确定已批准的 Spec", skill)
        self.assertIn("不能唯一确定时才询问", skill)
        self.assertNotIn("$implement-spec-subagent-lqy <", (ROOT / "README.md").read_text())

    def test_subagent_workspace_choice_requires_a_stable_shared_snapshot(self) -> None:
        entry = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        self.assertIn("不相交的小任务可共享 worktree", entry)
        self.assertIn("独立提交或滚动整合时优先独立 worktree", entry)
        self.assertIn("全部结束或已协调暂停", entry)
        self.assertNotIn("每个 worker 使用独立 worktree", entry)
        review = (CORE / "code-review-lqy/SKILL.md").read_text()
        self.assertIn("当前 Ticket 或明确授权的交付批次", review)
        self.assertIn("暂停该工作区的并发写入", review)
        self.assertIn("其它工作不混入", review)

    def test_delegation_passes_authorization_and_allows_bounded_readonly_help(self) -> None:
        entry = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        self.assertIn("也可由承接授权的主流程派发", entry)
        self.assertIn("无需逐票重复请求授权", entry)
        worker = (CORE / "implement-lqy/SKILL.md").read_text()
        for contract in ("只读查证", "不再拆派实施", "不绕过 review 预算", "共享工作区不操作 Git/index"):
            self.assertIn(contract, worker)
        self.assertNotIn("worker 不再派发 agents", worker)

    def test_review_report_budget_preserves_finding_evidence(self) -> None:
        review = (CORE / "code-review-lqy/SKILL.md").read_text()
        self.assertNotIn("最多 250 字", review)
        for contract in ("默认以 1000 字以内为目标", "必要证据较多时可更长", "文件位置", "证据", "影响"):
            self.assertIn(contract, review)
        self.assertIn("最多 6 轮", review)
        self.assertIn("最多 3 轮", review)
        provenance = (CORE / "code-review-lqy/LOCALIZATION.md").read_text()
        self.assertIn("Under 400 words", provenance)
        self.assertIn("local controls, not upstream requirements", provenance)

    def test_subagent_workers_defer_delivery_to_the_integrator(self) -> None:
        implementation = (CORE / "implement-lqy/SKILL.md").read_text()
        self.assertIn("受委派 worker", implementation)
        self.assertIn("私有分支仅本地 commit", implementation)
        self.assertIn("Review、push 与 issue 收口由整合者执行", implementation)
        entry = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        for contract in ("父子三字段必须一致", "集成 worktree 运行", "check_ready_issue_unblocked.py",
                         "1/3", "串行合并", "review fixed point", "不能释放依赖", "不等待整批"):
            self.assertIn(contract, entry)

    def test_planning_requires_sufficient_scope_instead_of_exhaustive_output(self) -> None:
        spec = (CORE / "to-spec-lqy/SKILL.md").read_text()
        tickets = (CORE / "to-tickets-lqy/SKILL.md").read_text()
        for skill in (spec, tickets):
            self.assertIn("最小充分", skill)
        for contract in ("不以篇幅或故事数量为目标", "关键业务假设", "停止扩写"):
            self.assertIn(contract, spec)
        for removed in ("一份很长的编号用户故事列表", "这份用户故事列表应该非常广"):
            self.assertNotIn(removed, spec)
        for contract in ("不按用户故事、章节或技术层机械拆票", "实际涉及的层", "不复制整份 spec"):
            self.assertIn(contract, tickets)
        for removed in ("贯穿每一层", "任何 prefactoring 都应该先完成"):
            self.assertNotIn(removed, tickets)

    def test_planning_bounds_business_claims_by_inputs_and_configuration(self) -> None:
        for name, boundary in (
            ("to-spec-lqy", "技术验证通过不等于业务验收或可上线"),
            ("to-tickets-lqy", "技术跑通不等于业务或上线验收"),
        ):
            skill = (CORE / name / "SKILL.md").read_text()
            with self.subTest(skill=name):
                for contract in ("代表性", "配置", "上线", "未验证", boundary):
                    self.assertTrue(contract in skill, f"{name} 缺少约束：{contract}")

    def test_planning_exposes_parallelism_without_starting_execution(self) -> None:
        spec = (CORE / "to-spec-lqy/SKILL.md").read_text()
        tickets = (CORE / "to-tickets-lqy/SKILL.md").read_text()
        self.assertIn("合理并行", spec)
        for contract in ("合理并行", "不按编号或发布顺序制造依赖", "共享写入", "实际文件与资源"):
            self.assertIn(contract, tickets)
        self.assertIn("implement-spec-subagent-lqy", tickets)
        self.assertIn("发布后停止", tickets)
        self.assertIn("不自动实施或启动循环", tickets)
        router = (CORE / "ask-matt-lqy/SKILL.md").read_text()
        self.assertIn("Ralph 是默认", router)
        self.assertIn("implement-spec-subagent-lqy", router)

    def test_grilling_uses_whole_frontier_and_fresh_fact_finding(self) -> None:
        skill = (CORE / "grilling-lqy/SKILL.md").read_text()
        for contract in ("一轮问完整个前沿", "全新上下文", "不继承当前对话", "只有依赖它的下游问题"):
            self.assertIn(contract, skill)
        self.assertNotIn("默认维持一次一个问题", skill)
        self.assertNotIn("不为每个事实强制创建 subagent", skill)

    def test_planning_skills_preserve_phase_authorization(self) -> None:
        contracts = {
            "setup-matt-pocock-skills-lqy": (
                "等待用户明确调用", "确认规划不等于授权实施",
                "规划阶段的子 agent 仅可只读查证或审查",
            ),
            "grilling-lqy": ("确认只表示共识成立，不授权实施或启动后续 skill", "确认后交还控制权"),
            "to-spec-lqy": (
                "最多启动一个只读 review agent", "只返回审查意见，不修改文件或实施",
                "完成后只提醒用户下一步调用 `$to-tickets-lqy`，然后停止",
            ),
            "to-tickets-lqy": (
                "最多启动一个只读 review agent", "只返回审查意见，不修改文件或实施",
                "只处理本阶段已授权的改动", "不得借此实施 Ticket 或接手其它业务改动",
                "发布后停止", "不自动实施或启动循环",
            ),
        }
        for name, expected in contracts.items():
            skill = (CORE / name / "SKILL.md").read_text()
            if name == "setup-matt-pocock-skills-lqy":
                skill = skill.split("```markdown\n", 1)[1].split("\n```", 1)[0]
            with self.subTest(skill=name):
                for phrase in expected:
                    self.assertIn(phrase, skill)
        self.assertNotIn("等用户确认后才实施", (CORE / "grilling-lqy" / "SKILL.md").read_text())

    def test_diagnosis_preserves_real_reproduction_inputs(self) -> None:
        skill = (CORE / "diagnosing-bugs-lqy" / "SKILL.md").read_text()
        for contract in ("仅在展示副本", "原始日志", "fixture", "真实凭据", "不新增安全依赖", "先向用户说明"):
            self.assertIn(contract, skill)
        self.assertNotIn("Call the Skill tool", skill)

    def test_github_operations_keep_comments_targets_and_open_blockers(self) -> None:
        for path in (
            CORE / "setup-matt-pocock-skills-lqy/issue-tracker-github.md",
            ROOT / "docs/agents/issue-tracker.md",
        ):
            with self.subTest(path=str(path)):
                text = path.read_text()
                self.assertNotIn('gh issue close <number> --comment', text)
                self.assertIn('gh issue comment <number> --body', text)
                self.assertIn('gh issue close <number>', text)
                self.assertIn('gh repo view --json nameWithOwner', text)
                self.assertIn('gh issue edit <child> --add-blocked-by <blocker>', text)
                self.assertIn('issue_dependencies_summary.blocked_by', text)
                self.assertIn('select(.state == "OPEN")', text)
                self.assertIn('## Blocked by', text)
                self.assertIn('## Git', text)

    def test_setup_checks_remote_without_initializing_or_migrating(self) -> None:
        setup = (CORE / "setup-matt-pocock-skills-lqy/SKILL.md").read_text()
        self.assertIn("没有 GitHub remote 时停止", setup)
        self.assertIn("gh repo view --json nameWithOwner", setup)
        self.assertIn("不得自动迁移或双写术语表", setup)
        self.assertNotIn("git init", setup)
        self.assertNotIn("git remote add", setup)

    def test_setup_seed_matches_current_branch_contract(self) -> None:
        seed = (CORE / "setup-matt-pocock-skills-lqy" / "issue-tracker-github.md").read_text()
        default = next((line for line in seed.splitlines() if line.startswith("- 未指定 `Branch`")), "")
        self.assertIn("当前 attached branch", default)
        self.assertIn("remote upstream", default)
        self.assertNotIn("远程默认 branch 对应的本地主分支", default)
        self.assertIn("不带 `ready-for-agent`", seed)

    def test_feature_gate_has_one_payload_and_short_workflow_pointers(self) -> None:
        setup = CORE / "setup-matt-pocock-skills-lqy"
        self.assertTrue((setup / "scripts/feature_docs.py").is_file())
        self.assertTrue((setup / "templates/feature.md").is_file())
        self.assertEqual((setup / "feature-docs.md").read_bytes(),
                         (ROOT / "docs/agents/feature-docs.md").read_bytes())
        self.assertIn("### Feature records", (ROOT / "AGENTS.md").read_text())
        implementation = (CORE / "implement-lqy/SKILL.md").read_text()
        for pointer in ("docs/agents/feature-docs.md", "check --staged", "check --ref HEAD"):
            self.assertIn(pointer, implementation)
        self.assertIn("不替代测试", implementation)

    def test_feature_gate_defaults_to_enabled_without_an_activation_marker(self) -> None:
        setup = (CORE / "setup-matt-pocock-skills-lqy/SKILL.md").read_text()
        policy = (CORE / "setup-matt-pocock-skills-lqy/feature-docs.md").read_text()
        self.assertIn("默认开启", setup)
        self.assertIn("不授权业务实施或启动 Ralph", setup)
        for contract in ("不需要单独激活或授权标记", "旧版“未启用”不等于明确关闭",
                         "不创建虚假能力记录、不安装 hooks", "明确关闭决定优先"):
            self.assertIn(contract, policy)
        self.assertNotIn("待启用（已授权）", setup + policy)

    def test_first_capability_delivery_bootstraps_gate_without_prior_setup(self) -> None:
        implementation = (CORE / "implement-lqy/SKILL.md").read_text()
        entry = (CORE / "implement-spec-subagent-lqy/SKILL.md").read_text()
        policy = (CORE / "setup-matt-pocock-skills-lqy/feature-docs.md").read_text()
        for contract in ("默认开启", "读取已安装 setup skill 的", "进入双轴 review 前",
                         "单票交付者或整合者", "项目明确关闭"):
            self.assertIn(contract, implementation)
        self.assertIn("implement-lqy` 的“Feature 当前事实”", entry)
        self.assertIn("由整合者处理默认首次启用", entry)
        for contract in ("不执行完整 setup、不修改 GitHub 标签", "worker 只交回",
                         "未启用（冲突）", "只读调查或仅同步 skills 不安装 hooks"):
            self.assertIn(contract, policy)
        self.assertNotIn("待启用（已授权）", implementation)
        self.assertNotIn("无延后授权", implementation)

    def test_failed_initial_validation_defers_installation_and_workers_wait(self) -> None:
        policy = (CORE / "setup-matt-pocock-skills-lqy/feature-docs.md").read_text()
        self.assertIn("尚无真实能力或业务测试未通过时暂缓", policy)
        self.assertIn("仅已启用项目的 worker 再执行", policy)
        self.assertIn("待启用项目的 worker 只交回就绪证据", policy)

    def test_installed_skill_sync_keeps_feature_data_and_carries_portable_tool(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project sync ") as directory:
            project = Path(directory)
            installed = project / ".agents/skills/setup-matt-pocock-skills-lqy"
            installed.mkdir(parents=True)
            (installed / "SKILL.md").write_text(
                "---\nname: setup-matt-pocock-skills-lqy\ndescription: old installed version\n---\n")
            record = project / "docs/features/existing.md"
            record.parent.mkdir(parents=True)
            record.write_text("项目自有事实，不应随 skills 升级覆盖。\n")
            before = record.read_bytes()
            policy = project / "docs/agents/feature-docs.md"
            policy.parent.mkdir(parents=True)
            policy.write_text("# Feature 记录\n\n## 当前启用状态\n未启用。\n")
            policy_before = policy.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/sync_installed_project_skills.py"),
                                     str(project)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(policy.read_bytes(), policy_before)
            self.assertFalse((project / ".feature-docs").exists())
            tool = installed / "scripts/feature_docs.py"
            self.assertEqual(tool.read_bytes(), (CORE / "setup-matt-pocock-skills-lqy/scripts/feature_docs.py").read_bytes())
            result = subprocess.run(["git", "-C", str(project), "init", "-b", "main"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([sys.executable, str(tool), "--repo", str(project), "install", "--scope", "lib/**"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / ".feature-docs/tool.py").is_file())
            self.assertEqual(record.read_bytes(), before)

    def test_glossary_relationships_and_parent_titles_are_documented(self) -> None:
        glossary = (CORE / "domain-modeling-lqy/GLOSSARY-FORMAT.md").read_text()
        for contract in ("**Order**", "**Customer**", "关系", "加粗"):
            self.assertIn(contract, glossary)
        tickets = (CORE / "to-tickets-lqy/SKILL.md").read_text()
        self.assertIn("父 issue 的标题", tickets)
        self.assertIn("标题 — #编号", tickets)
        self.assertIn("先单独发表评论", tickets)

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
        for command in ("gh issue edit <child> --add-blocked-by <blocker>",
                        'select(.state == "OPEN")', "gh repo view --json nameWithOwner"):
            self.assertIn(command, github)
        self.assertNotIn('gh issue close <number> --comment', github)
        gitlab = (setup / "issue-tracker-gitlab.md").read_text()
        self.assertIn("glab issue list -O json", gitlab)
        self.assertIn("projects/:id/issues/<child-iid>/links", gitlab)
        self.assertIn("glab mr list -O json", gitlab)
        self.assertIn("glab issue create --linked-issues <map> --link-type relates_to", gitlab)
        self.assertIn("glab api projects/:id/issues/<map>/links", gitlab)
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

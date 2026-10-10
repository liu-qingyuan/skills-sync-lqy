# skills-sync-lqy

我的 Pi / Codex Skills 仓库。目标是：

1. 同步 Matt Pocock 上游英文原版 skills，目录结构尽量跟上游一致。
2. 维护一套 `-zh` 中文本地化 baseline，作为从官方英文上游合并变化的中间层。
3. 维护一套当前对外安装的 `-lqy` 个人版 Matt skills。
4. 保留我自己的本地 skills，并用独立分类跟上游区分。
5. 通过一个简洁命令交互安装：

```bash
npx skills@latest add liu-qingyuan/skills-sync-lqy
```

不需要先 clone 本仓库；`npx skills` 会自己从 GitHub 拉取并让你交互选择要安装的 skills 和目标 agent。

## Quickstart

运行：

```bash
npx skills@latest add liu-qingyuan/skills-sync-lqy
```

然后在交互界面里选择你要的 skills。

如果你选择 Matt Pocock LQY 工作流相关 skills，建议同时选择并先运行 Codex skill：

```text
$setup-matt-pocock-skills-lqy
```

它只在用户显式调用时应用 LQY 默认值：GitHub Issues-only、补齐缺失的五个标准 triage labels、单领域术语表（新项目默认 `GLOSSARY.md`，旧项目保留既有权威路径）、中文输出、根目录 `AGENTS.md`，以及按真实能力试用的 Feature 记录门禁。不会覆盖项目记录/自定义 hooks、删除已有标签或自动启动 Ralph。需要自定义时先修改项目契约；英文 mirror 和中文 baseline 是维护材料，不在默认安装层自动执行。某些 agent 可能把同一个 skill 写成 `/setup-matt-pocock-skills-lqy`；在 Codex 里优先使用 `$setup-matt-pocock-skills-lqy`。

如果只安装我的本地 skills，例如 `clean`、`simple`、`gitnexus`、`handoff-out`，通常安装后即可使用。

安装后如果当前 Codex 会话没有自动加载新 skill，重启 Codex。

## 分类

本仓库把“可安装 skills”和“维护 baseline / 上游同步源”分开。当前 `npx skills@latest add liu-qingyuan/skills-sync-lqy` 展示的是 Matt `*-lqy` 层和本地/精选 skills，不展示官方英文 upstream，也不展示 `*-zh` baseline：

```text
skills/                    # 只放 npx 安装器应该展示的版本
  matt-lqy-core/           # Matt Pocock LQY 版：engineering + productivity
  matt-lqy-personal/       # Matt Pocock LQY 版：personal
  matt-lqy-misc/           # Matt Pocock LQY 版：misc
  matt-lqy-in-progress/    # Matt Pocock LQY 版：in-progress
  matt-lqy-deprecated/     # Matt Pocock LQY 版：deprecated
  amis-ui/                 # AMIS UI 相关：设计变量、Figma 还原等
  lqy-local/               # 我自己写/优化并长期使用的 skills
  lqy-curated/             # 我从外部素材整理/改造后维护的 skills

baselines/matt-zh/          # Matt 中文 baseline，只用于维护和对比，不参与安装展示
  matt-zh-core/
  matt-zh-personal/
  matt-zh-misc/
  matt-zh-in-progress/
  matt-zh-deprecated/

upstream/mattpocock/skills/ # Matt Pocock 官方英文上游镜像，只用于同步，不参与安装展示
  engineering/
  productivity/
  personal/
  misc/
  in-progress/
  deprecated/
```

`npx skills@latest` 的交互列表会按 `.claude-plugin/marketplace.json` 里的分组显示：

- `Matt Pocock LQY Core`：当前可安装的个人版主力层，合并 Engineering + Productivity。
- `AMIS UI`：AMIS UI / Figma 相关。
- `LQY Local`：我自己写/优化的本地 skills。
- `LQY Curated`：我整理/改造后维护的通用 skills。
- `Matt Pocock LQY Personal / Misc / In Progress / Deprecated`

## 重要区分

- `upstream/mattpocock/skills/productivity/handoff`：Matt Pocock 上游原版 `handoff`。
- `baselines/matt-zh/matt-zh-core/handoff-zh`：中文 baseline，用于合并上游变化和对比。
- `skills/matt-lqy-core/handoff-lqy`：当前安装器展示的 Matt LQY 版。
- `skills/lqy-local/handoff-out`：我的本地改版，用来输出可复制的交接 prompt，不写临时文件、不修改 workspace。

以后如果某个 Matt 上游 skill 被我改造，不要直接覆盖上游路径；中文 baseline 放到 `baselines/matt-zh/matt-zh-*/*-zh`，当前可安装个人版放到 `skills/matt-lqy-*/*-lqy`，独立本地改版放到 `skills/lqy-local/` 或 `skills/lqy-curated/`，例如 `handoff-out`。

## 本地 skills

### Lqy Local

- `clean`：锁定行为与范围后，清理死代码、重复、脆弱回退、无意义包装和过度抽象，并参考 `$simple` 与 `$codebase-design-lqy` 选择最小完整修复。
- `simple`：简化代码、文档、prompt、配置、计划或规格，同时保留意图和必要行为。
- `gitnexus`：GitNexus 代码图谱工具路由与使用指南。
- `mermaid-gate-lqy`：统一判断 Ticket/实现是否需要 Mermaid 设计图；需要时要求架构/调用关系图、时序图、状态图、类图各包含当前和目标两版。
- `ralph-plan-lqy`：规划或启动 Open Ralph + GitHub issue backlog 循环，Pi worker 默认；Pi 会话优先使用 `run_ralph` 工具，内置 blocker gate，并只处理 `ready-for-agent` issue。
- `handoff-out`：我的交接 prompt 输出版。

## Feature 微文档与本地门禁

复用 setup / implement，不新增 skill 或 CI 服务。项目记录放 `docs/features/`；先读自动索引，再按需展开能力的当前行为、限制和源码/测试入口。工具约定见 [docs/agents/feature-docs.md](docs/agents/feature-docs.md)。

本仓库先纳管 setup、单 Ticket 实施、已安装 skills 同步三个能力，不为全部 53 个 skills 补重复文档；范围由索引明确显示。

```bash
./.feature-docs/run install  # clone 后恢复本地 hooks；Git 不复制 hook 配置
./.feature-docs/run list
./.feature-docs/run check
python3 -m unittest discover -s skills/matt-lqy-core/setup-matt-pocock-skills-lqy/tests
```

提交前查真实 index，推送前查实际 tip；`review --confirm` 只刷新已复核事实的版本基准，不自动暂存或替代业务测试。已有 hooks/修改过的安装资产冲突则停止；新项目显式调用 setup，工具升级保留范围与业务记录。本地 hooks 可绕过，未纳管目录不宣称受保护。

## Git-bound Ralph 工作流

**Ralph 是批量实施标准，`implement-lqy` 仍只处理一个 Ticket。** 说“以 Ralph 为标准”或同步技能不是启动授权；循环只在显式调用或启动请求后运行。

`ralph-plan-lqy` 把一个 Ralph worker 绑定到一个 Git branch 和对应 worktree。进入 backlog 的具体 Ticket 必须是 open + `ready-for-agent`，正文最后包含固定的 `## Git` 契约；worker 只消费 `Branch` 精确匹配当前 attached branch 的 Ticket，并在 branch 内按 issue number 升序选择第一个通过 eligibility gate 的任务。

直接调用 `$ralph-plan-lqy` 即以 Pi 启动；明确要求只规划时除外。无 `run_ralph` 时回退 locked Pi CLI，子 iteration 禁止嵌套。

多 branch 并行来自多个独立 worktrees 中的串行 workers。每个 worker 通过 `.ralph/worker.lock` 持有 OS file lock，并使用自己 worktree 内的 `.ralph/` 状态、未提交修改和 Git 历史。同一 worktree 的第二个 worker 会被拒绝，不同 worktree 不互相阻塞。

- Ralph publication 和 eligibility 完全忽略 assignees，不读取、不修改，也不使用 assignee claim。
- PR 不进入 Ralph issue backlog；PR 保留 GitHub 原生 head/base 和正常 review 流程。
- 当前 branch 没有可领取 Ticket 时，只结束该 branch worker；其他 branch 的 backlog 不阻止它完成。
- 完成后不会自动合并、删除 branch 或清理 worktree；这些操作由维护者显式决定。

### AMIS UI

- `amis-test`：运行、检查和复现 Amis macOS 自动化，并验证保留的 `.xcresult`。
- `amis-variables`：把当前 `Amis V1.0 色卡` 的 48 个 Figma 语义变量映射到 SwiftUI tokens。
- `amis-pixel-implementation`：基于 Figma 在 Amis macOS SwiftUI 中实现并验证视觉、交互和无障碍契约。

### Lqy Curated

- `c4-architecture`
- `mermaid-visualizer`
- `pact`
- `playwright-ci`
- `playwright-cli`
- `playwright-core`

## Matt Pocock 三层维护

本仓库的 Matt skills 分三层：

1. `upstream/`：Matt 官方英文上游镜像，只用于同步。
2. `baselines/matt-zh/`：完整中文 `*-zh` baseline，只用于维护、翻译和对比，不参与安装展示。
3. `skills/matt-lqy-*/*-lqy`：当前对外安装的 LQY 个人版，必须完整自包含。

命名示例：

- `tdd` → `tdd-zh` baseline → `tdd-lqy` installable
- `triage` → `triage-zh` baseline → `triage-lqy` installable
- `handoff` → `handoff-zh` baseline → `handoff-lqy` installable
- `setup-matt-pocock-skills` → `setup-matt-pocock-skills-zh` baseline → `setup-matt-pocock-skills-lqy` installable

详细维护规则见：

```text
docs/localization/mattpocock-zh-skills.md
```

原则：官方英文版只负责同步上游，不出现在 `npx skills@latest add liu-qingyuan/skills-sync-lqy` 的安装选择列表中；中文 `*-zh` baseline 也不出现在安装选择列表中；`*-lqy` 是当前对外安装的 Matt 版本。

## 本轮选择性适配

审阅来源：`49dd158d1076134a641b33efb035946536778336`（v1.3.1 + main）。mirror 和中文 baseline 各保留 38 个 active 与 8 个 frozen legacy；安装层共 53 个 skills，其中 Matt LQY 38 个。

- 新增 `pr-lqy`（只写正文）、`retro-lqy`（人工触发、只建议）、`writing-for-agents-lqy`（agent 文档纪律）。
- 不安装 `chief-of-staff`、`implement-spec` 或额外调度层；不自动删除上游退役的个人技能，旧写作 skill 仍可显式选择。
- Pi `disable-model-invocation` 与 Codex `allow_implicit_invocation` 同步；已授权 Ralph worker 仍能加载 implement / tdd / review。
- 隐藏凭据仅影响展示副本，不改原始日志、`.env`、fixture、业务数据或真实复现输入；不增加安全整改。
- 新项目领域术语表默认 `GLOSSARY.md`；旧项目遵守已指定的同一份文档，不自动迁移或双写。

验证与安装记录：[交付报告](docs/reports/mattpocock-sync-2026-10-09.md)。

## Matt Pocock 上游同步

上游仓库：<https://github.com/mattpocock/skills>

当前同步记录见：

```text
docs/upstream-mirrors/mattpocock-skills.md
```

同步原则：

- Matt 官方英文版保留 Matt 的两层目录，例如 `upstream/mattpocock/skills/engineering/tdd`、`upstream/mattpocock/skills/productivity/handoff`，但只作为同步源，不写入 `.claude-plugin/marketplace.json`，不在安装器里显示。
- 英文 active mirror 与固定 upstream SHA 保持字节一致；legacy 明确记录旧来源。兼容性在安装层与本地 validator 处理，不为校验删除上游 frontmatter。
- 中文 baseline 统一放入 `baselines/matt-zh/matt-zh-*/*-zh`。
- 当前可安装 Matt 版本统一放入 `skills/matt-lqy-*/*-lqy`，并写入 `.claude-plugin/marketplace.json`。
- 同步后输出：上游哪些地方变了、对应中文 baseline 如何处理、对应 LQY 安装版是否需要适配。
- 本地独立改版必须另起名字，放进 `lqy-local` 或 `lqy-curated`，不要污染官方英文上游同步路径。

## 仓库结构

```text
.claude-plugin/
  marketplace.json      # npx skills 的分类来源，只列 installable skills
skills/
  <category>/
    <skill-name>/
      SKILL.md               # 可安装版本
      LOCALIZATION.md        # Matt LQY 版本记录 upstream + zh baseline 来源
      UPSTREAM.md            # curated 版本按需记录来源
baselines/
  matt-zh/
    matt-zh-*/<skill-name-zh>/
      SKILL.md               # 中文 baseline，不安装
      LOCALIZATION.md
upstream/
  mattpocock/
    skills/<category>/<skill-name>/
      SKILL.md               # 英文官方镜像，只用于同步
```

`skills/` 下每个包含 `SKILL.md` 的目录都是可安装 skill。`baselines/` 和 `upstream/` 下也保留 `SKILL.md`，但默认安装发现不会展示它们；不要把官方英文镜像或中文 baseline 放回 `skills/`，否则 `npx skills` 会把它们列出来。分类由 `.claude-plugin/marketplace.json` 控制。

## 给 AI Agent 的维护规则

后续维护这个仓库时，先读本 README，再改文件。

1. 用户安装入口保持简单，只推荐：

   ```bash
   npx skills@latest add liu-qingyuan/skills-sync-lqy
   ```

2. Quickstart 中 Matt setup skill 优先写 `$setup-matt-pocock-skills-lqy`；不要把 `*-zh` 写成用户安装后应调用的版本。
3. Matt Pocock 官方英文同步版放 `upstream/mattpocock/skills/<category>/<name>`，保持上游两层路径；不要放回 `skills/`，否则安装器会显示英文版。
4. 中文 baseline 放 `baselines/matt-zh/matt-zh-*/*-zh`；不要放回 `skills/`，否则安装器会显示 `*-zh`。
5. 当前可安装 Matt LQY 版放 `skills/matt-lqy-*/*-lqy`，必须自包含，并用 `LOCALIZATION.md` 记录对应 `*-zh` baseline 和官方上游。
6. 官方英文同步版和中文 baseline 都不加入 `.claude-plugin/marketplace.json`。
7. 新增或移动可安装 skill 后，必须同步更新 `.claude-plugin/marketplace.json`，否则交互列表分类会不对。
8. AMIS UI 相关技能放 `skills/amis-ui/`。
9. 本地自写技能放 `skills/lqy-local/`。
10. 外部整理/改造版放 `skills/lqy-curated/`。
11. 只记录外部链接、不准备维护安装版的内容，放 `docs/external-skill-links/`，不要放进 `skills/`。
12. 如果同步 Matt 上游，先 clone / fetch `https://github.com/mattpocock/skills.git`，对照它的 `skills/<category>/<name>` 结构更新到本仓库 `upstream/mattpocock/skills/<category>/<name>`；再合并变化到对应 `*-zh` baseline，最后检查对应 `*-lqy` 安装版是否需要适配。

AI 可以用下面命令做内部验证；这些不是用户日常安装命令。优先运行仓库级检查：

```bash
uv run --no-project --with pyyaml python scripts/check_matt_zh_skills.py
```

这个脚本会检查：

- `skills/` 只暴露可安装版本，Matt 英文官方镜像和中文 baseline 不能漏进安装列表。
- 38 个 Matt LQY `*-lqy` skills 都有 `LOCALIZATION.md`，并指向有效 `*-zh` baseline 和上游路径。
- 46 个 Matt 中文 `*-zh` baseline（38 active + 8 legacy）都有 `LOCALIZATION.md` 和有效上游路径。
- `.claude-plugin/marketplace.json` 必须和 `skills/` 下可安装目录一致，并且不能列出 `*-zh`。
- README 的 Codex setup 用法必须优先写 `$setup-matt-pocock-skills-lqy`。
- 所有可安装 skill 通过本仓库 YAML / 命名 / description / 调用策略校验；不依赖或修改用户系统 `quick_validate.py`。
- Pi 和 Codex 的隐式调用策略一致，已授权 Ralph worker 不被 implement 的调用 metadata 拦截。

再检查安装器发现结果：

```bash
npx skills@latest add . --list
```

## 更新已安装项目 skills

如果某个项目已经安装过本仓库的 skills，可以用脚本把该项目 `.agents/skills/` 中**已存在的同名 installable skills**更新到最新版本。脚本只从 `skills/` 读取可安装版本，不会从 `baselines/` 或 `upstream/` 同步，也不会自动新增项目未安装的 skill。

```bash
python3 scripts/sync_installed_project_skills.py /path/to/project --repo-url https://github.com/liu-qingyuan/skills-sync-lqy.git
```

先预览：

```bash
python3 scripts/sync_installed_project_skills.py /path/to/project --dry-run
```

新增维护契约测试与原有 Ralph / publisher 测试：

```bash
uv run --no-project --with pyyaml python -m unittest discover -s scripts/tests
python3 -m unittest discover -s skills/lqy-local/ralph-plan-lqy/tests
python3 -m unittest discover -s skills/matt-lqy-core/to-spec-lqy/tests
python3 -m unittest discover -s skills/matt-lqy-core/to-tickets-lqy/tests
python3 -m unittest discover -s skills/matt-lqy-core/triage-lqy/tests
python3 -m unittest discover -s skills/matt-lqy-core/setup-matt-pocock-skills-lqy/tests
```

这些测试使用隔离临时仓库与 fake gh，不会启动真实 Ralph 或修改真实 GitHub issues。

## GitNexus 依赖说明

`gitnexus` 不是纯离线通用说明 skill，它依赖本机 GitNexus：

- 本机需要能执行 `gitnexus --version`。
- 目标仓库需要已有 GitNexus index，或有权限先运行项目约定的索引命令。

## AGENTS.md setup

详细初始化参考见：[docs/agents-architecture-setup.md](docs/agents-architecture-setup.md)。

`AGENTS.md` 是给项目常驻读取的精简架构约束。运行 setup 会把本仓库根目录的 `AGENTS.md` 写入目标项目；若目标已有不同内容，会先生成 `.bak.<timestamp>` 备份。

```bash
./setup /path/to/project
```

# skills-sync-lqy

我的 Codex Skills 仓库。目标是：

1. 同步 Matt Pocock 上游英文原版 skills，目录结构尽量跟上游一致。
2. 维护一套 `-zh` 中文本地化版，作为可自由修改的本地 fork。
3. 保留我自己的本地 skills，并用独立分类跟上游区分。
4. 通过一个简洁命令交互安装：

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

如果你选择 Matt Pocock 中文工作流相关 skills，建议同时选择并先运行：

```text
/setup-matt-pocock-skills-zh
```

它会让 AI 询问当前项目的 issue tracker、triage labels、文档保存位置等，让 `to-issues-zh`、`to-prd-zh`、`triage-zh`、`tdd-zh`、`diagnosing-bugs-zh` 等技能知道项目约定。

如果只安装我的本地 skills，例如 `simple`、`pea`、`tea`、`gitnexus`、`handoff-out`，通常安装后即可使用。

安装后如果当前 Codex 会话没有自动加载新 skill，重启 Codex。

## 分类

本仓库把“可安装 skills”和“上游同步源”分开：

```text
skills/                  # 只放 npx 安装器应该展示的版本
  matt-zh-core/         # Matt Pocock 中文版：engineering + productivity
  matt-zh-personal/     # Matt Pocock 中文版：personal
  matt-zh-misc/         # Matt Pocock 中文版：misc
  matt-zh-in-progress/  # Matt Pocock 中文版：in-progress
  matt-zh-deprecated/   # Matt Pocock 中文版：deprecated
  amis-ui/              # AMIS UI 相关：设计变量、Figma 还原等
  lqy-local/            # 我自己写/优化并长期使用的 skills
  lqy-curated/          # 我从外部素材整理/改造后维护的 skills

upstream/mattpocock/skills/  # Matt Pocock 官方英文上游镜像，只用于同步，不参与安装展示
  engineering/
  productivity/
  personal/
  misc/
  in-progress/
  deprecated/
```

`npx skills@latest` 的交互列表会按 `.claude-plugin/marketplace.json` 里的分组显示：

- `Matt Pocock 中文 Core`：中文本地化主力版，合并 Engineering + Productivity。
- `AMIS UI`：AMIS UI / Figma 相关。
- `LQY Local`：我自己写/优化的本地 skills。
- `LQY Curated`：我整理/改造后维护的通用 skills。
- `Matt Pocock 中文 Personal / Misc / In Progress / Deprecated`

## 重要区分

- `upstream/mattpocock/skills/productivity/handoff`：Matt Pocock 上游原版 `handoff`。
- `skills/lqy-local/handoff-out`：我的本地改版，用来输出可复制的交接 prompt，不写临时文件、不修改 workspace。

以后如果某个 Matt 上游 skill 被我改造，不要直接覆盖上游路径；中文本地化放到 `skills/matt-zh-*/*-zh`，我的独立改版放到 `skills/lqy-local/` 或 `skills/lqy-curated/`，例如 `handoff-out`。

## 本地 skills

### Lqy Local

- `simple`：简化代码、文档、prompt、配置、计划或规格，同时保留意图和必要行为。
- `pea`：Project Engineering Architect；判断模块边界、接口、seam、adapter、contract、依赖方向、重构和质量门禁。
- `tea`：Testing Engineering Architect；判断测试分层、contract test、E2E 边界、回归保护和 CI 质量门禁。
- `gitnexus`：GitNexus 代码图谱工具路由与使用指南。
- `ralph-omx-plan`：生成 Open Ralph via OMX 的 prompt packet、模式选择、命令和参数说明。
- `handoff-out`：我的交接 prompt 输出版。

### AMIS UI

- `amis-variables`：AMIS V1.0 设计系统语义变量。
- `figma-pixel-implementation`：结合 Figma 做像素级 UI 还原。

### Lqy Curated

- `c4-architecture`
- `mermaid-visualizer`
- `pact`
- `playwright-ci`
- `playwright-cli`
- `playwright-core`

## Matt Pocock 中文版

中文版是官方英文上游的本地化 fork，统一使用 `-zh` 后缀，例如：

- `tdd` → `tdd-zh`
- `triage` → `triage-zh`
- `handoff` → `handoff-zh`
- `setup-matt-pocock-skills` → `setup-matt-pocock-skills-zh`

详细维护规则见：

```text
docs/localization/mattpocock-zh-skills.md
```

原则：官方英文版只负责同步上游，不出现在 `npx skills@latest add liu-qingyuan/skills-sync-lqy` 的安装选择列表中；中文 `*-zh` 版本才对外安装，并且可以按我的习惯继续本地化和改造。

## Matt Pocock 上游同步

上游仓库：<https://github.com/mattpocock/skills>

当前同步记录见：

```text
docs/upstream-mirrors/mattpocock-skills.md
```

同步原则：

- Matt 官方英文版保留 Matt 的两层目录，例如 `upstream/mattpocock/skills/engineering/tdd`、`upstream/mattpocock/skills/productivity/handoff`，但只作为同步源，不写入 `.claude-plugin/marketplace.json`，不在安装器里显示。
- 保留上游行为；如因本地 Codex 校验需要删掉不兼容 frontmatter 字段，要记录在同步文档里。
- 中文本地化版统一放入 `skills/matt-zh-*/*-zh`。
- 本地改版必须另起名字，放进 `matt-zh-*`、`lqy-local` 或 `lqy-curated`，不要污染官方英文上游同步路径。

## 仓库结构

```text
.claude-plugin/
  marketplace.json      # npx skills 的分类来源
skills/
  <category>/
    <skill-name>/
      SKILL.md               # 可安装版本
      LOCALIZATION.md        # Matt 中文版按需记录来源
      UPSTREAM.md            # curated 版本按需记录来源
upstream/
  mattpocock/
    skills/<category>/<skill-name>/
      SKILL.md               # 英文官方镜像，只用于同步
docs/
  upstream-mirrors/
  external-skill-links/
```

`skills/` 下每个包含 `SKILL.md` 的目录都是可安装 skill。`upstream/` 下也保留 `SKILL.md`，但默认安装发现不会展示它；不要把官方英文镜像放回 `skills/`，否则 `npx skills` 会把英文版也列出来。分类由 `.claude-plugin/marketplace.json` 控制。

## 给 AI Agent 的维护规则

后续维护这个仓库时，先读本 README，再改文件。

1. 用户安装入口保持简单，只推荐：

   ```bash
   npx skills@latest add liu-qingyuan/skills-sync-lqy
   ```

2. 不在 Quickstart 里新增复杂参数示例；让安装器交互选择。
3. Matt Pocock 官方英文同步版放 `upstream/mattpocock/skills/<category>/<name>`，保持上游两层路径；不要放回 `skills/`，否则安装器会显示英文版。
4. 官方英文同步版只作为同步源，不加入 `.claude-plugin/marketplace.json`。
5. 新增或移动可安装 skill 后，必须同步更新 `.claude-plugin/marketplace.json`，否则交互列表分类会不对。
6. Matt Pocock 中文本地化版放 `skills/matt-zh-*/*-zh`，这是对外安装的 Matt 版本，不要覆盖官方英文目录。
7. AMIS UI 相关技能放 `skills/amis-ui/`。
8. 本地自写技能放 `skills/lqy-local/`。
9. 外部整理/改造版放 `skills/lqy-curated/`。
10. 只记录外部链接、不准备维护安装版的内容，放 `docs/external-skill-links/`，不要放进 `skills/`。
11. 如果同步 Matt 上游，先 clone / fetch `https://github.com/mattpocock/skills.git`，对照它的 `skills/<category>/<name>` 结构更新到本仓库 `upstream/mattpocock/skills/<category>/<name>`；可以调整 `.claude-plugin/marketplace.json` 的中文显示分组，但不要把英文上游加入安装分组。同步后再人工/AI 合并变化到对应 `*-zh` 中文版。

AI 可以用下面命令做内部验证；这些不是用户日常安装命令。优先运行仓库级检查：

```bash
python3 scripts/check_matt_zh_skills.py
```

这个脚本会检查：

- `skills/` 只暴露可安装版本，Matt 英文官方镜像不能漏进安装列表。
- 35 个 Matt 中文 `*-zh` skills 都有 `LOCALIZATION.md` 和有效上游路径。
- 中文 `SKILL.md` 不能混入“官方英文上游”“本地化说明”等维护文案。
- `.claude-plugin/marketplace.json` 必须和 `skills/` 下可安装目录一致。
- 所有可安装 skill 必须通过 `quick_validate.py`。

再检查安装器发现结果：

```bash
npx skills@latest add . --list
```

如果只改了某个 skill，也可以额外验证对应目录：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<category>/<skill-name>
```

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

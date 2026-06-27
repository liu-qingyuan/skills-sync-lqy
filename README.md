# skills-sync-lqy

我的 Codex Skills 仓库。目标是：

1. 同步 Matt Pocock 上游原版 skills，目录结构尽量跟上游一致。
2. 保留我自己的本地 skills，并用独立分类跟上游区分。
3. 通过一个简洁命令交互安装：

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

如果你选择 Matt Pocock 工作流相关 skills，建议同时选择并先运行：

```text
/setup-matt-pocock-skills
```

它会让 AI 询问当前项目的 issue tracker、triage labels、文档保存位置等，让 Matt 那套 `to-issues`、`to-prd`、`triage`、`tdd`、`diagnosing-bugs` 等技能知道项目约定。

如果只安装我的本地 skills，例如 `simple`、`pea`、`tea`、`gitnexus`、`handoff-out`，通常安装后即可使用。

安装后如果当前 Codex 会话没有自动加载新 skill，重启 Codex。

## 分类

本仓库使用两层目录：

```text
skills/
  engineering/          # Matt Pocock 上游：工程类
  productivity/         # Matt Pocock 上游：生产力类
  personal/             # Matt Pocock 上游：个人工作流
  misc/                 # Matt Pocock 上游：杂项
  in-progress/          # Matt Pocock 上游：实验中
  deprecated/           # Matt Pocock 上游：已废弃但保留同步
  lqy-local/            # 我自己写/优化并长期使用的 skills
  lqy-curated/          # 我从外部素材整理/改造后维护的 skills
```

`npx skills@latest` 的交互列表会按 `.claude-plugin/marketplace.json` 里的分组显示：

- `Mattpocock Engineering`
- `Mattpocock Productivity`
- `Mattpocock Personal`
- `Mattpocock Misc`
- `Mattpocock In Progress`
- `Mattpocock Deprecated`
- `Lqy Local`
- `Lqy Curated`

## 重要区分

- `skills/productivity/handoff`：Matt Pocock 上游原版 `handoff`。
- `skills/lqy-local/handoff-out`：我的本地改版，用来输出可复制的交接 prompt，不写临时文件、不修改 workspace。

以后如果某个 Matt 上游 skill 被我改造，不要直接覆盖上游路径；改名放到 `skills/lqy-local/` 或 `skills/lqy-curated/`，例如 `handoff-out`。

## 本地 skills

### Lqy Local

- `simple`：简化代码、文档、prompt、配置、计划或规格，同时保留意图和必要行为。
- `pea`：Project Engineering Architect；判断模块边界、接口、seam、adapter、contract、依赖方向、重构和质量门禁。
- `tea`：Testing Engineering Architect；判断测试分层、contract test、E2E 边界、回归保护和 CI 质量门禁。
- `gitnexus`：GitNexus 代码图谱工具路由与使用指南。
- `ralph-omx-plan`：生成 Open Ralph via OMX 的 prompt packet、模式选择、命令和参数说明。
- `handoff-out`：我的交接 prompt 输出版。

### Lqy Curated

- `amis-variables`
- `c4-architecture`
- `figma-pixel-implementation`
- `mermaid-visualizer`
- `pact`
- `playwright-ci`
- `playwright-cli`
- `playwright-core`

## Matt Pocock 上游同步

上游仓库：<https://github.com/mattpocock/skills>

当前同步记录见：

```text
docs/upstream-mirrors/mattpocock-skills.md
```

同步原则：

- Matt 上游原版放回 Matt 的两层目录，例如 `skills/engineering/tdd`、`skills/productivity/handoff`。
- 保留上游行为；如因本地 Codex 校验需要删掉不兼容 frontmatter 字段，要记录在同步文档里。
- 本地改版必须另起名字，放进 `lqy-local` 或 `lqy-curated`，不要污染上游同步路径。

## 仓库结构

```text
.claude-plugin/
  marketplace.json      # npx skills 的分类来源
skills/
  <category>/
    <skill-name>/
      SKILL.md
      UPSTREAM_MATTOCOCK.md  # Matt 上游同步版才有
      UPSTREAM.md            # 其他 curated 版本按需添加
docs/
  upstream-mirrors/
  external-skill-links/
```

每个可安装 skill 都是一个包含 `SKILL.md` 的目录。`npx skills` 会递归发现这些目录；分类由 `.claude-plugin/marketplace.json` 控制。

## 给 AI Agent 的维护规则

后续维护这个仓库时，先读本 README，再改文件。

1. 用户安装入口保持简单，只推荐：

   ```bash
   npx skills@latest add liu-qingyuan/skills-sync-lqy
   ```

2. 不在 Quickstart 里新增复杂参数示例；让安装器交互选择。
3. Matt Pocock 上游同步版保持两层路径，不要拍平成一层。
4. 新增或移动 skill 后，必须同步更新 `.claude-plugin/marketplace.json`，否则交互列表分类会不对。
5. 本地自写技能放 `skills/lqy-local/`。
6. 外部整理/改造版放 `skills/lqy-curated/`。
7. 只记录外部链接、不准备维护安装版的内容，放 `docs/external-skill-links/`，不要放进 `skills/`。
8. 如果同步 Matt 上游，先 clone / fetch `https://github.com/mattpocock/skills.git`，对照它的 `skills/<category>/<name>` 结构更新。

AI 可以用下面命令做内部验证；这些不是用户日常安装命令：

```bash
npx skills@latest add . --list
```

如果改了某个 skill，再验证对应目录：

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

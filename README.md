# skills-sync-lqy

用于分发和维护我愿意长期使用的 Codex Skills。这个仓库按 `npx skills@latest` 的 GitHub source 格式组织：可安装 skill 只放在 `skills/<skill-name>/SKILL.md`。

> 本仓库里的 skill 以本仓库版本为准。即使某个 skill 最初来自外部或上游，只要已经放进 `skills/` 并经过精简/修改，就按本仓库维护的 fork / curated 版本使用。

## Quickstart（30 秒安装）

不需要先 clone。直接运行：

```bash
npx skills@latest add liu-qingyuan/skills-sync-lqy
```

然后按安装器提示选择要安装的 skills 和目标 agent。

如果你选择安装 Matt Pocock 工作流相关 skills，建议同时选择并先运行：

```text
/setup-matt-pocock-skills
```

它会让 AI 询问当前项目的 issue tracker、triage labels、文档保存位置等，让 Matt 那套 `to-issues`、`to-prd`、`triage`、`tdd`、`diagnosing-bugs` 等技能知道项目约定。

如果只安装本仓库自定义技能（例如 `simple`、`pea`、`tea`、`gitnexus`、`handoff-out`），通常安装后即可使用。

安装后如当前 Codex 会话没有自动加载新 skill，请重启 Codex。

## 可安装 skills

本仓库现在包含两类 skill：

1. **Matt Pocock 上游同步版**：从 `mattpocock/skills` 同步到本仓库，作为可安装 skills 一起出现在选择列表里。
2. **本仓库自定义 / 改造版**：我自己写或基于上游改造后维护的版本。

来源类型：

- `upstream-mirrored`：从上游同步进 `skills/` 的可安装版本，尽量保持上游行为。
- `local`：本仓库作者自写或明显优化维护的版本。
- `curated / customized`：来自外部或上游素材，经本仓库筛选、整理、精简或改造后维护的版本。

### Matt Pocock 上游同步版

已同步 Matt Pocock 上游 skills。完整清单和来源 commit 见：

```text
docs/upstream-mirrors/mattpocock-skills.md
```

其中包括：

- `setup-matt-pocock-skills`
- `ask-matt`
- `grill-with-docs`
- `diagnosing-bugs`
- `domain-modeling`
- `codebase-design`
- `tdd`
- `to-issues`
- `to-prd`
- `triage`
- `prototype`
- `improve-codebase-architecture`
- `grill-me`
- `handoff`
- `teach`
- 以及其他 Matt Pocock repo 中的 skills

### 本仓库自定义 / 改造版

| Skill | 来源类型 | 说明 |
| --- | --- | --- |
| `simple` | `local` | 简化代码、Markdown、文档、prompt、配置、流程图、计划或规格，同时保留意图和必要行为。 |
| `pea` | `local` | Project Engineering Architect：用于模块边界、接口、seam / adapter / contract、依赖方向、重构和质量门禁判断。 |
| `tea` | `local` | Testing Engineering Architect：用于测试分层、contract test、E2E 边界、回归保护和 CI 质量门禁判断。 |
| `gitnexus` | `local` | GitNexus 代码图谱工具路由与使用指南；依赖本机 GitNexus CLI/MCP 和目标仓库索引。 |
| `ralph-omx-plan` | `local` | 生成 Open Ralph via OMX 的 prompt packet、模式选择、命令和参数说明。 |
| `handoff-out` | `curated / customized` | 基于 Matt Pocock `handoff` 改造出的本仓库输出版：只在聊天中输出可复制工作合同 prompt，不写临时文件、不修改 workspace。 |
| `amis-variables` | `curated / customized` | Amis V1.0 设计系统语义变量参考，用于 surface/background、border/divider、text、icon token。 |
| `c4-architecture` | `curated / customized` | 用 C4 model 和 Mermaid 生成架构文档和 context/container/component/deployment diagram。 |
| `figma-pixel-implementation` | `curated / customized` | 从 Figma 节点进行像素级 UI 还原，强调事实提取、DOM/style/geometry 合约和截图验证。 |
| `mermaid-visualizer` | `curated / customized` | 把文本内容转换为 Mermaid 图表，适合流程、架构、对比、mindmap、sequence 等场景。 |
| `pact` | `curated / customized` | 开源 Pact + 自建 Pact Broker 契约测试参考，用于 consumer test、provider verification、can-i-deploy 和 CI gate。 |
| `playwright-ci` | `curated / customized` | Playwright CI/CD 配置参考，覆盖常见 CI、Docker、sharding、报告、覆盖率和 global setup/teardown。 |
| `playwright-cli` | `curated / customized` | 终端优先的 Playwright 浏览器自动化、截图/视频/trace、测试生成和 Electron 证据采集参考。 |
| `playwright-core` | `curated / customized` | Playwright E2E/API/component/visual/accessibility/security 测试模式参考。 |

## GitNexus 依赖说明

`gitnexus` 不是纯离线通用项目说明 skill，它依赖 GitNexus 支持：

- 本机需要能执行 `gitnexus --version`。
- 目标仓库需要已有 GitNexus index，或有权限先运行 `gitnexus analyze <repo-path>` / 项目约定的索引命令。

## 仓库结构

```text
skills/
  <skill-name>/
    SKILL.md
    UPSTREAM_MATTOCOCK.md   # 如果是 Matt Pocock 上游同步版
    UPSTREAM.md             # 如果是其他上游/本地改版说明

docs/upstream-mirrors/
  mattpocock-skills.md

docs/external-skill-links/
  mattpocock-skills.md
```

规则：

- 每个可安装 skill 放在 `skills/<skill-name>/`。
- 每个可安装 skill 目录必须包含 `SKILL.md`。
- Matt Pocock 上游同步版放在扁平路径 `skills/<upstream-skill-name>/`，并记录 `UPSTREAM_MATTOCOCK.md`。
- 本仓库改造版使用不同名字，例如上游 `handoff` 与本地改版 `handoff-out`。
- 额外的 `scripts/`、`assets/`、`references/`、`agents/` 等目录会和该 skill 一起维护。

## 混合上游与自定义 skill 的维护规则

- `skills/` 目录只放我愿意分发和维护的版本。
- 如果某个 skill 来自外部但已经被我改过：
  - 保留在 `skills/<name>/`。
  - 可以加简短 `UPSTREAM.md`，写来源链接、改动原则和当前维护者。
  - README 标成 `curated / customized`。
- 如果是 Matt Pocock 上游同步版：
  - 放在 `skills/<upstream-skill-name>/`。
  - 保留上游行为，记录 `UPSTREAM_MATTOCOCK.md`。
  - 更新时从 `mattpocock/skills` 重新同步。
- 如果某个上游 skill 被本仓库改造：
  - 使用不同名字，例如 `handoff-out`。
  - 不覆盖上游同步版名称。
- 如果只是记录外部链接但不维护安装版本，再放到 `docs/external-skill-links/`。

## 给 AI Agent 的说明

如果你是 AI Agent，正在读取这个仓库，请遵循以下规则：

1. `skills/` 下的每个目录都表示一个独立的 Codex skill。
2. 使用 skill 时先读取该目录下的 `SKILL.md`。
3. 只有当 `SKILL.md` 明确引用额外文件时，才继续读取 `scripts/`、`references/`、`assets/` 等内容。
4. 相对路径优先相对于 skill 自身目录解析。
5. 不要假设 README 之外存在未写明的全局规则。
6. 若 skill 自带脚本或模板，优先复用，不要手写重复逻辑。
7. `docs/upstream-mirrors/` 记录已同步上游；`docs/external-skill-links/` 只保存参考链接。

## 上游同步记录

- [Matt Pocock upstream mirror](docs/upstream-mirrors/mattpocock-skills.md)：记录已同步的 Matt Pocock skills、来源路径、来源 commit 和 frontmatter 兼容说明。
- [Matt Pocock external links](docs/external-skill-links/mattpocock-skills.md)：保留上游 README 和 skill 链接，方便人工对照。

## 如何 setup 项目 AGENTS.md

详细初始化参考见：[docs/agents-architecture-setup.md](docs/agents-architecture-setup.md)。

`AGENTS.md` 是给项目常驻读取的精简架构约束。运行 setup 会把本仓库根目录的 `AGENTS.md` 写入目标项目；若目标已有不同内容，会先生成 `.bak.<timestamp>` 备份。

```bash
./setup /path/to/project
```

检查写入结果：

```bash
sed -n '1,220p' /path/to/project/AGENTS.md
```

## Matt Pocock 上游与本地改版

- Matt Pocock 上游 skills 已同步到 `skills/<name>/`，详见 `docs/upstream-mirrors/mattpocock-skills.md`。
- `handoff` 是上游同步版。
- `handoff-out` 是本仓库基于 `handoff` 的本地改版：只在聊天里输出可复制 prompt，不写 `/tmp` 文档，也不修改 workspace。

## 已移除的外部镜像

以下外部 skill 镜像已从本仓库删除，不再作为 `liu-qingyuan/skills-sync-lqy` 的可安装 skill 提供：

- `frontend-slides`
  - Upstream: https://github.com/zarazhangrui/frontend-slides
  - Upstream plugin path: `plugins/frontend-slides`
  - 原本仓库安装路径: `skills/frontend-slides`
- `visual-explainer`
  - Upstream: https://github.com/nicobailon/visual-explainer.git
  - Upstream skill path: `plugins/visual-explainer`
  - 原本仓库安装路径: `skills/visual-explainer`
- `excalidraw-diagram`
  - 原本仓库安装路径: `skills/excalidraw-diagram`
- `feature-release-verifier`
  - 原本仓库安装路径: `skills/feature-release-verifier`
- `gitnexus-codex-wiki`
  - 原本仓库安装路径: `skills/gitnexus-codex-wiki`
- `obsidian-canvas-creator`
  - 原本仓库安装路径: `skills/obsidian-canvas-creator`
- `project-explainer-web`
  - 原本仓库安装路径: `skills/project-explainer-web`

如果需要这些 skill，请直接阅读对应 upstream 仓库并按 upstream 的方式安装；不要在本仓库恢复为 symlink、submodule 或只含相对路径的占位文本。

### 本机 OMX 内置 skill 说明

- `skill` 已从本仓库的远程镜像目录 `skills/skill` 删除，不再由 `liu-qingyuan/skills-sync-lqy` 分发。
- 这不代表应该删除本机 `~/.codex/skills/skill`。`skill` 是 OMX catalog 里的 active utility skill；本机应由 OMX 安装包或 `omx setup` 维护。
- 如本机误删，可从 OMX 安装包恢复，例如 `/opt/homebrew/lib/node_modules/oh-my-codex/skills/skill/`。

## 给维护者 / AI 的更新流程

后续维护这个仓库时，先让 AI 读取本 README，再按下面规则修改：

1. README 保持极简，安装入口只推荐：

   ```bash
   npx skills@latest add liu-qingyuan/skills-sync-lqy
   ```

2. 不在 README 里新增带安装参数的复杂示例；让安装器交互选择即可。
3. 可安装 skill 只放在 `skills/<skill-name>/SKILL.md`。
4. Matt Pocock 上游同步版按 `docs/upstream-mirrors/mattpocock-skills.md` 维护。
5. 外部链接只放在 `docs/external-skill-links/`；只有放入 `skills/` 的目录才是本仓库可安装 skill。
6. 如果 skill 来自外部但已被本仓库修改，按本仓库的 curated / customized 版本维护；如果是上游同步版，优先保持上游行为并记录来源 commit。
6. 修改后至少验证本地仓库能被识别：

   ```bash
   npx skills@latest add . --list
   ```

7. 如果改了某个 skill，再验证对应目录：

   ```bash
   python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
   ```

## 维护约定

- 新增本仓库可安装 skill 时统一放到 `skills/` 下。
- skill 目录名使用 ASCII 和 kebab-case。
- 说明写在 `SKILL.md`。
- 外部参考链接统一放到 `docs/external-skill-links/`，不要放到 `skills/`。
- 如果某条规则需要让 AI 遵循，请明确写进 `SKILL.md` 或本 README。

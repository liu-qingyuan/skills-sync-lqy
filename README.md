# skills-sync-lqy

这是一个用于同步和分发自定义 Codex Skills 的仓库。

当前包含的可安装 skills：

- `amis-variables`：记录 Amis V1.0 设计系统语义变量，用于选择 surface/background、border/divider、text、icon token，并保留 light/dark mode 值、使用规则和 pairing rules。
- `c4-architecture`：用 C4 model 和 Mermaid 生成软件架构文档，支持 context/container/component/deployment diagram。
- `mermaid-visualizer`：把文本内容转换为 Mermaid 图表，适合流程图、系统架构图、对比图、mindmap、sequence diagram 等文档/演示场景。
- `figma-pixel-implementation`：用于从 Figma 节点进行像素级 UI 还原，强调先提取颜色/尺寸/图标/状态资产事实，再用 DOM/style/geometry 合约和截图验证。
- `gitnexus`：为 OMX/Codex 工作流提供 GitNexus 代码图谱 grounding；需要本机已安装/配置 GitNexus CLI/MCP，并且目标仓库已有 GitNexus index。
- `karpathy-guidelines`：写代码、评审或重构时的行为准则，强调先明确假设、保持简单、外科手术式修改和可验证成功标准。
- `pact`：开源 Pact + 自建 Pact Broker 契约测试 skill，用于 consumer test、provider verification、can-i-deploy 和 CI gate。
- `pea`：Project Engineering Architect，用于项目工程架构、模块设计、接口设计、重构、事件/服务契约、依赖边界、策略治理和 CI/CD 质量门禁。
- `tea`：Testing Engineering Architect，用于测试工程架构、测试分层、contract test、E2E 边界、architecture check、回归保护和 CI 质量门禁。
- `handoff`：基于 Matt Pocock handoff 改版，用于直接输出可复制给另一个 AI 的结构化工作合同 prompt；按任务类型组织目标、边界、验收、验证和停止条件；不写临时文件、不修改 workspace。
- `playwright-ci`：非官方整理的 Playwright CI/CD 配置参考；仅在项目已有 CI 或用户要求配置 CI/CD 时使用。
- `playwright-cli`：基于官方 `playwright-cli install --skills` 的本地扩展版，用于终端优先浏览器自动化、截图/视频/trace、测试代码生成，并记录 Electron `_electron.launch()` 应用的录屏注意事项。
- `playwright-core`：非官方整理的 Playwright E2E/API/component/visual/accessibility/security 测试模式参考，覆盖 locator、assertions、fixtures、mock、auth、trace 调试与框架配方。
- `ralph-omx-plan`：把待办任务整理成 Open Ralph via OMX 的 prompt packet 和可复制的 `ralph-omx` 运行命令。

## GitNexus 依赖说明

`gitnexus` 不是纯离线通用项目说明 skill，它依赖 GitNexus 支持：

- 本机需要能执行 `gitnexus --version`。
- 目标仓库需要已有 GitNexus index，或有权限先运行 `gitnexus analyze <repo-path>` / 项目约定的索引命令。

---

## 仓库结构

```text
skills/
  amis-variables/
  c4-architecture/
  mermaid-visualizer/
  figma-pixel-implementation/
  gitnexus/
  karpathy-guidelines/
  pact/
  pea/
  tea/
  handoff/
  playwright-ci/
  playwright-cli/
  playwright-core/
  ralph-omx-plan/

docs/external-skill-links/
  mattpocock-skills.md
```

规则：

- 每个可安装 skill 放在 `skills/<skill-name>/`
- 每个可安装 skill 目录必须包含 `SKILL.md`
- 额外的 `scripts/`、`assets/`、`references/`、`agents/` 等目录会和 skill 一起维护
- `docs/external-skill-links/` 只放外部参考链接，不是安装镜像，也不是 Codex skill 目录

---

## 给 AI Agent 的说明

如果你是 AI Agent，正在读取这个仓库，请遵循以下规则：

1. `skills/` 下的每个目录都表示一个独立的 Codex skill
2. 使用 skill 时先读取该目录下的 `SKILL.md`
3. 只有当 `SKILL.md` 明确引用额外文件时，才继续读取 `scripts/`、`references/`、`assets/` 等内容
4. 相对路径优先相对于 skill 自身目录解析
5. 不要假设 README 之外存在未写明的全局规则
6. 若 skill 自带脚本或模板，优先复用，不要手写重复逻辑
7. `docs/external-skill-links/` 下的内容只供人类跳转阅读；不要自动安装、不要当成本仓库 skill、不要从这些链接推断本仓库提供对应 skill

---

## 外部 skill 链接（只读参考，不自动安装）

- [Matt Pocock / Skills For Real Engineers](docs/external-skill-links/mattpocock-skills.md)：除本仓库已明确放入 `skills/` 的本地改版 `handoff` 外，其余 Matt Pocock skills 只保存 upstream README 和各 skill 的链接，方便自行阅读后跳转安装；不镜像到 `skills/`，也不通过本仓库的安装命令安装。

---

## 如何安装本仓库 skills

使用 Codex 自带的 `skill-installer`：

### 安装 `amis-variables`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/amis-variables
```

### 安装 `c4-architecture`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/c4-architecture
```

### 安装 `mermaid-visualizer`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/mermaid-visualizer
```

### 安装 `figma-pixel-implementation`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/figma-pixel-implementation
```

### 安装 `gitnexus`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/gitnexus
```

### 安装 `karpathy-guidelines`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/karpathy-guidelines
```

### 安装 `pact`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/pact
```

### 安装 `pea`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/pea
```

### 安装 `tea`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/tea
```

### 安装 `handoff`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/handoff
```

### 安装 `playwright-ci`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/playwright-ci
```

### 安装 `playwright-cli`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/playwright-cli
```

### 安装 `playwright-core`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/playwright-core
```

### 安装 `ralph-omx-plan`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/ralph-omx-plan
```

安装完成后请重启 Codex：

```text
Restart Codex to pick up new skills.
```

---

## 如何更新

`skill-installer` 的行为是复制安装，不是实时同步。

如果本地已经存在同名 skill，更新时建议先删除，再重新安装：

```bash
rm -rf ~/.codex/skills/amis-variables
rm -rf ~/.codex/skills/c4-architecture
rm -rf ~/.codex/skills/mermaid-visualizer
rm -rf ~/.codex/skills/figma-pixel-implementation
rm -rf ~/.codex/skills/gitnexus
rm -rf ~/.codex/skills/karpathy-guidelines
rm -rf ~/.codex/skills/pact
rm -rf ~/.codex/skills/pea
rm -rf ~/.codex/skills/tea
rm -rf ~/.codex/skills/handoff
rm -rf ~/.codex/skills/playwright-ci
rm -rf ~/.codex/skills/playwright-cli
rm -rf ~/.codex/skills/playwright-core
rm -rf ~/.codex/skills/ralph-omx-plan
```

然后重新运行安装命令并重启 Codex。

---

## 如何长期同步

如果你希望多个设备长期同步，推荐使用 `git clone + 软链接`：

```bash
git clone https://github.com/liu-qingyuan/skills-sync-lqy.git ~/skills-sync-lqy
ln -s ~/skills-sync-lqy/skills/amis-variables ~/.codex/skills/amis-variables
ln -s ~/skills-sync-lqy/skills/c4-architecture ~/.codex/skills/c4-architecture
ln -s ~/skills-sync-lqy/skills/mermaid-visualizer ~/.codex/skills/mermaid-visualizer
ln -s ~/skills-sync-lqy/skills/figma-pixel-implementation ~/.codex/skills/figma-pixel-implementation
ln -s ~/skills-sync-lqy/skills/gitnexus ~/.codex/skills/gitnexus
ln -s ~/skills-sync-lqy/skills/karpathy-guidelines ~/.codex/skills/karpathy-guidelines
ln -s ~/skills-sync-lqy/skills/pact ~/.codex/skills/pact
ln -s ~/skills-sync-lqy/skills/pea ~/.codex/skills/pea
ln -s ~/skills-sync-lqy/skills/tea ~/.codex/skills/tea
ln -s ~/skills-sync-lqy/skills/handoff ~/.codex/skills/handoff
ln -s ~/skills-sync-lqy/skills/playwright-ci ~/.codex/skills/playwright-ci
ln -s ~/skills-sync-lqy/skills/playwright-cli ~/.codex/skills/playwright-cli
ln -s ~/skills-sync-lqy/skills/playwright-core ~/.codex/skills/playwright-core
ln -s ~/skills-sync-lqy/skills/ralph-omx-plan ~/.codex/skills/ralph-omx-plan
```

之后只需要：

```bash
cd ~/skills-sync-lqy
git pull
```

---

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

---

## 已选择镜像的外部 skill

- `handoff` 基于本机通过 `npx skills@latest add mattpocock/skills` 安装后的 `/Users/amis/.agents/skills/handoff/SKILL.md` 改版。
- Original upstream: https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md
- 本仓库安装路径: `skills/handoff`
- 本地改版行为：只在聊天里输出可复制 prompt，不写 `/tmp` 文档，也不修改 workspace。

---

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

---

## 维护约定

- 新增本仓库可安装 skill 时统一放到 `skills/` 下
- skill 目录名使用 ASCII 和 kebab-case
- 说明写在 `SKILL.md`
- 外部参考链接统一放到 `docs/external-skill-links/`，不要放到 `skills/`
- 如果某条规则需要让 AI 遵循，请明确写进 `SKILL.md` 或本 README

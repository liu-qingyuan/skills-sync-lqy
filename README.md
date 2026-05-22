# skills-sync-lqy

这是一个用于同步和分发自定义 Codex Skills 的仓库。

当前包含的 skills：

- `project-explainer-web`：生成项目或任务的说明型静态网页，默认输出中文，适合快速帮助人类或 AI 理解仓库、架构和任务背景。
- `feature-release-verifier`：用于验证功能是否具备发布条件，聚合 mock-ui、real-runtime、packaged-smoke 等验证证据并输出发布结论。
- `frontend-slides`：用于创建或转换零依赖 HTML 演示文稿；本镜像把嵌套 plugin skill 文件实体化，避免 GitHub archive/安装器把 symlink 转成无 frontmatter 文本导致 Codex 跳过加载。
- `gitnexus`：为 OMX/Codex 工作流提供 GitNexus 代码图谱 grounding；需要本机已安装/配置 GitNexus CLI/MCP，并且目标仓库已有 GitNexus index；可作为 `$deep-interview`、`$ralplan`、`$team`、`$autopilot`、`$ralph-omx-plan` 等 workflow 的上下文 modifier。
- `gitnexus-codex-wiki`：基于 GitNexus graph/index evidence 生成源码证据驱动的 markdown wiki 或 project-explainer-web 风格架构介绍网页；需要本机可运行 `gitnexus` CLI 和目标仓库 index，推荐与 `$gitnexus` skill 一起安装。
- `karpathy-guidelines`：写代码、评审或重构时的行为准则，强调先明确假设、保持简单、外科手术式修改和可验证成功标准。
- `playwright-cli`：用于通过 playwright-cli 做终端优先的浏览器自动化、截图/视频/trace、测试代码生成，并记录 Electron `_electron.launch()` 应用的录屏注意事项。
- `skill`：用于管理本地 Codex/OMX skills，包含 list/add/remove/edit/search/info/sync/setup/scan 等 CLI 式工作流说明。
- `ralph-omx-plan`：把待办任务整理成 Open Ralph via OMX 的 prompt packet 和可复制的 `ralph-omx` 运行命令，同时列出 `$ralplan`、`$ralph`、`$team` 等可选 OMX-native 执行路径。
- `visual-explainer`：链接同步自 `nicobailon/visual-explainer` 的 HTML 视觉说明 skill，用于生成架构图、计划评审、diff review、slide deck 和数据表等可视化页面。

## GitNexus 依赖说明

`gitnexus` 和 `gitnexus-codex-wiki` 不是纯离线通用项目说明 skill。它们都依赖 GitNexus 支持：

- 本机需要能执行 `gitnexus --version`。
- 目标仓库需要已有 GitNexus index，或有权限先运行 `gitnexus analyze <repo-path>` / 项目约定的索引命令。
- `gitnexus-codex-wiki` 使用 GitNexus graph/index evidence 写 wiki/架构网页；如果没有 GitNexus evidence，应改用 `project-explainer-web` 这类非图谱 skill。
- 安装 `gitnexus-codex-wiki` 时建议同时安装 `gitnexus`，这样可以先用 `$gitnexus` 做 preflight/context/impact grounding，再生成文档。

---

## 仓库结构

```text
skills/
  project-explainer-web/
  feature-release-verifier/
  frontend-slides/
  gitnexus/
  gitnexus-codex-wiki/
  karpathy-guidelines/
  playwright-cli/
  skill/
  ralph-omx-plan/
  visual-explainer/
```

规则：

- 每个 skill 放在 `skills/<skill-name>/`
- 每个 skill 目录必须包含 `SKILL.md`
- 额外的 `scripts/`、`assets/`、`references/`、`agents/` 等目录会和 skill 一起维护

---

## 给 AI Agent 的说明

如果你是 AI Agent，正在读取这个仓库，请遵循以下规则：

1. `skills/` 下的每个目录都表示一个独立的 Codex skill
2. 使用 skill 时先读取该目录下的 `SKILL.md`
3. 只有当 `SKILL.md` 明确引用额外文件时，才继续读取 `scripts/`、`references/`、`assets/` 等内容
4. 相对路径优先相对于 skill 自身目录解析
5. 不要假设 README 之外存在未写明的全局规则
6. 若 skill 自带脚本或模板，优先复用，不要手写重复逻辑

---

## 如何安装

使用 Codex 自带的 `skill-installer`：

### 安装 `project-explainer-web`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/project-explainer-web
```

### 安装 `feature-release-verifier`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/feature-release-verifier
```

### 安装 `frontend-slides`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/frontend-slides
```

### 安装 `gitnexus`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/gitnexus
```

### 安装 `gitnexus-codex-wiki`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/gitnexus-codex-wiki
```


### 安装 `karpathy-guidelines`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/karpathy-guidelines
```

### 安装 `playwright-cli`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/playwright-cli
```


### 安装 `skill`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/skill
```

### 安装 `ralph-omx-plan`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/ralph-omx-plan
```

### 安装 `visual-explainer`

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/visual-explainer
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
rm -rf ~/.codex/skills/project-explainer-web
rm -rf ~/.codex/skills/feature-release-verifier
rm -rf ~/.codex/skills/frontend-slides
rm -rf ~/.codex/skills/gitnexus
rm -rf ~/.codex/skills/gitnexus-codex-wiki
rm -rf ~/.codex/skills/karpathy-guidelines
rm -rf ~/.codex/skills/playwright-cli
rm -rf ~/.codex/skills/skill
rm -rf ~/.codex/skills/ralph-omx-plan
rm -rf ~/.codex/skills/visual-explainer
```

然后重新运行安装命令并重启 Codex。

---

## 如何长期同步

如果你希望多个设备长期同步，推荐使用 `git clone + 软链接`：

```bash
git clone https://github.com/liu-qingyuan/skills-sync-lqy.git ~/skills-sync-lqy
ln -s ~/skills-sync-lqy/skills/project-explainer-web ~/.codex/skills/project-explainer-web
ln -s ~/skills-sync-lqy/skills/feature-release-verifier ~/.codex/skills/feature-release-verifier
ln -s ~/skills-sync-lqy/skills/frontend-slides ~/.codex/skills/frontend-slides
ln -s ~/skills-sync-lqy/skills/gitnexus ~/.codex/skills/gitnexus
ln -s ~/skills-sync-lqy/skills/gitnexus-codex-wiki ~/.codex/skills/gitnexus-codex-wiki
ln -s ~/skills-sync-lqy/skills/karpathy-guidelines ~/.codex/skills/karpathy-guidelines
ln -s ~/skills-sync-lqy/skills/playwright-cli ~/.codex/skills/playwright-cli
ln -s ~/skills-sync-lqy/skills/skill ~/.codex/skills/skill
ln -s ~/skills-sync-lqy/skills/ralph-omx-plan ~/.codex/skills/ralph-omx-plan
ln -s ~/skills-sync-lqy/skills/visual-explainer ~/.codex/skills/visual-explainer
```

之后只需要：

```bash
cd ~/skills-sync-lqy
git pull
```

---


## 外部链接同步说明

`frontend-slides` 是从外部仓库/插件格式同步进来的 skill：

- Upstream: https://github.com/zarazhangrui/frontend-slides
- Upstream plugin path: `plugins/frontend-slides`
- 本仓库安装路径: `skills/frontend-slides`
- 维护说明: `skills/frontend-slides/plugins/frontend-slides/skills/frontend-slides/` 内的文件必须保留为实体文件副本，不要改回 symlink 或只含相对路径的占位文本；否则 Codex 会把嵌套 `SKILL.md` 判定为缺少 YAML frontmatter。

`visual-explainer` 是从外部仓库链接同步进来的 skill：

- Upstream: https://github.com/nicobailon/visual-explainer.git
- Upstream skill path: `plugins/visual-explainer`
- 本仓库安装路径: `skills/visual-explainer`
- 同步记录: `skills/visual-explainer/UPSTREAM.md`

这里保留一份可安装镜像，而不是 git submodule：Codex `skill-installer` 默认通过 GitHub archive 安装，archive 里不会自动展开 submodule，纯 submodule 会导致安装时找不到 `SKILL.md`。

---

## 维护约定

- 新增 skill 时统一放到 `skills/` 下
- skill 目录名使用 ASCII 和 kebab-case
- 说明写在 `SKILL.md`
- 如果某条规则需要让 AI 遵循，请明确写进 `SKILL.md` 或本 README

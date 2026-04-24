# skills-sync-lqy

这是一个用于同步和分发自定义 Codex Skills 的仓库。

当前包含的 skills：

- `project-explainer-web`：生成项目或任务的说明型静态网页，默认输出中文，适合快速帮助人类或 AI 理解仓库、架构和任务背景。
- `feature-release-verifier`：用于验证功能是否具备发布条件，聚合 mock-ui、real-runtime、packaged-smoke 等验证证据并输出发布结论。

---

## 仓库结构

```text
skills/
  project-explainer-web/
  feature-release-verifier/
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
```

然后重新运行安装命令并重启 Codex。

---

## 如何长期同步

如果你希望多个设备长期同步，推荐使用 `git clone + 软链接`：

```bash
git clone https://github.com/liu-qingyuan/skills-sync-lqy.git ~/skills-sync-lqy
ln -s ~/skills-sync-lqy/skills/project-explainer-web ~/.codex/skills/project-explainer-web
ln -s ~/skills-sync-lqy/skills/feature-release-verifier ~/.codex/skills/feature-release-verifier
```

之后只需要：

```bash
cd ~/skills-sync-lqy
git pull
```

---

## 维护约定

- 新增 skill 时统一放到 `skills/` 下
- skill 目录名使用 ASCII 和 kebab-case
- 说明写在 `SKILL.md`
- 如果某条规则需要让 AI 遵循，请明确写进 `SKILL.md` 或本 README

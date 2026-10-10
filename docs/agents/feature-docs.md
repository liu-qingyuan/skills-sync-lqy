# Feature 当前事实与本地门禁

## 读取与维护

- 任务开始执行 `./.feature-docs/run list`：只读名称、状态、freshness、路径与纳管范围，再展开相关页面。中断恢复先运行 `check`，不要根据旧对话假定完成。
- `docs/features/<feature>.md` 按能力保存**当前事实**：行为、限制、源码与公开测试入口。已有能力直接改原页，不为每个补丁另建记录，不追加历史流水账；Git 保存历史，Issues 保存任务进度。
- 只填写已确认的事实。`partial` 表示能力仍不完整；`implemented` 不等于已部署。不要复制代码或维护第二份领域术语表。

## 初始化与升级

仅显式 setup 安装。setup skill 携带 `scripts/feature_docs.py` 和 `templates/feature.md`；相对路径从该 skill 目录解析，`--repo` 指向任务 worktree。

```bash
# 选一个真实能力试用；globs 必须包含它的代码和相关测试，不预先补全全项目。
python3 <setup-skill>/scripts/feature_docs.py --repo <project> install \
  --scope '<actual-code-glob>' --scope '<actual-test-glob>'
```

按模板写对应页面并复核事实，再显式 `review <feature> --confirm`。尚无可确认的能力或测试入口时说明记录门禁未启用，不捏造引用或盖章。模板不是项目事实，不能直接整份当成完成记录。

- `.feature-docs/` 保存项目安装资产与范围；外部安装会复制单个零依赖工具，clone 不依赖全局 skills。项目内已跟踪的原实现可直接复用，不再复制一份。
- `install --scope '<new-glob>'` 只显式追加范围，不删除原范围；覆盖不到本任务时先纳管实际文件，不能为过门禁缩小范围。
- 从新版 setup skill 再执行 `install` 升级工具；不加 `--scope` 就保留原范围。修改过的安装资产或既有自定义 hooks 会被拒绝覆盖；报告冲突，待授权后接入，不能宣称已启用。
- 业务页面位于 `docs/features/`，不放 `.agents/skills/`；同步已安装 skills 不会覆盖它们，也不替项目刷新业务指纹。
- clone 后执行 `./.feature-docs/run install` 恢复 Git hooks；Git 不复制本地 hook 配置。安装资产必须随项目提交，不能被 `.gitignore` 忽略。

## 交付命令

```bash
./.feature-docs/run list
./.feature-docs/run check                           # 工作区，只读
# 先运行项目已有的相关测试，并核对页面事实；review 本身不运行测试。
./.feature-docs/run review <feature> --confirm        # 不自动暂存
# 或绑定已暂存代码，同时保留工作区页面正文：
./.feature-docs/run review <feature> --staged --confirm
./.feature-docs/run check --staged                    # 交付 index
./.feature-docs/run check --ref HEAD                  # 交付 commit
```

提交代码、测试和相关页面，不能只在工作区修好记录。pre-commit 检查真实 index，pre-push 检查实际推送 tip；失败不得报告交付完成。Ralph 复用这套 Git 门禁，不另建记忆或完成调度器。

## 契约与边界

JSON front matter 恰好包含 `title`、`status`、`code`、`tests`、`reviewed_code`；正文包含非空 `## 当前行为`、`## 限制与剩余`。状态只允许 `partial` / `implemented`；引用为仓库内相对 globs，测试可位于任意真实目录，不限语言。指纹覆盖声明、匹配路径、文件模式及代码/测试内容，不包含页面本身。

退出码：`0` 记录与选定版本一致，`1` 缺失/过期/冲突，`2` 调用或环境错误。检查不会写记录；复核必须 `--confirm`。

仅保证**声明范围内**的归属和版本绑定，不判断自然语言是否真实，不运行或替代业务测试，不硬限制 issue 关闭。Git 忽略的未跟踪文件不受管；受管 symlink/gitlink 拒绝，无关链接不展开。拥有 Shell 权限者仍能绕过本地 hooks；删除门禁配置也不是受保护的安全边界。

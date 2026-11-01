# Feature 记录

- 已启用时先运行 `./.feature-docs/run list`，只展开相关页面；中断恢复用 `check` 查过期记录，不自动盖章。
- `docs/features/<feature>.md` 只保存当前事实：改原页，不按补丁新建或追加日志。Git 保存历史，Issues 保存任务进度。
- 标题用 Markdown H1，正文描述用途和限制，保留非空 `## 当前行为`、`## 限制与剩余`。JSON 仅 `paths`（关联源码与测试的真实相对 globs）、`fingerprint`（工具维护的已确认版本指纹，不表示代码审查）。旧格式仍兼容，不自动改写。

## 同 worktree 并行（独立小任务）

- 派发前指定单一整合者，以及各 worker 不相交的实际写入文件和记录页；`paths` 是引用，不是写锁。同页、公共合同/样式/配置或其他共享文件由一人负责，不能按“模块名字不同”推定独立。
- worker 只改自己的代码、测试和页面，运行无共享产物的聚焦测试；仅已启用项目的 worker 再执行 `review <feature> --confirm`。待启用项目的 worker 只交回就绪证据，由整合者接续。其他页面未完成不阻断已启用项目的独立复核；全局 list/check 仍可能失败，不替别人改页或盖章。
- 只有整合者改共享 index、安装/范围配置，执行 commit/push/issue 收口及完整套件、共享 build/服务器测试。worker 不 add/reset/stash/checkout，不用 `review --staged`；需要共享文件时交回整合者串行处理，不另造分支或 worktree。
- 整合者只暂存获准交付的完整文件，核对 `git diff --cached --name-only` 和暂存 diff 内容后按下方流程交付；他人未暂存修改不混入提交。记录门禁不是写入隔离或调度器。

## 交付（单任务或已指定的整合者）

运行项目原有测试并核对事实，然后：

```bash
./.feature-docs/run review <feature> --confirm
# 一并暂存代码、测试、页面；需要绑定 index 时 review 可加 --staged。
./.feature-docs/run check --staged
# commit 后：
./.feature-docs/run check --ref HEAD
```

review 不自动暂存、不代替测试。pre-commit 查 index，pre-push 查实际 tip；失败先修复，不报告交付完成。

## 首次启用与延后接续

项目状态保存在 `docs/agents/feature-docs.md` 的 `## 项目启用状态` 下，由显式 setup 写入；安装 skill、同步模板或旧版“未启用”说明均不构成授权。明确停用决定优先。

- 显式 setup 在首次启用前先记录独立一行 `启用状态：待启用（已授权）`；已有真实能力且业务测试通过后按下方流程启用。尚无能力或业务测试未通过时保留待启用授权，不创建虚假能力记录、不安装 hooks。
- 首个真实能力及其测试通过后，仅项目状态明确为 `启用状态：待启用（已授权）` 时，由单票交付者或整合者在进入双轴 review 前接续首次启用。worker 只交回能力、文件范围与测试证据，不安装 hooks 或修改共享配置。尚无真实能力时继续待启用；无延后授权的旧项目保持原流程，仅提示显式启用。
- 接续时只定位已安装 setup skill 的工具与模板，不执行完整 setup、不修改 GitHub 标签。工具/模板相对该 skill 目录，项目数据相对当前交付 worktree；缺少工具时报告阻碍，不猜路径或冒称启用。
- 先运行业务测试并核对事实，只为本次一个真实能力选择源码与测试 globs，按模板建立记录，再安装、`review <feature> --confirm`、`list` / `check` 并核对 `core.hooksPath`。成功后将项目状态改为 `启用状态：已启用`，记录与门禁资产一并纳入本次 review 和下方交付检查，不补全历史。
- hooks/资产冲突时记录 `启用状态：未启用（冲突）` 并报告，不能覆盖定制或伪称门禁通过；需用户解决或明确授权后再启用。已启用项目仍按既有流程维护，不借接续重置范围或刷新业务指纹。

```bash
python3 <setup-skill>/scripts/feature_docs.py --repo <project> install --scope '<code-glob>' --scope '<test-glob>'
```

`install --scope` 只追加范围；从新版 setup 工具执行 `install` 升级，保留范围与业务页。记录不放 `.agents/skills/`；门禁资产随项目提交，不忽略。clone 后 `./.feature-docs/run install` 恢复 hooks。

只保证声明范围的引用、归属和版本绑定，不判断散文真假、执行业务测试或硬限制 issue 关闭；hooks 可绕过。受管链接拒绝，无关链接不展开，Git 忽略的未跟踪文件不受管。退出码 `0/1/2`：一致/缺失过期冲突/调用环境错误；check 只读。

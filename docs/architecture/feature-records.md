# Feature 微文档接入

## 当前 → 目标

当前：setup 配置 tracker；implement 通过 Git/issue 记录交付；仓库没有统一的 Feature 同步门禁。目标：在这些既有入口接入一个本地 CLI；不新增 skill、调度器、数据库或 CI 服务。

```mermaid
C4Context
  title Feature 记录接入的系统上下文
  Person(agent, "开发者 / Agent", "实施已授权任务")
  System(skills, "LQY skills", "分发约定和本地验证工具")
  System_Ext(project, "目标 Git 项目", "拥有源码、测试与 Feature 记录")
  System_Ext(tracker, "GitHub Issues", "保存任务与完成记录")
  Rel(agent, skills, "显式初始化 / 加载实施规则")
  Rel(skills, project, "安装门禁，不覆盖业务记录")
  Rel(agent, tracker, "记录授权任务的交付")
```

```mermaid
C4Container
  title 目标项目中的本地接入
  Person(agent, "开发者 / Agent", "复核当前事实")
  Container(cli, "Feature CLI", "Python 标准库", "安装、索引、快照校验与显式复核")
  Container(git, "本地 Git", "Git / shell hooks", "提供 index、commit 与提交边界")
  ContainerDb(records, "项目记录", "JSON + Markdown", "项目拥有的范围配置和微文档")
  Rel(agent, cli, "读取索引 / 复核指定功能", "CLI")
  Rel(git, cli, "提交前查 index；推送前查实际 tip", "CLI")
  Rel(cli, git, "读取精确快照", "Git CLI")
  Rel(cli, records, "验证；仅显式复核更新指纹", "文件")
```

## Module / Contract / Governance

- **Module / Interface**：setup skill 携带唯一实现；公共 CLI 为 `install/list/check/review`，项目统一入口 `.feature-docs/run`。内部隐藏 Git 快照、归属、指纹和安装收据。
- **Adapter / Seam**：Git 是真实 Adapter；以 CLI 退出码和真实 commit/push 为 test surface。工作区、index、commit 是不同的验证输入，不能互借内容。
- **Boundary / Locality**：`.feature-docs/config.json` 记录项目选择的 `managed` 范围与安装资产；`docs/features/` 是项目数据，不放入会被 skills 同步覆盖的安装目录。
- **Governance**：仅显式 setup 安装；既有 hooks、修改过的安装资产或冲突配置则拒绝覆盖。升级保留范围和业务记录；不自动生成能力事实或刷新业务指纹。
- **范围**：仅约束声明的 source globs；未纳管的目录不宣称受保护。本仓库先试用 setup、implement、已安装 skills 同步三个能力，不为每个 skill 复制说明。
- **质量边界**：Git hooks 检查记录结构、引用和版本绑定；业务测试仍由项目已有验证命令执行。不把散文准确性、业务测试通过、issue 关闭或不能绕过 hooks 伪装成 CLI 保证。
- **不变项**：to-spec/to-tickets、Mermaid gate、Ralph 调度与 Git-bound issue 契约不变；根 `./setup` 仍仅复制架构约束。

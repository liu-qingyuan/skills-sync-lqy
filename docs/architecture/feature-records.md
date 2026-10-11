# Feature 微文档接入

## 当前 → 目标

当前：Feature CLI 已接入既有 Git/issue 交付，但 review 会校验所有页面，另一个 worker 的未完成页面可能阻断独立任务。目标：同一 worktree 的独立文件可并行实现和复核，由单一整合者串行写 Git 与共享构建产物；review 只解析指定页面，check 仍校验完整交付快照。不新增分支、worktree、调度器或锁服务。

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

```mermaid
sequenceDiagram
  participant A as Worker A
  participant B as Worker B
  participant CLI as Feature CLI
  participant I as 单一整合者
  participant Git as 共享 Git index
  par 独立文件实现与验证
    A->>CLI: review feature-a --confirm
    CLI-->>A: 只复核 A 页面与关联文件
  and 独立文件实现与验证
    B->>CLI: review feature-b --confirm
    CLI-->>B: 只复核 B 页面与关联文件
  end
  A->>I: 交回文件范围与验证证据
  B->>I: 交回文件范围与验证证据
  I->>Git: 仅暂存获准交付的完整变更
  I->>CLI: check --staged
  CLI-->>I: 完整 index 检查结果
  I->>Git: 串行 commit / push
```

## Module / Contract / Governance

- **Module / Interface**：setup skill 携带唯一实现；公共 CLI 为 `install/list/check/review`，项目统一入口 `.feature-docs/run`。记录仅保留 `paths/fingerprint`，标题用 Markdown H1；用途和限制在正文，任务进度归 Issues。`paths` 关联源码与测试，`fingerprint` 绑定已确认的文件版本，不表示代码审查结论。旧三/五字段仍可读取、复核且不自动改写；内部隐藏 Git 快照、归属、指纹和安装收据。
- **Adapter / Seam**：Git 是真实 Adapter；以 CLI 退出码和真实 commit/push 为 test surface。工作区、index、commit 是不同的验证输入，不能互借内容。
- **Boundary / Locality**：`.feature-docs/config.json` 记录项目选择的 `managed` 范围与安装资产；`docs/features/` 是项目数据，不放入会被 skills 同步覆盖的安装目录。
- **Governance**：仅显式 setup 安装；既有 hooks、修改过的安装资产或冲突配置则拒绝覆盖。升级保留范围和业务记录；不自动生成能力事实或刷新业务指纹。并行任务先分配不相交的实际写入文件与记录页（paths 是引用，不是写锁）；worker 不写共享 index、提交、配置或构建产物，由已指派整合者收口。规则不是 Shell 隔离或任务锁，共享文件仍须串行。
- **范围**：仅约束声明的 source globs；未纳管的目录不宣称受保护。本仓库先试用 setup、implement、已安装 skills 同步三个能力，不为每个 skill 复制说明。
- **质量边界**：Git hooks 检查记录结构、引用和版本绑定；业务测试仍由项目已有验证命令执行。不把散文准确性、业务测试通过、issue 关闭或不能绕过 hooks 伪装成 CLI 保证。
- **不变项**：to-spec/to-tickets、Mermaid gate、Ralph 调度与 Git-bound issue 契约不变；根 `./setup` 仍仅复制架构约束。

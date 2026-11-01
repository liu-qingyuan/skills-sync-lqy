# Feature 微文档接入

## 当前 → 目标

当前：空仓库 setup 因没有真实能力而跳过门禁，后续实施只提示重跑 setup，缺少接续。目标：显式 setup 将延后首次启用的授权保存在项目说明；首个真实能力及测试通过后，由单票交付者或整合者在 review 前接续安装。无授权的旧项目保持原流程。CLI 和记录格式不变，不新增配置、调度器或锁服务；独立页面仍可并行复核，共享 Git 与构建仍串行交付。

```mermaid
C4Context
  title Feature 记录接入的系统上下文
  Person(agent, "开发者 / Agent", "实施已授权任务")
  System(skills, "LQY skills", "分发约定和本地验证工具")
  System_Ext(project, "目标 Git 项目", "拥有源码、测试与 Feature 记录")
  System_Ext(tracker, "GitHub Issues", "保存任务与完成记录")
  Rel(agent, skills, "显式 setup 授权 / 加载实施规则")
  Rel(skills, project, "按项目授权立即或延后首次安装，不覆盖业务记录")
  Rel(agent, tracker, "记录授权任务的交付")
```

```mermaid
C4Container
  title 目标项目中的本地接入
  Person(agent, "开发者 / Agent", "复核当前事实")
  Container(cli, "Feature CLI", "Python 标准库", "安装、索引、快照校验与显式复核")
  Container(git, "本地 Git", "Git / shell hooks", "提供 index、commit 与提交边界")
  ContainerDb(records, "项目记录", "JSON + Markdown", "项目拥有的范围配置和微文档")
  Rel(agent, cli, "按项目授权安装 / 读取索引 / 复核指定功能", "CLI")
  Rel(git, cli, "提交前查 index；推送前查实际 tip", "CLI")
  Rel(cli, git, "读取精确快照", "Git CLI")
  Rel(cli, records, "验证；仅显式复核更新指纹", "文件")
```

```mermaid
sequenceDiagram
  participant U as 用户
  participant S as 显式 Setup
  participant D as 项目 Feature 说明
  participant I as 单票交付者或整合者
  participant CLI as Feature CLI
  U->>S: setup 授权，不启动业务实施
  S->>D: 首次启用前记录待启用（已授权）
  alt 已有真实能力且业务测试通过
    S->>CLI: 安装、建记录并验证门禁
  else 尚无能力或业务测试未通过
    S->>D: 保留待启用，不装 hooks
  end
  U->>I: 授权首个能力实施
  I->>I: 实现并通过业务测试
  I->>D: 读取项目启用状态
  alt 待启用（已授权）且无明确停用
    I->>CLI: review 前安装、建记录并验证
    alt 安装与校验成功
      I->>D: 改为已启用，纳入本次 review 和交付
    else hooks 或资产冲突
      I->>D: 报告未启用（冲突），不覆盖定制
    end
  else 无延后授权
    I->>I: 保持原流程，仅提示显式启用
  end
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
- **Governance**：显式 setup 包含首次安装及空仓库延后接续的授权；仅该次 setup 可在项目 `docs/agents/feature-docs.md` 的 `## 项目启用状态` 下记录 `启用状态：待启用（已授权）`，明确停用决定优先。首个能力测试通过后，由单票交付者或整合者在 review 前接续；worker 只交回就绪证据。安装 skill、同步模板和旧版“未启用”说明均不授权；接续也不重跑完整 setup 或改标签。CLI 不解释授权状态，由 skills 执行此约定；既有 hooks、修改过的安装资产或冲突配置仍拒绝覆盖。升级保留范围和业务记录；不自动生成能力事实或刷新业务指纹。独立页面可并行复核，共享配置、Git 和构建由单一整合者串行处理；规则不是锁或调度器。
- **范围**：仅约束声明的 source globs；未纳管的目录不宣称受保护。本仓库先试用 setup、implement、已安装 skills 同步三个能力，不为每个 skill 复制说明。
- **质量边界**：Git hooks 检查记录结构、引用和版本绑定；业务测试仍由项目已有验证命令执行。不把散文准确性、业务测试通过、issue 关闭或不能绕过 hooks 伪装成 CLI 保证。
- **不变项**：to-spec/to-tickets、Mermaid gate、Ralph 调度与 Git-bound issue 契约不变；根 `./setup` 仍仅复制架构约束。

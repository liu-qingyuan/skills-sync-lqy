# Matt 中文 Skills 本地化语言

本上下文定义本仓库维护 Matt Pocock 中文 skills 时使用的统一中文术语。它只记录术语，不记录实现细节。

## Language

**追问**:
`grilling / grill` 的统一译法，表示持续提问、压实决策、打磨方案。
_Avoid_: 烧烤、拷问、盘问、采访

**追问会话**:
一次 `/grilling-zh` 流程。
_Avoid_: 烧烤会议、盘问会议、采访会话

**追问循环**:
围绕一个候选方案反复澄清约束、依赖、测试和接缝的流程。
_Avoid_: 烧烤循环

**Agent**:
保留英文 `agent`；必要时可写“AI agent”。普通“代理”只在技术含义明确时使用。
_Avoid_: 特工、代理人

**Issue**:
保留英文 `issue`，指 GitHub/GitLab issue 或等价工作项。
_Avoid_: 问题、票证、工单混用

**Issue tracker**:
保留英文 `issue tracker`，必要时补充“问题跟踪器”。
_Avoid_: 票证系统、问题系统

**Ticket**:
保留英文 `ticket`，指 decision-mapping 中等待调研、原型或追问解决的决策条目。
_Avoid_: 票证、门票、故障单

**PR**:
保留 `PR`，首次可写“PR（Pull Request）”。
_Avoid_: 拉取请求全文反复出现

**Triage**:
保留 `triage`，必要时解释为“分流/分诊”。
_Avoid_: 分类

**Label**:
统一译为“标签”。
_Avoid_: 角色字符串、状态字符串混用

**Brief**:
统一写为 `brief`，如 `agent brief`。
_Avoid_: 简介、摘要、简短评论混用

**工作流**:
`workflow` 的统一译法。
_Avoid_: 工作流程

**交接**:
`handoff` 的统一译法。
_Avoid_: 移交

**上下文**:
用于 AI context window；DDD 文件语义使用 `CONTEXT.md` 或“领域上下文”。
_Avoid_: 语境

**领域语言**:
`domain language` 的统一译法。
_Avoid_: 域语言

**深模块**:
`deep module` 的统一译法，表示小接口隐藏大量复杂性的模块。
_Avoid_: 深度模块

**模块加深**:
`deepening` 的统一译法，表示把浅模块或浅模块簇改造成深模块。
_Avoid_: 深化模块

**加深机会**:
`deepening opportunity` 的统一译法。
_Avoid_: 深化机会

**接缝**:
`seam` 的统一译法，表示无需修改某处即可改变行为的位置。
_Avoid_: 边界；除非明确指 DDD bounded context

**设计决策树**:
`design tree` 的统一译法。
_Avoid_: 设计树

**Markdown**:
保留英文 `Markdown`。
_Avoid_: 降价

**仓库**:
`repository / repo` 的统一译法。
_Avoid_: 存储库、回购

**Token**:
保留英文 `token`。
_Avoid_: 代币

**Context map**:
统一写作 `CONTEXT-MAP.md` 或 context map，表示多上下文仓库中列出各上下文位置和关系的索引文件。
_Avoid_: 地图、每个人居住的地方

**按需创建**:
`create lazily / lazily create` 的统一译法，表示只有出现真实写入需求时才创建文件或目录。
_Avoid_: 懒惰地创建

**调用 skill**:
`invoke / fire a skill` 的统一译法，表示触发并运行某个 skill。
_Avoid_: 解雇、发射

**合理性检查**:
`sanity check` 的统一译法，表示快速确认某个判断没有明显问题。
_Avoid_: 健全性检查

**语义本地化**:
先理解英文上游在具体 skill 场景中的意图，再用自然中文表达的翻译方式。
_Avoid_: 逐词机翻、逐字硬翻

# Matt Pocock skills 上游更新与 Pi / Codex 适配调查

调查日期：2026-10-09。范围：本仓库已记录上游基线到调查时最新 HEAD；视频用于解释作者意图，实际变更以源码、commit 和 CHANGELOG 为准。

**结论：更新知识和修复，不照搬执行框架。保留现有单 Ticket + Pi / Ralph 主流程；优先引入 PR 证据、人工复盘、文档写作原则及安全修复；暂不默认引入全 spec 多 agent 调度。**

此报告保留**授权实施前**的调查快照；下述版本、数量和验证结果均以当时为准。用户随后批准选择性适配，实际交付与最新审阅 SHA 见 [交付报告](mattpocock-sync-2026-10-09.md)。

## 1. 精确版本与当前状态

| 对象 | 实查结果 |
| --- | --- |
| 本仓库 / GitHub 默认分支 HEAD | `7879fb88d9614478f2d66f1571f13ea85f411136`，2026-07-28，`refactor(review): clean accepted changes before closure` |
| 本仓库记录的上游基线 | `d574778f94cf620fcc8ce741584093bc650a61d3`，对应 **v1.1.0**；上游 commit 时间 2026-07-08 |
| 本地引入该基线的提交 | `9632bc0e163780d82490fed8437315b49b3b1e28`，2026-07-09；这不是上游发布日期 |
| 调查时最新正式 release | **v1.3.1**，2026-10-04；tag commit `24fe0ef7737efae15c87225755e9f6f5965e4888` |
| 调查时最新 main HEAD | `b0618bc436ad893b3c5e84e55fba86586d34a404`，2026-10-08；已在结束调查前再次核对 |
| 基线到最新 HEAD | **269 个提交，含 merge commits**，不等于 269 项 skill 功能变化 |
| 本地版本标识 | 没有 Git tag；marketplace 各分组没有版本字段。不能把个人版直接称作官方 v1.3.1 |
| 当前三层数量 | 英文镜像 38；中文 baseline 38；Matt LQY 安装版 35；全仓库可安装版 50 |
| 最新上游数量 | 仍是 38，但名称和分类已变：Engineering 20、Productivity 7、In-progress 7、Misc 4 |

来源：`docs/upstream-mirrors/mattpocock-skills.md`、各镜像 provenance、Git 历史及 GitHub API。[完整上游比较][compare]、[v1.3.1 release][release]。

**“最新正式版”和“最新源码”必须分开。** 若追最新，建议记录为“v1.3.1 + main 修复，审阅到 `b0618bc…`”，而不是仅写 v1.3.1。个人版仍有独立取舍，不能因镜像已更新就声称所有 LQY 行为与上游一致。

## 2. 视频到底说了什么

视频：[New Skills! v1.3 brings /pr, /implement-spec, and /retro][video]，Matt Pocock，2026-10-05，14 分 34 秒。本次获取了视频元数据和英文自动字幕，并完整读取字幕；自动字幕的拼写以对应源码校正。

| 时间 | 作者的内容 | 对我们意味着什么 |
| --- | --- | --- |
| 00:25–04:54 | `implement-spec`：spec + tickets，任务依赖图，ready frontier，独立 worktree，汇入 integration branch，最后 review | 保留任务图知识，不默认采用整个调度实现 |
| 01:49–02:20、03:08–03:19 | **作者更推荐确定性脚本循环：可靠、便宜、每次运行相同；agent 调度是还没搭好脚本循环时的入门折中** | 不需要为了追版本把 Pi / Ralph 改成 agent babysitting |
| 02:44–02:58 | 作者说 subagents 现在能再生成 subagents | 是其运行环境的能力，不是选择同一个模型就自动获得的能力 |
| 04:54–08:10 | `pr`：最小视觉摘要、Before / After 证据、Merge Danger | 很适合吸收；不是自动开 PR 或自动合并的流程 |
| 08:10–09:37 | `CONTEXT.md` → `GLOSSARY.md`：旧名称过于模糊，文件实际已经只是术语表 | 文件契约迁移，不是要求放弃领域建模或重做架构 |
| 09:37–14:06 | `retro`：从真实会话寻找环境、工具和 guardrail 问题 | 值得增加人工触发的复盘 |
| 12:34–13:33 | **不要自动执行 retro 的每项建议**；持续自动修复会追逐误报、把工作流带偏 | 复盘输出建议和证据，修改仍由人决定 |

视频不是最新版本证明。例如视频谈到当时 release 状态的插曲，调查时 GitHub 已能查到 v1.3.0 与 v1.3.1；应以当前 API / Git 为准。

## 3. 从 v1.1.0 到现在，上游的实际变化

### 3.1 新增、改名、迁移和删除

| 上游变化 | 内容 | LQY 建议 |
| --- | --- | --- |
| 新增 `implement-spec` | 全 spec 的 task graph 调度；探索、实现、合并、review；实现 worker 各自 worktree | **暂不作为默认安装 / 主流程**。镜像和翻译可以跟进，调度保留现有 Ralph |
| 新增 `pr` | PR body 的 Summary / Evidence / Merge Danger 格式 | **优先新增 `pr-lqy`**，自动匹配“写 PR 正文”；不改变直接 commit/push 策略 |
| 新增 `retro` | 对真实会话提出环境改善建议；机械问题交给确定性检查，判断问题交给 review standards | **优先新增 `retro-lqy`**，仅人工触发、仅建议；日志按 Pi / Codex 实际来源读取，输出脱敏 |
| `writing-great-skills` → `writing-for-agents` | 不只写 skill，也覆盖 AGENTS.md / CLAUDE.md 和引用文档；词汇并入正文，skill mechanics 独立；改为 model-invoked | **新增 `writing-for-agents-lqy`** 并切换活跃引用；旧 `writing-great-skills-lqy` 保留为显式 legacy，不自动删除 |
| 新增 `to-questionnaire` | 为需要他人回答的决策生成问卷；追问的是“发给谁、需要什么回复”，不是让用户替对方答题 | 可选引入，不是本轮必需 |
| 新增 `wait-what` | 当前回复不易理解时，带缺失上下文重述 | 可选；中文语义适配，不必复刻英语风格标准 |
| `wizard` 从 beta 升为 Engineering / model-invoked | 为只有人能执行的授权、配置、迁移步骤生成交互 bash 向导；后续修了输入、env quoting、symlink、EOF 等问题 | 当前没有 wizard-lqy 安装版；仅镜像与翻译，有真实手工配置需求再引入，不自动读写凭据 |
| 新增 beta `chief-of-staff` | 长会话协调 subagents，全部工作委派，可能建议 schedule，持续改造环境 | **不建议纳入日常默认**：成本、scope 扩张和自动调度倾向不符合当前最小 Ticket 流程 |
| 新增 beta `setup-ts-deep-modules` | 用 dependency-cruiser 约束 TS 包 entry points / 私有子目录，并做 pass → fail → pass 验证 | 可吸收“边界规则要证明会失败”的知识；不要为更新 skill 自动加 TS 依赖或强制改项目目录 |
| 删除四个 deprecated skills | `design-an-interface`、`qa`、`request-refactor-plan`、`ubiquitous-language`；能力由设计、triage、spec、domain-modeling 等现存 skills 承担 | 默认推荐中退休；仍被使用的个人版先标明 frozen / personal，不直接删除 |
| 删除 `resolving-merge-conflicts` | 作者认为无需专用 skill，普通 agent 可以处理 | 不必照删当前 `resolving-merge-conflicts-lqy`；可以作为个人冻结版保留，标明不再跟随上游 |
| 删除 personal `edit-article`、`obsidian-vault` | 作者机器专用、非通用产品 | 不再算作持续维护的上游功能；个人需要时单独保留 / 重审路径 |
| Misc 明确冻结 | 四项仍存在，但上游不维护 | Claude hook 项不能当作 Pi / Codex 通用保护；不把 frozen 当作最新维护 |

按 skill 身份比较：8 个新增名称、8 个离开名称，其中包含 writing skill 的改名；另有 wizard 分类迁移。**总数恰好仍是 38，数量检查通过不代表内容已同步。**

### 3.2 现有核心 skills 的行为与知识变化

- **Grilling / grill-me / grill-with-docs / triage**：从一次一个问题改为按依赖 **frontier 分轮提问**。独立问题可以同轮，依赖未决答案的问题留到下一轮；facts 由 agent 查，decisions 由人答；确认之前不执行。最新修复要求“yes”接受推荐答案。建议吸收依赖意识和清晰确认，但保留用户单问偏好；查事实不必强制每次生成 subagent。
- **Writing-for-agents**：写作纪律从 skill 推广到所有 agent 文档。新增 / 强化 **cache** 判断：package.json、配置、目录和 `--help` 本来就是事实来源，容易查到的内容不应再抄一份；文档重点保存查不到的约定、理由和 gotcha。常驻 context pointers 付每轮 token 成本，正文按需展开；完成标准应可观察、覆盖必要行为。适合吸收，不把它变成更多常驻说明。
- **Wayfinder**：明确 **Decision ticket** 是决策问题，不是实施 Ticket；research 可以后台处理，其余 HITL 不能由 agent 替人回答。最新要求 wayfinder 不带 `ready-for-agent` 等 triage 状态、先拿到真实 issue id 再互引、研究分支不提 PR。我们应采纳防误入 Ralph 的语义和标签隔离，不默认添加一套 research 调度器。
- **Prototype**：logic 原型从终端 app 改为无安装、可双击的单 HTML，含 free-play 和 guided walkthroughs；原型是可重放的一手证据，不是完成后只能删掉。建议采纳交互 HTML；保留证据按项目现有约定，不强制每次生成 / push 分支。
- **Improve-codebase-architecture**：扫描前先按用户方向或近期 Git 变更热点缩小 scope，避免整理永不改动的角落。建议采纳；没有新增一套必须全仓改造的深模块理论。
- **TDD**：最新 seam 提案要写清“能发现什么、会漏什么”。上游继续保留红绿循环，且明确重构归 review；**我们当前 LQY 是 RED → GREEN → REFACTOR，这是真实个人差异，应保留绿色时的小范围重构，不机械覆盖**。从 spec 继承已确认 seam，只有真实歧义才询问，避免 Ralph 每 Ticket 被人工重复确认阻塞。
- **Diagnosing-bugs**：新增命令、输出和 captured artifacts 的 **Redact** 提示规则，不是数据清理器。LQY 只允许在展示副本隐藏确认的真实凭据，保留诊断结构和必要标识；不得回写 `.env`、原始日志、HAR、数据库、fixture 或真实本地复现输入，不增加安全依赖 / 认证整改。隐藏与诊断保真冲突时先说明并问用户。只有**已经尝试**临时 mutation 强制 RED 时，才用 pristine diff 证明改动实际落地；不是要求每次制造失败。事后保留证据与 follow-up，由人选择 retro 或架构调查，不自动整改。
- **Code-review**：上游仍是 Standards / Spec 两轴，保留 Fowler smell baseline；最新主动搜索完整 standards 文件，并修改 subagent dispatch 方式。**当前 LQY 有意不主动加载通用 smell checklist、最多四次 review Agent 调用、限制 focused closure、冻结 clean 文件范围；这些应保留**。仅合并明确标准来源的发现能力，不恢复扩大审查范围的规则。
- **To-spec / to-tickets**：清理 PRD 旧称；本地文件 tracker 改为一 Ticket 一文件；真实 tracker 的子 Ticket 挂到来源 issue 下；依赖优先 native edges。我们继续 GitHub-only。**不能照搬“native blockers 存在就省略正文 Blocked by”**：当前 Ralph 明确要求 `## Blocked by` 和 `## Git`，应保留 worker 的消费契约。
- **Implement**：用户给 Ticket reference 后，先实际 fetch 并说明标题；明确加载 tdd / code-review。这适合采纳，但保留个人版单 Ticket、oversized stop、验证后 commit/push 和按完成度关闭 issue。
- **Setup / tracker templates**：标签不仅写到文档，还要创建 GitHub 上缺失的 labels；读取 issue 时取 title/body/labels/comments；sub-issue 用受支持的 CLI / API。保留我们的固定 labels、中文 AGENTS.md、Issues-only，不恢复通用 tracker 访谈。
- **Ask-matt**：增加 phase boundary 判断：继续、清理上下文、portable handoff、bounded subagent、最后才 compact；最新要求先读实际 skill 再描述能力。可以采纳选择原则，不照搬特定模型的“150K smart zone”阈值。
- **Teach**：workspace 路径从调用目录解析，格式模板从 skill 目录解析；quiz 正确答案位置要变化。适合直接采纳。
- **Handoff / claude-handoff**：明确临时目录解析与安全传入 Claude 后台命令。可更新通用 `handoff-lqy` 的临时目录说明；**不要覆盖我们仅输出 prompt、不写文件的 `handoff-out`，也不引入 `claude --bg`**。

其余 writing beta / misc 的改动有元数据和文字整理；没有理由把它们升级成默认工程流程。英文移除 em-dash 的风格改动不必变成全仓中文重写。

### 3.3 视频之后的最新修复，不能漏同步

`v1.3.1..b0618bc` 的关键 commit：

| 日期 / commit | 变化 | 处理 |
| --- | --- | --- |
| 10-07 `f3fc563` | diagnosing mutation 要证明实际落地 | 优先采纳 |
| 10-07 `3da8c01` | code-review 搜索 standards、tracker 间接引用、foreground 并行指令 | 采纳 sources / pointer，不照搬 host 的 dispatch 参数 |
| 10-07 `5b7cade` | setup 创建缺失标签，修 gh / glab 命令 | 只取 GitHub 对应修复 |
| 10-07 `6d6a5b9` | implement fetch Ticket 并讲标题 | 采纳 |
| 10-07 `95249b0` | grilling 的 yes 表示接受推荐 | 采纳 |
| 10-07 `3f59913` | seam 的 catches / misses | 采纳 |
| 10-07 `ad5400b` | teach 路径与答案位置 | 采纳 |
| 10-07 `8295b8e` | wayfinder 标签隔离、真实 refs、research 无 PR | 采纳防污染规则，执行按个人授权 |
| 10-06 `cffab50` / `9e2abf8` | to-tickets 明确挂父 issue，native blockers 时省略正文 | 挂父 issue可取，省略正文与 Ralph 契约冲突，拒绝 |
| 10-06 `868c4cf` | wizard 输入、env、symlink、EOF 等修复 | 镜像 / baseline 跟进，暂不强制安装 |
| 10-08 `b0618bc` | README 新增各 harness 安装说明，突出 plugin 自更新 | 不订阅官方原版覆盖个人适配；自更新细节属上游说明，本次未实际安装测试 |

[v1.3.1 后比较][post-release]。

## 4. Pi / Codex 兼容性：模型和 harness 不是一回事

本机实查：**Pi 1.1.0；Codex CLI 0.156.1；gh 2.96.0**。换 OpenAI / Codex 模型不会把 Claude 的工具、沙箱、hooks 或 agent 生命周期带到 Pi。

| 能力 | Pi | 当前 Codex CLI | LQY 适配 |
| --- | --- | --- | --- |
| 加载 skill | 核心按描述匹配后读取 `SKILL.md`，可显式 `/skill:name` | 显式 `$name` 或隐式匹配后加载 | 指示“读取并执行对应 SKILL.md”；不要假设一定有 `Skill` tool |
| User-only 触发 | `disable-model-invocation: true` | `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false` | 按个人依赖分类维护，不机械套官方分类；Ralph 已授权加载 implement 的链路不能断 |
| 多 agent | 核心不内置；当前会话通过扩展暴露 `Agent` / `SubagentWorkflow` | `multi_agent` 为 stable / true | 不是不支持，是接口和运行条件不同；探测能力，不硬编码 Claude `Task` / Explore / Plan |
| worktree | 当前 Agent 工具可选 worktree；不是所有 Pi 环境都具备 | worktrees stable / true；CLI 有 `--worktree` | 启动 subagent 不等于自动隔离；开始写前确认真实 branch/base/worktree |
| 并行与汇总 | 本会话 foreground Agent 调用本身串行；并行须同一消息启动 background agents，再汇总 | 按实际 native subagent 接口 | 不照抄上游最新“foreground calls together”指令 |
| hooks / permission | 核心无默认沙箱 / 每次审批；扩展可以拦截工具 | hooks、plugins stable / true；有沙箱和审批 | Claude hook schema 不是通用；跨 host 需独立验证，不在 skill 更新时顺便改全局设置 |
| nested agents | 取决于扩展权限和子 agent 工具集 | 取决于 agent 配置 / 限制 | 不要求子 agent 再调度；保留 bounded review，运行层约束才是硬保证 |

官方上游在 v1.2.3 已主动删除部分 Claude 专用工具 / agent type 名称，并非只支持 Claude。但是最新依赖调用仍写 `Call the Skill tool`，当前 Pi 会话没有这个工具，必须适配。

最新上游**没有新增独立的 `.claude/agents` / `.codex/agents` 角色定义文件**。`implementer`、`merger`、`exploration` 是 skill 文本描述的职责；`agents/openai.yaml` 是 skill 的 Codex 元数据，不是一个 worker 的实现。

上游 10-06 明确拒绝在每个 skill 内加递归深度规则，认为应由 harness 限制。[相关决定][recursion]。我们不能据此删掉现有 leaf reviewer / 四次预算等个人约束；反而应确认运行层权限确实生效，不能把自然语言禁令当硬隔离。

### 当前 metadata 缺口

- 当前 **35 个 Matt LQY skills 都没有 `agents/openai.yaml`**；全仓其他部分有少量这种文件。
- 镜像维护文档明确说，为通过本机 Codex `quick_validate.py`，省略了上游 `disable-model-invocation` 等 frontmatter。
- 当前 Pi 已识别该字段，Codex 有自己的 policy；旧 validator 的允许字段仍不包括它。**校验通过不代表 user-only 语义被保留**。
- 更新前应调整本仓库的校验策略，支持必要的 host metadata，并检查触发策略。不要直接修改用户的 Codex 系统 validator，也不要为了通过旧检查丢掉权限语义。
- 不是所有 upstream user-only 都应照抄：`implement-lqy` 已有 Ralph worker 加载场景，应保留已授权自动链路；`retro` 和启动长期循环则不能因模型判断擅自触发。
- 不写死 Opus / Haiku 等 Claude 名称，也不在通用 skill 中绑死某个 OpenAI 模型版本。运行时由用户 / harness 选择模型。

Codex 多 agent、plugin、worktree 结论来自本机 CLI help / feature 输出；本次未实际启动 Codex worker、安装 plugin 或验证其 worktree / hooks 运行结果。参考 [Codex skills][codex-skills]、[subagents][codex-subagents]，以及本机 Pi README、`docs/skills.md`、`docs/security.md`。

## 5. 必须保留的个人差异与迁移风险

### 5.1 保留，不被“同步”抹掉

1. GitHub Issues-only；外部 PR 不作为 triage / Ralph 请求入口。
2. 中文 issue、comment、summary；label / 命令 / 标识符保留原 token。
3. `## Git` 的 branch / base branch / 完整 immutable base SHA；显式 branch 规则、dirty gate、worktree lock。
4. Ralph 只处理当前 branch 的 open + ready-for-agent 实施 Ticket，忽略 assignee；Wayfinder claim 不改变 worker 领取规则。
5. `implement-lqy` 单 Ticket、oversized stop、验证后提交 / 推送及完成度决定 close。
6. `code-review-lqy` 两轴、最多四次 agent 调用、禁止扩展 smell 审查、受限 clean 与 focused closure。
7. 个人 TDD 的 green-only refactor、最小完整 Interface、按风险选测试层级。
8. `handoff-out` 只给 copy-paste prompt；现有简单化原则、架构 gate 和深模块补充知识。

### 5.2 CONTEXT → GLOSSARY 必须整体处理

推荐未来新项目以 `GLOSSARY.md` 为标准；本仓库根 `CONTEXT.md` 实际已经是纯术语表，适合迁移。但本轮没有执行 rename。

迁移不能只改一个文件：需同步 `AGENTS.md` 的 Domain docs、`docs/agents/domain.md`、setup 的模板与 multi-context 检测、domain-modeling 的格式文件、tdd / diagnosis / architecture / triage 等读取方、README 和 `scripts/check_matt_zh_skills.py` 的根路径检查，以及已安装副本。

旧项目可采用**有限过渡**：按项目明确配置的领域文档路径；尚未迁移时允许继续读旧 CONTEXT，写入仍指向同一份权威文档。不要同时维护两份 glossary，不增加永久的“所有文件名都试一遍”回退链。

术语也应修正：当前 root glossary 的 Ticket 只定义为 decision-mapping 条目；更新时区分普通实施 **Ticket** 与 **Decision ticket**，并解释 task graph / frontier。DDD 概念与 ADR 的价值保留，改文件名不等于否定它们。

### 5.3 全 spec 多 agent 的额外风险

即使当前工具支持并行，也不能直接照搬 `implement-spec`：

- 自动创建 integration branch 与本地既有“未指定则当前 branch”的 Git 契约冲突。
- worker 开始前需要确定干净的 integration base；现有 Pi worktree 隔离不包含主工作区未提交变更。
- 多 worker “报告前已同步 integration tip”也**不能保证随后合并一定 fast-forward**，另一个 worker 可能先推进 tip；必须有单一 merge ownership、验证及失败停止。
- 共享研究文件必须所有 worker 真可访问，不能只给另一 worktree 不存在的绝对路径。
- 完成 worker 不等于完成集成验证；不能提前 close blockers 或删掉未合并 worktree。
- 本会话 `SubagentWorkflow` 仅在用户显式选择多 agent orchestration 时可用；运行 Ralph 也要用户明确启动。两者都不是普通 skill 自行升级成的默认行为。

因此推荐：**日常继续 implement-lqy；需要批量时使用已有确定性 Ralph；明确需要隔离并行的大 spec 再单独设计、验证可选流程。** 不默认增加 merger / exploration agent 层级或新调度平台。

## 6. 本机安装副本确实存在版本漂移

对 `skills/*/*/SKILL.md` 与 `~/.agents/skills/<name>/SKILL.md` 逐项字节比较：

- 50 个仓库可安装 skills 中，本机该目录已装 30 个；其余未安装不代表错误，也不是需要全部补装。
- 这 30 个的 SKILL.md 中 **2 个不同**：`code-review-lqy`、`clean`。
- 当前安装的 review 缺少仓库最新 accepted / wrong 方向判定、冻结文件范围的 clean gate、cleanup 后 focused closure 等规则；clean 也仍是旧正文。
- 安装目录是副本，不是本仓库 symlink；**更新仓库不会自动更新它们**。
- 本次比较只证明 SKILL.md 的漂移，不证明所有 supporting files 都相同，也没有检查所有其它项目安装目录。

现有同步脚本可安全先 dry-run（本次已执行）：

```bash
python3 scripts/sync_installed_project_skills.py "$HOME" --source "$PWD" --dry-run
```

输出计划更新 30 个匹配 skills，跳过 29 个其他来源 skills；**dry-run 不比较是否有差异，也不执行复制**。实际更新仍应先检查并备份安装副本的个人编辑。

它只更新“目标已安装的同名 skill”，**不会安装 pr / retro，也不会自动把 writing-great-skills 改名**；新增和迁移必须单独处理。Pi 的 `/reload` 或新会话用于重新发现资源；当前已读入的旧指令不会凭文件复制自动从上下文消失。

## 7. 推荐的更新批次

### P0：先确保版本、触发与消费契约清楚

- 固定上游目标 `b0618bc…`；分别记录官方 tag、已审阅 SHA、个人采纳 / 拒绝事项，不只改日期或总数。
- 整理 user-only / model-invoked / 已授权 worker 加载的分类，修 metadata 与 validator 的落差。
- 保留上述 Git / Ralph / review 契约；为 native dependency 的更新保留正文 Blocked by。
- 更新运行时副本的步骤必须纳入交付，先确认安装副本改动不是用户有意的独立定制。

### P1：高收益、低耦合的知识与修复

- 新增个人版 pr、retro；更新 writing-for-agents 及其依赖引用。
- 更新 diagnosis 脱敏 / mutation 证据，implement Ticket fetch，teach 路径 / quiz，setup labels / gh 操作。
- 吸收 architecture 热点 scope、grilling 依赖轮次与推荐确认、wayfinder 的决策标签隔离。
- 在同一受控批次处理 GLOSSARY 迁移及所有消费者；不能部分 skill 写新名、其他继续只读旧名。

### P2：有真实需求再加

- questionnaire、wait-what、wizard、shareable prototype 的补充功能。
- research-lqy 可在需要可引用的持久调查产物时引入，优先复用现有 agent 能力，提供无委派时的串行路径。
- retired / personal / misc 先整理推荐与 frozen 状态；不要无条件删除已使用的个人版。

### 暂缓

- 默认 implement-spec / chief-of-staff、自动 retro 修复、自动 schedules、Claude hooks 迁移、TS 专用约束安装。

三层维护顺序仍保持：**英文 mirror → 中文 baseline → LQY 选择性适配**。上游删除的 skill 若仍被 LQY provenance 引用，先按旧 SHA 归档 / 标 frozen，再更新链接；不能删除引用目标或假称 frozen 内容来自最新 HEAD。最新镜像 inventory 与个人安装清单必须分开。

## 8. 本轮验证证据与限制

| 检查 | 结果 |
| --- | --- |
| 上游 metadata、release、tag、基线与 HEAD、diff / log | 已核对，临时 clone 在仓库外；结束前再次确认 HEAD 未变 |
| 视频 | 已获取 metadata 与 400 行英文自动字幕，完整读取；未逐帧验证画面 |
| `python3 scripts/check_matt_zh_skills.py` | 初次失败：当前 Python 无 PyYAML，50 次 quick_validate 都是 `ModuleNotFoundError: yaml`，不是 50 项内容错误 |
| `uv run --no-project --with pyyaml python scripts/check_matt_zh_skills.py` | **通过**：50 / 35 / 38 / 38；依赖只在临时 uv 环境提供，不改项目或系统 Python |
| `npx skills@latest add . --list` | **发现 50 个可安装 skills**；仅 list，没有安装或更新 |
| 已装 SKILL.md 比较 | 30 个有对应安装，2 个正文不同 |
| sync script dry-run | 计划处理 30、跳过 29；未复制 |
| Pi / Codex / gh 能力 | 版本、Codex feature flags / plugin help / worktree help、gh sub-issue flags 已实查 |
| `git diff --check` | 本轮报告写入后重新执行；没有 skill 实现变更 |

这些检查证明的是**当前仓库结构和调查事实**，不是已完成最新同步。尚未执行：更新后的 Pi / Codex 触发 smoke、Ralph 消费 / Git contract 回归、全 spec 并行集成试验或 plugin 自更新验证。

后续更新验收至少包括：现有仓库 validator 与安装发现、各 skill frontmatter / metadata、GLOSSARY 全消费者一致性、显式与隐式触发、无 Skill tool 的加载路径、无 subagent 的串行路径，以及 Ralph producer / branch workflow 相关测试。仅修改镜像 SHA 或跑数量检查不足以交付。

## 9. 一句话总结

**我们需要的是最新、已评估、适配自己的知识和契约，不是最新的 Claude 工作流副本。优先更新 pr / retro / writing 原则与安全修复，保留 Pi / Ralph、单 Ticket 和 bounded review；多 agent 全 spec 调度留作显式选择的可选能力。**

## 主要来源

- [本仓库](https://github.com/liu-qingyuan/skills-sync-lqy)、`docs/upstream-mirrors/mattpocock-skills.md`、`docs/localization/mattpocock-zh-skills.md`、`docs/agents/issue-tracker.md`、各 LQY SKILL.md / LOCALIZATION.md、两个 scripts。
- [上游 CHANGELOG（固定 SHA）][changelog]，区分 1.2、1.3.0、1.3.1；GitHub release 的 body 有累计内容，不据重复正文重复计算功能。
- [implement-spec 源码][implement-spec]、[pr 源码][pr]、[retro 源码][retro]、[writing-for-agents 源码][writing]。
- [上游调用约定][invocation]、[维护范围][scope]、[递归归 harness 的决定][recursion]。
- [Codex skills][codex-skills]、[Codex subagents][codex-subagents]；本机 Pi 包 README、`docs/skills.md`、`docs/security.md`。

[video]: https://www.youtube.com/watch?v=BsJGo1wFTvQ
[release]: https://github.com/mattpocock/skills/releases/tag/v1.3.1
[compare]: https://github.com/mattpocock/skills/compare/d574778f94cf620fcc8ce741584093bc650a61d3...b0618bc436ad893b3c5e84e55fba86586d34a404
[post-release]: https://github.com/mattpocock/skills/compare/24fe0ef7737efae15c87225755e9f6f5965e4888...b0618bc436ad893b3c5e84e55fba86586d34a404
[changelog]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/CHANGELOG.md
[implement-spec]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/implement-spec/SKILL.md
[pr]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/pr/SKILL.md
[retro]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/retro/SKILL.md
[writing]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL.md
[invocation]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/.agents/invocation.md
[scope]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/SCOPE.md
[recursion]: https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/.out-of-scope/subagent-recursion.md
[codex-skills]: https://developers.openai.com/codex/skills/
[codex-subagents]: https://developers.openai.com/codex/agent-configuration/subagents/

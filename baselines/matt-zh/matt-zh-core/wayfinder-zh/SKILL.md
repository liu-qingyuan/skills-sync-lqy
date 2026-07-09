---
name: wayfinder-zh
description: 为超过一个 agent 会话容量的大块工作做规划：在 issue tracker 上维护共享 map，逐个解决调查 Ticket，直到通向 destination 的路径清晰。
---

一个松散想法出现了：它太大，无法塞进一个 agent 会话，而且被迷雾包住。从这里到 **destination** 的路还看不清。Wayfinding 的目标是找到那条路，而不是直接冲向 destination。这个 skill 会把路线绘制成仓库 issue tracker 上的一张**共享 map**，然后一次处理一个 Ticket，直到路线清晰。

每个 effort 的 destination 都不同，给它命名是绘图的第一个动作，因为它塑造每一个 Ticket。它可能是一份可交接并迭代的 spec、一个规划前必须锁定的决策，或一个就地完成的变化（例如数据结构迁移）。这张 map 不绑定领域：工程工作、课程内容，任何符合形状的工作都可以。

## Plan, don't do

Wayfinder 默认是**规划**：每个 Ticket 解决一个决策，map 在路线清楚时完成，也就是在某人真正去做之前没有剩余决策。想直接做事的拉力通常说明你已经到达 map 边缘，该交接了。某个 effort 可以在 **Notes** 中覆盖这一点，让执行本身进入 map；但没有这种说明时，产出决策，而不是交付物。

## Refer by name

每张 map 和每个 Ticket 都是 issue，因此都有一个**名称**：它的标题。在所有给人读的地方（叙述、map 的 Decisions so far）都用名称引用它，不要只写裸 id、编号或 slug。一堵 `#42, #43, #44` 看不懂；名称可以一眼读出。id 和 URL 不会消失，名称会包住它的链接，但它们只在名称里面，不单独代替名称。

## The Map

map 是这个仓库 issue tracker 上的单个 issue，带 `wayfinder:map` 标签，是 canonical artifact。它的 Ticket 是 map 的 child issues。

map 是**索引**，不是存储。它列出已做决策，并指向保存细节的 Ticket；一个决策只存在于一个地方，也就是它的 Ticket。所以 map 不复述它，只写 gist 并链接。

**map、child Ticket、blocking 和 frontier query 的物理表达取决于 tracker。** issue tracker 应该已经提供；如果没有，请运行 `/setup-matt-pocock-skills-zh`。查看 tracker 文档中的 `Wayfinding operations` 部分，了解此仓库如何表达它们。如果没有提供 tracker，默认使用 local-markdown tracker。

### map body

整张 map 的低分辨率视图，每个会话加载一次。开放 Ticket **不**列在这里；它们是开放 child issues，通过查询找到。

```markdown
## Destination

<到达这张 map 终点时是什么样子：这个 effort 正在寻找路线通向的 spec、decision 或 change。一两行；每个会话先用它定位，再选择 Ticket。>

## Notes

<domain；每个会话应该咨询的 skills；此 effort 的固定偏好>

## Decisions so far

<!-- 索引：每个已关闭 Ticket 一行。足够判断相关性，然后通过链接放大细节 -->

- [<closed ticket title>](link) — <one-line gist of the answer>

## Not yet specified

<!-- 见 “Fog of war”：还无法 ticket 的 in-scope fog；frontier 前进后会毕业 -->

## Out of scope

<!-- 见 “Out of scope”：已判定超出 destination 的工作；关闭，不会毕业 -->
```

### Tickets

每个 Ticket 都是 map 的 **child issue**；tracker 的 issue id 是它的身份。正文是问题，大小限制为一个 100K token agent 会话：

```markdown
## Question

<this ticket resolves 的决策或调查>
```

每个 Ticket 带一个 `wayfinder:<type>` 标签，值为 `research`、`prototype`、`grilling`、`task` 之一（见 [Ticket Types](#ticket-types)）。

会话在做任何工作前，先通过把 Ticket assign 给驱动这张 map 的 dev 来 **claim** 它，这样并发会话会跳过它。assignee 本身就是 claim：一个开放且未分配的 Ticket 是 unclaimed。

Blocking 使用 tracker 的**原生**依赖关系，这很重要，因为它会在 tracker 自己的 UI 中可视化 frontier，让人不用打开 map 就能看到可领取项。只有缺少原生 blocking 的 tracker 才回退到 body convention。一个 Ticket 的所有 blocking Ticket 都关闭后，它就是 **unblocked**；**frontier** 是开放、unblocked、unclaimed 的 children，也就是已知区域的边缘。

答案不属于 body；它在 resolution 时记录（见 [Work through the map](#work-through-the-map)）。解决 Ticket 时创建的资产从 issue 链接出去，不粘贴进来。

## Ticket Types

每个 Ticket 要么是 **HITL**（human in the loop，由能代表自己发言的人参与完成），要么是 **AFK**（agent 独自驱动）。HITL Ticket 只能通过实时交流解决；agent 不能替人回答人的那一边（一个自己回答自己问题的 grilling agent 已经坏了）。

- **Research** (AFK)：阅读文档、第三方 API，或知识库等本地资源。创建 Markdown summary 作为 linked asset。需要当前 working directory 之外的知识时使用。
- **Prototype** (HITL)：通过制作便宜、粗糙、具体的 artifact 来提高讨论保真度，例如 outline、rough take、stub，或通过 `/prototype-zh` 创建 UI/logic code。把 prototype 作为 asset 链接。关键问题是“它应该看起来如何”或“它应该如何表现”时使用。
- **Grilling** (HITL)：通过 `/grilling-zh` 和 `/domain-modeling-zh` skills 进行对话，一次一个问题。默认类型。
- **Task** (HITL or AFK)：在做出**决策**前必须完成的手工工作；本身没有要决定、prototype 或 research 的内容，但讨论被它阻塞。例如注册服务以便评估 API、配置访问权限、迁移数据以便观察其形状。这是唯一一种“做事”而不是“做决策”的类型；它只有在 unblock 一个决策时才值得存在，而不是因为它交付 destination。agent 能独自驱动时就 AFK；否则给人一份精确 checklist。工作完成时 resolve；答案记录完成了什么，以及后续 Ticket 依赖的事实（credential 位置、新 URL、row count 等）。

## Fog of war

map 是_故意_不完整的：不要绘制你还看不见的东西。live Ticket 之外是 **fog of war**：你能隐约看见将会出现的决策和调查，但还无法钉住，因为它们悬挂在仍未解决的问题上。解决一个 Ticket 会清除它前方的迷雾，让现在可以说明的内容毕业为新 Ticket，一次一个，直到通向 destination 的路线清楚且不再剩下 Ticket。

map 的 **Not yet specified** section 用来写下这种低分辨率视图：可疑的问题、稍后要回访的区域。它是朝向 destination 的未知 frontier；这里的内容都在 scope 内，只是还不够锋利，无法成为 Ticket。按当前视野允许的松散程度记录；它也给协作者一个路标，说明 effort 正朝哪里走。

**Fog or ticket?** 测试是：你现在能不能精确陈述问题；不是你现在能不能回答问题。

- **Ticket when** 问题已经锋利，即使它被 block、你暂时不能行动。
- **Not yet specified when** 你还不能把问题表达到那么锋利。不要把 fog 预先切成 Ticket 大小的块；fog 比 Ticket 粗，一个 patch 可能在 frontier 抵达后毕业成多个 Ticket，也可能一个都没有。

**Not yet specified** 排除已决定的事（Decisions so far）、live Ticket，以及 out of scope（下一节）。

## Out of scope

fog 只会朝 destination 聚集。destination 固定 scope，所以超出它的工作是 **out of scope**；它不是 fog，也不属于 **Not yet specified**。它在 map 上有自己的 **Out of scope** section：你已经有意识排除在_这个_ effort 之外的工作。这里由 scope 决定，不由清晰度决定。

out-of-scope work 永远不会毕业；frontier 会停在 destination。因此只有当 destination 被重画时，它才会回来，而且作为一个新的 effort，而不是恢复旧 effort。

把某事判出 scope 是 scope 行为，不是路线上的一步。当一个已存在 Ticket 被发现位于 destination 之外（绘图时误纳入，或 resolution 暴露出这一点），**关闭它**（关闭的 Ticket 明确不在 frontier 上），并在 **Out of scope** section 留一行：gist 加上为什么 out of scope，链接到已关闭 Ticket。它不进入 **Decisions so far**，后者记录实际走过的路线；scope boundary 不是路线上的一步。

## Invocation

两种模式。无论哪种，**每个会话最多 resolve 一个 Ticket。**

### Chart the map

用户带着松散想法调用。

1. **Name the destination.** 运行 `/grilling-zh` 和 `/domain-modeling-zh` 会话，钉住这张 map 正在寻找路线通向什么：spec、decision 或 change。destination 固定 scope，所以它先确定。
2. **Map the frontier.** 再次 grilling，但这次 **breadth-first**：横向展开整个空间，而不是在某一条线深挖，浮现开放决策和现在可行动的第一步。**如果这没有浮现 fog**，说明通往 destination 的路已经清楚，整个旅程小到一个会话能处理；你不需要 map。停止并询问用户想如何继续。
3. **Create the map**（标签 `wayfinder:map`）：填好 Destination 和 Notes，Decisions-so-far 为空，把 fog 草绘到 **Not yet specified**。
4. **Create the tickets you can specify now**，作为 map 的 child issues；然后在**第二遍**连接 blocking edges（issues 需要先有 id 才能互相引用）。连接会把它们分成 frontier 和 blocked；所有还不能说明的内容都留在 fog，即 **Not yet specified** section。
5. 停止。charting the map 是一个会话的工作；不要同时 resolve Ticket。

### Work through the map

用户带着 map（URL 或编号）调用。Ticket 是**可选的**；如果没有指定，由你选择下一个决策，而不是用户。

1. 加载 **map**：低分辨率视图，不是每个 Ticket body。
2. 选择 Ticket。如果用户点名了一个，就使用它。否则按顺序拿第一个 frontier Ticket。**Claim it**：任何工作前先 assign 给自己。
3. Resolve it：**按需 zoom**。只在需要时获取相关或已关闭 Ticket 的完整 body；调用 `## Notes` block 指定的 skills。不确定时，使用 `/grilling-zh` 和 `/domain-modeling-zh`。
4. 记录 resolution：把答案作为 **resolution comment** 发布，**close** issue，并向 map 的 Decisions-so-far 追加一个 context pointer。
5. 添加新浮现的 Ticket（先创建再连接）；让答案已经变得可说明的 fog 毕业，毕业后从 **Not yet specified** 中清掉，让它只作为新 Ticket 存在。如果答案揭示某个 Ticket（当前或另一个）位于 destination 之外，把它判定为 out of scope，而不是沿路线 resolve。如果该决策让 map 的其他部分失效，更新或删除那些 Ticket。

用户可能并行运行 unblocked Ticket，所以要预期其他会话正在并发编辑 tracker。

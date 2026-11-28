# 任务示例

按所解决的问题分组。每项任务都写明启动 run 的 trigger、run 做什么、下一步触发什么。大多数工厂从其中一种开始，通过串接下一种逐步成长。

## 未经 triage 的 Ticket 堆积

**Explore 任务**
- Trigger：创建 Ticket，或有人给它打标签。
- 执行：对照代码库核实 Ticket 的主张，能复现时尝试复现，将其归类（容易判断、需要人处理、不是 bug），在 Ticket 上留下发现供 implementer 使用。绝不 push。
- 后续触发：容易判断的情况启动 implementer run。其他情况以 Ticket 标为等待人工处理结束。

## 已就绪的 Ticket 无人实现

**Implementer 任务**
- Trigger：人或 explore run 将 Ticket 标为 ready。
- 执行：实现 Ticket，直到自动检查通过，创建草稿 PR。
- 后续触发：自动 review run。

## PR 等待 review

**自动 review 任务**
- Trigger：PR 创建但尚无自动 review，或有人给它打标签。
- 执行：根据代码库标准和它所来自的 Ticket review diff。
- 后续触发：失败时启动 rework run；通过后结束，由 PR 等待人工 review 后再由人合并。

## 自动 review 失败后无人修复

**Rework 任务**
- Trigger：自动 review run 判定 PR 不通过。
- 执行：只修复自动 review 指出的内容，然后 push。
- 后续触发：再次运行自动 review。失败达到设定次数后结束，给 PR 打上等待人工处理的标签。

## Spec 过大，单次 run 无法完成

**Decompose 任务**
- Trigger：给 spec Ticket 打上标签。
- 执行：把 spec 拆成 Ticket，每个 Ticket 都记录其依赖的其他 Ticket。
- 后续触发：implementer run。

此处 implementer run 选择下一个依赖均已关闭的 Ticket，反复触发自己，直到没有剩余 Ticket。

## 迁移到更严格的自动检查

启用了新 lint 规则（或更严格的类型设置），但只有部分文件通过。规则对通过的文件强制执行，失败文件留在例外清单中。

**Ratchet 任务**
- Trigger：每日时钟。
- 执行：从例外清单移除一个文件，修复到更严格的检查通过，然后创建 PR。
- 后续触发：自动 review run。例外清单清空后，ratchet run 无文件可取，迁移便完成。

每天一个小 PR 可以降低人工 review 成本，检查只会变得更严格。

## 用户报告 bug，但没人读

应用中的反馈按钮是一种 Ticket source：把每份报告创建成已带 explore 标签的 Ticket。其余交给 explore run。

## 生产问题发现太迟

监测器（慢查询、错误率）是一种 Ticket source。每个问题创建一个 Ticket；再次发现同一问题时改为给仍开放的 Ticket 留评论。修复合并后若问题持续，就重新打开 Ticket。

## 工厂自身的 run 失败

**Fix 任务**
- Trigger：orchestrator 报告某次 run 失败。
- 执行：将失败日志创建为 Ticket；若可以修复，尝试以 PR 提交修复。
- 后续触发：自动 review run。fix run 自身工作中的失败不会触发任何新 run，因此修复不会链式扩散。因为 fix 修改了工厂本身，所以始终要有人工 review。

## 代码库逐渐偏离目标

**Architecture 任务**
- Trigger：每晚的时钟。
- 执行：扫描近期改动，寻找重构候选，创建一个汇总 Ticket。
- 后续触发：无。人选中候选并给它打标签，启动常规链。

## 同样的错误反复出现

**Retro 任务**
- Trigger：PR 合并，限流至每十个已合并 PR 取一个。
- 执行：读取 PR、其 Ticket、自动 review 以及 run 日志，以 PR 形式提出工厂自身指令的修改。
- 后续触发：自动 review run。

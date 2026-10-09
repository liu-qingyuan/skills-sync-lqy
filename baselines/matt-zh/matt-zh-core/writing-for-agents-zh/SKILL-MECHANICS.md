# Skill 机制

[`writing-for-agents-zh`](SKILL.md) 中仅适用于 Skill 的分支：当文档是 Skill 时有哪些变化（frontmatter、调用方式的选择、路由 Skill）。其他写作原则都在 `SKILL.md` 的通用参考中。

## 调用方式

两种选择，分别承担不同负担：

- **由模型调用**的 Skill 保留 `description`，因此 Agent 可以自主触发，其他 Skill 也可访问。用户仍可以输入 Skill 名称：模型可调用*始终包含*用户可调用；description 只会增加 Agent 的发现途径，不会剥夺人的入口。description 是 Skill 的顶层上下文指针，必须常驻上下文：以持续的上下文负担换取可发现性。如果模型可调用的 Skill 内容全是参考，它还可以成为共享参考的统一存放处：其他 Skill 能调用它，多处需要的参考因此可以集中存放。操作方式：不设置 `disable-model-invocation`，编写面向模型、涵盖触发分支的 description（完整遵循 `SKILL.md` 的指针写作规则）。
- **由用户调用**的 Skill 从 Agent 的可发现范围移除 description：只有人输入名称才能调用，其他 Skill 也无法调用。没有上下文负担，但增加认知负担：人要记住它的存在。操作方式：设置 `disable-model-invocation: true`；description 改为面向人的一句话简介，不列触发条件清单。

只有 Agent 必须自行访问该 Skill 或其他 Skill 必须访问它时，才选模型调用。如果总是由人手动调用，就选用户调用，不增加上下文负担。

两个用户调用的 Skill 都需要的共享参考不能存放在其中任何一个：没有 description，两者无法互相触发。应将其移至 Skill 系统之外的普通文件，让任意 Skill 都能指向它。

## 按调用方式拆分

按调用方式拆分（按顺序拆分见 `SKILL.md`）：当存在一个独立引导词应当自行触发 Skill（你确实会在提示词中用这个触发词），或其他 Skill 必须访问它时，就可拆出一个模型调用的 Skill。新增常驻 description 会增加上下文负担，因此独立访问必须值得付出成本。

## 路由 Skill

当用户调用的 Skill 多到难以记住，累积认知负担可以用**路由 Skill**解决：一个用户调用的 Skill，列出其他 Skill 的名称和各自适用时机，让人只需记住一个。它只能给提示，不能代为触发：用户调用的 Skill 没有供 Agent 发现的 description，只有人能访问它们。

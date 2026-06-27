# CONTEXT.md 格式

## 结构
```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```
## 规则

- **固执己见。** 当同一概念存在多个单词时，选择最好的一个并将其他单词列在“_避免_”下。
- **保持定义严格。** 最多一到两句话。定义它是什么，而不是它做什么。
- **仅包含特定于该项目上下文的术语。** 即使项目广泛使用一般编程概念（超时、错误类型、实用程序模式），它们也不属于其中。在添加术语之前，先问一下：这是该上下文特有的概念，还是通用的编程概念？只有前者属于。
- **当自然集群出现时，将术语分组在副标题**下。如果所有术语都属于一个单一的内聚区域，那么平面列表就可以了。

## 单上下文仓库与多上下文仓库

**单一上下文（大多数存储库）：** 存储库根目录下有一个 `CONTEXT.md`。

**多个上下文：** 存储库根目录中的 `CONTEXT-MAP.md` 列出了上下文、它们所在的位置以及它们彼此之间的关系：
```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```
该技能推断出应用哪种结构：

- 如果 `CONTEXT-MAP.md` 存在，则读取它以查找上下文
- 如果仅存在根`CONTEXT.md`，则单个上下文
- 如果两者都不存在，则在第一个术语解析时懒惰地创建根“CONTEXT.md”

当存在多个上下文时，推断当前主题与哪一个相关。如果不清楚，请询问。
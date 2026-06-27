---
name: ubiquitous-language-zh
description: 从当前对话中提取 DDD 风格统一语言 glossary，标记歧义并提出标准术语，保存到 UBIQUITOUS_LANGUAGE.md。
---

# 无处不在的语言

从当前对话中提取领域术语并将其形式化为一致的术语表，并保存到本地文件。

## 流程

1. **扫描对话**以查找与领域相关的名词、动词和概念
2. **识别问题**：
   - 相同的词用于不同的概念（歧义）
   - 同一概念使用不同的词（同义词）
   - 含糊或承载过多含义的术语
3. **提出一个规范术语表**，其中包含明确取舍后的术语选择
4. **使用以下格式写入工作目录中的`UBIQUITOUS_LANGUAGE.md`**
5. **在对话中内嵌输出摘要**

## 输出格式

使用以下结构编写“UBIQUITOUS_LANGUAGE.md”文件：
```md
# Ubiquitous Language

## Order lifecycle

| Term        | Definition                                              | Aliases to avoid      |
| ----------- | ------------------------------------------------------- | --------------------- |
| **Order**   | A customer's request to purchase one or more items      | Purchase, transaction |
| **Invoice** | A request for payment sent to a customer after delivery | Bill, payment request |

## People

| Term         | Definition                                  | Aliases to avoid       |
| ------------ | ------------------------------------------- | ---------------------- |
| **Customer** | A person or organization that places orders | Client, buyer, account |
| **User**     | An authentication identity in the system    | Login, account         |

## Relationships

- An **Invoice** belongs to exactly one **Customer**
- An **Order** produces one or more **Invoices**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once a **Fulfillment** is confirmed. A single **Order** can produce multiple **Invoices** if items ship in separate **Shipments**."
> **Dev:** "So if a **Shipment** is cancelled before dispatch, no **Invoice** exists for it?"
> **Domain expert:** "Exactly. The **Invoice** lifecycle is tied to the **Fulfillment**, not the **Order**."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** — these are distinct concepts: a **Customer** places orders, while a **User** is an authentication identity that may or may not represent a **Customer**.
```
## 规则

- **明确取舍。** 当同一概念存在多个说法时，选定最合适的一个，并把其他说法列为需要避免的别名。
- **明确标记冲突。** 如果对话中使用的术语含糊不清，请在“标记的歧义”部分中指出该术语并提供明确的建议。
- **仅包含与领域专家相关的术语。** 跳过模块或类的名称，除非它们在领域语言中具有含义。
- **保持定义严格。** 最多一句话。定义它是什么，而不是它做什么。
- **显示关系。** 使用粗体术语名称并在明显的地方表达基数。
- **仅包含领域术语。** 跳过通用编程概念（数组、函数、端点），除非它们具有特定于领域的含义。
- **当自然集群出现时（例如按子域、生命周期或参与者），将术语分组到多个表中**。每个组都有自己的标题和表格。如果所有术语都属于一个单一的内聚域，那么一张表就可以了——不要强制分组。
- **编写示例对话。** 开发人员和领域专家之间的简短对话（3-5 次交流），演示术语如何自然地交互。对话应澄清相关概念之间的界限并准确显示术语的使用。

<示例>

## 对话示例

> **开发人员：**“如何在没有 Docker 的情况下测试 **同步服务**？”

> **领域专家：**“提供**文件系统层**而不是**Docker层**。它实现相同的**沙箱服务**接口，但使用本地目录作为**沙箱**。”

> **开发人员：**“那么**同步**仍然会创建一个**捆绑包**并解压它？”

> **领域专家：**“正是如此。**同步服务**不知道它正在与哪一层通信。它调用 `exec` 和 `copyIn` — **文件系统层** 只是将它们作为本地 shell 命令运行。”

</示例>

## 重新运行

当在同一个对话中再次调用时：

1. 阅读现有的`UBIQUITOUS_LANGUAGE.md`
2. 纳入后续讨论中的任何新术语
3. 如果理解有所发展，则更新定义
4. 重新标记任何新的歧义
5. 重写示例对话以纳入新术语
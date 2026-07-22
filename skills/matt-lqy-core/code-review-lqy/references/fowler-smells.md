# Fowler Smell Baseline

仓库记录的规则优先。以下 smells 都是 judgment-call heuristics，不是硬性违规；跳过工具已经强制执行的内容。

- **Mysterious Name**：名称不能说明用途。重命名；找不到诚实名称时检查设计。
- **Duplicated Code**：多个 hunk 或文件出现相同逻辑。提取共享形状。
- **Feature Envy**：方法主要读取其他对象的数据。把行为移到数据所有者。
- **Data Clumps**：同一组字段或参数反复一起出现。打包成类型。
- **Primitive Obsession**：primitive/string 代替领域概念。引入小型领域类型。
- **Repeated Switches**：相同类型判断在多处重复。使用 polymorphism 或共享 map。
- **Shotgun Surgery**：一个变化要求分散修改许多文件。把共同变化收进一个模块。
- **Divergent Change**：一个模块因多个无关原因变化。按变化原因拆分。
- **Speculative Generality**：spec 不需要的抽象、参数或 hook。删除并 inline。
- **Message Chains**：caller 依赖长对象导航。由首个对象隐藏穿行。
- **Middle Man**：类型或函数主要负责转发。直接调用真实目标。
- **Refused Bequest**：子类型忽略大部分继承内容。改用 composition。

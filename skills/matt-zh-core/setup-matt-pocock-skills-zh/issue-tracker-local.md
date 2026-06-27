# 问题跟踪器：本地 Markdown

此存储库的问题和 PRD 以降价文件形式存在于“.scratch/”中。

## 惯例

- 每个目录一个功能：`.scratch/<feature-slug>/`
- PRD 是 `.scratch/<feature-slug>/PRD.md`
- 实现问题是`.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从`01`开始编号
- 分类状态记录为每个问题文件顶部附近的“状态：”行（有关角色字符串，请参阅“分类标签.md”）
- 评论和对话历史记录附加到文件底部的“## Comments”标题下

## 当技能说“发布到问题跟踪器”时

在 `.scratch/<feature-slug>/` 下创建一个新文件（如果需要，创建目录）。

## 当技能说“获取相关票证”时

读取引用路径中的文件。用户通常会直接传递路径或问题编号。
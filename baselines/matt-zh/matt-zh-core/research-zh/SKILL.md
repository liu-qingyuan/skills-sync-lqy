---
name: research-zh
description: 针对高信任 primary sources 调查一个问题，并把 findings 作为 Markdown 文件保存到仓库。用于用户想调研主题、收集 docs/API 事实，或把阅读工作交给后台 agent 时。
---

启动一个**后台 agent** 来做 research，这样你可以在它阅读时继续工作。

它的职责：

1. 针对 **primary sources** 调查问题：official docs、source code、specs、first-party APIs；不要依赖对它们的二手解读。每个 claim 都要追溯到拥有该事实的 source。
2. 把 findings 写入一个 Markdown 文件，并为每个 claim 引用 source。
3. 保存到仓库已有的同类 notes 位置；匹配现有约定。如果没有约定，放到合理位置并说明保存在哪里。

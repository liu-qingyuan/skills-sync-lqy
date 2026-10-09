# HTML 报告格式

架构评审输出为操作系统临时目录中的一个独立 HTML 文件。Tailwind 和 Mermaid 都从 CDN 加载。Mermaid 适合依赖、调用关系等图结构；手写 div 和内联 SVG 适合更具编辑设计感的视觉表达，例如体量图、剖面图。两者混用，不要所有图都依赖 Mermaid，否则视觉会变得单调。

## 脚手架

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review for {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## 页首

仓库名、日期，以及紧凑的图例：实线框 = 模块，虚线 = 接缝，红色箭头 = 泄漏，粗深色框 = 深模块。不写介绍段落，直接展示候选项。

## 候选项卡片

以图为主，文字少而朴素，严格使用 `/codebase-design-lqy` 的术语。

每个候选项用一个 `<article>`：

- **标题**：简短，点明要做的深化，例如“合并订单接收管道”。
- **徽章行**：推荐强度（`Strong` = 翠绿色、`Worth exploring` = 琥珀色、`Speculative` = 石板色），加上依赖类别标签（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **文件**：等宽列表，使用 `font-mono text-sm`。
- **Before / After 图**：核心部分，两列并排，模式见下文。
- **问题**：一句话，说清痛点。
- **方案**：一句话，说清改什么。
- **收益**：列表，每条不超过 6 个词，例如“测试只跨一个接口”“定价逻辑停止泄漏”“删除四个浅包装器”。
- **ADR 提示**（如适用）：琥珀色背景框中的一行。

不写成段的解释。如果图需要一段文字才能看懂，就重画。

## 图表模式

按候选项选择合适的模式，并混合使用。不要每张图都一样，多样性本身就是目标之一。

### Mermaid 图（依赖与调用关系的常用方式）

当重点是“X 调用 Y，Y 调用 Z，这些关系哪里混乱”时，使用 Mermaid `flowchart` 或 `graph`。把它包在 Tailwind 卡片中，避免像随手贴上的图。用 `classDef` 设置样式，把泄漏边画成红色、深模块画成深色。时序图适合表达“之前六次往返，之后一次”。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手写方框与箭头（Mermaid 布局不合适时）

模块用带边框和标签的 `<div>`。箭头用内联 SVG `<line>` 或 `<path>`，绝对定位在相对定位的容器上。如果目标图要表现为一个粗边框深模块，内部细节灰显，就用这种方式；Mermaid 难以呈现所需的视觉分量。

### 剖面图（适合分层的浅模块）

堆叠水平条带（`h-12 border-l-4`），展示一次调用经过的各层。之前：六个几乎不做事的薄层。之后：一条粗条带，标出合并后的职责。

### 体量图（适合“接口几乎和实现一样复杂”）

每个模块画两个矩形，分别表示接口表面积与实现。之前：接口矩形几乎和实现矩形一样高，体现浅。之后：接口矩形短、实现矩形高，体现深。

### 调用图收拢

之前：函数调用树用嵌套方框呈现。之后：同一棵树收进一个方框，内部调用灰显，因为它们已成为内部细节。

## 风格指南

- 简洁的编辑设计风格，而不是企业仪表盘。留足空白。标题可用衬线字体；`font-serif` 与 stone/slate 色系很搭。
- 克制用色：一种强调色（翠绿或靛蓝），另用红色标泄漏、琥珀色标警告。
- 图高约 320px，让 Before / After 能舒适并排，不必滚动。
- 图内模块标签使用 `text-xs uppercase tracking-wider`，使它们看起来像示意图标注，而不是 UI。
- 只有 Tailwind CDN 与 Mermaid ESM 导入脚本。其余内容静态，不放应用代码；除 Mermaid 自身渲染外，不增加交互。

## 首选推荐

一张较大的卡片：候选项名称、一句话说明推荐原因、链接到对应卡片的锚点。仅此而已。

## 语气

用简洁朴素的中文，但架构名词和动词直接取自 `/codebase-design-lqy`，不能为了简短而偏离词汇表。

**准确使用：** module（模块）、interface（接口）、implementation（实现）、depth（深度）、deep（深）、shallow（浅）、seam（接缝）、adapter（适配器）、leverage（杠杆）、locality（局部性）。

**不要替换为：** component、service、unit（替代 module）；API、signature（替代 interface）；boundary（替代 seam）；layer、wrapper（实际指 module 时）。

**符合风格的表述：**

- “订单接收模块很浅：接口几乎和实现一样复杂。”
- “定价逻辑跨接缝泄漏。”
- “深化：一个接口，一个测试位置。”
- “两个适配器证明接缝确有必要：生产用 HTTP，测试用内存。”

**收益列表**用词汇表术语说明所得，例如“局部性：缺陷集中在一个模块”“杠杆：一个接口，N 个调用点”“接口缩小，实现吸收包装器”。不要写“更易维护”“代码更干净”：它们不在词汇表里，也不足以说明收益。

不要含糊措辞、铺垫，或“值得注意的是……”之类的废话。能改成列表的句子就改成列表，能删掉的条目就删掉。需要某个术语时，先在 `/codebase-design-lqy` 词汇表中找，不要直接另造一个。

---
name: wizard-zh
description: 生成一个交互式 bash wizard，引导人完成手工流程：第三方设置、一次性迁移、A 到 B 状态切换、打开 URL、收集值、逐步确认，并写入 .env 和 GitHub Actions secrets。
---

# Wizard

**wizard** 是一个 bash 脚本，逐步引导人完成某个手工流程。这个流程手动做很繁琐，每次重新向 AI 解释也很繁琐。wizard 会打开每个 URL，说明要点击和复制什么，收集值，把值写到该去的地方（`.env`、GitHub secrets），在每个阶段确认，并显示剩余进度。它可能配置第三方服务、执行一次性迁移，或把项目从一个状态移动到另一个状态。

令人愉快的 UX 已经由 [template.sh](template.sh) 解决：带剩余时间的进度、确认 gate、跨平台 URL 打开（包括 WSL）、隐藏 secret 输入、幂等 `.env` upsert、`gh secret`/`gh variable` 写入，以及结束 summary。**你的工作只是界定流程 scope 并编写各个 stage。** `STAGES` 标记上方的 library 在每个 wizard 中都相同；一致性就是重点，永远不要手动编辑它。

wizard 默认是临时的：为一次运行而构建，保存到 scratch 或 `scripts/` 路径，任务完成后删除。只有用户想要一个可重复设置路径、应该留在仓库里时，才提交它。

## 流程

### 1. 界定流程 scope

找出人必须完成的每个手工步骤，以及过程中要捕获的每个值。先读仓库，不要冷启动提问：

- 对 setup：`.env`、`.env.example`、`.env.*`、`README`、`docker-compose*`、framework config，以及 `.github/workflows/*`（每个 `secrets.*` / `vars.*` reference 都是 wizard 必须产出的值）。
- 对 migration 或 transition：当前状态、目标状态，以及两者之间不可逆的操作。

然后向用户展示按顺序排列的 stages，以及每个 stage 产出的值，并确认；用户可能添加、删除或重排。

**完成标准：** 每个 stage 都已按顺序命名；对每个捕获值，你知道 (a) 人从哪里获得它，(b) 它写到哪里（`.env`、GitHub secret、两者，或 nowhere，因为有些 stage 只是动作），(c) 它是否是 secret（隐藏输入）或 public。

### 2. 映射每个 stage 的 journey

为每个 stage 写出人要遵循的精确路径：打开哪个 URL、在那里做什么、值显示在哪里、填充哪个变量。例如 “Dashboard → Developers → API keys → Reveal test key → copy”。如果你并不知道当前 UI 或精确命令，就说明这一点并询问用户或查 docs；不要编造可能不存在的步骤。

**完成标准：** 每个 stage 都追踪到一个陌生人也能执行的具体说明。

### 3. 编写 wizard

把 `template.sh` 复制到目标路径。用按依赖顺序排列的一个 `stage` 替换示例 stage。使用 library helpers：`stage`、`say`/`step`、`open_url`、`ask`/`ask_secret`、`write_env`、`set_secret`/`set_var`、`pause`、`confirm`，并把 `TOTAL_STAGES` 和 `TOTAL_MINUTES` 设置为诚实估计（这会驱动剩余时间显示）。

保持 template 设定的标准：先打开 URL 再询问它的值；任何 secret 都使用 `ask_secret`；每个持久化值都 `write_env`；只有 CI 实际需要的值才 `set_secret`；任何不可逆动作前都 `confirm`。每个 `stage` 都会清屏，让屏幕上只显示当前步骤；一个 stage 保持一个聚焦任务，避免人需要的信息滚走。不要触碰 marker 上方的 library。

### 4. 验证并交接

- `bash -n <script>`；如果可用，运行 `shellcheck`。
- `chmod +x <script>`。
- 不要自己端到端运行；它会打开浏览器并等待人输入。改为静态 trace：第 1 步中的每个值都被捕获，并落到第 1 步指定的位置；每个 `set_secret` 名称都精确匹配 CI 中的 `secrets.*` reference。
- 告诉用户如何运行它。如果它是可重复 setup path，提交它并从 README 链接，这样下一个人运行脚本，而不是再问 AI。

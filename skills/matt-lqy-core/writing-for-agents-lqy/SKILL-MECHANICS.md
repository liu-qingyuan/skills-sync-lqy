# Skill mechanics

## 调用与依赖

- **Model-invoked**：描述面向模型，说明不同触发分支；公共纪律可以由用户或已授权流程加载。
- **User-invoked**：Pi 的 `disable-model-invocation: true` 与 Codex `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` 同步。用户是入口；其它 skill 缺少其前置条件时提示用户显式调用，不擅自启动。
- Ralph worker 已获授权实施 Ticket，可以加载 `implement-lqy`、tdd 与 review。不要把上游 user-only 分类机械套到这个授权链。

需要执行另一份纪律时，明确“读取并执行 `<name>` 的 SKILL.md”，按当前 skills 列表的实际路径定位；不假设存在 Claude `Skill` tool，也不把裸 `/name` 当作已经加载。

相对 supporting-file 路径从 skill 目录解析，项目数据路径从任务 workspace 解析。安装版必须自包含，不能依赖本仓库 mirror 或 baseline。

## 拆分

只有独立触发概念或真实复用需要才抽出 model-invoked skill；它会永久增加描述成本。Router 只是给人推荐入口，不能自动启动 user-only 流程。

按 sequence 拆分的判断见 [SKILL.md](SKILL.md)。不要为调用形式新增 dispatcher、registry 或多 agent 平台。

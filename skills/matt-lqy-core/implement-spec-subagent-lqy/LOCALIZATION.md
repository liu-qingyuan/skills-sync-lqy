# implement-spec-subagent-lqy localization

- Upstream skill: `implement-spec`
- Upstream path: `upstream/mattpocock/skills/engineering/implement-spec`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/implement-spec-zh`
- LQY installable path: `skills/matt-lqy-core/implement-spec-subagent-lqy`
- Source commit (original import): `49dd158d1076134a641b33efb035946536778336`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336`
- Policy: optional subagent execution after user authorization, which an authorized parent may pass to workers; Ralph remains default. Unlike upstream's mandatory private worktrees, use a shared checkout for disjoint small tasks or isolated worktrees for independent commits/rolling integration, subject to project rules. Read-only helper delegation stays within scope and review budget. Reuse the frozen Git/blocker contract, per-Ticket TDD and bounded review of a Ticket or explicitly authorized delivery batch; shared writes stop before snapshot validation and delivery. One integrator pushes/closes issues. No new dispatcher, automatic reset, recursive implementation or destructive cleanup.

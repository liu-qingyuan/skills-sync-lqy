# implement-spec-subagent-lqy localization

- Upstream skill: `implement-spec`
- Upstream path: `upstream/mattpocock/skills/engineering/implement-spec`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/implement-spec-zh`
- LQY installable path: `skills/matt-lqy-core/implement-spec-subagent-lqy`
- Source commit (original import): `49dd158d1076134a641b33efb035946536778336`
- Upstream reviewed commit: `49dd158d1076134a641b33efb035946536778336`
- Policy: explicit optional subagent execution using the current session's available capabilities; Ralph remains default. Reuse the frozen integration-target Git/blocker contracts, per-Ticket TDD and bounded review. Workers use private worktrees and only commit locally; a single integrator reviews, verifies, pushes and closes issues. No automatic reset, nested implementation, unbounded review or destructive cleanup.

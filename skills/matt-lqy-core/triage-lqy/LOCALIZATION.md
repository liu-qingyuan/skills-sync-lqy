# triage-lqy localization

- Upstream skill: `triage`
- Upstream path: `upstream/mattpocock/skills/engineering/triage`
- Chinese baseline path: `baselines/matt-zh/matt-zh-core/triage-zh`
- LQY installable path: `skills/matt-lqy-core/triage-lqy`
- Policy: installable personal LQY layer, copied from the Chinese baseline and self-contained. Keep this file updated when upstream or zh baseline changes.
- LQY extension: ordinary GitHub issues entering the Ralph backlog use `publish_ready_issue.py` for shared Git contract resolution, typed workspace provision, body/brief readback, status cleanup, and label-last publication. PRs retain native head/base handling and never enter this flow; Ralph publication does not use assignees.

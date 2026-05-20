# Upstream link

This skill is mirrored from:

- Repository: https://github.com/nicobailon/visual-explainer.git
- Skill path: `plugins/visual-explainer`
- Source commit: `8f1d0e38ab0f265632a31d2fd032f7b730c98c15`
- Synced on: 2026-05-20

## Refresh from latest upstream

From the `skills-sync-lqy` repository root:

```bash
rm -rf /tmp/visual-explainer-skill-sync
git clone --depth 1 https://github.com/nicobailon/visual-explainer.git /tmp/visual-explainer-skill-sync
rm -rf skills/visual-explainer
cp -a /tmp/visual-explainer-skill-sync/plugins/visual-explainer skills/visual-explainer
cat > skills/visual-explainer/UPSTREAM.md <<'EOM'
# Upstream link

This skill is mirrored from:

- Repository: https://github.com/nicobailon/visual-explainer.git
- Skill path: `plugins/visual-explainer`
- Source commit: `$(git -C /tmp/visual-explainer-skill-sync rev-parse HEAD)`
- Synced on: `$(date +%F)`

Install from this sync repo:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo liu-qingyuan/skills-sync-lqy \
  --path skills/visual-explainer
```
EOM
```

This repo intentionally stores a mirrored copy instead of a git submodule because the Codex `skill-installer` downloads GitHub archives by default; archive installs cannot validate `SKILL.md` inside an uninitialized submodule.

#!/usr/bin/env bash
set -u

mode="preflight"
task=""
repo="$(pwd)"
out_dir=".omx/context"

usage() {
  cat <<'USAGE'
Usage: gitnexus-preflight.sh [--mode MODE] [--task TEXT] [--repo PATH] [--out-dir DIR]

Writes a Markdown GitNexus grounding report and prints its path.
This script is read-only: it does not analyze, reindex, clean, or edit source.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode) mode="${2:-}"; shift 2 ;;
    --task) task="${2:-}"; shift 2 ;;
    --repo) repo="${2:-}"; shift 2 ;;
    --out-dir) out_dir="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)
      if [ -z "$task" ]; then task="$1"; else task="$task $1"; fi
      shift ;;
  esac
done

if [ -z "$task" ]; then task="gitnexus-grounding"; fi

slug=$(printf '%s' "$task" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g' | cut -c1-80)
if [ -z "$slug" ]; then slug="gitnexus-grounding"; fi
stamp=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$repo/$out_dir" 2>/dev/null || mkdir -p "$out_dir"
case "$out_dir" in
  /*) out="$out_dir/gitnexus-$slug-$stamp.md" ;;
  *) out="$repo/$out_dir/gitnexus-$slug-$stamp.md" ;;
esac

run_block() {
  local title="$1"; shift
  {
    echo "### $title"
    echo
    echo '```text'
    echo "+ $*"
    (cd "$repo" && "$@") 2>&1 || true
    echo '```'
    echo
  } >> "$out"
}

{
  echo "# GitNexus grounding: $task"
  echo
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Mode: $mode"
  echo "Repo path: $repo"
  echo
  echo "## Summary"
  echo
  echo "This preflight is read-only. It checks GitNexus/Codex MCP availability and index health before a primary workflow plans or edits code."
  echo
} > "$out"

if command -v git >/dev/null 2>&1; then
  run_block "Git root" git rev-parse --show-toplevel
  run_block "Git HEAD" git rev-parse --short HEAD
  run_block "Git working tree short status" git status --short
else
  {
    echo "## Git"
    echo
    echo "git command not found."
    echo
  } >> "$out"
fi

if command -v gitnexus >/dev/null 2>&1; then
  run_block "GitNexus version" gitnexus --version
  run_block "GitNexus status" gitnexus status
  run_block "GitNexus list" gitnexus list
else
  {
    echo "## GitNexus"
    echo
    echo "gitnexus command not found. Install/configure GitNexus before relying on graph context."
    echo
  } >> "$out"
fi

if command -v codex >/dev/null 2>&1; then
  run_block "Codex MCP list" codex mcp list
else
  {
    echo "## Codex MCP"
    echo
    echo "codex command not found; cannot verify MCP registration."
    echo
  } >> "$out"
fi

{
  echo "## Recommended next steps"
  echo
  echo "- If index is fresh: use GitNexus MCP or CLI \`context\`, \`impact\`, and \`cypher\` for known symbols."
  echo "- If index is stale/missing: run \`gitnexus analyze\` from the repo root, or \`gitnexus index <path>\` for an existing .gitnexus folder."
  echo "- If composing with \`\$deep-interview\`: ask user intent/boundary questions after reading this report; do not ask where code lives until graph/source checks are exhausted."
  echo "- If composing with \`\$plan\` or \`\$ralplan\`: cite this report and direct source file/line evidence in the plan."
  echo
  echo "Report path: $out"
} >> "$out"

printf '%s\n' "$out"

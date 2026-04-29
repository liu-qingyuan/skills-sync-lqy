#!/usr/bin/env bash
set -u -o pipefail

repo="."
out=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="${2:-}"
      shift 2
      ;;
    --out)
      out="${2:-}"
      shift 2
      ;;
    -h|--help)
      cat <<'HELP'
Usage: preflight.sh [--repo PATH] [--out FILE]

Capture non-secret GitNexus/Codex-wiki preflight evidence for a repository.
HELP
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$repo" ]]; then
  echo "--repo must not be empty" >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 2
fi

if ! command -v gitnexus >/dev/null 2>&1; then
  echo "gitnexus CLI not found on PATH" >&2
  exit 3
fi

if [[ ! -d "$repo" ]]; then
  echo "Repository path does not exist: $repo" >&2
  exit 2
fi

repo_abs=$(cd "$repo" && pwd)
if ! git_root=$(git -C "$repo_abs" rev-parse --show-toplevel 2>/dev/null); then
  echo "Not inside a git repository: $repo_abs" >&2
  exit 4
fi
commit=$(git -C "$git_root" rev-parse HEAD 2>/dev/null || true)
version=$(gitnexus --version 2>/dev/null || true)
created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

render() {
  cat <<REPORT
# GitNexus Codex Wiki preflight

- generated_at: $created_at
- repo_root: $git_root
- commit: $commit
- gitnexus_version: $version
- execution_boundary: GitNexus supplies graph/index context; Codex authors markdown directly.

## gitnexus status

\`\`\`text
$(cd "$git_root" && gitnexus status 2>&1)
\`\`\`

## gitnexus list

\`\`\`text
$(gitnexus list 2>&1)
\`\`\`

## index guidance

If status reports no index or a stale index, do not make graph-dependent wiki claims until the index is created or refreshed with authorized local GitNexus commands such as \`gitnexus analyze\`.
REPORT
}

if [[ -n "$out" ]]; then
  mkdir -p "$(dirname "$out")"
  render > "$out"
  echo "Wrote preflight evidence: $out"
else
  render
fi

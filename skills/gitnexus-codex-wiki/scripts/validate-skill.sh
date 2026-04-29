#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$skill_dir/scripts/validate-skill.py" "$skill_dir" "$@"

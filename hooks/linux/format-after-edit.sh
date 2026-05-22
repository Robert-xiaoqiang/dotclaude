#!/usr/bin/env bash
# PostToolUse(Edit|Write) hook — formats the edited file by extension,
# if the matching formatter is installed. No-ops otherwise.
set -euo pipefail
file=$(python3 -c 'import json,sys;print((json.load(sys.stdin).get("tool_input") or {}).get("file_path",""))')
[ -n "$file" ] && [ -f "$file" ] || exit 0
case "$file" in
  *.py)                                   command -v black    >/dev/null && black -q "$file" ;;
  *.js|*.ts|*.jsx|*.tsx|*.json|*.css|*.md) command -v prettier >/dev/null && prettier --write "$file" >/dev/null 2>&1 ;;
  *.go)                                   command -v gofmt    >/dev/null && gofmt -w "$file" ;;
  *.rs)                                   command -v rustfmt  >/dev/null && rustfmt "$file" 2>/dev/null ;;
esac
exit 0

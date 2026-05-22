#!/usr/bin/env bash
# PreToolUse(Edit|Write) hook — blocks Claude from editing secret files.
# Reads the hook event JSON on stdin; exit 2 = block (stderr shown to Claude).
set -euo pipefail
python3 -c '
import json, re, sys
d = json.load(sys.stdin)
p = (d.get("tool_input") or {}).get("file_path", "") or ""
pats = [r"\.env($|\.)", r"\.pem$", r"\.key$", r"id_rsa", r"credentials", r"\.secret"]
if any(re.search(x, p, re.I) for x in pats):
    sys.stderr.write("Blocked: %r looks like a secret file; edit it manually.\n" % p)
    sys.exit(2)
'

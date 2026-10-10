#!/usr/bin/env bash
# Push an Overleaf-backed git repo, reading the token from $CPFS_HOME/.secret.
#
# WHY THIS EXISTS. The Overleaf remote authenticates with a token, not an SSH
# key, so git-push's key discovery does not apply to it. The token lives in
# $CPFS_HOME/.secret as OVERLEAF_TOKEN and must never be pasted into a command,
# a commit message or a transcript. This wrapper reads it, hands it to git
# through a one-shot credential helper, filters it out of all output, and
# deletes the helper on exit even if the push fails.
#
# Overleaf also times out server-side on a push it has already applied, so a
# rejection is not proof that nothing landed. This re-fetches afterwards and
# compares, which is the only reliable check.
#
#   usage: overleaf-push.sh [remote] [branch]     (defaults: origin, current)
set -euo pipefail

REMOTE=${1:-origin}
BRANCH=${2:-$(git branch --show-current)}
: "${CPFS_HOME:?CPFS_HOME is not set}"
SECRET="$CPFS_HOME/.secret"
[ -r "$SECRET" ] || { echo "no readable $SECRET" >&2; exit 1; }

set -a; . "$SECRET"; set +a
[ -n "${OVERLEAF_TOKEN:-}" ] || { echo "OVERLEAF_TOKEN not in $SECRET" >&2; exit 1; }

HELPER=$(mktemp); trap 'rm -f "$HELPER"' EXIT
printf '#!/bin/sh\necho username=git\necho password=%s\n' "$OVERLEAF_TOKEN" > "$HELPER"
chmod 700 "$HELPER"
scrub () { sed "s/$OVERLEAF_TOKEN/[token]/g; s/olp_[A-Za-z0-9]*/[token]/g"; }
g () { git -c credential.helper="$HELPER" "$@" 2>&1 | scrub; }

# Someone else edits the Overleaf project concurrently, so never push without
# rebasing onto what is there.
echo "==> pull --rebase"
g pull --rebase | tail -5

echo "==> pushing $BRANCH -> $REMOTE/$BRANCH"
PUSH_OK=yes
g push "$REMOTE" "$BRANCH" | tail -4 || PUSH_OK=no

echo "==> verifying against the remote"
g fetch "$REMOTE" >/dev/null || true
LOCAL=$(git rev-parse HEAD)
UPSTREAM=$(git rev-parse "$REMOTE/$BRANCH")
if [ "$LOCAL" = "$UPSTREAM" ]; then
  echo "LANDED: $REMOTE/$BRANCH is at $(git rev-parse --short HEAD)"
else
  echo "NOT LANDED: local $(git rev-parse --short HEAD), remote $(git rev-parse --short "$REMOTE/$BRANCH")"
  [ "$PUSH_OK" = no ] && echo "(the push also reported an error; a timeout here can still mean it applied, so re-run)"
  exit 1
fi

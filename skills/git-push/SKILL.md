---
name: git-push
description: "Push local commits to the correct remote and branch with the right SSH key, after fetching and verifying the branch is strictly ahead. Never force-pushes main and never bypasses hooks."
when_to_use: "Use ONLY when the user explicitly asks to push. Never runs automatically after a commit."
---
# Skill: git-push

## Purpose
Push local commits to the correct remote repository and branch, using an SSH private key when needed.

## Rules

### SSH key
- When pushing, use an SSH private key found under `~/.ssh/` (search recursively, including subdirectories like `~/.ssh/sn2github/sn2github`).
- Discovery: run `find ~/.ssh -type f ! -name "*.pub" ! -name "known_hosts*" ! -name "config" ! -name "authorized_keys" 2>/dev/null` to find all private key files.
- `known_hosts*` with the glob, not `known_hosts`: `ssh-keygen -R` leaves a `known_hosts.old` behind, which the bare name does not exclude. It then shows up as a second "key" and invites picking the wrong one, or reporting "exactly one key" when there are two.
- If a match looks doubtful, confirm before using it: a private key's first line is `-----BEGIN ... PRIVATE KEY-----`.
- Invoke git with `GIT_SSH_COMMAND="ssh -i <key_path> -o IdentitiesOnly=yes"` so the correct key is used regardless of ssh-agent state.
- If multiple keys exist, list them and confirm which to use unless the user has already specified.
- If exactly one key is found, use it automatically without asking.
- **A bare `ssh -T git@github.com` proves nothing about which account you will push as**, because it
  uses the default `id_rsa` rather than the key you intend. Observed: that test returned a different
  GitHub user, the push failed with `Could not read from remote repository`, and the cause looked
  like a network or repo-existence problem rather than the wrong identity. Test with
  `ssh -i <key> -o IdentitiesOnly=yes -T git@github.com` and read the username it greets you by.

### Token remotes (Overleaf), not SSH keys
- An Overleaf remote authenticates with a token, so the key discovery above does not apply to it.
- The token is `OVERLEAF_TOKEN` in `$CPFS_HOME/.secret`. **Read it from there.** Never paste a token
  into a command, a commit message, a script that gets committed, or a transcript, and never echo it.
- Use the bundled `overleaf-push.sh` (`skills/git-push/overleaf-push.sh`), which sources the file,
  passes the token through a one-shot credential helper, filters it out of every line of output,
  deletes the helper via an EXIT trap, rebases first because a co-author edits the project
  concurrently, and then re-fetches to confirm what actually landed.
- **An Overleaf push that reports `remote rejected ... Request timed out` may still have been
  applied.** Observed: a push timed out after 360 s, Overleaf had committed it under its own
  "Update on Overleaf." message, and the retry then failed with `fetch first`. So a failure is not
  evidence that nothing landed. Always re-fetch and compare before retrying or re-committing.
- `$CPFS_HOME/.secret` may hold a different, newer token than one quoted earlier in a conversation.
  The file is the source of truth, not the chat history.

### Verify remote state before pushing
- ALWAYS run `git fetch <remote>` first, then compare local HEAD vs remote with `git status -sb` or `git log --oneline <remote>/<branch>..HEAD` and `git log --oneline HEAD..<remote>/<branch>`.
- If the remote is ahead, STOP and warn the user — do NOT force-push. Suggest `git pull --rebase` or a merge, let the user decide.
- If local and remote have diverged, surface both sides of the divergence before taking any action.
- Only push after confirming the local branch is strictly ahead of (or equal to) the remote branch.

### Multiple remotes
- If `git remote -v` shows more than one remote (e.g. `origin`, `upstream`, `fork`), never assume `origin`.
- Print the remote list and explicitly confirm (or take from user args) which remote to push to.
- Each remote may have different URLs/permissions — verify the target URL before pushing.

### Multiple branches
- If the working tree has multiple local branches or the user has not specified a branch, confirm the current branch with `git branch --show-current` and ask before pushing a non-current branch.
- Use explicit refspec `git push <remote> <local-branch>:<remote-branch>` when source and destination names differ.
- For a brand-new branch, use `git push -u <remote> <branch>` to set upstream tracking.

### Correct repo + branch guard
- Before the actual push, echo a one-line summary: `pushing <local-branch> → <remote>/<remote-branch> (<remote-url>)` so the user can see and abort if wrong.
- Never push to `main`/`master` with `--force` or `--force-with-lease` unless the user explicitly requests it, and even then warn first.
- Never bypass hooks (`--no-verify`) unless the user explicitly asks.

## Typical flow
1. `git remote -v` and `git branch --show-current` — identify remote + branch.
2. `GIT_SSH_COMMAND="ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes" git fetch <remote>`.
3. `git status -sb` — check ahead/behind counts.
4. If behind or diverged → stop, report to user.
5. Echo push summary line.
6. `GIT_SSH_COMMAND="ssh -i ~/.ssh/<key> -o IdentitiesOnly=yes" git push <remote> <branch>`.
7. Report the pushed commit range and remote URL back to the user.

## When to Use
- ONLY when the user explicitly asks to push (e.g. "push it", "push to remote", "/git-push").
- NEVER push automatically after a commit. Auto git-commit is allowed, auto git-push is NOT.
- If you just committed changes, report what was committed and STOP. Do not chain `&& git push`.
- Wait for the user's explicit instruction before invoking this skill.

## Companions
`git-commit` (the commit side, including the hook that strips signatures before a commit exists) · `naming-descriptive` (what a branch is called).

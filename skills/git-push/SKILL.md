# Skill: git-push

## Purpose
Push local commits to the correct remote repository and branch, using an SSH private key when needed.

## Rules

### SSH key
- When pushing, use an SSH private key found under `~/.ssh/` (search recursively, including subdirectories like `~/.ssh/sn2github/sn2github`).
- Discovery: run `find ~/.ssh -type f ! -name "*.pub" ! -name "known_hosts" ! -name "config" ! -name "authorized_keys" 2>/dev/null` to find all private key files.
- Invoke git with `GIT_SSH_COMMAND="ssh -i <key_path> -o IdentitiesOnly=yes"` so the correct key is used regardless of ssh-agent state.
- If multiple keys exist, list them and confirm which to use unless the user has already specified.
- If exactly one key is found, use it automatically without asking.

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

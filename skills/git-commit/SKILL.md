---
name: git-commit
description: "Create git commits following the user's conventions: no AI attribution or Co-Authored-By trailers, concise messages about what and why, and untracked files surfaced rather than silently skipped."
when_to_use: "Use whenever creating a git commit."
---
# Skill: git-commit

## Purpose
Create git commits following the user's conventions.

## Rules
- NEVER include `Co-Authored-By` trailers in commit messages
- NEVER include any AI attribution lines in commit messages
- Keep commit messages concise (1-2 lines)
- Focus on the "what" and "why", not the "how"
- Always check untracked files (`git status -u`) — ask the user whether to stage, gitignore, or leave them. Don't silently skip untracked files.

## When to Use
- Whenever creating a git commit

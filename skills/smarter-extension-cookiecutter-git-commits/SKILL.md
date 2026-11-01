---
name: smarter-extension-cookiecutter-git-commits
description: Use whenever the user asks you to "write a git commit" (or a commit message, or the git add) in the Smarter Extension Cookiecutter template repository (smarter-sh/smarter-extension-cookiecutter). Covers the never-execute rule, authorship, the multiple -m command format, choosing the conventional-commit type (which decides the template's semantic-release release), the 72-character header, and the body.
---

# Cookiecutter Git Commits

## The rule: write, never execute

"Write a git commit", in any wording or tone, means **output the command as text**. Never execute
`git commit`, `git add`, `git reset`, `git restore --staged`, `git push`, `git tag`, `git stash`
or any other git command that writes. Read-only commands are fine. Don't volunteer commit messages.

## Authorship

You are the author: `--author="Claude <noreply@anthropic.com>"`. The last `-m` is
`Co-authored-by: Lawrence McDaniel <lpm0073@gmail.com>`.

## Command format

```console
git commit --author="Claude <noreply@anthropic.com>" \
  -m "<type>(<scope>): <subject>" \
  -m "<body paragraph>" \
  -m "<body paragraph or bullet list>" \
  -m "Co-authored-by: Lawrence McDaniel <lpm0073@gmail.com>"
```

- One `-m` per paragraph; a bullet list in a single `-m`, with real newlines.
- No heredoc, no `-F`, and no `git add` in the same block. When asked for the `git add`, write it
  as a separate block with explicit paths. Paths under `{{cookiecutter.repository_name}}/` must be
  single-quoted, or the shell may mangle the braces.
- Avoid backticks, `$` and `!` in the double quotes (zsh history expansion).
- Never write a CI skip instruction anywhere in the message (`[skip ci]` and its variants).
- Header: 72 characters or fewer (commitlint enforces it). Measure: `printf %s "<header>" | wc -c`.
- `chore(release): ...` belongs to semantic-release. Never write it.

## Type: it decides the template's release

semantic-release releases the template on each push to `main`, and authors can generate from a
tag. `feat` (a new question, a new starter, a new capability of the generated repository) releases
a minor version; `fix` and `perf` a patch; a `BREAKING CHANGE:` paragraph (a question removed or
renamed, so `--no-input` scripts break) a major one; `docs`, `test`, `ci`, `refactor`, `style`,
`build` and `chore` nothing. When in doubt, it's `fix`.

**Scope**: `hooks`, `starter`, `skills`, `ci`, `pre-commit`, ... or none.

## Body

The problem first; then a bullet per change, naming files, questions and generated files; then the
tests (`make test`, `make test-generated`, generated pre-commit) and what they proved; then the
status, including which official extensions need the same change to a shared file.

Start your reply with a one-line `Written for:` audience note.

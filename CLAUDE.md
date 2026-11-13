# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

This is the Cookiecutter template for new Smarter Extensions. `cookiecutter.json` holds the
questions, `hooks/` checks the answers and finishes the generated project, and
`{{cookiecutter.repository_name}}/` is the repository it generates: a working extension modeled on
the official ones (`../smarter-extension-weather`, `-calculator`, `-date-calculator`), with
Smarter's repository setup (`../smarter`: pre-commit, Makefile, conventional commits,
semantic-release) and its own agent skills.

Detailed know-how lives in the Agent Skills under `skills/` (symlinked to `.claude/skills`).
**Load `smarter-extension-cookiecutter-development` first for any change.** The skills inside
`{{cookiecutter.repository_name}}/skills/` are part of the template's output, for the generated
extension, not instructions for this repository; read them when you change them.

## Hard rules

1. **Never run git write commands.** "Write a git commit" means print the command as text. See
   `smarter-extension-cookiecutter-git-commits`.
2. **Run the tests yourself** after any change: `make test`, and `make test-generated` and
   `make lint-generated` for any change to what is generated. Never ask the user to. Report
   failures honestly. Don't lint untracked files with `pre-commit run --files`: a hook's rewrite
   of one reports "Passed".
3. **Files shared with the official extensions stay identical**: `release.config.js`,
   `package.json`, `.github/workflows/release.yml`, `.github/workflows/test.yml`, `scripts/` and
   `skills/` in `{{cookiecutter.repository_name}}/`. A change to one is made in every official
   extension too, in the same piece of work.
4. **Smarter is the standard for repository setup.** Copy its conventions (`../smarter`:
   `.pre-commit-config.yaml`, `Makefile`, `.editorconfig`, commitlint) rather than inventing new
   ones.
5. **The `smarter-api` container holds live cloud credentials.** Generated tests mock every
   third-party service.
6. **The template is the example authors copy.** Every module, class, function and method it
   generates, and every one in its tests and hooks, has a full Sphinx docstring (`:param:`,
   `:returns:`, `:raises:`). `test_docstrings` checks it; see
   `smarter-extension-cookiecutter-development`.
7. **This repository is public.** No API keys, tokens, account ids or private hostnames.

## Commit authorship

You are the author: `--author="Claude <noreply@anthropic.com>"`. Lawrence McDaniel is the
co-author: the last `-m` is `Co-authored-by: Lawrence McDaniel <lpm0073@gmail.com>`.

## Definition of done

- `make test` passes, and `make test-generated` and `make lint-generated` for changes to what is
  generated.
- The pre-commit hooks pass on the changed files.
- The README's questions table and tree match `cookiecutter.json` and the template.
- Your summary says what changed, what you verified, what you skipped, and whether the official
  extensions need the same change.

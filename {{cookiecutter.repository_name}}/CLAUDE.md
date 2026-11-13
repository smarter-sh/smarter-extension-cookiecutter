# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

This is the **{{ cookiecutter.extension_name }}** Smarter Extension (slug
`{{ cookiecutter.extension_slug }}`, package `{{ cookiecutter.package_name }}`):
{{ cookiecutter.description }} Its tool is `{{ cookiecutter.tool_name }}`
(`{{ cookiecutter.package_name }}.tools:{{ cookiecutter.tool_class }}`).

A Smarter Extension is a Python package that a Smarter platform installs from the signed registry
(smarter-sh/extensions-registry) and runs inside itself. Its tools subclass
`smarter.apps.llmtool.extension.SmarterExtensionTool`, so the tests run against a checkout of
smarter-sh/smarter: the sibling `../smarter` and its `smarter-api` container.

This repository was generated from smarter-sh/smarter-extension-cookiecutter. Detailed know-how
lives in the Agent Skills under `skills/` (symlinked to `.claude/skills`).
**Load `smarter-extension-development` first for any change.**

## Hard rules

1. **Never run git write commands.** "Write a git commit" means print the command as text. See
   `smarter-extension-git-commits`.
2. **Never edit `version` in `pyproject.toml`, or `CHANGELOG.md`.** semantic-release writes them
   on each push to `main`, and the commit type decides the release. See `smarter-extension-release`.
3. **Run the tests yourself**, after any change: `make validate` (the tests with coverage, then
   `manage.py validate_extension`). Never ask the user to. Report failures honestly.
4. **The `smarter-api` container holds the developer's credentials.** Tests mock every third-party
   service and use placeholder keys. Don't run anything there that writes to real infrastructure.
5. **Import only what the platform installs** (`../smarter/smarter/requirements/base.txt`), and
   use relative imports inside the package.
6. **The pre-commit hooks are the lint standard**: run them on the changed files.
7. **Every module, class, function and method has a Sphinx docstring**, tests included: a one-line
   summary, a body that says why, and `:param:`, `:returns:` and `:raises:` fields. The tool class's
   docstring is the exception: it is the LLM's description of the tool. See
   `smarter-extension-development`.
8. **This repository is public.** No API keys, tokens, account ids or private hostnames.

## Commit authorship

{{ cookiecutter.author_name }} is the author: no `--author`. The last `-m` is
`Co-authored-by: Claude <noreply@anthropic.com>`. See `smarter-extension-git-commits`.

## Common commands

```bash
make validate                                        # tests, coverage, validate_extension
git diff --name-only | xargs venv/bin/pre-commit run --files
make package                                         # the release archive, in dist/
```

## Definition of done

- The change follows the patterns of the official extensions, and the tests cover it (coverage
  stays at 100%).
- You ran `make validate`, and the pre-commit hooks on the changed files.
- The package docstring, README and the tool and field descriptions match the code.
- Everything you added or changed has a docstring in the style of the starter code.
- Your summary says what changed, what you verified, what you skipped, and which commit type (and
  so which release) the change needs.

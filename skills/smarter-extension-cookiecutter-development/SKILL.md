---
name: smarter-extension-cookiecutter-development
description: Start here for any change to the Smarter Extension Cookiecutter template (smarter-sh/smarter-extension-cookiecutter) - its questions in cookiecutter.json, the pre- and post-generation hooks, the generated repository under {{cookiecutter.repository_name}}/ (starter tools, tests, pyproject.toml, Makefile, pre-commit, workflows, CLAUDE.md and skills), the template's tests, or keeping the template and the official extensions in step. Covers the layout, Jinja and its traps (GitHub expressions, copy-without-render), the starters, testing by generating, and the files shared with the official extensions.
---

# Smarter Extension Cookiecutter Development

The template generates a new Smarter Extension repository. Its output must always be a working
extension: one that passes its own tests at 100% coverage, `manage.py validate_extension`, and
every pre-commit hook, from the first commit.

## Layout

| Path                                 | What lives there                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------- |
| `cookiecutter.json`                  | Questions, defaults derived from earlier answers, `__prompts__`, choices        |
| `hooks/pre_gen_project.py`           | Refuses answers Smarter would refuse. Jinja-rendered, so not valid Python as is |
| `hooks/post_gen_project.py`          | Removes the other starter's files, picks the license, links `.claude/skills`    |
| `{{cookiecutter.repository_name}}/`  | The generated repository                                                        |
| `.../{{cookiecutter.package_name}}/` | The starter tool: `tools.py`, and `models.py`, `services.py` for web-api        |
| `.../_licenses/`                     | One file per license choice; the hook moves the chosen one to `LICENSE`         |
| `.../skills/`, `.../CLAUDE.md`       | The generated extension's agent instructions                                    |
| `tests/test_bake.py`                 | Generates extensions with different answers, and checks them                    |
| `skills/`, `CLAUDE.md`               | Instructions for working on the template itself                                 |

## Jinja traps

Cookiecutter renders every file and file name under `{{cookiecutter.repository_name}}/` with
Jinja, except those matched by `_copy_without_render` in `cookiecutter.json`.

- **GitHub Actions expressions** (`${{ secrets.X }}`) are Jinja syntax. Workflows are in
  `_copy_without_render`, so they can't use answers. A workflow that needs one must escape every
  GitHub expression (`{{ '${{' }} ... }}`) instead; prefer keeping it unrendered.
- **Shell and Go templates** (`docker inspect -f '{{.State.Running}}'` in `run-tests.sh`) break
  rendering too: `scripts/*` is unrendered.
- **Strings that answers go into**: `pyproject.toml` (TOML strings), docstrings, the
  pre-generation hook. The hook renders answers with `| tojson`, which is a valid Python string
  literal whatever the answer holds, and refuses double quotes, backslashes and line breaks in
  the free-text answers.
- **Whitespace**: use `{%-` and `-%}` so a skipped block leaves no blank lines; the generated
  files must pass black, Prettier and end-of-file-fixer as generated. `test_nothing_unrendered`
  catches a leftover tag, the generated-lint CI job catches formatting.
- A reStructuredText title's underline is rendered to the title's length
  (`{{ "=" * cookiecutter.extension_name | length }}`).

## The starters

- **web-api**: a tool that calls an HTTP API with `requests` (installed by the platform), an
  `api_key` secret setting and an `api_url` setting, Pydantic arguments and result models, and a
  `services.py` that turns every failure into `ServiceError`, which the tool turns into an
  `ExtensionToolError` for the LLM. Modeled on smarter-extension-weather.
- **pure-function**: a tool with no settings or dependencies, which computes its result in
  Python, and bounds its input. Modeled on smarter-extension-calculator.

Both follow the tool protocol and conventions in the generated
`skills/smarter-extension-development/SKILL.md`. Keep them small: an author replaces them.

## Docstrings: the template is the example

Authors copy the starter's style, so every Python file the template generates, its tests, its
hooks and the shared release scripts meet Smarter's docstring standard (`../smarter`'s
`smarter-docstrings` skill) in full, more strictly than Smarter's own tests do:

- Every module, class, function and method has a docstring, tests and `setUpClass` included, and
  every module-level constant has one on the line after it.
- The opening `"""` on its own line, a one-line summary ending with a period, a blank line, a body
  that says why, then the fields: `:param:` for each argument but `self` and `cls`, `:returns:`
  unless it returns None, `:raises <Error>: when ...` (`AssertionError` for a test).
- Two exceptions hold no fields, because Smarter reads them: the tool class's docstring (the LLM's
  description of the tool) and `<package>/__init__.py`'s (the administrators' documentation).

`test_docstrings` in `tests/test_bake.py` checks both generated starters and the template's tests
with `docstring_problems()`. It can't check the hooks, which are Jinja until rendered: review them
by hand. The generated `CONTRIBUTING.md`, `CLAUDE.md` and `smarter-extension-development` skill
state the standard for authors; keep them in step with it.

## Answers

Every question has a default, so `cookiecutter --no-input` always works (CI relies on it). A new
question needs: a default, a `__prompts__` entry, a check in `pre_gen_project.py` if a bad answer
would produce an extension Smarter refuses (copy the rule from Smarter's
`smarter.apps.llmtool.extension.manifest` or `protocol`), a test in `test_bake.py`, and a row in
the README's table.

## Testing

```bash
make test             # tests/test_bake.py: no Smarter needed
make test-generated   # generate both starters into build/, run each one's scripts/run-tests.sh --validate
make lint-generated   # generate each starter, cached and uncached, and run its pre-commit hooks
```

`make test-generated` needs the `smarter-app` container of `../smarter` running. Run it, and
`make lint-generated`, after any change to what is generated.

**Never lint generated output by passing untracked files to `pre-commit run --files`.** pre-commit
detects a hook's rewrite with `git diff`, which doesn't see untracked files, so a hook that
rewrites one (pydocstringformatter, isort, black, Prettier) reports "Passed". `make lint-generated`
compares the linted copy with an untouched one instead, so a rewrite fails, as it does in CI,
where the files are staged. For the same reason, a template file that isn't committed yet can't be
checked by running the hooks on it.

Two other traps:

- The template renders different code for each starter and for `cache_ttl` 0 and above, so lint
  every combination. `lint-generated` and CI do.
- This repository's `.prettierignore` excludes `{{cookiecutter.repository_name}}/`, so Prettier
  run from here silently skips the generated skills and README. Format them in a generated copy,
  or a copy outside this repository.

CI (`.github/workflows/test.yml`) runs the template tests and the template repository's own hooks,
then, per starter and `cache_ttl`, generates an extension, runs its tests against a sparse
checkout of Smarter with `--fail-under=100`, and runs its hooks on the staged files.

## Files shared with the official extensions

`release.config.js`, `package.json`, `.github/workflows/release.yml`, `.github/workflows/test.yml`,
`scripts/package.py`, `scripts/set_version.py`, `scripts/run-tests.sh` and everything under
`skills/`, in `{{cookiecutter.repository_name}}/`, are byte for byte the same as in
smarter-extension-weather, -calculator and -date-calculator (`test_shared_files_unchanged` checks
that generation doesn't change them). Change them here and in every official extension, in the
same piece of work, and check:

```bash
T='{{cookiecutter.repository_name}}'
for r in weather calculator date-calculator; do E=../smarter-extension-$r
  for f in release.config.js package.json .github/workflows/release.yml .github/workflows/test.yml \
    scripts/package.py scripts/set_version.py scripts/run-tests.sh; do diff -q "$T/$f" "$E/$f"; done
  diff -rq "$T/skills" "$E/skills"; done
```

Everything else in the generated repository (pre-commit, Makefile, lint workflow, issue
templates, README, CLAUDE.md) is newer than the official extensions, which don't have all of it
yet. Bringing them up to the template is a separate change in each.

## Repository setup follows Smarter

The generated repository and this one copy `../smarter`'s setup: `.pre-commit-config.yaml` (minus
its React hooks), the Makefile's target names and banners, `.editorconfig`, `commitlint.config.js`,
`.prettierrc.json`, the pull request template. When Smarter's setup changes (e.g. a hook's version, a
new hook), follow it here. One intended difference: `.flake8` here selects flake8's normal checks,
with line length 120.

## Definition of done

- `make test` passes, and `make test-generated` and `make lint-generated` for any change to
  what is generated.
- The README's questions table and tree match the template.
- Shared files are the same here and in the official extensions, or your summary says which
  official extensions still need the change.

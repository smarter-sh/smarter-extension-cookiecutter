# Smarter Extension Cookiecutter

[![Test Status](https://github.com/smarter-sh/smarter-extension-cookiecutter/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/smarter-sh/smarter-extension-cookiecutter/actions/workflows/test.yml)
[![Latest Release](https://img.shields.io/github/v/release/smarter-sh/smarter-extension-cookiecutter?label=release)](https://github.com/smarter-sh/smarter-extension-cookiecutter/releases)
[![Docs](https://img.shields.io/badge/Read%20the%20Docs-smarter.sh-blue?logo=readthedocs)](https://docs.smarter.sh/en/latest/smarter-framework/smarter-extensions.html)
[![License: GNU AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/) template for a new
[Smarter Extension](https://docs.smarter.sh/en/latest/smarter-framework/smarter-extensions.html): a
Python package that adds tools to the LLMs of every Smarter platform that installs it. It generates
a repository that is set up the way the official extensions
([weather](https://github.com/smarter-sh/smarter-extension-weather),
[calculator](https://github.com/smarter-sh/smarter-extension-calculator),
[date-calculator](https://github.com/smarter-sh/smarter-extension-date-calculator)) are, with a
working tool whose tests pass at 100% coverage from the first commit.

## Use it

```console
pip install cookiecutter
cookiecutter gh:smarter-sh/smarter-extension-cookiecutter
```

To generate from a given release of the template, add `--checkout v<version>`.

It asks:

| Question                      | Default                       | Meaning                                                                                                                                     |
| ----------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `extension_name`              | My Extension                  | The name administrators see (`display-name`)                                                                                                |
| `extension_slug`              | from the name: `my-extension` | The permanent identifier that LLMClients list. Lowercase words and hyphens, ≤ 32                                                            |
| `package_name`                | from the slug: `my_extension` | The Python package                                                                                                                          |
| `repository_name`             | `smarter-extension-<slug>`    | The GitHub repository, by convention                                                                                                        |
| `description`                 |                               | One line on what it gives LLMs                                                                                                              |
| `starter`                     | `web-api`                     | `web-api`: a tool that calls an HTTP API, with `api_key` and `api_url` settings. `pure-function`: a tool that computes its result in Python |
| `tool_name`                   | the package name              | The tool's name. The LLM sees `ext_<slug>_<tool_name>`                                                                                      |
| `tool_class`                  | from the tool name            | The tool's Python class                                                                                                                     |
| `cache_ttl`                   | 0                             | Seconds to cache results. Only for a tool that changes nothing and answers the same whoever asks                                            |
| `timeout`                     | 30                            | Seconds a call may run, 1 to 300                                                                                                            |
| `requires_smarter`            | `>=0.27`                      | The Smarter versions it works with                                                                                                          |
| `author_name`, `author_email` |                               | You                                                                                                                                         |
| `github_owner`                |                               | The GitHub user or organization of the repository                                                                                           |
| `publisher_id`                | the GitHub owner              | Your publisher id in the [registry](https://github.com/smarter-sh/extensions-registry)                                                      |
| `license`                     | `AGPL-3.0`                    | `AGPL-3.0` (Smarter's), `MIT` or `Apache-2.0`                                                                                               |

Answers that would make an extension that Smarter refuses (an invalid slug or tool name, a timeout
out of range, quotes in a name) stop generation with a message that says why.

## What you get

```text
smarter-extension-<slug>/
├── pyproject.toml            [project] and [tool.smarter]: slug, tools, settings
├── <package>/
│   ├── __init__.py           the documentation administrators read, in reStructuredText
│   ├── tools.py              the tool: a SmarterExtensionTool subclass
│   ├── models.py             its arguments and result (web-api)
│   └── services.py           the calls to the third-party API (web-api)
├── tests/                    unittest tests, services mocked, 100% coverage
├── scripts/                  run-tests.sh, and the release's set_version.py and package.py
├── .github/workflows/        test.yml (tests + Codecov), lint.yml (pre-commit), release.yml
├── release.config.js         semantic-release: versions, CHANGELOG, archive, GitHub release
├── .pre-commit-config.yaml   Smarter's lint standard, and commitlint on commit messages
├── Makefile                  init, test, validate, lint, package
├── CLAUDE.md, skills/        instructions for AI coding agents (.claude/skills links to skills/)
└── README, LICENSE, SECURITY, CONTRIBUTING, CHANGELOG, issue and pull request templates
```

The repository follows [Smarter](https://github.com/smarter-sh/smarter)'s own setup: the same
pre-commit hooks (black, flake8, isort, autoflake, bandit, codespell, pyupgrade,
pydocstringformatter, Prettier, commitlint), Makefile conventions, conventional commits and
semantic-release. Its README explains the first steps: the tests run in a
[Smarter development environment](https://github.com/smarter-sh/smarter), and each release is
published with a pull request to the
[Smarter Extension registry](https://github.com/smarter-sh/extensions-registry).

## Develop the template

```console
make init             # a virtual environment with cookiecutter and pre-commit, and the hooks
make test             # generate extensions with different answers, and check them
make test-generated   # generate both starters, and run their own tests in a Smarter container
make bake             # generate one into build/, to look at
make lint
```

| Path                                | Contents                                                    |
| ----------------------------------- | ----------------------------------------------------------- |
| `cookiecutter.json`                 | The questions, their defaults and prompts                   |
| `hooks/pre_gen_project.py`          | Checks the answers                                          |
| `hooks/post_gen_project.py`         | Keeps the starter's files and the license, links the skills |
| `{{cookiecutter.repository_name}}/` | The generated repository                                    |
| `tests/test_bake.py`                | The template's tests                                        |
| `skills/`, `CLAUDE.md`              | Instructions for AI coding agents working on the template   |

The release scripts, the release and test workflows, `scripts/run-tests.sh` and `skills/` in the
generated repository are the same files the official extensions use. A change to one of them is
made here and in every official extension.

Releases are made by semantic-release, on each push to `main`, from the commits' conventional
commit types.

## License

GNU AGPL v3. See [LICENSE](LICENSE). The extensions you generate are licensed as you choose.

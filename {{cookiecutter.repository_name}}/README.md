{%- set repo = cookiecutter.github_owner ~ "/" ~ cookiecutter.repository_name -%}
# Smarter Extension: {{ cookiecutter.extension_name }}

[![Test Status](https://github.com/{{ repo }}/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/{{ repo }}/actions/workflows/test.yml)
[![Lint Status](https://github.com/{{ repo }}/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/{{ repo }}/actions/workflows/lint.yml)
[![Coverage](https://img.shields.io/codecov/c/github/{{ repo }}/main?label=coverage&logo=codecov)](https://codecov.io/gh/{{ repo }})
[![Latest Release](https://img.shields.io/github/v/release/{{ repo }}?label=release)](https://github.com/{{ repo }}/releases)
[![Smarter Extension](https://img.shields.io/badge/Smarter%20Extension-community-0b6e4f)](https://github.com/smarter-sh/extensions-registry)
[![Docs](https://img.shields.io/badge/Read%20the%20Docs-smarter.sh-blue?logo=readthedocs)](https://docs.smarter.sh/en/latest/smarter-framework/smarter-extensions.html)
[![License: {{ cookiecutter.license }}](https://img.shields.io/badge/License-{{ cookiecutter.license | replace('-', '--') }}-blue.svg)](LICENSE)

A [Smarter Extension](https://docs.smarter.sh/en/latest/smarter-framework/smarter-extensions.html)
for LLMs: {{ cookiecutter.description }} Its tool, `{{ cookiecutter.tool_name }}`, is offered to
LLMs as `ext_{{ cookiecutter.extension_slug | replace('-', '_') }}_{{ cookiecutter.tool_name }}`.

## Install

In the Django admin console of a Smarter platform, go to **LLMTool › Extensions › Browse
extensions**, and install **{{ cookiecutter.extension_name }}**.
{%- if cookiecutter.starter == "web-api" %} Configure its `api_key` setting,{% endif %} enable it,
and list it in an LLMClient's manifest:

```yaml
spec:
  extensions:
    - {{ cookiecutter.extension_slug }}
```

## Develop

An extension runs inside a Smarter platform, so its tests run against Smarter's code, in the
`smarter-api` container of a [Smarter development environment](https://github.com/smarter-sh/smarter)
cloned beside this repository (its `make init`, then `make run`).

```console
make init        # a virtual environment, and the pre-commit hooks
make test        # the tests, with coverage, in the smarter-api container
make validate    # the tests, then the checks that the installer and the registry make
make lint        # every pre-commit hook, on every file
make package     # dist/{{ cookiecutter.extension_slug }}-<version>.zip, as a release builds it
```

- `pyproject.toml`: `[project]` and `[tool.smarter]`, with the slug, the tools and the settings
- `{{ cookiecutter.package_name }}/__init__.py`: the documentation that administrators read, in reStructuredText
- `{{ cookiecutter.package_name }}/tools.py`: the `{{ cookiecutter.tool_name }}` tool
{%- if cookiecutter.starter == "web-api" %}
- `{{ cookiecutter.package_name }}/models.py`: the tool's arguments and result
- `{{ cookiecutter.package_name }}/services.py`: the calls to the third-party service
{%- endif %}
- `tests/`: unittest tests, run against Smarter
- `scripts/`: the test runner, and the release's version and archive scripts
- `skills/`, `CLAUDE.md`: instructions for AI coding agents

Start with the [developer guide](https://docs.smarter.sh/en/latest/smarter-framework/extensions/developer-guide.html),
and the official extensions, e.g.
[smarter-extension-weather](https://github.com/smarter-sh/smarter-extension-weather). The rules
that matter most:

- Import only the standard library, Smarter, and the libraries that the platform already installs,
  and declare them in `dependencies`. An extension can't install libraries.
- Use relative imports inside `{{ cookiecutter.package_name }}/`.
- Write the tool's docstring and its arguments' descriptions for the LLM, which reads them.
- Mock every third-party service in the tests.
- The slug, `{{ cookiecutter.extension_slug }}`, is permanent.

## Release

Releases are made by [semantic-release](https://semantic-release.gitbook.io/), on each push to
`main`, from the commits' [conventional commit](https://www.conventionalcommits.org/) types: a
`fix:` or `perf:` releases a patch, a `feat:` a minor version, and a `BREAKING CHANGE:` a major
version. Don't edit `version` in `pyproject.toml` or `CHANGELOG.md` by hand: the release sets the
version, adds its notes to the changelog, tags the commit `v<version>`, and attaches the archive
and its sha256 to the GitHub release. See `release.config.js`.

Before the first release:

- In the repository's **Settings › Actions › General**, give workflows **Read and write
  permissions**: the release pushes its commit and tag.
- The first release is 1.0.0. To start at 0.1.0 instead, tag the first commit `v0.0.0` and push
  the tag before the first `feat:`.
- Add the `CODECOV_TOKEN` secret, for the coverage badge.

Then publish each release in the
[Smarter Extension registry](https://github.com/smarter-sh/extensions-registry), with a pull
request that adds `extensions/{{ cookiecutter.extension_slug }}/<version>.yaml`. The release
workflow's summary prints its `archive_url` and `sha256`. The first time, add yourself to its
`publishers.yaml` as `{{ cookiecutter.publisher_id }}`, with `badge: community`.

## License

{{ cookiecutter.license }}. See [LICENSE](LICENSE).

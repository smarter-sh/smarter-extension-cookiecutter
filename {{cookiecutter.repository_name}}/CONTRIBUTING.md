# Contributing

Thank you for helping improve the {{ cookiecutter.extension_name }} Smarter Extension.

1. Set up a [Smarter development environment](https://github.com/smarter-sh/smarter): clone it
   beside this repository, and run its `make init` and `make run`. The tests run in its
   `smarter-api` container, against Smarter's code.
2. In this repository, run `make init`, which creates a virtual environment and installs the
   pre-commit hooks.
3. Make your change, with tests: `make test` runs them with coverage, which stays at 100%, and
   `make validate` also checks the extension as the Smarter installer will. Follow the
   [code style](#code-style-and-documentation) below.
4. Commit with a [conventional commit](https://www.conventionalcommits.org/) message. Its type
   decides the release: `fix` and `perf` release a patch, `feat` a minor version, and a
   `BREAKING CHANGE:` paragraph a major version. `docs`, `test`, `ci`, `refactor` and `chore`
   release nothing. The commit-msg hook checks the format.
5. Open a pull request against `main`. Don't change `version` in `pyproject.toml` or
   `CHANGELOG.md`: the release does.

## Code style and documentation

This extension follows [Smarter](https://github.com/smarter-sh/smarter)'s standard, and the
pre-commit hooks that `make init` installs check most of it: black and isort with a line length
of 120, flake8, bandit, codespell and Prettier.

Every module, class, function and method has a docstring, tests included, in reStructuredText
for Sphinx. The starter code shows the form:

```python
def search(query: str, api_url: str, api_key: str) -> list[JsonValue]:
    """
    Search the service.

    :param query: What to search for.
    :param api_url: The service's search api.
    :param api_key: The service's API key.
    :returns: The service's results.
    :raises ServiceError: If the request fails, or the response has no list of results.
    """
```

- A one-line summary that ends with a period, then a blank line, then the body.
- The body says why, when that isn't obvious: why a limit exists, why caching is safe, what a
  test protects against.
- A `:param:` for each argument, `:returns:` unless the function returns None, and `:raises:` for
  each exception a caller should handle. The type annotations give the types.
- A module-level constant has a docstring on the line after it.

Two docstrings are read by Smarter rather than by developers. The tool class's docstring is the
tool's description for the LLM, so it says what the tool does and when to use it. The package's
`__init__.py` docstring is the extension's documentation for administrators.

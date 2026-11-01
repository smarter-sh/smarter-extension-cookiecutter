"""
Check the answers before the project is generated, with the rules Smarter applies to an extension.

The rules are copied from Smarter's extension validation, so that a generated extension always loads.

Cookiecutter renders this file with the answers (as JSON strings, which are Python string literals
too, whatever they contain), then runs it. A non-zero exit stops generation.
"""

import keyword
import re
import sys

SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
"""A slug, as ``smarter.apps.llmtool.extension.manifest`` accepts it: lowercase words separated by single hyphens."""
TOOL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,47}$")
"""A tool name, as ``smarter.apps.llmtool.extension.protocol`` accepts it: a letter, then letters, digits and underscores."""
PUBLISHER = re.compile(r"^[a-z0-9][a-z0-9-]*$")
"""A publisher id, as the Smarter Extension registry accepts it: lowercase letters, digits and hyphens."""
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
"""A plausible email address: something, an @, and a domain with a dot."""

ANSWERS = {
    "extension_name": {{ cookiecutter.extension_name | tojson }},
    "extension_slug": {{ cookiecutter.extension_slug | tojson }},
    "package_name": {{ cookiecutter.package_name | tojson }},
    "repository_name": {{ cookiecutter.repository_name | tojson }},
    "tool_name": {{ cookiecutter.tool_name | tojson }},
    "tool_class": {{ cookiecutter.tool_class | tojson }},
    "cache_ttl": {{ cookiecutter.cache_ttl | tojson }},
    "timeout": {{ cookiecutter.timeout | tojson }},
    "author_name": {{ cookiecutter.author_name | tojson }},
    "author_email": {{ cookiecutter.author_email | tojson }},
    "description": {{ cookiecutter.description | tojson }},
    "publisher_id": {{ cookiecutter.publisher_id | tojson }},
}
"""The answers that can make an extension Smarter refuses, by question name."""


def problems(answers: dict[str, str]) -> list[str]:
    """
    Check the answers against the rules Smarter applies when it validates an extension.

    :param answers: The answers, by question name, as strings.
    :returns: A description of each answer that would make an extension Smarter refuses, naming the
        question and how to fix it. Empty when every answer is acceptable.
    """
    found = []
    slug = answers["extension_slug"]
    if not SLUG.match(slug) or len(slug) > 32:
        found.append(f"extension_slug {slug!r}: use at most 32 lowercase letters and digits, in words separated by hyphens")
    for field in ("package_name", "tool_class"):
        value = answers[field]
        if not value.isidentifier() or keyword.iskeyword(value):
            found.append(f"{field} {value!r} is not a Python identifier")
    if answers["package_name"] != answers["package_name"].lower():
        found.append(f"package_name {answers['package_name']!r}: use lowercase")
    if not TOOL_NAME.match(answers["tool_name"]):
        found.append(
            f"tool_name {answers['tool_name']!r}: use a letter, then at most 47 letters, digits and underscores"
        )
    if not answers["cache_ttl"].isdigit():
        found.append(f"cache_ttl {answers['cache_ttl']!r} is not a whole number of seconds")
    if not answers["timeout"].isdigit() or not 1 <= int(answers["timeout"]) <= 300:
        found.append(f"timeout {answers['timeout']!r} is not a whole number of seconds from 1 to 300")
    if not EMAIL.match(answers["author_email"]):
        found.append(f"author_email {answers['author_email']!r} is not an email address")
    if not PUBLISHER.match(answers["publisher_id"]):
        found.append(f"publisher_id {answers['publisher_id']!r}: use lowercase letters, digits and hyphens")
    if not answers["extension_name"].strip():
        found.append("extension_name is empty")
    for field in ("extension_name", "description", "author_name"):
        # they are written into pyproject.toml's strings and into docstrings.
        if any(character in answers[field] for character in '"\\\n'):
            found.append(f"{field} may not contain double quotes, backslashes or line breaks")
    return found


def main() -> int:
    """
    Check the answers, and print each problem on standard error.

    :returns: The exit status: 1 if an answer is refused, which stops generation, otherwise 0.
    """
    found = problems(ANSWERS)
    for problem in found:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

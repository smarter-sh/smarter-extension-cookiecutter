"""
Finish the generated project.

Keep only the starter's files and the chosen license, link .claude/skills to skills/, and print
the next steps.

Cookiecutter renders this file with the answers, then runs it in the generated project's root.
"""

import os
import shutil
from pathlib import Path

STARTER = "{{ cookiecutter.starter }}"
"""The chosen starter: ``web-api`` or ``pure-function``."""
LICENSE = "{{ cookiecutter.license }}"
"""The chosen license, the name of its file in ``_licenses/``, without ``.txt``."""
PACKAGE = "{{ cookiecutter.package_name }}"
"""The extension's Python package."""
REPOSITORY = "{{ cookiecutter.repository_name }}"
"""The generated repository's directory name."""

WEB_API_ONLY = [Path(PACKAGE) / "models.py", Path(PACKAGE) / "services.py", Path("tests") / "test_services.py"]
"""Files that only the web-api starter has."""


def main() -> None:
    """
    Finish the generated project, in the current directory, and print the next steps.

    Removes the web-api starter's files unless it was chosen, moves the chosen license to
    ``LICENSE`` and removes the others, and links ``.claude/skills`` to ``skills/``, or copies it
    where symlinks aren't allowed.
    """
    root = Path.cwd()
    if STARTER != "web-api":
        for path in WEB_API_ONLY:
            (root / path).unlink(missing_ok=True)

    licenses = root / "_licenses"
    (licenses / f"{LICENSE}.txt").replace(root / "LICENSE")
    shutil.rmtree(licenses)

    # Claude Code reads skills from .claude/skills. A symlink keeps one copy, in skills/, where
    # other agents find them too. Cookiecutter doesn't copy symlinks reliably on every platform.
    link = root / ".claude" / "skills"
    link.parent.mkdir(exist_ok=True)
    if not link.exists() and not link.is_symlink():  # e.g. generated again, with --overwrite-if-exists
        try:
            os.symlink("../skills", link, target_is_directory=True)
        except OSError:
            # Windows without symlink rights: a copy works, but must be refreshed when skills/ changes.
            shutil.copytree(root / "skills", link)

    print(f"""
Created {REPOSITORY}.

Next steps:
  cd {REPOSITORY}
  git init -b main && git add . && git commit -m "feat: initial commit"
  make init      # a Python virtual environment, and the pre-commit hooks
  make test      # the tests, in a running Smarter development container (smarter-app)

Then replace the starter tool with yours: see README.md, and CLAUDE.md if you use a coding agent.
""")


if __name__ == "__main__":
    main()

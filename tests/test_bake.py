"""
Test the template: generate ("bake") extensions with different answers, and check what comes out.

They need only cookiecutter (requirements/local.txt). Running a generated extension's own tests needs
Smarter: the Test workflow does that, and so does ``make test-generated``.
"""

import ast
import tempfile
import tomllib
import unittest
from pathlib import Path

from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

TEMPLATE = Path(__file__).resolve().parent.parent
"""The template repository's root, which holds ``cookiecutter.json``."""
TEMPLATE_PROJECT = TEMPLATE / "{{cookiecutter.repository_name}}"
"""The template of the generated repository, before rendering."""
UNRENDERED = ("{{ cookiecutter", "{{cookiecutter", "{%")
"""Jinja markers that must not survive rendering."""
SHARED = [
    "release.config.js",
    "package.json",
    ".github/workflows/release.yml",
    ".github/workflows/test.yml",
    "scripts/package.py",
    "scripts/set_version.py",
    "scripts/run-tests.sh",
]
"""Files copied unchanged into every extension, and kept identical in the official extensions."""


def bake(output: Path, **answers: str) -> Path:
    """
    Generate an extension from the template without prompting, and return its directory.

    Answers that aren't given take their defaults from ``cookiecutter.json``. The pre- and
    post-generation hooks run, as they do for an author.

    :param output: The directory to generate the extension in.
    :param answers: Answers to the template's questions, by question name, e.g.
        ``starter="pure-function"``.
    :returns: The generated repository's directory, inside ``output``.
    :raises FailedHookException: when the pre-generation hook refuses an answer.
    """
    return Path(cookiecutter(str(TEMPLATE), no_input=True, output_dir=str(output), extra_context=answers))


def docstring_problems(root: Path) -> list[str]:
    """
    Find the Python code under a directory that doesn't meet Smarter's docstring standard.

    The standard is Smarter's (its ``smarter-docstrings`` skill), which Sphinx renders: every module,
    class and function has a docstring, whose first line is a one-line summary ending with a period,
    and a function's docstring has the fields :func:`missing_fields` requires. The template is the
    example that authors copy, so it must meet the standard it asks of them.

    :param root: The directory to check, recursively.
    :returns: One description per problem, naming the file, the line and the object. Empty when the
        code meets the standard.
    :raises SyntaxError: when a Python file under ``root`` doesn't parse.
    """
    found = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        where = path.relative_to(root)
        if not ast.get_docstring(tree):
            found.append(f"{where}: the module has no docstring")
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            name = f"{where}:{node.lineno} {node.name}"
            docstring = ast.get_docstring(node)
            if not docstring:
                found.append(f"{name} has no docstring")
                continue
            if not docstring.splitlines()[0].endswith("."):
                found.append(f"{name}: the summary isn't one line ending with a period")
            if not isinstance(node, ast.ClassDef):
                found += [f"{name} has no {field}" for field in missing_fields(node, docstring)]
    return found


def missing_fields(function: ast.FunctionDef | ast.AsyncFunctionDef, docstring: str) -> list[str]:
    """
    Find the reStructuredText fields that a function's docstring lacks.

    The fields required are a ``:param <name>:`` for each argument except ``self`` and ``cls``, and a
    ``:returns:`` unless the function returns None. A function without a return annotation is taken
    to return None, as test methods do.

    :param function: The function's syntax tree.
    :param docstring: The function's docstring.
    :returns: Each missing field, e.g. ``:param query:``. Empty when none is missing.
    """
    arguments = function.args.posonlyargs + function.args.args + function.args.kwonlyargs
    arguments += [a for a in (function.args.vararg, function.args.kwarg) if a]
    missing = [
        f":param {a.arg}:" for a in arguments if a.arg not in ("self", "cls") and f":param {a.arg}:" not in docstring
    ]
    returns = function.returns
    returns_none = returns is None or (isinstance(returns, ast.Constant) and returns.value is None)
    if not returns_none and ":returns:" not in docstring:
        missing.append(":returns:")
    return missing


class TestDefaults(unittest.TestCase):
    """
    Test an extension generated with the default answers.

    The defaults choose the web-api starter and the AGPL-3.0 license. They are what CI and
    ``cookiecutter --no-input`` generate, so they must always produce a working extension.
    """

    @classmethod
    def setUpClass(cls):
        """
        Generate one extension, with the default answers, for every test in the class.

        Generating once keeps the tests fast; no test changes the generated files.

        Sets ``cls.tmp``, the temporary directory, and ``cls.project``, the generated repository.

        :raises FailedHookException: when the hooks refuse the default answers.
        """
        cls.tmp = tempfile.TemporaryDirectory()
        cls.project = bake(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        """
        Remove the generated extension and its temporary directory.

        :returns: None.
        """
        cls.tmp.cleanup()

    def test_names(self):
        """
        Test that the default answers reach ``pyproject.toml``.

        The names are derived from ``extension_name``: the slug, the package, the repository and the
        tool's class. The web-api starter adds its two settings and its ``requests`` dependency.

        :raises AssertionError: when a name, the version, the timeout, the settings or the
            dependencies differ from what the defaults should produce.
        """
        self.assertEqual(self.project.name, "smarter-extension-my-extension")
        pyproject = tomllib.loads((self.project / "pyproject.toml").read_text())
        self.assertEqual(pyproject["project"]["name"], "smarter-extension-my-extension")
        self.assertEqual(pyproject["project"]["version"], "0.0.0")
        smarter = pyproject["tool"]["smarter"]
        self.assertEqual(smarter["slug"], "my-extension")
        self.assertEqual(smarter["package"], "my_extension")
        self.assertEqual(smarter["display-name"], "My Extension")
        self.assertEqual(smarter["tools"], ["my_extension.tools:MyExtension"])
        self.assertEqual(smarter["timeout"], 30)
        self.assertEqual([s["name"] for s in smarter["settings"]], ["api_key", "api_url"])
        self.assertEqual(pyproject["project"]["dependencies"], ["requests>=2.31"])

    def test_web_api_files(self):
        """
        Test that the web-api starter keeps its own files.

        The post-generation hook removes these files for the other starters, so this checks that it
        leaves them alone when web-api is chosen.

        :raises AssertionError: when ``models.py``, ``services.py`` or ``tests/test_services.py`` is
            missing.
        """
        for name in ("my_extension/models.py", "my_extension/services.py", "tests/test_services.py"):
            self.assertTrue((self.project / name).is_file(), name)

    def test_python_parses(self):
        """
        Test that every generated Python file is valid Python once rendered.

        Jinja blocks in Python files can leave broken indentation or syntax behind, which the
        generated extension's own tests would only show in a Smarter container.

        :raises SyntaxError: when a generated Python file doesn't parse.
        """
        for path in self.project.rglob("*.py"):
            ast.parse(path.read_text(), filename=str(path))

    def test_nothing_unrendered(self):
        """
        Test that no Jinja tag is left in a generated file.

        A leftover tag means a file was copied without rendering when it should have been, or a tag
        was mistyped. The skills are skipped: they name the template's own directory on purpose.

        :raises AssertionError: when a generated file, outside ``skills/``, holds a Jinja marker.
        """
        for path in self.project.rglob("*"):
            if path.is_file() and "skills" not in path.parts:
                text = path.read_text(errors="ignore")
                for marker in UNRENDERED:
                    self.assertNotIn(marker, text, f"{path.relative_to(self.project)} has {marker}")

    def test_docstrings(self):
        """
        Test that the generated web-api extension meets Smarter's docstring standard.

        Authors copy the starter's style, so every module, class and function in it is documented as
        :func:`docstring_problems` requires, including the release scripts shared with the official
        extensions.

        :raises AssertionError: when a generated Python file falls short of the standard.
        """
        self.assertEqual(docstring_problems(self.project), [])

    def test_github_expressions_kept(self):
        """
        Test that GitHub's own expressions survive in the workflows.

        ``${{ ... }}`` is Jinja syntax too. The workflows are in ``_copy_without_render``, so
        Cookiecutter copies them as they are instead of rendering, or failing on, the expressions.

        :raises AssertionError: when the test workflow lost its ``CODECOV_TOKEN`` expression.
        """
        self.assertIn("${{ secrets.CODECOV_TOKEN }}", (self.project / ".github/workflows/test.yml").read_text())

    def test_shared_files_unchanged(self):
        """
        Test that generation copies the files shared with the official extensions byte for byte.

        These files are kept identical in smarter-extension-weather, -calculator and
        -date-calculator, so generation must not change them. ``run-tests.sh`` must stay executable,
        or the Makefile and CI can't run it.

        :raises AssertionError: when a shared file differs from the template's copy, or
            ``run-tests.sh`` isn't executable.
        """
        for name in SHARED:
            self.assertEqual((self.project / name).read_bytes(), (TEMPLATE_PROJECT / name).read_bytes(), name)
        self.assertTrue((self.project / "scripts/run-tests.sh").stat().st_mode & 0o111, "run-tests.sh is executable")

    def test_license(self):
        """
        Test that the default license is the AGPL, and that the other licenses are removed.

        The post-generation hook moves the chosen license from ``_licenses/`` to ``LICENSE``, then
        removes ``_licenses/``.

        :raises AssertionError: when ``LICENSE`` isn't the AGPL, or ``_licenses/`` remains.
        """
        self.assertIn("GNU AFFERO GENERAL PUBLIC LICENSE", (self.project / "LICENSE").read_text())
        self.assertFalse((self.project / "_licenses").exists())

    def test_agent_files(self):
        """
        Test the generated instructions for AI coding agents.

        Claude Code reads skills from ``.claude/skills``, which the post-generation hook links to
        ``skills/``, so that other agents share the one copy. CLAUDE.md is rendered with the
        extension's slug, and names the commit co-author.

        :raises AssertionError: when the link is missing or points elsewhere, a skill isn't reachable
            through it, or CLAUDE.md lacks the co-author or the slug.
        """
        link = self.project / ".claude" / "skills"
        self.assertTrue(link.is_symlink())
        self.assertEqual(str(link.readlink()), "../skills")
        self.assertTrue((link / "smarter-extension-development" / "SKILL.md").is_file())
        claude = (self.project / "CLAUDE.md").read_text()
        self.assertIn("Co-authored-by: Claude <noreply@anthropic.com>", claude)
        self.assertIn("`my-extension`", claude)

    def test_uncached_by_default(self):
        """
        Test that the tool's results aren't cached unless the author asks for it.

        Caching is only safe for a tool that changes nothing and answers the same whoever asks, which
        the template can't know, so ``cache_ttl`` defaults to 0.

        :raises AssertionError: when the generated tool has a ``cache_ttl`` other than 0.
        """
        self.assertIn("cache_ttl = 0\n", (self.project / "my_extension/tools.py").read_text())


class TestPureFunction(unittest.TestCase):
    """
    Test an extension generated with the pure-function starter, and other answers that change file contents.

    The answers differ from every default that changes a file: the name, the starter, the license,
    the cache time, the timeout and the author.
    """

    @classmethod
    def setUpClass(cls):
        """
        Generate one pure-function extension, with an MIT license and a cache, for every test in the class.

        Sets ``cls.tmp``, the temporary directory, and ``cls.project``, the generated repository.

        :raises FailedHookException: when the hooks refuse the answers.
        """
        cls.tmp = tempfile.TemporaryDirectory()
        cls.project = bake(
            Path(cls.tmp.name),
            extension_name="Date Calculator",
            starter="pure-function",
            license="MIT",
            cache_ttl="3600",
            timeout="5",
            author_name="Ada Lovelace",
        )

    @classmethod
    def tearDownClass(cls):
        """
        Remove the generated extension and its temporary directory.

        :returns: None.
        """
        cls.tmp.cleanup()

    def test_names(self):
        """
        Test that the names and the timeout follow the answers, and that a pure function has no settings.

        :raises AssertionError: when the slug, the tool's path or the timeout differ from the answers,
            or ``[tool.smarter]`` declares settings.
        """
        smarter = tomllib.loads((self.project / "pyproject.toml").read_text())["tool"]["smarter"]
        self.assertEqual(smarter["slug"], "date-calculator")
        self.assertEqual(smarter["tools"], ["date_calculator.tools:DateCalculator"])
        self.assertEqual(smarter["timeout"], 5)
        self.assertNotIn("settings", smarter)

    def test_no_web_api_files(self):
        """
        Test that the post-generation hook removes the web-api starter's files and its dependency.

        A pure function calls no API, so it has no models, services, service tests or ``requests``.

        :raises AssertionError: when a web-api file remains, or the extension has dependencies.
        """
        for name in ("date_calculator/models.py", "date_calculator/services.py", "tests/test_services.py"):
            self.assertFalse((self.project / name).exists(), name)
        pyproject = tomllib.loads((self.project / "pyproject.toml").read_text())
        self.assertEqual(pyproject["project"]["dependencies"], [])

    def test_cache_ttl(self):
        """
        Test that a cached tool states its cache time, and documents why caching is safe.

        :raises AssertionError: when the tool's ``cache_ttl`` isn't the answer, or its docstring
            doesn't explain that the answer is the same whoever asks.
        """
        tools = (self.project / "date_calculator/tools.py").read_text()
        self.assertIn("cache_ttl = 3600\n", tools)
        self.assertIn("whoever asks", tools)

    def test_mit_license(self):
        """
        Test that the MIT license is chosen, and names the author.

        :raises AssertionError: when ``LICENSE`` isn't the MIT license, or lacks the author's name.
        """
        text = (self.project / "LICENSE").read_text()
        self.assertTrue(text.startswith("MIT License"))
        self.assertIn("Ada Lovelace", text)

    def test_docstrings(self):
        """
        Test that the generated pure-function extension meets Smarter's docstring standard.

        :raises AssertionError: when a generated Python file falls short of the standard.
        """
        self.assertEqual(docstring_problems(self.project), [])

    def test_docs_heading(self):
        """
        Test that the package docstring's title underline is as long as the title.

        Smarter shows the package docstring to administrators as reStructuredText, where an underline
        shorter than its title is an error. The template renders the underline to the title's length.

        :raises AssertionError: when the title or its underline is wrong.
        """
        lines = (self.project / "date_calculator/__init__.py").read_text().splitlines()
        self.assertEqual(lines[1:3], ["Date Calculator", "==============="])


class TestAnswersChecked(unittest.TestCase):
    """
    Test that the pre-generation hook refuses answers that would make an extension Smarter refuses.

    The hook copies Smarter's rules, so that an author learns of a bad answer before generating, not
    when Smarter refuses to load the extension.
    """

    def assertRefused(self, **answers):
        """
        Assert that the pre-generation hook refuses the answers, and that nothing is generated.

        :param answers: Answers to the template's questions, by question name; the others take their
            defaults.
        :raises AssertionError: when generation succeeds, or leaves files behind.
        """
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FailedHookException):
                bake(Path(tmp), **answers)
            self.assertEqual(list(Path(tmp).iterdir()), [], "nothing is generated")

    def test_bad_slug(self):
        """
        Test that a slug Smarter refuses is refused.

        A slug is lowercase words separated by hyphens, at most 32 characters.

        :raises AssertionError: when a slug with spaces and capitals, or one of 33 characters, is
            accepted.
        """
        self.assertRefused(extension_slug="Not A Slug")
        self.assertRefused(extension_slug="a" * 33)

    def test_bad_tool_name(self):
        """
        Test that a tool name that doesn't start with a letter is refused.

        :raises AssertionError: when the tool name ``1tool`` is accepted.
        """
        self.assertRefused(tool_name="1tool")

    def test_bad_numbers(self):
        """
        Test that a cache time that isn't a number, and a timeout over 300 seconds, are refused.

        :raises AssertionError: when either answer is accepted.
        """
        self.assertRefused(cache_ttl="an hour")
        self.assertRefused(timeout="301")

    def test_quotes(self):
        """
        Test that double quotes in a free-text answer are refused.

        The free-text answers are written into ``pyproject.toml``'s strings and into docstrings, which
        a double quote would end early.

        :raises AssertionError: when a description with double quotes is accepted.
        """
        self.assertRefused(description='Says "hello"')

    def test_keyword_package(self):
        """
        Test that a package name that is a Python keyword is refused, as it can't be imported.

        :raises AssertionError: when the package name ``class`` is accepted.
        """
        self.assertRefused(package_name="class")


class TestTemplateDocstrings(unittest.TestCase):
    """Test that the template's own Python code meets the docstring standard it asks of authors."""

    def test_docstrings(self):
        """
        Test that the template's tests meet Smarter's docstring standard.

        The hooks aren't checked here: they are Jinja templates, not Python, until Cookiecutter
        renders them.

        :raises AssertionError: when a test module falls short of the standard.
        """
        self.assertEqual(docstring_problems(TEMPLATE / "tests"), [])


if __name__ == "__main__":
    unittest.main()

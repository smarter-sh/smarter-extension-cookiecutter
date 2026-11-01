"""Tests of the {{ cookiecutter.tool_name }} tool{% if cookiecutter.starter == "web-api" %}, with its service mocked{% endif %}."""

import unittest
{%- if cookiecutter.starter == "web-api" %}
from unittest.mock import patch

from pydantic import SecretStr
{%- endif %}
from smarter.apps.llmtool.extension.testing import call_tool{% if cookiecutter.starter == "web-api" %}, tool_context{% endif %}
{% if cookiecutter.starter == "web-api" %}
from {{ cookiecutter.package_name }}.services import ServiceError
from {{ cookiecutter.package_name }}.tools import {{ cookiecutter.tool_class }}

API_URL = "https://api.example.com/v1/search"
"""The ``api_url`` setting the tests call the tool with."""
CONTEXT = tool_context("{{ cookiecutter.extension_slug }}", api_key=SecretStr("test-key"), api_url=API_URL)
"""A call's context, with test settings in place of an administrator's."""


class Test{{ cookiecutter.tool_class }}(unittest.TestCase):
    """
    Test the {{ cookiecutter.tool_name }} tool, as the platform calls it.

    ``search()`` is mocked: the tests never call the third-party API.
    """

    def test_definition(self):
        """
        Test that the platform will load the tool, and offers the LLM the right arguments.

        :raises AssertionError: when Smarter's checks find a problem with the tool, or ``query`` isn't
            its only required argument.
        """
        self.assertEqual({{ cookiecutter.tool_class }}.problems(), [])
        self.assertEqual({{ cookiecutter.tool_class }}.parameters()["required"], ["query"])

    def test_cache_ttl(self):
        """
        Test that the tool caches its results for as long as the author chose.

        :raises AssertionError: when ``cache_ttl`` differs from the template's answer.
        """
        self.assertEqual({{ cookiecutter.tool_class }}.cache_ttl, {{ cookiecutter.cache_ttl }})

    def test_search(self):
        """
        Test that the tool searches with the query and its settings, and returns the results with the query.

        :raises AssertionError: when ``search()`` is called with other arguments, or the result differs.
        """
        with patch("{{ cookiecutter.package_name }}.tools.search", return_value=[{"title": "A"}]) as search:
            result = call_tool({{ cookiecutter.tool_class }}, {"query": "eclipses"}, CONTEXT)
        search.assert_called_once_with("eclipses", API_URL, "test-key")
        self.assertEqual(result, {"query": "eclipses", "results": [{"title": "A"}]})

    def test_service_unavailable(self):
        """
        Test that a service failure reaches the LLM as an error it can explain.

        The tool turns a ``ServiceError`` into an ``ExtensionToolError``, which the platform returns to
        the LLM as ``{"error": ...}`` instead of failing the request.

        :raises AssertionError: when the result isn't the expected error.
        """
        with patch("{{ cookiecutter.package_name }}.tools.search", side_effect=ServiceError("timed out")):
            result = call_tool({{ cookiecutter.tool_class }}, {"query": "eclipses"}, CONTEXT)
        self.assertEqual(result, {"error": "The service is unavailable: timed out"})

    def test_invalid_arguments(self):
        """
        Test that a missing or empty query is refused before the service is called.

        :raises AssertionError: when either call returns something other than an invalid arguments
            error.
        """
        self.assertIn("Invalid arguments", call_tool({{ cookiecutter.tool_class }}, {})["error"])
        self.assertIn("Invalid arguments", call_tool({{ cookiecutter.tool_class }}, {"query": ""})["error"])
{%- else %}
from {{ cookiecutter.package_name }}.tools import MAX_CHARACTERS, {{ cookiecutter.tool_class }}


class Test{{ cookiecutter.tool_class }}(unittest.TestCase):
    """Test the {{ cookiecutter.tool_name }} tool, as the platform calls it."""

    def test_definition(self):
        """
        Test that the platform will load the tool, and offers the LLM the right arguments.

        :raises AssertionError: when Smarter's checks find a problem with the tool, or ``text`` isn't
            its only required argument.
        """
        self.assertEqual({{ cookiecutter.tool_class }}.problems(), [])
        self.assertEqual({{ cookiecutter.tool_class }}.parameters()["required"], ["text"])

    def test_cache_ttl(self):
        """
        Test that the tool caches its results for as long as the author chose.

        :raises AssertionError: when ``cache_ttl`` differs from the template's answer.
        """
        self.assertEqual({{ cookiecutter.tool_class }}.cache_ttl, {{ cookiecutter.cache_ttl }})

    def test_counts(self):
        """
        Test that the tool counts the words, characters and lines of the text.

        :raises AssertionError: when a count is wrong.
        """
        result = call_tool({{ cookiecutter.tool_class }}, {"text": "one two\nthree"})
        self.assertEqual(result, {"words": 3, "characters": 13, "lines": 2})

    def test_empty_text(self):
        """
        Test that an empty text has no words, characters or lines.

        :raises AssertionError: when a count isn't 0.
        """
        self.assertEqual(call_tool({{ cookiecutter.tool_class }}, {"text": ""}), {"words": 0, "characters": 0, "lines": 0})

    def test_too_long(self):
        """
        Test that a text over ``MAX_CHARACTERS`` is refused with an error the LLM can explain.

        The limit keeps one call from holding a platform worker for long.

        :raises AssertionError: when the result isn't the expected error.
        """
        result = call_tool({{ cookiecutter.tool_class }}, {"text": "a" * (MAX_CHARACTERS + 1)})
        self.assertEqual(result, {"error": f"The text is too long: at most {MAX_CHARACTERS} characters."})

    def test_invalid_arguments(self):
        """
        Test that a call without a text is refused.

        :raises AssertionError: when the call returns something other than an invalid arguments error.
        """
        self.assertIn("Invalid arguments", call_tool({{ cookiecutter.tool_class }}, {})["error"])
{%- endif %}

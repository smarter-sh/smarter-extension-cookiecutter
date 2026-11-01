"""The {{ cookiecutter.extension_name }} extension's tools."""
{% if cookiecutter.starter == "web-api" %}
from pydantic import JsonValue
from smarter.apps.llmtool.extension import ExtensionContext, ExtensionToolError, SmarterExtensionTool

from .models import {{ cookiecutter.tool_class }}Arguments, {{ cookiecutter.tool_class }}Result
from .services import ServiceError, search


# The class docstring is the tool's description for the LLM, which decides from it when to call the
# tool. Keep it to what the tool does, for the LLM, not for developers.
class {{ cookiecutter.tool_class }}(SmarterExtensionTool):
    """{{ cookiecutter.description }}"""

    name = "{{ cookiecutter.tool_name }}"
    """The tool's name, which the LLM sees as ``ext_{{ cookiecutter.extension_slug | replace('-', '_') }}_{{ cookiecutter.tool_name }}``."""
    arguments_model = {{ cookiecutter.tool_class }}Arguments
    """The arguments the LLM must give, which Smarter validates and offers to the LLM as a JSON schema."""
    cache_ttl = {{ cookiecutter.cache_ttl }}
    {%- if cookiecutter.cache_ttl | int > 0 %}
    """A search changes nothing, and its result depends only on the query and the settings, not on who asks."""
    {%- else %}
    """Results aren't cached: cache them only if the tool changes nothing and answers the same whoever asks."""
    {%- endif %}

    def call(self, arguments: {{ cookiecutter.tool_class }}Arguments, context: ExtensionContext) -> JsonValue:
        """
        Search the third-party API for the query, with the extension's settings.

        :param arguments: The LLM's arguments, validated.
        :param context: The call's context: the extension's settings and a logger.
        :returns: The query and its results, as JSON.
        :raises ExtensionToolError: when the service fails, so that the LLM is told why.
        """
        settings = context.settings
        try:
            results = search(arguments.query, settings.api_url, settings.api_key.get_secret_value())
        except ServiceError as e:
            raise ExtensionToolError(f"The service is unavailable: {e}") from e
        context.logger.info("%s found %d results", self.name, len(results))
        return {{ cookiecutter.tool_class }}Result(query=arguments.query, results=results).model_dump(mode="json")
{%- else %}
from pydantic import BaseModel, Field, JsonValue
from smarter.apps.llmtool.extension import ExtensionContext, ExtensionToolError, SmarterExtensionTool

MAX_CHARACTERS = 100_000
"""The longest text accepted, so that one call can't hold a platform worker for long."""


class {{ cookiecutter.tool_class }}Arguments(BaseModel):
    """The arguments of the {{ cookiecutter.tool_name }} tool."""

    text: str = Field(..., description="The text to count the words, characters and lines of.")


# The class docstring is the tool's description for the LLM, which decides from it when to call the
# tool. Keep it to what the tool does, for the LLM, not for developers.
class {{ cookiecutter.tool_class }}(SmarterExtensionTool):
    """{{ cookiecutter.description }}"""

    name = "{{ cookiecutter.tool_name }}"
    """The tool's name, which the LLM sees as ``ext_{{ cookiecutter.extension_slug | replace('-', '_') }}_{{ cookiecutter.tool_name }}``."""
    arguments_model = {{ cookiecutter.tool_class }}Arguments
    """The arguments the LLM must give, which Smarter validates and offers to the LLM as a JSON schema."""
    cache_ttl = {{ cookiecutter.cache_ttl }}
    {%- if cookiecutter.cache_ttl | int > 0 %}
    """The same text always has the same counts, whoever asks."""
    {%- else %}
    """Results aren't cached: cache them only if the tool changes nothing and answers the same whoever asks."""
    {%- endif %}

    def call(self, arguments: {{ cookiecutter.tool_class }}Arguments, context: ExtensionContext) -> JsonValue:
        """
        Count the words, characters and lines of the text.

        :param arguments: The LLM's arguments, validated.
        :param context: The call's context. This tool doesn't use it.
        :returns: The counts, as JSON.
        :raises ExtensionToolError: when the text is longer than ``MAX_CHARACTERS``.
        """
        text = arguments.text
        if len(text) > MAX_CHARACTERS:
            raise ExtensionToolError(f"The text is too long: at most {MAX_CHARACTERS} characters.")
        return {"words": len(text.split()), "characters": len(text), "lines": len(text.splitlines())}
{%- endif %}

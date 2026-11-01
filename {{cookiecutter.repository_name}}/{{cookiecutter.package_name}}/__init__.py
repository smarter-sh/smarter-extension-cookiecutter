"""
{{ cookiecutter.extension_name }}
{{ "=" * cookiecutter.extension_name | length }}

{{ cookiecutter.description }}
{%- if cookiecutter.starter == "web-api" %}

Settings
--------

``api_key``
    Required. The API key of the service that ``{{ cookiecutter.tool_name }}`` calls.

``api_url``
    The service's search api. Change it only to use another deployment of the same api.
{%- endif %}

Tools
-----
{% if cookiecutter.starter == "web-api" %}
``{{ cookiecutter.tool_name }}(query)``
    Searches the service for ``query``, and returns its results.
{%- else %}
``{{ cookiecutter.tool_name }}(text)``
    Counts the words, characters and lines of ``text``.
{%- endif %}
"""

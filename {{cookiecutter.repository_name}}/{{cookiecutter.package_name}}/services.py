"""Calls to the third-party service that {{ cookiecutter.tool_name }} uses, kept out of the tool so each can be tested alone."""

import requests
from pydantic import JsonValue

TIMEOUT = 10
"""Seconds to wait for the service: less than the extension's timeout, so that the tool can explain a slow service."""


class ServiceError(Exception):
    """The service failed, or its response is not as expected."""


def search(query: str, api_url: str, api_key: str) -> list[JsonValue]:
    """
    Search the service.

    :param query: What to search for.
    :param api_url: The service's search api.
    :param api_key: The service's API key.
    :returns: The service's results.
    :raises ServiceError: If the request fails, or the response has no list of results.
    """
    try:
        response = requests.get(
            api_url, params={"q": query}, headers={"Authorization": f"Bearer {api_key}"}, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise ServiceError(str(e)) from e
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        raise ServiceError("the response has no list of results")
    return results


__all__ = ["ServiceError", "search"]

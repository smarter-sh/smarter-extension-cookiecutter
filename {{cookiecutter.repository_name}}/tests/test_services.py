"""Tests of the calls to the third-party service, with requests mocked."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from {{ cookiecutter.package_name }}.services import TIMEOUT, ServiceError, search

API_URL = "https://api.example.com/v1/search"
"""The ``api_url`` the tests search."""


def response(data=None, error: Exception | None = None) -> MagicMock:
    """
    Return a mocked ``requests`` response.

    :param data: What the response's ``json()`` returns.
    :param error: An exception for the response's ``raise_for_status()`` to raise, or None for a
        successful response.
    :returns: The mocked response, for ``requests.get`` to return.
    """
    mocked = MagicMock()
    mocked.json.return_value = data
    if error:
        mocked.raise_for_status.side_effect = error
    return mocked


class TestSearch(unittest.TestCase):
    """
    Test ``search()``, the call to the third-party API.

    ``requests.get`` is mocked: the tests never call the API.
    """

    def test_results(self):
        """
        Test that the API is called with the query and the API key, and that its list of results is returned.

        :raises AssertionError: when the request or the returned results differ from what's expected.
        """
        with patch("{{ cookiecutter.package_name }}.services.requests.get", return_value=response({"results": [1, 2]})) as get:
            self.assertEqual(search("eclipses", API_URL, "test-key"), [1, 2])
        get.assert_called_once_with(
            API_URL, params={"q": "eclipses"}, headers={"Authorization": "Bearer test-key"}, timeout=TIMEOUT
        )

    def test_http_error(self):
        """
        Test that an HTTP error status, e.g. a refused API key, becomes a ``ServiceError``.

        :raises AssertionError: when no ``ServiceError`` naming the status is raised.
        """
        error = requests.HTTPError("401 Client Error: Unauthorized")
        with patch("{{ cookiecutter.package_name }}.services.requests.get", return_value=response(error=error)):
            with self.assertRaisesRegex(ServiceError, "401"):
                search("eclipses", API_URL, "test-key")

    def test_unreachable(self):
        """
        Test that a connection failure becomes a ``ServiceError``.

        :raises AssertionError: when no ``ServiceError`` naming the failure is raised.
        """
        with patch("{{ cookiecutter.package_name }}.services.requests.get", side_effect=requests.ConnectionError("refused")):
            with self.assertRaisesRegex(ServiceError, "refused"):
                search("eclipses", API_URL, "test-key")

    def test_no_results(self):
        """
        Test that a response without a list of results becomes a ``ServiceError``.

        Checking the response's shape here means the tool fails with a clear message, rather than
        crashing later on.

        :raises AssertionError: when any of the malformed responses doesn't raise a ``ServiceError``.
        """
        for data in ({"items": []}, ["not", "a", "dict"], {"results": "not a list"}):
            with self.subTest(data=data):
                with patch("{{ cookiecutter.package_name }}.services.requests.get", return_value=response(data)):
                    with self.assertRaisesRegex(ServiceError, "no list of results"):
                        search("eclipses", API_URL, "test-key")

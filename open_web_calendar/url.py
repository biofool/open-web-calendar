# SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>
#
# SPDX-License-Identifier: GPL-2.0-only

"""This contains URL specific customizations and parameters."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import parse_qs, urlencode, urlparse


def assert_public_http_url(url: str) -> None:
    """Raise ValueError unless ``url`` is a public http(s) URL (SSRF guard).

    Every user-supplied fetch target (``url=``, ``specification_url``,
    CalDAV endpoints, redirect hops) must pass through here — otherwise a
    URL pointing at the cloud metadata endpoint or an internal host turns
    the service into an internal request proxy.
    """
    try:
        parts = urlparse(url)
    except ValueError as exc:
        raise ValueError("malformed URL") from exc
    if parts.scheme not in ("http", "https"):
        raise ValueError(f"refused non-http(s) URL scheme: {parts.scheme or '?'}")
    host = parts.hostname
    if not host:
        raise ValueError("URL has no host")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"host does not resolve: {host}") from exc
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError as exc:
            raise ValueError(f"host resolved to an unparseable address: {host}") from exc
        if (
            ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified
        ):
            raise ValueError(f"host {host} resolves to a non-public address")


class URLCapability:
    """The capabilities of a URL.

    This is saved in the hash behind the URL.
    This hash is discarded for all requests to servers.
    As such, we can safe configuration data in it.
    """

    @classmethod
    def from_url(cls, url: str):
        """Get the capabilities from a URL."""
        parsed = urlparse(url)
        return cls.from_string(parsed.fragment)

    @classmethod
    def from_string(cls, parameters: str):
        """Get the capabilities from a URL."""
        return cls({k: v[0] for k, v in parse_qs(parameters).items()})

    def __init__(self, values: dict[str, str] | None = None):
        """Create a capability based on a hash."""
        self._values = {} if values is None else values.copy()

    def to_string(self) -> str:
        """As a string."""
        return urlencode(self._values)

    def get(self, name: str, default: str = "") -> str:
        """Get a value."""
        return self._values.get(name, default)

    def get_false(self, name: str) -> bool:
        """Return if this is true or false, default false."""
        return self.get(name).lower() == "true"

    def can_add_email_attendee(self) -> bool:
        return self.get_false("can_add_email_attendee")

    def __repr__(self):
        """repr(self)"""
        return f"{self.__class__.__name__}({self._values!r})"

    def restrict(self, url: str) -> str:
        """Return the URL with the restictions set by me."""
        plain_url = url.split("#", 1)[0]
        return plain_url + "#" + self.to_string()


__all__ = ["URLCapability", "assert_public_http_url"]

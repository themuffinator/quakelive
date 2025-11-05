#!/usr/bin/env python3
"""Simulate the client-side auth flow to document request lifecycle logging."""

from __future__ import annotations

import itertools
import textwrap


def token_preview(token: str) -> str:
    if not token:
        return "<empty>"

    if len(token) <= 12:
        return token

    return f"{token[:7]}…{token[-4:]}"


class Sample:
    def __init__(self, provider: str, token: str) -> None:
        self.provider = provider
        self.token = token

    @property
    def endpoint(self) -> str:
        return {
            "steam": "/steam/session/validate",
            "standalone": "/launcher/auth/verify",
        }.get(self.provider, "<none>")

    def dispatch_logs(self) -> list[str]:
        preview = token_preview(self.token)
        payload_template = {
            "steam": "steam payload summary: ticket=%s (len=%d)",
            "standalone": "standalone payload summary: token=%s (len=%d)",
        }.get(self.provider, "%s payload summary: token=%s (len=%d)")

        return [
            f"[auth] {self.provider} dispatch ({self.endpoint}): submitting credential",
            f"[auth] {payload_template % (preview, len(self.token))}",
        ]

    def classify(self) -> tuple[str, str]:
        """Return (outcome, message) mirroring ql_auth.c heuristics."""
        value = self.token

        if self.provider == "steam":
            if len(value) < 16:
                return "failure", "Steam ticket rejected: payload too short"
            if "retry" in value:
                return "retry", "Steam service busy, retry with refreshed ticket"
            if any(marker in value for marker in ("denied", "invalid")):
                return "failure", "Steam backend denied the ticket"
            return "success", f"Steam session established (ticket={token_preview(value)})"

        if self.provider == "standalone":
            if len(value) < 12:
                return "failure", "Standalone token rejected: payload too short"
            if "refresh" in value:
                return "retry", "Launcher token expired, request a refresh"
            if any(marker in value for marker in ("revoke", "denied")):
                return "failure", "Launcher revoked the token"
            return "success", f"Standalone token accepted (token={token_preview(value)})"

        return "failure", "No transport for credential kind"

    def format_result(self) -> str:
        outcome, message = self.classify()
        return f"[auth] {self.provider} result -> outcome={outcome}, message=\"{message}\""


def main() -> None:
    banner = textwrap.dedent(
        """
        == Auth Flow Lifecycle ==
        Provider/token combinations demonstrate success, retry, and failure paths.
        """
    ).strip()
    print(banner)

    samples = [
        Sample("steam", "TICKET-0123456789abcdef"),
        Sample("steam", "retry:TICKET-FFFFFFFF"),
        Sample("standalone", "JWT-abcdef-refresh"),
        Sample("standalone", "TOKEN-VALID-1234567890"),
    ]

    for index, sample in enumerate(samples, start=1):
        print()
        print(f"-- Scenario {index}: {sample.provider} --")
        for line in itertools.chain(sample.dispatch_logs(), [sample.format_result()]):
            print(line)


if __name__ == "__main__":
    main()

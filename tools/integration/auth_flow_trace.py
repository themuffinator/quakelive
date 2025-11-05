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
    def __init__(self, provider: str, kind: str, token: str) -> None:
        self.provider = provider
        self.kind = kind
        self.token = token

    @property
    def endpoint(self) -> str:
        return {
            "steam": "/steam/session/validate",
            "standalone": "/launcher/auth/verify",
        }.get(self.kind, "<none>")

    def dispatch_logs(self) -> list[str]:
        preview = token_preview(self.token)
        payload_template = {
            "steam": "ticket=%s (len=%d)",
            "standalone": "token=%s (len=%d)",
        }.get(self.kind, "credential=%s (len=%d)")

        return [
            f"[auth] {self.provider} dispatch ({self.endpoint}): submitting credential",
            f"[auth] {self.provider} payload summary: {payload_template % (preview, len(self.token))}",
        ]

    def classify(self) -> tuple[str, str]:
        """Return (outcome, message) mirroring ql_auth.c heuristics."""
        value = self.token

        preview = token_preview(value)

        if self.kind == "steam":
            if len(value) < 16:
                if self.provider == "Open Steam Adapter":
                    return "failure", "Open adapter rejected Steam credential: payload too short"
                return "failure", "Steam ticket rejected: payload too short"

            if any(marker in value for marker in ("denied", "invalid")):
                if self.provider in ("Open Steam Adapter", "Hybrid"):
                    return "failure", "Open adapter respected Steam denial"
                return "failure", "Steam backend denied the ticket"

            if "retry" in value and self.provider == "Hybrid":
                return "success", f"Hybrid fallback accepted credential via open adapter (token={preview})"

            if self.provider == "Open Steam Adapter":
                return "success", f"Open adapter accepted Steam ticket (ticket={preview})"

            if "retry" in value:
                return "retry", "Steam service busy, retry with refreshed ticket"

            return "success", f"Steam session established (ticket={preview})"

        if self.kind == "standalone":
            if len(value) < 12:
                return "failure", "Standalone token rejected: payload too short"
            if "refresh" in value:
                return "retry", "Launcher token expired, request a refresh"
            if any(marker in value for marker in ("revoke", "denied")):
                return "failure", "Launcher revoked the token"
            return "success", f"Standalone token accepted (token={preview})"

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
        Sample("Steamworks", "steam", "TICKET-0123456789abcdef"),
        Sample("Hybrid", "steam", "retry:TICKET-FFFFFFFF"),
        Sample("Open Steam Adapter", "standalone", "JWT-abcdef-refresh"),
        Sample("Open Steam Adapter", "standalone", "TOKEN-VALID-1234567890"),
    ]

    for index, sample in enumerate(samples, start=1):
        print()
        print(f"-- Scenario {index}: {sample.provider} --")
        for line in itertools.chain(sample.dispatch_logs(), [sample.format_result()]):
            print(line)


if __name__ == "__main__":
    main()

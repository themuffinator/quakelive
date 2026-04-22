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
    def __init__(self, title: str, provider: str, kind: str, token: str) -> None:
        self.title = title
        self.provider = provider
        self.kind = kind
        self.token = token

    @property
    def endpoint(self) -> str:
        return {
            "steam": "/steam/session/validate",
            "standalone": "/launcher/auth/verify",
        }.get(self.kind, "<none>")

    @property
    def policy(self) -> str:
        return "compatibility-only"

    def _stage_log(self, provider: str, stage: str, endpoint: str, detail: str) -> str:
        return f"[auth] {provider} [{self.policy}] {stage} ({endpoint}): {detail}"

    def _payload_log(self) -> str:
        preview = token_preview(self.token)
        payload_template = {
            "steam": "ticket=%s (len=%d)",
            "standalone": "token=%s (len=%d)",
        }.get(self.kind, "credential=%s (len=%d)")

        return f"[auth] {self.provider} [{self.policy}] payload summary: {payload_template % (preview, len(self.token))}"

    def dispatch_logs(self) -> list[str]:
        lines = [
            self._stage_log(self.provider, "dispatch", self.endpoint, "submitting credential"),
            self._payload_log(),
        ]

        if (
            self.provider == "Hybrid"
            and self.kind == "steam"
            and len(self.token) >= 16
            and "retry" in self.token
            and not any(marker in self.token for marker in ("denied", "invalid"))
        ):
            lines.append(
                self._stage_log(
                    "Hybrid",
                    "hybrid-fallback",
                    "/steam/session/validate",
                    "Steamworks heuristic compatibility backend returned retry; dispatching open adapter fallback",
                )
            )
            lines.append(
                self._stage_log(
                    "Open Steam Adapter",
                    "dispatch",
                    "/launcher/auth/verify",
                    "submitting fallback credential",
                )
            )

        return lines

    def classify(self) -> tuple[str, str]:
        """Return (outcome, message) mirroring ql_auth.c heuristics."""
        value = self.token

        preview = token_preview(value)

        if self.kind == "steam":
            if len(value) < 16:
                if self.provider == "Open Steam Adapter":
                    return "failure", "Open adapter heuristic compatibility backend rejected Steam credential: payload too short"
                return "failure", "Steamworks heuristic compatibility backend rejected ticket: payload too short"

            if any(marker in value for marker in ("denied", "invalid")):
                if self.provider in ("Open Steam Adapter", "Hybrid"):
                    return "failure", "Open adapter heuristic compatibility backend respected Steam denial"
                return "failure", "Steamworks heuristic compatibility backend denied the ticket"

            if "retry" in value and self.provider == "Hybrid":
                return "success", f"Hybrid fallback accepted credential via heuristic open adapter (token={preview})"

            if self.provider == "Open Steam Adapter":
                return "success", f"Open adapter heuristic compatibility backend accepted Steam ticket (ticket={preview})"

            if "retry" in value:
                return "retry", "Steamworks heuristic compatibility backend reported busy; retry with refreshed ticket"

            return "success", f"Steamworks heuristic compatibility backend accepted ticket (ticket={preview})"

        if self.kind == "standalone":
            if len(value) < 12:
                return "failure", "Open adapter heuristic compatibility backend rejected standalone token: payload too short"
            if "refresh" in value:
                return "retry", "Open adapter heuristic compatibility backend requested launcher token refresh"
            if any(marker in value for marker in ("revoke", "denied")):
                return "failure", "Open adapter heuristic compatibility backend treated token as revoked"
            return "success", f"Open adapter heuristic compatibility backend accepted standalone token (token={preview})"

        return "failure", "No transport for credential kind"

    def format_result(self) -> str:
        outcome, message = self.classify()
        return f"[auth] {self.provider} [{self.policy}] result -> outcome={outcome}, message=\"{message}\""


def main() -> None:
    banner = textwrap.dedent(
        """
        == Auth Flow Lifecycle ==
        Provider/token combinations demonstrate success, retry, and failure paths.
        """
    ).strip()
    print(banner)

    samples = [
        Sample("Steamworks success", "Steamworks", "steam", "TICKET-0123456789abcdef"),
        Sample("Steamworks malformed", "Steamworks", "steam", "SHORT-TICKET"),
        Sample("Steamworks denied", "Steamworks", "steam", "TICKET-denied-0123456789"),
        Sample("Hybrid fallback", "Hybrid", "steam", "retry:TICKET-FFFFFFFF"),
        Sample("Open adapter refresh", "Open Steam Adapter", "standalone", "JWT-abcdef-refresh"),
        Sample("Open adapter revoked", "Open Steam Adapter", "standalone", "TOKEN-revoke-1234567890"),
        Sample("Open adapter success", "Open Steam Adapter", "standalone", "TOKEN-VALID-1234567890"),
    ]

    for index, sample in enumerate(samples, start=1):
        print()
        print(f"-- Scenario {index}: {sample.title} --")
        for line in itertools.chain(sample.dispatch_logs(), [sample.format_result()]):
            print(line)


if __name__ == "__main__":
    main()

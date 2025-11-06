#!/usr/bin/env python3
"""Simulate the client-side auth flow to document request lifecycle logging."""

from __future__ import annotations

import itertools
import textwrap
from typing import Optional


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

    def _steam_backend(self) -> tuple[str, str]:
        value = self.token
        preview = token_preview(value)

        if len(value) < 16:
            return "failure", "Steam ticket rejected: payload too short"

        if any(marker in value for marker in ("denied", "invalid")):
            return "failure", "Steam backend denied the ticket"

        if "retry" in value:
            return "retry", "Steam service busy, retry with refreshed ticket"

        return "success", f"Steam session established (ticket={preview})"

    def _open_adapter_backend_for_steam(self) -> tuple[str, str]:
        value = self.token
        preview = token_preview(value)

        if len(value) < 16:
            return "failure", "Open adapter rejected Steam credential: payload too short"

        if any(marker in value for marker in ("denied", "invalid")):
            return "failure", "Open adapter respected Steam denial"

        return "success", f"Open adapter accepted Steam ticket (ticket={preview})"

    def _standalone_backend(self) -> tuple[str, str]:
        value = self.token
        preview = token_preview(value)

        if len(value) < 12:
            return "failure", "Standalone token rejected: payload too short"
        if "refresh" in value:
            return "retry", "Launcher token expired, request a refresh"
        if any(marker in value for marker in ("revoke", "denied")):
            return "failure", "Launcher revoked the token"
        return "success", f"Standalone token accepted (token={preview})"

    @staticmethod
    def _format_stage_result(handled: bool, message: str, outcome: str, label: Optional[str] = None) -> str:
        backend_part = f", backend={label}" if label else ""
        sanitized = message if message else "<no message>"
        return f"handled={'true' if handled else 'false'}{backend_part}, outcome={outcome}, message=\"{sanitized}\""

    def simulate(self) -> tuple[str, str, list[str]]:
        endpoint = self.endpoint
        stage_logs: list[str] = []

        def log_stage(stage_prefix: str, suffix: str, detail: str) -> None:
            stage_logs.append(f"[auth] {self.provider} {stage_prefix}.{suffix} ({endpoint}): {detail}")

        if self.kind == "steam":
            if self.provider == "Hybrid":
                log_stage("steamworks", "invoke", "invoking Steamworks backend")
                steam_outcome, steam_message = self._steam_backend()
                log_stage(
                    "steamworks",
                    "result",
                    self._format_stage_result(True, steam_message, steam_outcome, "Steamworks"),
                )

                if steam_outcome == "success":
                    return steam_outcome, steam_message, stage_logs

                log_stage("open_adapter", "invoke", "invoking Open Steam Adapter backend")
                fallback_outcome, fallback_message = self._open_adapter_backend_for_steam()

                if fallback_outcome == "success":
                    preview = token_preview(self.token)
                    fallback_message = (
                        f"Hybrid fallback accepted credential via open adapter (token={preview})"
                    )
                    log_stage(
                        "open_adapter",
                        "result",
                        self._format_stage_result(True, fallback_message, fallback_outcome, "Open Steam Adapter"),
                    )
                    return fallback_outcome, fallback_message, stage_logs

                log_stage(
                    "open_adapter",
                    "result",
                    self._format_stage_result(True, fallback_message, fallback_outcome, "Open Steam Adapter"),
                )
                return steam_outcome, steam_message, stage_logs

            if self.provider == "Open Steam Adapter":
                log_stage("open_adapter", "invoke", "invoking Open Steam Adapter backend")
                outcome, message = self._open_adapter_backend_for_steam()
                log_stage(
                    "open_adapter",
                    "result",
                    self._format_stage_result(True, message, outcome, "Open Steam Adapter"),
                )
                return outcome, message, stage_logs

            log_stage("steamworks", "invoke", "invoking Steamworks backend")
            outcome, message = self._steam_backend()
            log_stage(
                "steamworks",
                "result",
                self._format_stage_result(True, message, outcome, "Steamworks"),
            )
            return outcome, message, stage_logs

        if self.kind == "standalone":
            log_stage("standalone", "invoke", "invoking Open Steam Adapter backend")
            outcome, message = self._standalone_backend()
            log_stage(
                "standalone",
                "result",
                self._format_stage_result(True, message, outcome, "Open Steam Adapter"),
            )
            return outcome, message, stage_logs

        log_stage("unknown", "result", self._format_stage_result(False, "No transport for credential kind", "failure"))
        return "failure", "No transport for credential kind", stage_logs

    def format_result(self, outcome: str, message: str) -> str:
        sanitized = message if message else "<no message>"
        return f"[auth] {self.provider} result -> outcome={outcome}, message=\"{sanitized}\""


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
        outcome, message, stage_logs = sample.simulate()
        for line in itertools.chain(sample.dispatch_logs(), stage_logs, [sample.format_result(outcome, message)]):
            print(line)


if __name__ == "__main__":
    main()

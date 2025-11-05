"""Launch helper for capturing deterministic trace artefacts."""

from __future__ import annotations

import json
import os
import selectors
import subprocess
import time
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Sequence, TextIO

from .collector import TraceCollector
from .errors import TraceCaptureError


@dataclass
class TraceLauncherConfig:
    """Configuration for :class:`TraceLauncher`."""

    command: Sequence[str]
    output_dir: Path
    cwd: Optional[Path] = None
    env: Optional[Mapping[str, str]] = None
    match_duration: float = 60.0
    poll_interval: float = 0.05
    termination_timeout: float = 5.0
    capture_stdout: bool = True
    capture_stderr: bool = True


@dataclass
class TraceLaunchResult:
    """Summary of a completed trace capture."""

    output_dir: Path
    manifest_path: Path
    runtime_seconds: float
    exit_code: int
    digests: Mapping[str, str]
    counts: Mapping[str, int]
    metadata: Mapping[str, object]
    unknown_lines: Sequence[str] = field(default_factory=tuple)


class TraceLauncher:
    """Launches an instrumented client and captures trace artefacts."""

    def __init__(self, config: TraceLauncherConfig) -> None:
        if not config.command:
            raise TraceCaptureError("A launch command must be provided.")

        self.config = config

    def launch(self) -> TraceLaunchResult:
        """Execute the configured command and persist trace artefacts."""

        cfg = self.config
        output_dir = cfg.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        if cfg.env:
            env.update(cfg.env)

        stdout_handle = (output_dir / "stdout.log").open("w", encoding="utf-8")
        stderr_handle = (output_dir / "stderr.log").open("w", encoding="utf-8")

        collector = TraceCollector(output_dir)

        start_time = time.monotonic()
        timeout_triggered = False

        process = subprocess.Popen(
            list(cfg.command),
            stdout=subprocess.PIPE if cfg.capture_stdout else None,
            stderr=subprocess.PIPE if cfg.capture_stderr else None,
            cwd=str(cfg.cwd) if cfg.cwd else None,
            env=env,
            text=True,
            bufsize=1,
        )

        selector = selectors.DefaultSelector()
        if process.stdout is not None:
            selector.register(process.stdout, selectors.EVENT_READ, data="stdout")
        if process.stderr is not None:
            selector.register(process.stderr, selectors.EVENT_READ, data="stderr")

        try:
            self._pump_streams(process, selector, collector, stdout_handle, stderr_handle)
        finally:
            selector.close()
            stdout_handle.close()
            stderr_handle.close()

        if process.poll() is None:
            timeout_triggered = time.monotonic() - start_time >= cfg.match_duration
            if timeout_triggered:
                process.terminate()
                try:
                    process.wait(timeout=cfg.termination_timeout)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=cfg.termination_timeout)
            else:
                process.wait()
        else:
            timeout_triggered = False

        runtime = time.monotonic() - start_time
        exit_code = process.returncode if process.returncode is not None else -1

        digests = collector.finalize()

        manifest = self._build_manifest(
            cfg=cfg,
            runtime=runtime,
            exit_code=exit_code,
            timeout_triggered=timeout_triggered,
            digests=digests,
            collector=collector,
        )

        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

        return TraceLaunchResult(
            output_dir=output_dir,
            manifest_path=manifest_path,
            runtime_seconds=runtime,
            exit_code=exit_code,
            digests=digests,
            counts=collector.counts,
            metadata=manifest.get("metadata", {}),
            unknown_lines=collector.unknown_lines,
        )

    def _pump_streams(
        self,
        process: subprocess.Popen[str],
        selector: selectors.BaseSelector,
        collector: TraceCollector,
        stdout_handle: TextIO,
        stderr_handle: TextIO,
    ) -> None:
        cfg = self.config
        deadline = time.monotonic() + cfg.match_duration

        while True:
            if not selector.get_map():
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(cfg.poll_interval)
                continue

            timeout = max(0.0, deadline - time.monotonic())
            timeout = min(timeout, cfg.poll_interval)
            events = selector.select(timeout or cfg.poll_interval)
            for key, _ in events:
                stream_name = key.data
                handle = stdout_handle if stream_name == "stdout" else stderr_handle
                line = key.fileobj.readline()
                if line == "":
                    selector.unregister(key.fileobj)
                    continue
                handle.write(line)
                handle.flush()
                collector.handle_line(line)

            if time.monotonic() >= deadline:
                break

    def _build_manifest(
        self,
        *,
        cfg: TraceLauncherConfig,
        runtime: float,
        exit_code: int,
        timeout_triggered: bool,
        digests: Mapping[str, str],
        collector: TraceCollector,
    ) -> MutableMapping[str, object]:
        manifest: MutableMapping[str, object] = {
            "command": list(cfg.command),
            "cwd": str(cfg.cwd) if cfg.cwd else None,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "runtime_seconds": runtime,
            "match_duration_seconds": cfg.match_duration,
            "exit_code": exit_code,
            "timeout_triggered": timeout_triggered,
            "digests": digests,
            "counts": collector.counts,
            "unknown_lines": list(collector.unknown_lines),
        }

        if collector.metadata:
            manifest["metadata"] = dict(collector.metadata)

        return manifest


def parse_env_overrides(values: Sequence[str]) -> Mapping[str, str]:
    overrides: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise TraceCaptureError(f"Invalid environment override: {item!r}")
        key, value = item.split("=", 1)
        overrides[key] = value
    return overrides


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Capture Quake Live trace artefacts.")
    parser.add_argument("--output", required=True, help="Directory where artefacts are stored")
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Maximum capture duration in seconds (default: 60)",
    )
    parser.add_argument("--cwd", help="Working directory for the launched process")
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Environment overrides applied to the launched process",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute (prefix with -- to separate from harness args)",
    )

    args = parser.parse_args(argv)

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("A command to execute must be provided after --")

    env_overrides = parse_env_overrides(args.env)

    config = TraceLauncherConfig(
        command=command,
        output_dir=Path(args.output).expanduser().resolve(),
        cwd=Path(args.cwd).expanduser().resolve() if args.cwd else None,
        env=env_overrides,
        match_duration=args.duration,
    )

    launcher = TraceLauncher(config)
    result = launcher.launch()
    print(f"Trace artefacts stored in {result.output_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

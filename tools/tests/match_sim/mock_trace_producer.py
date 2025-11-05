"""Emit a deterministic set of trace events for tests."""

from __future__ import annotations

import json
import sys
import time


def emit(channel: str, payload: dict) -> None:
    sys.stdout.write(f"TRACE:{channel}:{json.dumps(payload)}\n")
    sys.stdout.flush()


def main() -> None:
    emit("META", {"map": "qztourney7", "match_id": "unittest"})
    emit("RNG", {"seed": 123456, "reason": "match_warmup"})
    emit("SYS", {"id": 1, "name": "trap_Print", "args": ["match start"]})
    emit("ENT", {"time": 1, "entities": [{"id": 1, "health": 125}]})
    emit("SYS", {"id": 2, "name": "trap_SendServerCommand", "args": [1, "score"]})
    time.sleep(0.05)
    emit("ENT", {"time": 2, "entities": [{"id": 1, "health": 100}]})


if __name__ == "__main__":
    main()

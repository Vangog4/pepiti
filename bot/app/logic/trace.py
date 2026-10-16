"""Lightweight AI call tracing.

Always logs structured events. If LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY
are set and the ``langfuse`` package is importable, also sends a generation.
No hard dependency on Langfuse — safe for VDS without extra RAM services.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("pepito.ai")


def _langfuse_client() -> Any | None:
    pk = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
    sk = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
    if not pk or not sk:
        return None
    try:
        from langfuse import Langfuse  # type: ignore

        kwargs: dict[str, Any] = {"public_key": pk, "secret_key": sk}
        host = os.getenv("LANGFUSE_HOST", "").strip()
        if host:
            kwargs["host"] = host
        return Langfuse(**kwargs)
    except Exception:
        return None


@dataclass
class AiCallTrace:
    kind: str
    model: str
    attempt: int = 0
    started: float = field(default_factory=time.monotonic)
    success: bool = False
    schema_ok: bool | None = None
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def ok(self, *, schema_ok: bool | None = None, **meta: Any) -> None:
        self.success = True
        if schema_ok is not None:
            self.schema_ok = schema_ok
        self.meta.update(meta)

    def fail(self, err: BaseException | str, **meta: Any) -> None:
        self.success = False
        self.error = str(err)[:300]
        self.meta.update(meta)

    @property
    def latency_ms(self) -> int:
        return int((time.monotonic() - self.started) * 1000)

    def emit(self) -> None:
        payload = {
            "kind": self.kind,
            "model": self.model,
            "attempt": self.attempt,
            "success": self.success,
            "schema_ok": self.schema_ok,
            "latency_ms": self.latency_ms,
            "error": self.error,
            **self.meta,
        }
        if self.success:
            logger.info("ai_call %s", payload)
        else:
            logger.warning("ai_call %s", payload)

        client = _langfuse_client()
        if client is None:
            return
        try:
            client.generation(
                name=self.kind,
                model=self.model,
                metadata=payload,
                level="DEFAULT" if self.success else "WARNING",
            )
            # best-effort flush; don't block bot on network
            if hasattr(client, "flush"):
                client.flush()
        except Exception as e:
            logger.debug("langfuse emit failed: %s", e)


@contextmanager
def ai_trace(kind: str, model: str, attempt: int = 0, **meta: Any) -> Iterator[AiCallTrace]:
    tr = AiCallTrace(kind=kind, model=model, attempt=attempt, meta=dict(meta))
    try:
        yield tr
    finally:
        tr.emit()

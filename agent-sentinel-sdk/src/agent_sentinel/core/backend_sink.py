"""
Optional backend event sink.

When SENTINEL_API_KEY and SENTINEL_API_URL are set, detected security
events are pushed to the Agent Sentinel backend in the background.
The sink uses a daemon thread with a bounded queue so it never blocks
the user's agent, never crashes on network failure, and shuts down
cleanly when the process exits.

If the env vars are not set, the sink is a no-op.
"""

import atexit
import json
import logging
import os
import queue
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_BATCH_SIZE = 10
_FLUSH_INTERVAL_SECONDS = 2.0
_QUEUE_MAX = 5000


class BackendEventSink:
    """
    Fire-and-forget event sink that batches and POSTs security events
    to the Agent Sentinel backend API.

    Usage is automatic — the GlobalEventRegistry creates one on import
    if the environment is configured.
    """

    def __init__(self, api_url: str, api_key: str):
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key
        self._queue: queue.Queue[Dict[str, Any]] = queue.Queue(maxsize=_QUEUE_MAX)
        self._shutdown = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="sentinel-backend-sink", daemon=True
        )
        self._thread.start()
        atexit.register(self.flush_and_stop)
        logger.debug(
            "BackendEventSink started — pushing events to %s", self._api_url
        )

    def enqueue(self, event_dict: Dict[str, Any]) -> None:
        """
        Add an event to the outbound queue.

        Drops the event silently if the queue is full — we never want
        to back-pressure the user's agent.
        """
        try:
            self._queue.put_nowait(event_dict)
        except queue.Full:
            logger.warning("Event sink queue full — dropping event")

    def flush_and_stop(self) -> None:
        """Flush remaining events and stop the background thread."""
        self._shutdown.set()
        if self._thread.is_alive():
            self._thread.join(timeout=5.0)

    # ----- internal -----

    def _run(self) -> None:
        """Background loop: drain the queue in batches and POST them."""
        while not self._shutdown.is_set():
            batch = self._drain_batch()
            if batch:
                self._post_batch(batch)
            else:
                self._shutdown.wait(timeout=_FLUSH_INTERVAL_SECONDS)

        # Final flush on shutdown
        remaining = self._drain_batch(max_items=_QUEUE_MAX)
        if remaining:
            self._post_batch(remaining)

    def _drain_batch(self, max_items: int = _BATCH_SIZE) -> List[Dict[str, Any]]:
        batch: List[Dict[str, Any]] = []
        while len(batch) < max_items:
            try:
                batch.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return batch

    def _post_batch(self, batch: List[Dict[str, Any]]) -> None:
        """POST a batch of events to the backend. Failures are logged, never raised."""
        import requests  # Lazy import — only needed when sink is active

        url = f"{self._api_url}/api/events"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        for event in batch:
            try:
                resp = requests.post(
                    url, json=event, headers=headers, timeout=5
                )
                if resp.status_code == 201:
                    logger.debug("Event pushed to backend: %s", event.get("id", "?"))
                else:
                    logger.warning(
                        "Backend returned %d for event %s: %s",
                        resp.status_code,
                        event.get("id", "?"),
                        resp.text[:200],
                    )
            except Exception as exc:
                logger.debug("Failed to push event to backend: %s", exc)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_sink: Optional[BackendEventSink] = None


def get_backend_sink() -> Optional[BackendEventSink]:
    """
    Return the module-level BackendEventSink, or None if not configured.

    Initialised lazily on first call so that importing the module
    has no side effects if the env vars are not set.
    """
    global _sink
    if _sink is not None:
        return _sink

    api_key = os.getenv("SENTINEL_API_KEY", "")
    api_url = os.getenv("SENTINEL_API_URL", "")
    if api_key and api_url:
        _sink = BackendEventSink(api_url, api_key)
    return _sink

"""File system watcher with debounced sync trigger."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

log = logging.getLogger(__name__)


class DebouncedHandler(FileSystemEventHandler):
    """Triggers a callback after a debounce period of filesystem quiet."""

    def __init__(self, callback: Callable[[], None], debounce_seconds: float = 5.0):
        super().__init__()
        self._callback = callback
        self._debounce = debounce_seconds
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def _reset_timer(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        log.info("Debounce elapsed — triggering sync")
        try:
            self._callback()
        except Exception:
            log.exception("Sync callback failed")

    def on_any_event(self, event: FileSystemEvent) -> None:
        # Ignore directory events and .git internals
        if event.is_directory:
            return
        src = str(getattr(event, "src_path", ""))
        if "/.git/" in src or "\\.git\\" in src:
            return
        log.debug("FS event: %s %s", event.event_type, src)
        self._reset_timer()


def watch(repo_path: Path, callback: Callable[[], None], debounce_seconds: float = 5.0) -> None:
    """Watch a directory and call `callback` after changes settle.

    Blocks until interrupted (Ctrl+C).
    """
    handler = DebouncedHandler(callback, debounce_seconds)
    observer = Observer()
    observer.schedule(handler, str(repo_path), recursive=True)
    observer.start()
    log.info("Watching %s (debounce: %.1fs)", repo_path, debounce_seconds)

    try:
        while observer.is_alive():
            observer.join(timeout=1)
    except KeyboardInterrupt:
        log.info("Stopping watcher")
    finally:
        observer.stop()
        observer.join()

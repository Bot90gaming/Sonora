"""
Safe QThread helper.

The problem: when you do `self._thread = QThread()` the old QThread loses its
last Python reference, CPython GC destroys the wrapper, and Qt crashes with
"QThread: Destroyed while thread '' is still running".

Solution: keep every in-flight thread in a module-level set so Python never
drops the reference.  Each thread removes itself from the set on `finished`.
"""
from __future__ import annotations
from PyQt6.QtCore import QThread

_live: set[QThread] = set()


def start_thread(worker_obj, thread: QThread | None = None) -> QThread:
    """
    Create (or reuse) a QThread, move *worker_obj* onto it, wire
    worker_obj.run → thread.started, keep a Python reference until finished,
    then return the thread (already started).

    Caller is responsible for connecting worker signals before calling this.
    """
    t = thread or QThread()
    _live.add(t)
    t.finished.connect(lambda: _live.discard(t))
    t.finished.connect(t.deleteLater)
    t.started.connect(worker_obj.run)
    worker_obj.moveToThread(t)
    t.start()
    return t


def retire_thread(t: QThread | None) -> None:
    """
    Quit a thread (if running) without waiting.  The thread stays in _live
    until it actually finishes, so Python never GC's the wrapper early.
    """
    if t is None:
        return
    try:
        if t.isRunning():
            t.quit()
    except RuntimeError:
        pass  # C++ object already gone — nothing to do

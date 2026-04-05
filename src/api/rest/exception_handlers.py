"""Auto-discovery of domain exception handlers.

Scans ``api/rest/*/error_handlers.py`` modules for an ``exception_handlers``
dict and merges them into a single registry.  Adding a new domain requires
only creating its ``error_handlers.py`` — no changes to ``main.py``.
"""

import importlib
from collections.abc import Callable
from pathlib import Path


def collect_exception_handlers() -> dict[type[Exception], Callable]:
    handlers: dict[type[Exception], Callable] = {}
    rest_dir = Path(__file__).parent
    for entry in sorted(rest_dir.iterdir()):
        if not entry.is_dir() or not (entry / "error_handlers.py").exists():
            continue
        module = importlib.import_module(f"src.api.rest.{entry.name}.error_handlers")
        domain_handlers = getattr(module, "exception_handlers", None)
        if domain_handlers:
            handlers.update(domain_handlers)
    return handlers

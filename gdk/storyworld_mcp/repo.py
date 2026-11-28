"""Locate the GPTStoryworld scripts the tools wrap, and import them without letting them print.

The skill scripts print progress to stdout, which carries the MCP protocol, so every call into them
runs under ``quiet()``.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import json
import sys
from pathlib import Path
from typing import Any, Iterator


class StoryworldError(Exception):
    """A refusal with a stable code the model can act on."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


BUILDING = Path("codex-skills") / "storyworld-building" / "scripts"
SMALL = Path("codex-skills") / "small-storyworld-builder" / "scripts"
HYPERWORLD = Path("codex-skills") / "hyperworld-builder" / "scripts"
HG_ENV = Path("verifiers_envs") / "storyworld-hypergames-env"
ROUTING_PROBE = Path("tools") / "probe_morality_batch_routing.py"


@contextlib.contextmanager
def quiet() -> Iterator[io.StringIO]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        yield buffer


class Repo:
    def __init__(self, root: Path, deny: list[str] | None = None):
        self.root = root.resolve()
        # Paths no tool may read (a benchmark harness passes each task's grading-only files).
        self.deny = {(p if Path(p).is_absolute() else self.root / p).resolve() for p in (deny or [])}
        if not (self.root / BUILDING / "sweepweave_validator.py").is_file():
            raise StoryworldError(
                "not_a_checkout", f"{self.root} has no {BUILDING.as_posix()}/sweepweave_validator.py"
            )
        for sub in (BUILDING, SMALL, HYPERWORLD, ROUTING_PROBE.parent, Path("mcp-storyworld-encounter")):
            path = str(self.root / sub)
            if (self.root / sub).is_dir() and path not in sys.path:
                sys.path.insert(0, path)
        self._modules: dict[str, Any] = {}

    def module(self, name: str) -> Any:
        if name not in self._modules:
            with quiet():
                self._modules[name] = importlib.import_module(name)
        return self._modules[name]

    def has_hyperworld(self) -> bool:
        return (self.root / HYPERWORLD / "hyperworld_engine.py").is_file()

    def has_hg_env(self) -> bool:
        return (self.root / HG_ENV / "tests").is_dir()

    def inside(self, raw: str) -> Path:
        """A repo-relative or absolute path that must resolve inside the checkout (and outside .git)."""
        path = Path(raw)
        path = (path if path.is_absolute() else self.root / path).resolve()
        try:
            rel = path.relative_to(self.root)
        except ValueError as exc:
            raise StoryworldError("outside_root", f"{raw} is outside {self.root}") from exc
        if rel.parts and rel.parts[0] == ".git":
            raise StoryworldError("outside_root", f"{raw} is inside .git")
        self.check_readable(path)
        return path

    def check_readable(self, path: Path) -> None:
        if path.resolve() in self.deny:
            raise StoryworldError("denied_path", f"{self.rel(path)} is closed to tools in this session")

    def rel(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)


def sha256_file(path: Path) -> str:
    """SHA-256 with CRLF read as LF in text files, so hashes match across autocrlf checkouts."""
    data = path.read_bytes()
    if b"\0" not in data[:4096]:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def estimate_tokens(text: str) -> int:
    """A tokenizer-free estimate (4 characters per token), used for packet budgets."""
    return len(text) // 4 + 1

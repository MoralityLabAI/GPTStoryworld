"""Shared paths, hashing, splits, parsing helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = PKG_DIR.parents[1]
DATA_DIR = PKG_DIR / "data"
MANIFEST_PATH = PKG_DIR / "manifest.json"
SEED = 20261128
TRACKS = ("builder", "small", "hypergames")
SKILL_OF_TRACK = {"builder": "storyworld-builder", "small": "small-storyworld", "hypergames": "hypergames"}

BUILD_SCRIPTS = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"
SMALL_SCRIPTS = REPO_ROOT / "codex-skills" / "small-storyworld-builder" / "scripts"
HG_SRC = REPO_ROOT / "verifiers_envs" / "storyworld-hypergames-env" / "src"
CAMELOT_BENCH = REPO_ROOT / "InkyWorlds" / "camelots-reckoning" / "bench" / "bench_repair.py"

SPLIT_DEV_PERCENT = 70

_paths_ready = False


def ensure_paths() -> None:
    """Make the sibling repo modules importable (validator, gate, swmd tools, hypergames gym)."""
    global _paths_ready
    if _paths_ready:
        return
    for p in (BUILD_SCRIPTS, SMALL_SCRIPTS, HG_SRC):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    _paths_ready = True


def rel(path: Path) -> str:
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def abspath(repo_rel: str) -> Path:
    return REPO_ROOT / repo_rel


def file_sha256(path: Path) -> str:
    """SHA-256 of a file; CRLF is normalised to LF for text files so the hash survives autocrlf checkouts."""
    data = Path(path).read_bytes()
    if b"\0" not in data[:4096]:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_of(task_id: str) -> str:
    h = int(hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:8], 16)
    return "dev" if h % 100 < SPLIT_DEV_PERCENT else "test"


def est_tokens(text: str) -> int:
    """Packet-size estimate used throughout: ceil(chars / 4)."""
    return (len(text) + 3) // 4


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_THINK = re.compile(r"<think>.*?</think>", re.S)
_FENCE = re.compile(r"^```[A-Za-z0-9_-]*\s*\n?(.*?)\n?```\s*$", re.S)


def strip_wrappers(text: str) -> str:
    text = _THINK.sub("", text).strip()
    m = _FENCE.match(text)
    if m:
        text = m.group(1).strip()
    return text


def parse_json_artifact(raw: str):
    """Return (obj, model_parse_ok, parse_ok).

    model_parse_ok: the raw artifact is a bare JSON document.
    parse_ok: a JSON object is recoverable after stripping think blocks, code fences and prose.
    """
    try:
        return json.loads(raw), True, True
    except Exception:
        pass
    text = strip_wrappers(raw)
    try:
        return json.loads(text), False, True
    except Exception:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1]), False, True
        except Exception:
            pass
    return None, False, False


def read_artifact(path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_bytes().decode("utf-8-sig", errors="replace")


def write_temp_json(obj, suffix=".json") -> Path:
    fd = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8")
    json.dump(obj, fd)
    fd.close()
    return Path(fd.name)


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def finish(task: dict, checks: dict, score: float, passed: bool, error: str | None = None) -> dict:
    out = {"task_id": task["task_id"], "track": task["track"], "score": round(max(0.0, min(1.0, score)), 4),
           "passed": bool(passed), "checks": checks}
    if error:
        out["error"] = error
    return out


def bool_checks_mean(checks: dict) -> float:
    vals = [1.0 if v else 0.0 for k, v in checks.items()
            if isinstance(v, bool) and not k.startswith("metric_")]
    return mean(vals)

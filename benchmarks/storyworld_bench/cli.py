"""Entry point for `python benchmarks/storyworld_bench/cli.py <cmd>` (same as `python -m benchmarks.storyworld_bench`)."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from benchmarks.storyworld_bench.app import main
else:
    from .app import main

if __name__ == "__main__":
    raise SystemExit(main())

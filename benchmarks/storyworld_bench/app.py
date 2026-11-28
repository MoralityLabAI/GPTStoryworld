"""StoryworldBench CLI: tasks, score, run, selftest, freeze, verify."""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import builder, common as C, hypergames, small

TRACK_MODULES = {"builder": builder, "small": small, "hypergames": hypergames}
PUBLIC_FIELDS = ("task_id", "track", "skill", "prompt", "inputs", "grading_only", "budget_tokens", "scorer",
                 "answer_format")


def grading_only(task: dict) -> list:
    """Repo paths that hold or compute a task's answer; a harness whose agent can read files must refuse them."""
    paths = set(task.get("grading_only", ()))
    oracle = task["private"].get("oracle", {})
    if "path" in oracle:
        paths.add(oracle["path"])
    return sorted(paths)
ORACLE_BAR = 0.99
NULL_CEILING = 0.02


# ---------------------------------------------------------------- manifest
def generate_all() -> tuple[dict, dict]:
    """Deterministically build every task, the generated data files and the manifest."""
    files: dict = {}
    track_sources: dict = {}
    tasks: list = []
    for track in C.TRACKS:
        srcs: set = set()
        tasks += TRACK_MODULES[track].generate(files, srcs)
        track_sources[track] = sorted(srcs)
    tasks.sort(key=lambda t: (C.TRACKS.index(t["track"]), t["task_id"]))
    ids = [t["task_id"] for t in tasks]
    assert len(ids) == len(set(ids)), "duplicate task ids"
    all_sources = sorted(set().union(*track_sources.values()))
    manifest = {
        "bench": "storyworld_bench", "version": 1, "seed": C.SEED, "split_dev_percent": C.SPLIT_DEV_PERCENT,
        "sources": {p: C.file_sha256(C.abspath(p)) for p in all_sources},
        "track_sources": track_sources,
        "data_files": {k: C.bytes_sha256(v) for k, v in sorted(files.items())},
        "tasks": [dict(t, split=C.split_of(t["task_id"]), grading_only=grading_only(t)) for t in tasks],
    }
    return manifest, files


def freeze() -> dict:
    manifest, files = generate_all()
    if C.DATA_DIR.exists():
        shutil.rmtree(C.DATA_DIR)
    for name, data in files.items():
        out = C.DATA_DIR / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    C.MANIFEST_PATH.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest


def load_manifest() -> dict:
    if not C.MANIFEST_PATH.exists():
        raise SystemExit("manifest.json missing: run `python -m benchmarks.storyworld_bench freeze`")
    return json.loads(C.MANIFEST_PATH.read_text(encoding="utf-8"))


def verify(manifest: dict, tracks=C.TRACKS) -> list:
    """Return the list of source/data files whose hash differs from the frozen manifest."""
    bad = []
    wanted = sorted(set().union(*(manifest["track_sources"][t] for t in tracks)))
    for p in wanted:
        f = C.abspath(p)
        if not f.exists() or C.file_sha256(f) != manifest["sources"][p]:
            bad.append(p)
    for name, h in manifest["data_files"].items():
        f = C.DATA_DIR / name
        if (name.split("/")[0] in tracks) and (not f.exists() or C.file_sha256(f) != h):
            bad.append(f"data/{name}")
    return bad


def select(manifest: dict, track=None, split=None) -> list:
    out = [t for t in manifest["tasks"] if (not track or t["track"] == track) and (not split or split == "all" or t["split"] == split)]
    return out


def public(task: dict) -> dict:
    return {k: task[k] for k in PUBLIC_FIELDS}


def task_by_id(manifest: dict, task_id: str) -> dict:
    for t in manifest["tasks"]:
        if t["task_id"] == task_id:
            return t
    raise KeyError(task_id)


# ---------------------------------------------------------------- scoring
def score_task(task: dict, artifact) -> dict:
    mod = TRACK_MODULES[task["track"]]
    raw = C.read_artifact(artifact)
    try:
        return mod.score(task, raw)
    except Exception as exc:  # scorer failures are reported, never crash a run
        return {"task_id": task["task_id"], "track": task["track"], "score": 0.0, "passed": False, "checks": {},
                "error": f"scorer error {type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------- agents
def agent_text(task: dict, kind: str) -> bytes:
    spec = task["private"][kind]
    if "path" in spec:
        return C.abspath(spec["path"]).read_bytes()
    return spec["text"].encode("utf-8")


def inlined_prompt(task: dict) -> str:
    """Prompt plus the content of generated input files (those under data/); sources stay referenced by path."""
    text = task["prompt"]
    for name, rel in task["inputs"].items():
        p = C.abspath(rel)
        if C.DATA_DIR in p.parents and p.exists():
            text += f"\n\n--- input `{name}` ---\n{p.read_text(encoding='utf-8')}"
    return text


def openai_call(base_url: str, model: str, task: dict, seed: int) -> str:
    base = base_url.rstrip("/")
    url = base + ("/chat/completions" if base.endswith("/v1") else "/v1/chat/completions")
    body = {"model": model, "temperature": 0, "max_tokens": task["budget_tokens"], "seed": seed,
            "messages": [{"role": "user", "content": inlined_prompt(task)}]}
    headers = {"Content-Type": "application/json"}
    import os
    if os.environ.get("OPENAI_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["OPENAI_API_KEY"]
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=1800) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"].get("content") or ""


def produce_artifact(agent: str, task: dict, path: Path, seed: int) -> str | None:
    """Write the agent's artifact; returns an error string when the agent itself failed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if agent == "baseline:null":
        path.write_bytes(b"")
    elif agent == "baseline:oracle":
        path.write_bytes(agent_text(task, "oracle"))
    elif agent == "baseline:identity":
        path.write_bytes(agent_text(task, "identity"))
    elif agent.startswith("openai:"):
        base, _, model = agent[len("openai:"):].partition("#")
        try:
            path.write_text(openai_call(base, model, task, seed), encoding="utf-8")
        except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
            path.write_bytes(b"")
            return f"agent error {type(exc).__name__}: {exc}"
    else:
        raise SystemExit(f"unknown agent: {agent}")
    return None


def summarize(track: str, agent: str, rows: list, manifest: dict) -> dict:
    sums: dict = {}
    counts: dict = {}
    for r in rows:
        for k, v in r["checks"].items():
            if isinstance(v, (bool, int, float)):
                sums[k] = sums.get(k, 0.0) + float(v)
                counts[k] = counts.get(k, 0) + 1
    live = {p: C.file_sha256(C.abspath(p)) for p in manifest["track_sources"][track] if C.abspath(p).exists()}
    return {
        "track": track, "agent": agent, "n": len(rows),
        "mean_score": round(C.mean(r["score"] for r in rows), 4),
        "pass_rate": round(C.mean(1.0 if r["passed"] else 0.0 for r in rows), 4),
        "per_check_means": {k: round(sums[k] / counts[k], 4) for k in sorted(sums)},
        "source_hashes": live,
        "sources_match_manifest": all(manifest["sources"].get(p) == h for p, h in live.items())
        and len(live) == len(manifest["track_sources"][track]),
    }


def run_track(track, agent, out_dir: Path, manifest, limit=None, seed=C.SEED, split="dev") -> dict:
    tasks = select(manifest, track, split)
    if limit is not None and limit < len(tasks):
        picked = random.Random(seed).sample(range(len(tasks)), limit)
        tasks = [tasks[i] for i in sorted(picked)]
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    with (out_dir / "results.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for t in tasks:
            art = out_dir / "artifacts" / (t["task_id"] + ".artifact")
            t0 = time.time()
            agent_err = produce_artifact(agent, t, art, seed)
            res = score_task(t, art)
            if agent_err:
                res["error"] = agent_err
            res.update({"agent": agent, "split": t["split"], "seconds": round(time.time() - t0, 2)})
            rows.append(res)
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            fh.flush()
    summary = summarize(track, agent, rows, manifest)
    summary["split"] = split
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    return summary


# ---------------------------------------------------------------- commands
def cmd_tasks(a) -> int:
    manifest = load_manifest()
    bad = verify(manifest, [a.track] if a.track else C.TRACKS)
    if bad:
        print(f"warning: {len(bad)} source file(s) differ from the frozen manifest: {bad[:3]}", file=sys.stderr)
    for t in select(manifest, a.track, a.split):
        sys.stdout.write(json.dumps(public(t), ensure_ascii=False) + "\n")
    return 0


def cmd_score(a) -> int:
    manifest = load_manifest()
    try:
        task = task_by_id(manifest, a.task)
    except KeyError:
        print(json.dumps({"task_id": a.task, "track": None, "score": 0.0, "passed": False, "checks": {},
                          "error": "unknown task_id"}))
        return 2
    print(json.dumps(score_task(task, a.artifact), ensure_ascii=False))
    return 0


def cmd_run(a) -> int:
    manifest = load_manifest()
    if a.split != "dev" and a.agent.startswith("openai:") and not a.confirm_one_shot:
        raise SystemExit("the test split is for one-shot reporting only: pass --confirm-one-shot to run a model on it")
    summary = run_track(a.track, a.agent, Path(a.out), manifest, a.limit, a.seed, a.split)
    print(json.dumps({k: v for k, v in summary.items() if k != "source_hashes"}, indent=1))
    return 0


def cmd_selftest(a) -> int:
    manifest = load_manifest()
    problems = []
    bad = verify(manifest)
    if bad:
        problems.append(f"source hash mismatch: {bad[:5]}")
    fresh, _ = generate_all()
    if json.dumps(fresh, sort_keys=True) != json.dumps(manifest, sort_keys=True):
        problems.append("regenerated manifest differs from manifest.json (run freeze if the sources changed on purpose)")
    for t in manifest["tasks"]:
        if t["split"] != C.split_of(t["task_id"]):
            problems.append(f"split drift for {t['task_id']}")
    tmp = Path(tempfile.mkdtemp(prefix="swbench_selftest_"))
    try:
        print(f"{'track':<11}{'agent':<16}{'n':>3}{'mean':>8}{'pass':>7}")
        for track in C.TRACKS:
            for agent in ("baseline:null", "baseline:oracle"):
                s = run_track(track, agent, tmp / track / agent.split(":")[1], manifest, split="all")
                print(f"{track:<11}{agent:<16}{s['n']:>3}{s['mean_score']:>8.3f}{s['pass_rate']:>7.2f}")
                if agent.endswith("oracle") and (s["mean_score"] < ORACLE_BAR or s["pass_rate"] < ORACLE_BAR):
                    problems.append(f"{track}: oracle below bar ({s['mean_score']}, pass {s['pass_rate']})")
                if agent.endswith("null") and s["mean_score"] > NULL_CEILING:
                    problems.append(f"{track}: null above {NULL_CEILING} ({s['mean_score']})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if problems:
        print("SELFTEST FAILED")
        for p in problems:
            print(" -", p)
        return 1
    print("SELFTEST OK")
    return 0


def cmd_freeze(a) -> int:
    m = freeze()
    print(f"froze {len(m['tasks'])} tasks, {len(m['sources'])} sources, {len(m['data_files'])} data files")
    return 0


def cmd_verify(a) -> int:
    bad = verify(load_manifest())
    print("sources match manifest" if not bad else f"MISMATCH: {bad}")
    return 1 if bad else 0


def cmd_upstream(a) -> int:
    ok, out = hypergames.upstream_receipt_check()
    print(("ok: " if ok else "FAILED: ") + out)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="storyworld_bench", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("tasks", help="print tasks as JSONL")
    p.add_argument("--track", choices=C.TRACKS)
    p.add_argument("--split", choices=("dev", "test"))
    p.set_defaults(fn=cmd_tasks)
    p = sub.add_parser("score", help="score one artifact")
    p.add_argument("--task", required=True)
    p.add_argument("--artifact", required=True)
    p.set_defaults(fn=cmd_score)
    p = sub.add_parser("run", help="run an agent over a track")
    p.add_argument("--track", required=True, choices=C.TRACKS)
    p.add_argument("--agent", required=True, help="baseline:null | baseline:oracle | baseline:identity | openai:<base_url>#<model>")
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int)
    p.add_argument("--seed", type=int, default=C.SEED)
    p.add_argument("--split", choices=("dev", "test", "all"), default="dev")
    p.add_argument("--confirm-one-shot", action="store_true")
    p.set_defaults(fn=cmd_run)
    for name, fn, h in (("selftest", cmd_selftest, "null and oracle baselines on every track"),
                        ("freeze", cmd_freeze, "regenerate data/ and manifest.json"),
                        ("verify", cmd_verify, "check source hashes against manifest.json"),
                        ("upstream", cmd_upstream, "run the hypergames env's own receipt checker")):
        sub.add_parser(name, help=h).set_defaults(fn=fn)
    return ap


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = build_parser().parse_args(argv)
    return a.fn(a)

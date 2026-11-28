"""Hypergame eval families built on the Cairo hyperworld engine (codex-skills/hyperworld-builder).

Every item is a question about the exact Bayesian posterior over the engine's 1,024 hidden worlds, asked
from the public evidence trace only (no grader-only state reaches a prompt). Each evidence item reports
the parity of some binary factors through a binary symmetric channel; relays of an earlier source root
carry no new information. The grader recomputes the posterior from the public trace with the engine's
own ``update`` and checks it equals the engine's posterior, then derives:

- ``marginal``: P(factor = 1).
- ``parity``: P(factor_a XOR factor_b = 1), which moves while both marginals stay put.
- ``p2_alignment``: the engine's second-order belief 2 P(Z_a = Z_b) - 1 between two actors.
- ``fresh_count``: how many evidence items carry independent information.

The naive baseline counts every relay as fresh evidence. ``traps_only`` keeps the items whose naive
answer is wrong, so a family scores the duplicated-source failure directly.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from random import Random
from typing import Any

from .repo import HG_ENV, HYPERWORLD, Repo, StoryworldError, quiet, sha256_file

KINDS = ("marginal", "parity", "p2_alignment", "fresh_count")
SCHEMA = "storyworld-gdk/hypergame-family/0.1"
TOLERANCE = Fraction(1, 2000)
FAMILY_RE_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_-")


def parse_answer(raw: Any) -> Fraction | None:
    if isinstance(raw, dict):
        raw = raw.get("answer")
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, (int, float)):
        return Fraction(str(raw))
    text = str(raw).strip().rstrip("%")
    try:
        value = Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None
    return value / 100 if str(raw).strip().endswith("%") else value


def correct(kind: str, answer: Fraction | None, exact: Fraction) -> bool:
    if answer is None:
        return False
    if kind == "fresh_count":
        return answer == exact
    return abs(answer - exact) <= TOLERANCE


class Hypergames:
    def __init__(self, repo: Repo, work_dir: Path, *, read_only: bool):
        self.repo = repo
        self.evals = work_dir.resolve() / "evals"
        self.read_only = read_only

    def engine(self) -> Any:
        if not self.repo.has_hyperworld():
            raise StoryworldError("not_available", f"{HYPERWORLD.as_posix()} is not in this checkout")
        return self.repo.module("hyperworld_engine")

    def policies(self) -> list[str]:
        """The engine's scripted policies plus ``random`` (seeded uniform play over legal actions)."""
        self.engine()
        return sorted(self.repo.module("play_hyperworld").POLICIES) + ["random"]

    def chooser(self, family: str, seed: int, policy: str) -> Any:
        play = self.repo.module("play_hyperworld")
        if policy == "random":
            rng = Random(f"storyworld-gdk:{family}:{seed}")
            return lambda game: rng.choice(sorted(game.legal_actions()))
        return lambda game: play.choose_scripted(game, play.POLICIES[policy][game.turn])

    def family_dir(self, family: Any) -> Path:
        if not isinstance(family, str) or not family or set(family) - FAMILY_RE_CHARS or len(family) > 48:
            raise StoryworldError("bad_argument", "family is 1-48 chars of a-z, 0-9, _ and -")
        return self.evals / family

    # ---- engine replay ----

    def replay(self, seed: int, actions: list[str]) -> Any:
        hw = self.engine()
        game = hw.CairoHyperworld(int(seed))
        with quiet():
            for action in actions:
                if action not in game.legal_actions():
                    raise StoryworldError("illegal_action", f"turn {game.turn + 1}: {action!r} is not legal; "
                                          f"legal: {list(game.legal_actions())}")
                game.step(action)
        return game

    def view(self, seed: int, actions: list[str] | None = None) -> dict[str, Any]:
        game = self.replay(seed, list(actions or []))
        with quiet():
            view = game.view()
        keep = ("turn", "total_turns", "role", "posterior_entropy_bits", "factor_beliefs", "authority_index",
                "oversight_index", "choices", "unlock_conditions", "encounter", "ending")
        out = {k: view[k] for k in keep if k in view}
        out["seen_evidence"] = [{k: e[k] for k in ("turn", "speaker", "source_root", "factor_topics", "observed_parity",
                                                   "reliability_fraction", "counted_as_independent")}
                                for e in view.get("seen_evidence", [])]
        graph = view.get("belief_graph", {})
        out["belief_graph"] = {k: graph.get(k) for k in ("phase", "modeled_supporters", "snap_detected", "ever_snapped")}
        out["seed"] = int(seed)
        return out

    # ---- exact grading from the public trace ----

    def posteriors(self, events: list[Any]) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
        hw = self.engine()
        exact = naive = hw.prior()
        for event in events:
            naive = hw.update(naive, event.signal_mask, event.observed, event.reliability)
            if event.counted_as_independent:
                exact = hw.update(exact, event.signal_mask, event.observed, event.reliability)
        return exact, naive

    def _parity(self, posterior: tuple[Fraction, ...], a: int, b: int) -> Fraction:
        hw = self.engine()
        return sum((posterior[w] for w in hw.STATES if ((w >> a) ^ (w >> b)) & 1), Fraction(0))

    def _prompt(self, events: list[Any], question: str, answer_format: str) -> str:
        hw = self.engine()
        factors = "\n".join(f"- {fid}: {desc}" for fid, desc, _ in hw.FACTORS)
        rows = []
        for i, event in enumerate(events, 1):
            topics = [hw.FACTORS[j][0] for j in range(hw.WIDTH) if (event.signal_mask >> j) & 1]
            rows.append(f"{i}. turn {event.turn + 1}, speaker {event.speaker}, source_root {event.source_root}, "
                        f"factors [{', '.join(topics)}], reported parity {event.observed}, "
                        f"reliability {event.reliability}")
        return (
            "A fictional council scenario has ten hidden binary factors. Before any evidence, all 1,024 joint "
            "assignments are equally likely.\n\nFactors:\n" + factors + "\n\n"
            "Evidence model: each evidence item reports the parity (XOR) of the listed factors. The report equals "
            "the true parity with probability `reliability`, independently across distinct source roots. An item "
            "whose source_root already appeared earlier is a relay of that same report: it repeats the earlier "
            "reading and carries no new information.\n\nEvidence so far:\n" + "\n".join(rows) + "\n\n"
            f"Question: {question}\n\n{answer_format}"
        )

    def _items_for(self, family: str, seed: int, turn: int, game_events: list[Any], posterior: tuple[Fraction, ...],
                   kinds: list[str], traps_only: bool) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        hw = self.engine()
        events = list(game_events)
        exact, naive = self.posteriors(events)
        if exact != posterior:
            raise StoryworldError("grader_mismatch", f"seed {seed} turn {turn}: public-trace posterior differs from the engine")
        topics = sorted({j for e in events for j in range(hw.WIDTH) if (e.signal_mask >> j) & 1})
        prob = 'Reply with JSON only: {"answer": "<exact fraction p/q, or a decimal to 4 places>"}'
        out = []

        def add(kind: str, question: str, fmt: str, exact_v: Fraction, naive_v: Fraction, uniform_v: Fraction, extra: dict) -> None:
            if traps_only and correct(kind, naive_v, exact_v):
                return
            item_id = f"{family}:{seed}:{turn}:{kind}"
            out.append(({"id": item_id, "kind": kind, "prompt": self._prompt(events, question, fmt), "answer_format": fmt},
                        {"id": item_id, "kind": kind, "seed": seed, "turn": turn, "exact": str(exact_v),
                         "exact_float": float(exact_v), "naive": str(naive_v), "uniform": str(uniform_v), **extra}))

        # Targets: the largest relay-counting error first, then the factor most entangled in parity reports,
        # then the answer furthest from 1/2 (ties go to the lowest factor index).
        fresh_events = [e for e in events if e.counted_as_independent]
        overlap = {j: sum(1 for e in fresh_events if (e.signal_mask >> j) & 1) for j in topics}
        if "marginal" in kinds and topics:
            gaps = [(abs(hw.marginal(naive, j) - hw.marginal(exact, j)), overlap[j],
                     abs(hw.marginal(exact, j) - Fraction(1, 2)), -j) for j in topics]
            j = -max(gaps)[3]
            add("marginal", f"What is the exact posterior probability that {hw.FACTORS[j][0]} = 1?", prob,
                hw.marginal(exact, j), hw.marginal(naive, j), Fraction(1, 2), {"factor": hw.FACTORS[j][0]})
        pairs = [(a, b) for i, a in enumerate(topics) for b in topics[i + 1:]]
        if "parity" in kinds and pairs:
            scored = [(abs(self._parity(naive, a, b) - self._parity(exact, a, b)), overlap[a] + overlap[b],
                       abs(self._parity(exact, a, b) - Fraction(1, 2)), -a, -b) for a, b in pairs]
            *_, a, b = max(scored)
            a, b = -a, -b
            add("parity", f"What is the exact posterior probability that {hw.FACTORS[a][0]} XOR {hw.FACTORS[b][0]} = 1?",
                prob, self._parity(exact, a, b), self._parity(naive, a, b), Fraction(1, 2),
                {"factors": [hw.FACTORS[a][0], hw.FACTORS[b][0]]})
        actors = [(a, b) for a, b in pairs if hw.FACTORS[a][2] and hw.FACTORS[b][2]]
        if "p2_alignment" in kinds and actors:
            def p2(post: tuple[Fraction, ...], a: int, b: int) -> Fraction:
                return hw.alignment_p2(post, hw.FACTORS[a][2], hw.FACTORS[b][2])

            scored = [(abs(p2(naive, a, b) - p2(exact, a, b)), overlap[a] + overlap[b], abs(p2(exact, a, b)), -a, -b)
                      for a, b in actors]
            *_, a, b = max(scored)
            a, b = -a, -b
            ca, cb = hw.FACTORS[a][2], hw.FACTORS[b][2]
            question = (f"In this scenario's stipulated mind model, {ca} judges {cb} aligned exactly when their factors "
                        f"{hw.FACTORS[a][0]} and {hw.FACTORS[b][0]} are equal. The second-order belief score is "
                        f"2 * P({hw.FACTORS[a][0]} = {hw.FACTORS[b][0]}) - 1, in [-1, 1]. What is its exact value?")
            add("p2_alignment", question, 'Reply with JSON only: {"answer": "<exact fraction p/q, or a decimal to 4 places>"}',
                hw.alignment_p2(exact, ca, cb), hw.alignment_p2(naive, ca, cb), Fraction(0), {"actors": [ca, cb]})
        if "fresh_count" in kinds and events:
            fresh = Fraction(sum(1 for e in events if e.counted_as_independent))
            add("fresh_count", "How many of the evidence items above carry independent information?",
                'Reply with JSON only: {"answer": <integer>}', fresh, Fraction(len(events)), Fraction(len(events)), {})
        return out

    def _build(self, family: str, seeds: list[int], policy: str, turns: list[int], kinds: list[str],
               traps_only: bool, max_items: int) -> tuple[list[dict], list[dict]]:
        items, grader = [], []
        hw = self.engine()
        for seed in seeds:
            game = hw.CairoHyperworld(int(seed))
            choose = self.chooser(family, seed, policy)
            taken: list[str] = []
            for turn in range(1, max(turns) + 1):
                with quiet():
                    action = choose(game)
                    game.step(action)
                taken.append(action)
                if turn not in turns:
                    continue
                for item, grade in self._items_for(family, seed, turn, game.events, game._posterior, kinds, traps_only):
                    grade["actions"] = list(taken)
                    items.append(item)
                    grader.append(grade)
                    if len(items) >= max_items:
                        return items, grader
        return items, grader

    @staticmethod
    def baselines(grader: list[dict]) -> dict[str, float]:
        n = max(1, len(grader))
        out = {}
        for name in ("exact", "naive", "uniform"):
            hits = sum(correct(g["kind"], Fraction(g[name]), Fraction(g["exact"])) for g in grader)
            out["oracle" if name == "exact" else name] = round(hits / n, 4)
        return out

    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def _sources(self) -> dict[str, str]:
        base = self.repo.root / HYPERWORLD
        return {f"{HYPERWORLD.as_posix()}/{name}": sha256_file(base / name)
                for name in ("hyperworld_engine.py", "hyperworld_phase.py", "hyperworld_reaction_math.py", "play_hyperworld.py")
                if (base / name).is_file()}

    def _validate(self, policy: str, turns: list[int], kinds: list[str]) -> None:
        if policy not in self.policies():
            raise StoryworldError("bad_argument", f"policy is one of {sorted(self.policies())}")
        if not turns or any(not isinstance(t, int) or not 1 <= t <= 7 for t in turns):
            raise StoryworldError("bad_argument", "turns is a non-empty list of integers 1..7")
        if not kinds or set(kinds) - set(KINDS):
            raise StoryworldError("bad_argument", f"kinds is a non-empty subset of {list(KINDS)}")

    # ---- tools ----

    def status(self) -> dict[str, Any]:
        families = []
        for manifest in sorted(self.evals.glob("*/manifest.json")):
            data = json.loads(manifest.read_text(encoding="utf-8"))
            families.append({k: data.get(k) for k in ("family", "items", "accepted", "baselines", "frozen")})
        return {"hyperworld_engine": self.repo.has_hyperworld(), "hypergames_env": self.repo.has_hg_env(),
                "policies": sorted(self.policies()) if self.repo.has_hyperworld() else [],
                "kinds": list(KINDS), "families": families}

    def family_build(self, family: str, seeds: list[int], policy: str = "random", turns: list[int] | None = None,
                     kinds: list[str] | None = None, traps_only: bool = True, max_items: int = 120) -> dict[str, Any]:
        if self.read_only:
            raise StoryworldError("read_only", "this session is read-only (storyworld --approve write)")
        folder = self.family_dir(family)
        turns = sorted(set(turns or [4, 6, 7]))
        kinds = list(kinds or KINDS)
        self._validate(policy, turns, kinds)
        if not seeds or len(seeds) > 64 or any(not isinstance(s, int) or s < 0 for s in seeds):
            raise StoryworldError("bad_argument", "seeds is 1..64 non-negative integers (public dev seeds)")
        if (folder / "manifest.json").is_file() and json.loads((folder / "manifest.json").read_text(encoding="utf-8")).get("frozen"):
            raise StoryworldError("family_frozen", f"{family} is frozen; build a new family name")
        items, grader = self._build(family, list(seeds), policy, turns, kinds, bool(traps_only), int(max_items))
        base = self.baselines(grader)
        reasons = []
        if not items:
            reasons.append("no items (traps_only with no relays in this policy; try another policy or more turns)")
        if base.get("oracle") != 1.0:
            reasons.append("oracle below 1.0: the scorer and the grader disagree")
        if base.get("naive", 1.0) > 0.5:
            reasons.append("naive relay-counting baseline scores above 0.5")
        if base.get("uniform", 1.0) > 0.25:
            reasons.append("uniform-prior baseline scores above 0.25")
        by_kind: dict[str, int] = {}
        for item in items:
            by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + 1
        manifest = {"schema": SCHEMA, "family": family, "policy": policy, "turns": turns, "kinds": kinds,
                    "traps_only": bool(traps_only), "dev_seeds": list(seeds), "items": len(items), "by_kind": by_kind,
                    "baselines": base, "accepted": not reasons, "rejection_reasons": reasons,
                    "tolerance": str(TOLERANCE), "sources": self._sources(), "frozen": False}
        self._write_jsonl(folder / "items.jsonl", items)
        self._write_jsonl(folder / "grader.jsonl", grader)
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        sample = items[0]["prompt"] if items else ""
        return {**manifest, "folder": str(folder), "sample_prompt": sample}

    def _load_answers(self, answers: Any) -> dict[str, Any]:
        if isinstance(answers, list):
            return {str(row.get("id")): row.get("answer") for row in answers if isinstance(row, dict)}
        if isinstance(answers, str):
            path = Path(answers)
            if not path.is_absolute():
                path = self.repo.root / path
            self.repo.check_readable(path)
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            return {str(row.get("id")): row.get("answer") for row in rows}
        raise StoryworldError("bad_argument", "answers is a list of {id, answer} or a path to such a JSONL file")

    def family_score(self, family: str, answers: Any, split: str = "dev") -> dict[str, Any]:
        folder = self.family_dir(family)
        if split == "dev":
            grader_path = folder / "grader.jsonl"
        elif split == "heldout":
            location = folder / "heldout_location.json"
            if not location.is_file():
                raise StoryworldError("not_frozen", f"{family} has no held-out split (hyperworld_family_freeze)")
            grader_path = Path(json.loads(location.read_text(encoding="utf-8"))["dir"]) / "grader.jsonl"
        else:
            raise StoryworldError("bad_argument", "split is dev or heldout")
        if not grader_path.is_file():
            raise StoryworldError("unknown_family", f"no grader for {family} ({split})")
        grader = [json.loads(line) for line in grader_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        given = self._load_answers(answers)
        per_kind: dict[str, list[int]] = {}
        rows = []
        for grade in grader:
            answer = parse_answer(given.get(grade["id"]))
            ok = correct(grade["kind"], answer, Fraction(grade["exact"]))
            fell = answer is not None and correct(grade["kind"], answer, Fraction(grade["naive"])) and not ok
            per_kind.setdefault(grade["kind"], []).append(int(ok))
            rows.append({"id": grade["id"], "correct": ok, "answered": answer is not None, "naive_trap": fell})
        n = max(1, len(rows))
        return {"family": family, "split": split, "items": len(rows), "score": round(sum(r["correct"] for r in rows) / n, 4),
                "answered": sum(r["answered"] for r in rows), "naive_trap_rate": round(sum(r["naive_trap"] for r in rows) / n, 4),
                "per_kind": {k: round(sum(v) / len(v), 4) for k, v in per_kind.items()},
                "wrong": [r["id"] for r in rows if not r["correct"]][:40]}

    def family_freeze(self, family: str, heldout_dir: str, heldout_seeds: int = 16) -> dict[str, Any]:
        if self.read_only:
            raise StoryworldError("read_only", "this session is read-only (storyworld --approve write)")
        folder = self.family_dir(family)
        manifest_path = folder / "manifest.json"
        if not manifest_path.is_file():
            raise StoryworldError("unknown_family", f"no family {family}; hyperworld_family_build first")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("frozen"):
            raise StoryworldError("family_frozen", f"{family} is already frozen")
        if not manifest.get("accepted"):
            raise StoryworldError("not_accepted", f"{family} failed acceptance: {manifest.get('rejection_reasons')}")
        target = Path(heldout_dir)
        if not target.is_absolute():
            raise StoryworldError("bad_argument", "heldout_dir must be an absolute path outside the repository")
        target = target.resolve() / family
        try:
            target.relative_to(self.repo.root)
            raise StoryworldError("bad_argument", "heldout_dir must be outside the repository so held-out seeds never reach git")
        except ValueError:
            pass
        if not 1 <= int(heldout_seeds) <= 64:
            raise StoryworldError("bad_argument", "heldout_seeds 1..64")
        dev = set(manifest["dev_seeds"])
        seeds: list[int] = []
        while len(seeds) < int(heldout_seeds):
            seed = secrets.randbelow(2**31)
            if seed not in dev and seed not in seeds:
                seeds.append(seed)
        items, grader = self._build(family, seeds, manifest["policy"], manifest["turns"], manifest["kinds"],
                                    manifest["traps_only"], 10_000)
        target.mkdir(parents=True, exist_ok=True)
        (target / "seeds.json").write_text(json.dumps({"family": family, "seeds": seeds}) + "\n", encoding="utf-8", newline="\n")
        self._write_jsonl(target / "items.jsonl", items)
        self._write_jsonl(target / "grader.jsonl", grader)
        manifest["frozen"] = True
        manifest["heldout"] = {"items": len(items), "seeds": len(seeds), "seeds_sha256": sha256_file(target / "seeds.json"),
                               "items_sha256": sha256_file(target / "items.jsonl"),
                               "grader_sha256": sha256_file(target / "grader.jsonl"), "baselines": self.baselines(grader)}
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        (folder / "heldout_location.json").write_text(json.dumps({"dir": str(target)}) + "\n", encoding="utf-8", newline="\n")
        return {"family": family, "frozen": True, "heldout": manifest["heldout"], "heldout_dir": str(target)}

    def hg_selftest(self) -> dict[str, Any]:
        """The hypergames env's own unit tests and source-hashed receipt checks (CPU, stdlib)."""
        if not self.repo.has_hg_env():
            raise StoryworldError("not_available", f"{HG_ENV.as_posix()} is not in this checkout")
        env_dir = self.repo.root / HG_ENV
        env = {**os.environ, "PYTHONPATH": str(env_dir / "src"), "PYTHONIOENCODING": "utf-8"}
        out = {}
        for name, args in (("unit_tests", ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"]),
                           ("receipts", ["scripts/check_local_receipts.py"])):
            proc = subprocess.run([sys.executable, *args], cwd=env_dir, env=env, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-6:]
            out[name] = {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": tail}
        return {"ok": all(v["ok"] for v in out.values()), **out}

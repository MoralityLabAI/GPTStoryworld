"""The storyworld workspace: whole-world tools (builder mode) and one-encounter micro-edits (small mode).

A world is ``<work>/worlds/<name>/storyworld.json``. Every write goes through ``Workspace.commit``:
the candidate is checked with ``sweepweave_validator.validate_storyworld`` and refused when it adds a
validator error, the previous version is kept under ``.history/``, and the write is appended to the
world's ``ledger.jsonl``.
"""

from __future__ import annotations

import copy
import json
import random
import re
import shutil
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .repo import Repo, StoryworldError, estimate_tokens, quiet, sha256_json

WORLD_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
ENC_RE = re.compile(r"^page_[A-Za-z0-9_]{1,60}$")
MAX_IMPORT_BYTES = 16 * 1024 * 1024
# Top-level scalars world_set_fields may change; cast, spools and encounters have their own tools.
META_FIELDS = ("IFID", "about_text", "css_theme", "debug_mode", "display_mode", "creation_time", "modified_time",
               "storyworld_title", "storyworld_author", "sweepweave_version", "font_size", "language", "rating")
EXAMPLES = (
    "storyworlds/cairo_directorate_hyperworld/storyworld.json",
    "InkyWorlds/camelots-reckoning/storyworld.json",
)


def bool_const(value: bool = True) -> dict[str, Any]:
    return {"pointer_type": "Boolean Constant", "script_element_type": "Pointer", "value": bool(value)}


def num_const(value: float) -> dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": float(value)}


def str_const(text: str) -> dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": str(text)}


def num_ptr(character: str, prop: str, coefficient: float = 1.0) -> dict[str, Any]:
    return {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer", "character": character,
            "keyring": [prop], "coefficient": float(coefficient)}


def nudge(character: str, prop: str, delta: float) -> dict[str, Any]:
    target = num_ptr(character, prop)
    return {"effect_type": "Bounded Number Effect", "Set": target,
            "to": {"script_element_type": "Operator", "operator_type": "Nudge", "operands": [target, num_const(delta)]}}


def masking_errors(errors: list[str]) -> list[str]:
    """Validator errors from its first stage (missing top-level keys, multiplayer turns). The validator stops after
    that stage, so later errors stay hidden until these are fixed."""
    return [e for e in errors if e.endswith(": missing") or e.startswith(("multiplayer:", "turns:"))]


def text_of(script: Any) -> str:
    if isinstance(script, dict):
        return str(script.get("value", ""))
    return "" if script is None else str(script)


class Workspace:
    def __init__(self, repo: Repo, work_dir: Path, *, card_budget: int, read_budget: int, read_only: bool):
        self.repo = repo
        self.work = work_dir.resolve()
        self.worlds = self.work / "worlds"
        self.card_budget = card_budget
        self.read_budget = read_budget
        self.read_only = read_only

    # ---- helpers ----

    def _name(self, world: Any) -> str:
        if not isinstance(world, str) or not WORLD_RE.match(world):
            raise StoryworldError("bad_argument", f"world must match {WORLD_RE.pattern}, got {world!r}")
        return world

    def path(self, world: str) -> Path:
        return self.worlds / self._name(world) / "storyworld.json"

    def load(self, world: str) -> dict[str, Any]:
        path = self.path(world)
        if not path.is_file():
            known = sorted(p.parent.name for p in self.worlds.glob("*/storyworld.json"))
            raise StoryworldError("unknown_world", f"no world {world!r}; worlds: {known or 'none'} (world_new or world_import)")
        return json.loads(path.read_text(encoding="utf-8-sig"))

    def errors_for(self, data: dict[str, Any], scratch: Path) -> list[str]:
        scratch.parent.mkdir(parents=True, exist_ok=True)
        scratch.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8", newline="\n")
        try:
            with quiet():
                return list(self.repo.module("sweepweave_validator").validate_storyworld(str(scratch)))
        finally:
            scratch.unlink(missing_ok=True)

    def errors(self, world: str) -> list[str]:
        with quiet():
            return list(self.repo.module("sweepweave_validator").validate_storyworld(str(self.path(world))))

    def require_write(self) -> None:
        if self.read_only:
            raise StoryworldError("read_only", "this session is read-only (storyworld --approve write)")

    def commit(self, world: str, data: dict[str, Any], op: str, detail: dict[str, Any], *, new: bool = False,
               baseline: list[str] | None = None) -> dict[str, Any]:
        """Validate and write ``data``; refuse when it adds validator errors. Returns validator status.

        A new world is judged against ``baseline`` (an import keeps the errors it arrived with). An edit that
        clears first-stage errors may reveal errors the validator had not reached yet; that counts as progress.
        """
        self.require_write()
        path = self.path(world)
        before = (baseline or []) if new else self.errors(world)
        after = self.errors_for(data, path.parent / ".pending.json")
        added = sorted(set(after) - set(before))
        if added and len(masking_errors(after)) < len(masking_errors(before)):
            added = []
        if added:
            raise StoryworldError("invalid_world", f"{op} refused, the world is unchanged; new validator errors: {added[:12]}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            history = path.parent / ".history"
            history.mkdir(exist_ok=True)
            index = len(list(history.glob("*.json"))) + 1
            shutil.copyfile(path, history / f"{index:04d}.json")
        data["modified_time"] = float(int(time.time()))
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "op": op, "detail": detail,
                 "valid": not after, "errors": len(after), "digest": sha256_json(data)[:16]}
        with (path.parent / "ledger.jsonl").open("a", encoding="utf-8", newline="\n") as ledger:
            ledger.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"world": world, "op": op, "valid": not after, "validator_errors": after[:12]}

    @staticmethod
    def encounter(data: dict[str, Any], encounter_id: Any) -> dict[str, Any]:
        for enc in data.get("encounters", []):
            if enc.get("id") == encounter_id:
                return enc
        raise StoryworldError("unknown_encounter", f"no encounter {encounter_id!r} (encounter_list shows ids)")

    @staticmethod
    def option(enc: dict[str, Any], option_id: Any) -> dict[str, Any]:
        for opt in enc.get("options", []) or []:
            if opt.get("id") == option_id:
                return opt
        ids = [o.get("id") for o in enc.get("options", []) or []]
        raise StoryworldError("unknown_option", f"{enc.get('id')} has no option {option_id!r}; options: {ids}")

    @staticmethod
    def reaction(opt: dict[str, Any], reaction_id: Any) -> dict[str, Any]:
        for rxn in opt.get("reactions", []) or []:
            if rxn.get("id") == reaction_id:
                return rxn
        ids = [r.get("id") for r in opt.get("reactions", []) or []]
        raise StoryworldError("unknown_reaction", f"{opt.get('id')} has no reaction {reaction_id!r}; reactions: {ids}")

    @staticmethod
    def props(data: dict[str, Any]) -> dict[str, list[str]]:
        return {c.get("id"): sorted((c.get("bnumber_properties") or {}).keys()) for c in data.get("characters", [])}

    # ---- whole-world tools ----

    def world_list(self) -> dict[str, Any]:
        worlds = []
        for path in sorted(self.worlds.glob("*/storyworld.json")):
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            worlds.append({"world": path.parent.name, "title": data.get("storyworld_title", ""),
                           "encounters": len(data.get("encounters", [])), "bytes": path.stat().st_size,
                           "valid": not self.errors(path.parent.name)})
        examples = [p for p in EXAMPLES if (self.repo.root / p).is_file()]
        for path in sorted(self.repo.root.glob("storyworlds/*/storyworld.json"))[:20]:
            rel = self.repo.rel(path)
            if rel not in examples:
                examples.append(rel)
        return {"work_dir": str(self.work), "worlds": worlds, "importable_examples": examples}

    def world_new(self, world: str, title: str, about: str, motif: str, target_encounters: int = 20,
                  endings: int = 4) -> dict[str, Any]:
        self.require_write()
        if self.path(world).exists():
            raise StoryworldError("world_exists", f"{world} exists; pick another name or edit it")
        if not 16 <= int(target_encounters) <= 80 or not 2 <= int(endings) <= 8:
            raise StoryworldError("bad_argument", "target_encounters 16..80 and endings 2..8")
        scratch = self.path(world).parent / ".seed.json"
        scratch.parent.mkdir(parents=True, exist_ok=True)
        try:
            with quiet():
                self.repo.module("fresh_storyworld_seed").build_world(
                    world.replace("-", "_"), scratch, int(target_encounters), title, about, motif, int(endings))
            data = json.loads(scratch.read_text(encoding="utf-8"))
        finally:
            scratch.unlink(missing_ok=True)
        status = self.commit(world, data, "world_new", {"title": title, "target_encounters": target_encounters,
                                                         "endings": endings}, new=True)
        return {**status, **self._counts(data)}

    def world_import(self, world: str, source: str) -> dict[str, Any]:
        self.require_write()
        if self.path(world).exists():
            raise StoryworldError("world_exists", f"{world} exists; pick another name")
        src = self.repo.inside(source)
        if not src.is_file() or src.suffix != ".json" or src.stat().st_size > MAX_IMPORT_BYTES:
            raise StoryworldError("bad_argument", f"{source}: needs an existing .json file up to {MAX_IMPORT_BYTES} bytes")
        data = json.loads(src.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or not isinstance(data.get("encounters"), list):
            raise StoryworldError("bad_argument", f"{source} is not a storyworld (no encounters list)")
        errors = self.errors_for(data, self.path(world).parent / ".pending.json")
        status = self.commit(world, data, "world_import", {"source": self.repo.rel(src)}, new=True, baseline=errors)
        return {**status, **self._counts(data)}

    def _counts(self, data: dict[str, Any]) -> dict[str, Any]:
        encs = data.get("encounters", [])
        options = [o for e in encs for o in e.get("options", []) or []]
        reactions = [r for o in options for r in o.get("reactions", []) or []]
        effects = [x for r in reactions for x in r.get("after_effects", []) or []]
        terminal = [e["id"] for e in encs if not e.get("options")]
        nonterminal = max(1, len(encs) - len(terminal))
        return {"encounters": len(encs), "terminal_encounters": len(terminal), "options": len(options),
                "reactions": len(reactions), "effects": len(effects),
                "options_per_nonterminal": round(len(options) / nonterminal, 3),
                "reactions_per_option": round(len(reactions) / max(1, len(options)), 3),
                "effects_per_reaction": round(len(effects) / max(1, len(reactions)), 3),
                "wild_consequences": sum(1 for r in reactions if r.get("consequence_id") == "wild")}

    def world_summary(self, world: str) -> dict[str, Any]:
        data = self.load(world)
        encs = data.get("encounters", [])
        swmd = self.repo.module("json_to_swmd")
        with quiet():
            full, mini = swmd.emit_full(data), swmd.emit_minified(data)
        return {"world": world, "title": data.get("storyworld_title", ""), "about": text_of(data.get("about_text")),
                **self._counts(data),
                "characters": [{"id": c.get("id"), "name": c.get("name"), "properties": p}
                               for c, p in zip(data.get("characters", []), self.props(data).values())],
                "spools": [{"id": s.get("id"), "encounters": len(s.get("encounters") or []),
                            "starts_active": bool(s.get("starts_active"))} for s in data.get("spools", [])],
                "endings": [e["id"] for e in encs if not e.get("options")],
                "tokens": {"json": estimate_tokens(json.dumps(data, ensure_ascii=False)),
                           "swmd": estimate_tokens(full), "swmd_min": estimate_tokens(mini)}}

    def world_validate(self, world: str) -> dict[str, Any]:
        self.load(world)
        errors = self.errors(world)
        return {"world": world, "valid": not errors, "error_count": len(errors), "errors": errors[:40]}

    def world_quality(self, world: str) -> dict[str, Any]:
        data = self.load(world)
        errors = self.errors(world)
        with quiet():
            report = self.repo.module("storyworld_quality_gate").evaluate_storyworld(data, errors)
        checks = report.get("checks", [])
        failed = [{"name": c.get("name"), "actual": c.get("actual"), "target": c.get("target")}
                  for c in checks if not c.get("pass")]
        return {"world": world, "pass": bool(report.get("pass")), "valid": not errors,
                "checks_passed": len(checks) - len(failed), "checks_total": len(checks), "failed": failed}

    def world_rehearse(self, world: str, runs: int = 300, seed: int = 42, max_steps: int = 80) -> dict[str, Any]:
        """Random-play rehearsal with wild routing (tools/probe_morality_batch_routing.run_episode)."""
        data = self.load(world)
        if not 1 <= int(runs) <= 5000 or not 5 <= int(max_steps) <= 400:
            raise StoryworldError("bad_argument", "runs 1..5000, max_steps 5..400")
        probe = self.repo.module("probe_morality_batch_routing")
        rng = random.Random(int(seed))
        ends: Counter[str] = Counter()
        turns = []
        with quiet():
            for _ in range(int(runs)):
                row = probe.run_episode(data, rng, int(max_steps))
                ends[row["end"]] += 1
                turns.append(row["turns"])
        terminal = [e["id"] for e in data.get("encounters", []) if not e.get("options")]
        reached = [t for t in terminal if ends.get(t)]
        secret = sum(n for k, n in ends.items() if k.startswith("page_secret_"))
        return {"world": world, "runs": int(runs), "seed": int(seed),
                "endings": {k: round(n / int(runs), 4) for k, n in ends.most_common()},
                "dead_end_rate": round(ends.get("DEAD_END", 0) / int(runs), 4),
                "timeout_rate": round(ends.get("TIMEOUT", 0) / int(runs), 4),
                "unreachable_endings": [t for t in terminal if t not in reached],
                "secret_ending_rate": round(secret / int(runs), 4),
                "mean_turns": round(sum(turns) / max(1, len(turns)), 2),
                "dominant_ending_share": round(max(ends.values()) / int(runs), 4) if ends else 0.0}

    def world_read(self, world: str, format: str = "swmd") -> dict[str, Any]:
        data = self.load(world)
        if format == "json":
            text = json.dumps(data, ensure_ascii=False)
        elif format in ("swmd", "swmd_min"):
            module = self.repo.module("json_to_swmd")
            with quiet():
                text = module.emit_full(data) if format == "swmd" else module.emit_minified(data)
        else:
            raise StoryworldError("bad_argument", "format is swmd, swmd_min or json")
        tokens = estimate_tokens(text)
        if tokens > self.read_budget:
            raise StoryworldError("budget_exceeded", f"{world} as {format} is ~{tokens} tokens; this session reads up to "
                                  f"{self.read_budget} (try swmd_min, or encounter_card one encounter at a time)")
        return {"world": world, "format": format, "tokens": tokens, "text": text}

    def world_export_swmd(self, world: str) -> dict[str, Any]:
        self.require_write()
        data = self.load(world)
        module = self.repo.module("json_to_swmd")
        with quiet():
            full, mini = module.emit_full(data), module.emit_minified(data)
        folder = self.path(world).parent
        (folder / "storyworld.swmd.md").write_text(full, encoding="utf-8", newline="\n")
        (folder / "storyworld.swmd.min.md").write_text(mini, encoding="utf-8", newline="\n")
        return {"world": world, "swmd": str(folder / "storyworld.swmd.md"), "swmd_tokens": estimate_tokens(full),
                "swmd_min": str(folder / "storyworld.swmd.min.md"), "swmd_min_tokens": estimate_tokens(mini)}

    def world_patch_swmd(self, world: str, swmd: str) -> dict[str, Any]:
        """Apply full SWMD-0 prose (titles, texts, option and reaction text, consequence targets)."""
        data = self.load(world)
        module = self.repo.module("swmd_patch_json")
        scratch = self.path(world).parent / ".patch.swmd.md"
        scratch.write_text(swmd, encoding="utf-8", newline="\n")
        try:
            with quiet():
                parsed = module.parse_swmd_full(scratch)
                patched, report = module.patch_world(data, parsed)
        finally:
            scratch.unlink(missing_ok=True)
        status = self.commit(world, patched, "world_patch_swmd", {"report": report})
        return {**status, "patch_report": report}

    def world_artistry_pass(self, world: str, gate_pct: float = 0.09) -> dict[str, Any]:
        data = self.load(world)
        if not 0.0 <= float(gate_pct) <= 0.3:
            raise StoryworldError("bad_argument", "gate_pct 0..0.3")
        with quiet():
            out = self.repo.module("apply_artistry_pass").apply_artistry(copy.deepcopy(data), gate_pct=float(gate_pct))
        status = self.commit(world, out, "world_artistry_pass", {"gate_pct": gate_pct})
        return {**status, **self._counts(out)}

    # ---- one-encounter tools ----

    def encounter_list(self, world: str, offset: int = 0, limit: int = 40) -> dict[str, Any]:
        data = self.load(world)
        encs = data.get("encounters", [])
        spools: dict[str, list[str]] = {}
        for spool in data.get("spools", []):
            for eid in spool.get("encounters") or []:
                spools.setdefault(eid, []).append(spool.get("id"))
        limit = max(1, min(int(limit), 80))
        rows = [{"id": e.get("id"), "title": e.get("title", ""), "options": len(e.get("options") or []),
                 "terminal": not e.get("options"), "spools": spools.get(e.get("id"), [])}
                for e in encs[int(offset):int(offset) + limit]]
        return {"world": world, "total": len(encs), "offset": int(offset), "encounters": rows}

    def encounter_card(self, world: str, encounter_id: str) -> dict[str, Any]:
        """One encounter, its neighbours and the cast, sized to the session's card budget."""
        data = self.load(world)
        enc = self.encounter(data, encounter_id)
        module = self.repo.module("json_to_swmd")
        titles = {e.get("id"): e.get("title", "") for e in data.get("encounters", [])}

        def options(with_scripts: bool) -> list[dict[str, Any]]:
            out = []
            for opt in enc.get("options") or []:
                row: dict[str, Any] = {"id": opt.get("id"), "text": text_of(opt.get("text_script")), "reactions": []}
                if with_scripts:
                    row["visible_if"] = module.expr(opt.get("visibility_script", True))
                for rxn in opt.get("reactions") or []:
                    item: dict[str, Any] = {"id": rxn.get("id"), "text": text_of(rxn.get("text_script")),
                                            "consequence": rxn.get("consequence_id")}
                    if with_scripts:
                        item["desirability"] = module.expr(rxn.get("desirability_script", 0))
                        item["effects"] = [module.effect_line(x) for x in rxn.get("after_effects") or []]
                    else:
                        item["effects"] = len(rxn.get("after_effects") or [])
                    row["reactions"].append(item)
                out.append(row)
            return out

        incoming = sorted({e.get("id") for e in data.get("encounters", []) for o in e.get("options") or []
                           for r in o.get("reactions") or [] if r.get("consequence_id") == encounter_id})
        outgoing = sorted({r.get("consequence_id") for o in enc.get("options") or [] for r in o.get("reactions") or []})
        card: dict[str, Any] = {
            "world": world, "encounter_id": encounter_id, "title": enc.get("title", ""),
            "text": text_of(enc.get("text_script")), "terminal": not enc.get("options"),
            "turn_window": [enc.get("earliest_turn", 0), enc.get("latest_turn", 0)],
            "spools": enc.get("connected_spools", []),
            "cast": self.props(data),
            "incoming": [{"id": i, "title": titles.get(i, "")} for i in incoming[:12]],
            "outgoing": [{"id": i, "title": titles.get(i, "wild routing")} for i in outgoing[:12]],
        }
        with quiet():
            card["options"] = options(True)
            tokens = estimate_tokens(json.dumps(card, ensure_ascii=False))
            if tokens > self.card_budget:
                card["options"] = options(False)
                card["scripts_omitted"] = True
                tokens = estimate_tokens(json.dumps(card, ensure_ascii=False))
        if tokens > self.card_budget:
            card["text"] = card["text"][: self.card_budget * 2] + " [truncated]"
            card["truncated"] = True
            tokens = estimate_tokens(json.dumps(card, ensure_ascii=False))
        card["card_tokens"] = tokens
        card["card_budget"] = self.card_budget
        return card

    def encounter_edit_text(self, world: str, encounter_id: str, title: str | None = None, text: str | None = None,
                            options: list[dict[str, Any]] | None = None,
                            reactions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        data = self.load(world)
        enc = self.encounter(data, encounter_id)
        changed = []
        if title is not None:
            enc["title"] = str(title)
            changed.append("title")
        if text is not None:
            enc["text_script"] = str_const(text)
            changed.append("text")
        for row in options or []:
            self.option(enc, row.get("option_id"))["text_script"] = str_const(row.get("text", ""))
            changed.append(row.get("option_id"))
        for row in reactions or []:
            opt = self.option(enc, row.get("option_id"))
            self.reaction(opt, row.get("reaction_id"))["text_script"] = str_const(row.get("text", ""))
            changed.append(row.get("reaction_id"))
        if not changed:
            raise StoryworldError("bad_argument", "nothing to change: give title, text, options or reactions")
        return {**self.commit(world, data, "encounter_edit_text", {"encounter": encounter_id, "changed": changed}),
                "changed": changed}

    def _consequence(self, data: dict[str, Any], target: Any) -> str:
        ids = {e.get("id") for e in data.get("encounters", [])}
        if target != "wild" and target not in ids:
            raise StoryworldError("unknown_encounter", f"consequence_id {target!r} is neither 'wild' nor an encounter id")
        return str(target)

    def _effects(self, data: dict[str, Any], rows: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        props = self.props(data)
        out = []
        for row in rows or []:
            char, prop, delta = row.get("character"), row.get("property"), row.get("delta")
            if char not in props or prop not in props[char]:
                raise StoryworldError("unknown_property", f"{char}.{prop} is not a cast property; cast: {props}")
            if not isinstance(delta, (int, float)) or not -1.0 <= float(delta) <= 1.0:
                raise StoryworldError("bad_argument", f"delta for {char}.{prop} must be a number in [-1, 1]")
            out.append(nudge(char, prop, float(delta)))
        return out

    def _desirability(self, data: dict[str, Any], spec: Any) -> dict[str, Any]:
        if spec is None:
            return num_const(0.5)
        if isinstance(spec, (int, float)):
            return num_const(float(spec))
        props = self.props(data)
        terms = []
        for term in spec.get("terms") or []:
            char, prop = term.get("character"), term.get("property")
            if char not in props or prop not in props[char]:
                raise StoryworldError("unknown_property", f"{char}.{prop} is not a cast property; cast: {props}")
            terms.append(num_ptr(char, prop, float(term.get("coefficient", 1.0))))
        terms.append(num_const(float(spec.get("constant", 0.0))))
        if len(terms) == 1:
            return terms[0]
        return {"script_element_type": "Operator", "operator_type": "Addition", "operands": terms}

    def _build_reactions(self, data: dict[str, Any], option_id: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            raise StoryworldError("bad_argument", "an option needs at least one reaction")
        out = []
        for index, row in enumerate(rows):
            out.append({"id": f"rxn_{option_id[4:]}_{index}", "graph_offset_x": 0, "graph_offset_y": 0,
                        "text_script": str_const(row.get("text", "")),
                        "consequence_id": self._consequence(data, row.get("consequence_id", "wild")),
                        "desirability_script": self._desirability(data, row.get("desirability")),
                        "after_effects": self._effects(data, row.get("effects"))})
        return out

    def _new_option(self, data: dict[str, Any], enc: dict[str, Any], text: str, reactions: list[dict[str, Any]]) -> dict[str, Any]:
        taken = {o.get("id") for e in data.get("encounters", []) for o in e.get("options") or []}
        index = len(enc.get("options") or [])
        while f"opt_{enc['id']}_{index}" in taken:
            index += 1
        option_id = f"opt_{enc['id']}_{index}"
        return {"id": option_id, "graph_offset_x": 0, "graph_offset_y": 0, "text_script": str_const(text),
                "visibility_script": bool_const(True), "performability_script": bool_const(True),
                "reactions": self._build_reactions(data, option_id, reactions)}

    def option_add(self, world: str, encounter_id: str, text: str, reactions: list[dict[str, Any]]) -> dict[str, Any]:
        data = self.load(world)
        enc = self.encounter(data, encounter_id)
        option = self._new_option(data, enc, text, reactions)
        enc.setdefault("options", []).append(option)
        status = self.commit(world, data, "option_add", {"encounter": encounter_id, "option": option["id"]})
        return {**status, "option_id": option["id"], "reaction_ids": [r["id"] for r in option["reactions"]]}

    def reaction_set(self, world: str, encounter_id: str, option_id: str, reaction_id: str,
                     consequence_id: str | None = None, add_effects: list[dict[str, Any]] | None = None,
                     clear_effects: bool = False, desirability: Any = None) -> dict[str, Any]:
        data = self.load(world)
        rxn = self.reaction(self.option(self.encounter(data, encounter_id), option_id), reaction_id)
        if consequence_id is not None:
            rxn["consequence_id"] = self._consequence(data, consequence_id)
        if clear_effects:
            rxn["after_effects"] = []
        if add_effects:
            rxn.setdefault("after_effects", []).extend(self._effects(data, add_effects))
        if desirability is not None:
            rxn["desirability_script"] = self._desirability(data, desirability)
        status = self.commit(world, data, "reaction_set", {"encounter": encounter_id, "reaction": reaction_id})
        return {**status, "effects": len(rxn.get("after_effects") or [])}

    def encounter_add(self, world: str, encounter_id: str, title: str, text: str, spool_id: str,
                      options: list[dict[str, Any]] | None = None, earliest_turn: int = 0,
                      latest_turn: int = 999) -> dict[str, Any]:
        data = self.load(world)
        if not isinstance(encounter_id, str) or not ENC_RE.match(encounter_id):
            raise StoryworldError("bad_argument", f"encounter_id must match {ENC_RE.pattern}")
        if any(e.get("id") == encounter_id for e in data.get("encounters", [])):
            raise StoryworldError("encounter_exists", f"{encounter_id} exists; edit it instead")
        spool = next((s for s in data.get("spools", []) if s.get("id") == spool_id), None)
        if spool is None:
            raise StoryworldError("unknown_spool", f"no spool {spool_id!r}; spools: {[s.get('id') for s in data.get('spools', [])]}")
        now = float(int(time.time()))
        enc = {"id": encounter_id, "title": str(title), "creation_index": len(data["encounters"]),
               "creation_time": now, "modified_time": now, "connected_spools": [spool_id],
               "earliest_turn": int(earliest_turn), "latest_turn": int(latest_turn),
               "graph_position_x": 0, "graph_position_y": 0, "text_script": str_const(text),
               "acceptability_script": bool_const(True), "desirability_script": num_const(0.0), "options": []}
        data["encounters"].append(enc)
        for row in options or []:
            enc["options"].append(self._new_option(data, enc, row.get("text", ""), row.get("reactions") or []))
        spool.setdefault("encounters", []).append(encounter_id)
        status = self.commit(world, data, "encounter_add", {"encounter": encounter_id, "spool": spool_id})
        return {**status, "encounter_id": encounter_id, "terminal": not enc["options"],
                "option_ids": [o["id"] for o in enc["options"]]}

    # ---- structure: metadata, spools, cast ----

    def world_set_fields(self, world: str, fields: dict[str, Any]) -> dict[str, Any]:
        data = self.load(world)
        unknown = sorted(set(fields) - set(META_FIELDS))
        if not fields or unknown:
            raise StoryworldError("bad_argument", f"fields must be a non-empty subset of {list(META_FIELDS)}; unknown: {unknown}")
        for key, value in fields.items():
            if isinstance(value, (dict, list)):
                raise StoryworldError("bad_argument", f"{key} takes a string, number or boolean")
            data[key] = value
        return self.commit(world, data, "world_set_fields", {"fields": sorted(fields)})

    def spool_set(self, world: str, spool_id: str, encounters: list[str] | None = None,
                  starts_active: bool | None = None, create: bool = False) -> dict[str, Any]:
        data = self.load(world)
        spools = data.setdefault("spools", [])
        spool = next((x for x in spools if x.get("id") == spool_id), None)
        if spool is None:
            if not create:
                raise StoryworldError("unknown_spool", f"no spool {spool_id!r}; spools: {[x.get('id') for x in spools]} "
                                      "(create: true adds one)")
            now = float(int(time.time()))
            spool = {"id": spool_id, "spool_type": "General", "spool_name": spool_id, "starts_active": False,
                     "creation_index": len(spools), "creation_time": now, "modified_time": now, "encounters": []}
            spools.append(spool)
        if encounters is not None:
            ids = {e.get("id") for e in data.get("encounters", [])}
            missing = [e for e in encounters if e not in ids]
            if missing:
                raise StoryworldError("unknown_encounter", f"not encounter ids: {missing[:12]}")
            spool["encounters"] = list(encounters)
            for enc in data.get("encounters", []):
                linked = enc.setdefault("connected_spools", [])
                if enc.get("id") in encounters and spool_id not in linked:
                    linked.append(spool_id)
                elif enc.get("id") not in encounters and spool_id in linked:
                    linked.remove(spool_id)
        if starts_active is not None:
            spool["starts_active"] = bool(starts_active)
        status = self.commit(world, data, "spool_set", {"spool": spool_id, "encounters": encounters is not None,
                                                         "starts_active": starts_active})
        return {**status, "spool": {"id": spool_id, "encounters": len(spool.get("encounters") or []),
                                    "starts_active": bool(spool.get("starts_active"))}}

    def character_add(self, world: str, character_id: str, name: str, properties: list[str],
                      description: str = "") -> dict[str, Any]:
        data = self.load(world)
        if not re.match(r"^char_[a-z0-9_]{1,40}$", str(character_id)):
            raise StoryworldError("bad_argument", "character_id must match ^char_[a-z0-9_]{1,40}$")
        if any(c.get("id") == character_id for c in data.get("characters", [])):
            raise StoryworldError("character_exists", f"{character_id} exists")
        if not properties or any(not re.match(r"^[A-Za-z][A-Za-z0-9_]{0,40}$", str(x)) for x in properties):
            raise StoryworldError("bad_argument", "properties: 1+ names of letters, digits and _")
        now = float(int(time.time()))
        data.setdefault("characters", []).append({
            "creation_index": len(data["characters"]), "creation_time": now, "id": character_id, "modified_time": now,
            "name": str(name), "pronoun": "they", "description": str(description),
            "bnumber_properties": {prop: 0 for prop in properties}, "string_properties": {}, "list_properties": {}})
        authored = data.setdefault("authored_properties", [])
        known = {a.get("id") for a in authored}
        for prop in properties:
            if prop not in known:
                authored.append({"id": prop, "property_name": prop, "property_type": "bounded number", "default_value": 0,
                                 "depth": 0, "attribution_target": "all cast members", "affected_characters": [],
                                 "creation_index": len(authored), "creation_time": now, "modified_time": now})
        status = self.commit(world, data, "character_add", {"character": character_id, "properties": properties})
        return {**status, "characters": len(data["characters"])}

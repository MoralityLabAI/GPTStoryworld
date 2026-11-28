"""MCP stdio server for the Storyworld GDK app (newline-delimited JSON-RPC 2.0, MCP 2025-06-18).

    python -m storyworld_mcp.server --root GPTSTORYWORLD [--work DIR] [--mode builder|small|hypergames|all]
        [--card-budget TOKENS] [--read-budget TOKENS] [--read-only] [--deny PATH]...

``--mode`` decides which tools are listed: small mode never lists whole-world reads, so a low-context
model cannot pull a world into its window. Stdout carries protocol frames only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import IO, Any, Callable

from . import VERSION
from .hypergames import KINDS, Hypergames
from .repo import Repo, StoryworldError
from .worlds import Workspace

PROTOCOL = "2025-06-18"
MODES = ("builder", "small", "hypergames", "all")
INSTRUCTIONS = {
    "builder": "Storyworld builder tools (large context). Read a whole world with world_read (SWMD is the compact "
               "authoring view), change it with world_patch_swmd, the encounter tools or world_artistry_pass, and "
               "check it with world_validate, world_quality and world_rehearse. Every write is validated with "
               "sweepweave_validator and refused, with the world unchanged, when it adds a validator error.",
    "small": "Small-storyworld tools (low context). Work one encounter at a time: encounter_list, then encounter_card "
             "for the encounter you edit, then one micro-edit (encounter_edit_text, option_add, reaction_set, "
             "encounter_add). Cards are sized to the session's packet budget. Every write is validated and refused, "
             "with the world unchanged, when it adds a validator error; read the error code and fix the call.",
    "hypergames": "Hypergame eval tools. hyperworld_view replays the Cairo hyperworld engine from a seed and actions. "
                  "hyperworld_family_build turns seeded engine traces into exact-graded posterior questions and reports "
                  "oracle, naive (relay-counting) and uniform baselines; a family is accepted only when the oracle "
                  "scores 1.0 and both baselines stay low. hyperworld_family_freeze draws held-out seeds outside the "
                  "repository and records only their hashes. Never state a score a tool did not return.",
}
INSTRUCTIONS["all"] = " ".join(INSTRUCTIONS[m] for m in ("builder", "small", "hypergames"))

WORLD = {"type": "string", "description": "World name in the workspace (a-z, 0-9, _ and -)."}
ENC = {"type": "string", "description": "Encounter id, e.g. page_scene_03."}
EFFECTS = {"type": "array", "description": "Nudges applied when the reaction fires.",
           "items": {"type": "object", "additionalProperties": False, "required": ["character", "property", "delta"],
                     "properties": {"character": {"type": "string"}, "property": {"type": "string"},
                                    "delta": {"type": "number", "minimum": -1, "maximum": 1}}}}
DESIRABILITY = {"description": "A number, or {constant, terms: [{character, property, coefficient}]} (linear in cast properties).",
                "anyOf": [{"type": "number"},
                          {"type": "object", "additionalProperties": False,
                           "properties": {"constant": {"type": "number"},
                                          "terms": {"type": "array", "items": {
                                              "type": "object", "additionalProperties": False,
                                              "required": ["character", "property", "coefficient"],
                                              "properties": {"character": {"type": "string"}, "property": {"type": "string"},
                                                             "coefficient": {"type": "number"}}}}}}]}
REACTIONS = {"type": "array", "minItems": 1, "items": {
    "type": "object", "additionalProperties": False, "required": ["text", "consequence_id"],
    "properties": {"text": {"type": "string"},
                   "consequence_id": {"type": "string", "description": "An encounter id, or 'wild' for engine routing."},
                   "effects": EFFECTS, "desirability": DESIRABILITY}}}
OPTIONS = {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["text", "reactions"],
                                      "properties": {"text": {"type": "string"}, "reactions": REACTIONS}}}


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required or [], "additionalProperties": False}


class Tool:
    def __init__(self, name: str, description: str, input_schema: dict[str, Any], handler: Callable[..., dict],
                 *, read_only: bool, modes: tuple[str, ...]):
        self.name, self.description, self.schema = name, description, input_schema
        self.handler, self.read_only, self.modes = handler, read_only, modes

    def listing(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "inputSchema": self.schema,
                "annotations": {"readOnlyHint": self.read_only}}


class Service:
    def __init__(self, root: Path, work: Path, mode: str, card_budget: int, read_budget: int, read_only: bool,
                 deny: list[str] | None = None):
        self.repo = Repo(root, deny)
        self.mode = mode
        self.read_only = read_only
        self.ws = Workspace(self.repo, work, card_budget=card_budget, read_budget=read_budget, read_only=read_only)
        self.hg = Hypergames(self.repo, work, read_only=read_only)
        self.registry = self._registry()

    def _registry(self) -> list[Tool]:
        ws, hg = self.ws, self.hg
        both = ("builder", "small", "all")
        builder = ("builder", "all")
        hyper = ("hypergames", "all")
        tools = [
            Tool("world_list", "List workspace worlds and importable example worlds from the repository.",
                 schema({}), ws.world_list, read_only=True, modes=("builder", "small", "hypergames", "all")),
            Tool("world_new", "Create a fresh valid seed world (fresh_storyworld_seed.py): spools, cast, wild routing, endings.",
                 schema({"world": WORLD, "title": {"type": "string"}, "about": {"type": "string"}, "motif": {"type": "string"},
                         "target_encounters": {"type": "integer", "minimum": 16, "maximum": 80},
                         "endings": {"type": "integer", "minimum": 2, "maximum": 8}},
                        ["world", "title", "about", "motif"]), ws.world_new, read_only=False, modes=both),
            Tool("world_import", "Copy a storyworld JSON from the repository into the workspace under a new name; a world with "
                 "validator errors is imported as it is (valid: false) so it can be repaired.",
                 schema({"world": WORLD, "source": {"type": "string", "description": "Repository-relative path to a storyworld .json."}},
                        ["world", "source"]), ws.world_import, read_only=False, modes=both),
            Tool("world_summary", "Counts, cast and properties, spools, endings and token sizes of a world.",
                 schema({"world": WORLD}, ["world"]), ws.world_summary, read_only=True, modes=both),
            Tool("world_validate", "Run sweepweave_validator on a world.", schema({"world": WORLD}, ["world"]),
                 ws.world_validate, read_only=True, modes=both),
            Tool("world_quality", "Run storyworld_quality_gate (strict thresholds) and list the failed checks.",
                 schema({"world": WORLD}, ["world"]), ws.world_quality, read_only=True, modes=both),
            Tool("world_rehearse", "Random-play rehearsal with wild routing: ending distribution, dead ends, unreachable endings.",
                 schema({"world": WORLD, "runs": {"type": "integer", "minimum": 1, "maximum": 5000},
                         "seed": {"type": "integer"}, "max_steps": {"type": "integer", "minimum": 5, "maximum": 400}},
                        ["world"]), ws.world_rehearse, read_only=True, modes=both),
            Tool("world_read", "Read a whole world as SWMD (default), SWMD-min or JSON, up to the session's read budget.",
                 schema({"world": WORLD, "format": {"type": "string", "enum": ["swmd", "swmd_min", "json"]}}, ["world"]),
                 ws.world_read, read_only=True, modes=builder),
            Tool("world_export_swmd", "Write storyworld.swmd.md and storyworld.swmd.min.md next to the world.",
                 schema({"world": WORLD}, ["world"]), ws.world_export_swmd, read_only=False, modes=builder),
            Tool("world_patch_swmd", "Apply full SWMD-0 text (encounter titles and text, option and reaction text, consequence "
                 "targets) to the world; formulas and effects are kept.",
                 schema({"world": WORLD, "swmd": {"type": "string", "description": "Full SWMD-0 markdown (world_read format swmd)."}},
                        ["world", "swmd"]), ws.world_patch_swmd, read_only=False, modes=builder),
            Tool("world_artistry_pass", "Run apply_artistry_pass: desirability formulas, effects and late visibility gates.",
                 schema({"world": WORLD, "gate_pct": {"type": "number", "minimum": 0, "maximum": 0.3}}, ["world"]),
                 ws.world_artistry_pass, read_only=False, modes=builder),
            Tool("encounter_list", "List encounters (id, title, option count, terminal, spools), paginated.",
                 schema({"world": WORLD, "offset": {"type": "integer", "minimum": 0},
                         "limit": {"type": "integer", "minimum": 1, "maximum": 80}}, ["world"]),
                 ws.encounter_list, read_only=True, modes=both),
            Tool("encounter_card", "One encounter with its options, reactions, effects, neighbours and cast, within the card budget.",
                 schema({"world": WORLD, "encounter_id": ENC}, ["world", "encounter_id"]),
                 ws.encounter_card, read_only=True, modes=both),
            Tool("encounter_edit_text", "Rewrite an encounter's title or text, or option and reaction text, by id.",
                 schema({"world": WORLD, "encounter_id": ENC, "title": {"type": "string"}, "text": {"type": "string"},
                         "options": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                                "required": ["option_id", "text"],
                                                                "properties": {"option_id": {"type": "string"}, "text": {"type": "string"}}}},
                         "reactions": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                                  "required": ["option_id", "reaction_id", "text"],
                                                                  "properties": {"option_id": {"type": "string"},
                                                                                 "reaction_id": {"type": "string"},
                                                                                 "text": {"type": "string"}}}}},
                        ["world", "encounter_id"]), ws.encounter_edit_text, read_only=False, modes=both),
            Tool("option_add", "Add an option with its reactions (text, consequence, effects, desirability) to an encounter.",
                 schema({"world": WORLD, "encounter_id": ENC, "text": {"type": "string"}, "reactions": REACTIONS},
                        ["world", "encounter_id", "text", "reactions"]), ws.option_add, read_only=False, modes=both),
            Tool("reaction_set", "Change one reaction: consequence, added effects, cleared effects or desirability.",
                 schema({"world": WORLD, "encounter_id": ENC, "option_id": {"type": "string"}, "reaction_id": {"type": "string"},
                         "consequence_id": {"type": "string"}, "add_effects": EFFECTS, "clear_effects": {"type": "boolean"},
                         "desirability": DESIRABILITY}, ["world", "encounter_id", "option_id", "reaction_id"]),
                 ws.reaction_set, read_only=False, modes=both),
            Tool("encounter_add", "Add an encounter to a spool; with no options it is a terminal ending.",
                 schema({"world": WORLD, "encounter_id": ENC, "title": {"type": "string"}, "text": {"type": "string"},
                         "spool_id": {"type": "string"}, "options": OPTIONS,
                         "earliest_turn": {"type": "integer", "minimum": 0}, "latest_turn": {"type": "integer", "minimum": 0}},
                        ["world", "encounter_id", "title", "text", "spool_id"]), ws.encounter_add, read_only=False, modes=both),
            Tool("world_set_fields", "Set top-level metadata fields (IFID, about_text, css_theme, titles, modes, times).",
                 schema({"world": WORLD, "fields": {"type": "object", "description": "Field name to a string, number or boolean.",
                                                    "additionalProperties": {"type": ["string", "number", "boolean"]}}},
                        ["world", "fields"]), ws.world_set_fields, read_only=False, modes=both),
            Tool("spool_set", "Set a spool's encounter list (in play order) or starts_active; create: true adds a new spool.",
                 schema({"world": WORLD, "spool_id": {"type": "string"},
                         "encounters": {"type": "array", "items": {"type": "string"}},
                         "starts_active": {"type": "boolean"}, "create": {"type": "boolean"}},
                        ["world", "spool_id"]), ws.spool_set, read_only=False, modes=both),
            Tool("character_add", "Add a cast member with bounded-number properties (each starts at 0).",
                 schema({"world": WORLD, "character_id": {"type": "string", "description": "char_<name>"},
                         "name": {"type": "string"}, "description": {"type": "string"},
                         "properties": {"type": "array", "items": {"type": "string"}, "minItems": 1}},
                        ["world", "character_id", "name", "properties"]), ws.character_add, read_only=False, modes=both),
            Tool("hyperworld_status", "Whether the hyperworld engine and hypergames env are present; policies, item kinds, families.",
                 schema({}), hg.status, read_only=True, modes=hyper),
            Tool("hyperworld_view", "Replay the Cairo hyperworld from a seed and a list of actions; returns the public view.",
                 schema({"seed": {"type": "integer", "minimum": 0}, "actions": {"type": "array", "items": {"type": "string"}, "maxItems": 7}},
                        ["seed"]), hg.view, read_only=True, modes=hyper),
            Tool("hyperworld_family_build", "Build an exact-graded eval family from seeded engine traces; reports baselines and acceptance.",
                 schema({"family": {"type": "string"}, "seeds": {"type": "array", "items": {"type": "integer", "minimum": 0},
                                                                  "minItems": 1, "maxItems": 64},
                         "policy": {"type": "string"}, "turns": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 7}},
                         "kinds": {"type": "array", "items": {"type": "string", "enum": list(KINDS)}},
                         "traps_only": {"type": "boolean"}, "max_items": {"type": "integer", "minimum": 1, "maximum": 500}},
                        ["family", "seeds"]), hg.family_build, read_only=False, modes=hyper),
            Tool("hyperworld_family_score", "Score answers ({id, answer} list or JSONL path) against a family's dev or held-out grader.",
                 schema({"family": {"type": "string"}, "answers": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                         "split": {"type": "string", "enum": ["dev", "heldout"]}}, ["family", "answers"]),
                 hg.family_score, read_only=True, modes=hyper),
            Tool("hyperworld_family_freeze", "Draw held-out seeds into a directory outside the repository and record their hashes.",
                 schema({"family": {"type": "string"}, "heldout_dir": {"type": "string"},
                         "heldout_seeds": {"type": "integer", "minimum": 1, "maximum": 64}}, ["family", "heldout_dir"]),
                 hg.family_freeze, read_only=False, modes=hyper),
            Tool("hg_selftest", "Run the hypergames env's unit tests and source-hashed receipt checks (CPU, a few minutes).",
                 schema({}), hg.hg_selftest, read_only=True, modes=hyper),
        ]
        return tools

    def visible(self) -> list[Tool]:
        return [t for t in self.registry if self.mode in t.modes and (t.read_only or not self.read_only)]

    def tools(self) -> list[dict[str, Any]]:
        return [t.listing() for t in self.visible()]

    def call(self, name: str, arguments: Any) -> dict[str, Any]:
        tool = next((t for t in self.visible() if t.name == name), None)
        if tool is None:
            raise StoryworldError("unknown_tool", f"{name} is not a {self.mode}-mode tool in this session")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            raise StoryworldError("bad_argument", "arguments must be an object")
        allowed = set(tool.schema["properties"])
        extra = sorted(set(arguments) - allowed)
        missing = sorted(set(tool.schema["required"]) - set(arguments))
        if extra or missing:
            raise StoryworldError("bad_argument", f"{name}: missing {missing}, unknown {extra}; parameters: {sorted(allowed)}")
        return tool.handler(**arguments)


def _result(payload: dict[str, Any], error: bool = False) -> dict[str, Any]:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return {"content": [{"type": "text", "text": text}], "structuredContent": payload, "isError": error}


def handle(service: Service, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    if "id" not in message:
        return None
    reply: dict[str, Any] = {"jsonrpc": "2.0", "id": message["id"]}
    params = message.get("params") or {}
    if method == "initialize":
        reply["result"] = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {"listChanged": False}},
                           "serverInfo": {"name": "storyworld", "version": VERSION},
                           "instructions": INSTRUCTIONS[service.mode]}
    elif method == "ping":
        reply["result"] = {}
    elif method == "tools/list":
        reply["result"] = {"tools": service.tools()}
    elif method == "tools/call":
        try:
            reply["result"] = _result(service.call(str(params.get("name")), params.get("arguments")))
        except StoryworldError as exc:
            reply["result"] = _result({"error": exc.code, "detail": exc.detail}, error=True)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            reply["result"] = _result({"error": "internal_error", "detail": f"{type(exc).__name__}: {exc}"}, error=True)
    else:
        reply["error"] = {"code": -32601, "message": f"method not found: {method}"}
    return reply


def serve(service: Service, reader: IO[bytes], writer: IO[bytes]) -> None:
    for raw in reader:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("not an object")
        except ValueError:
            response: dict[str, Any] | None = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            response = handle(service, message)
        if response is not None:
            writer.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
            writer.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Storyworld MCP server")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="GPTStoryworld checkout")
    parser.add_argument("--work", type=Path, help="workspace (default <root>/gdk/work)")
    parser.add_argument("--mode", choices=MODES, default="all")
    parser.add_argument("--card-budget", type=int, default=6144, help="encounter card size cap, in estimated tokens")
    parser.add_argument("--read-budget", type=int, default=48000, help="world_read size cap, in estimated tokens")
    parser.add_argument("--read-only", action="store_true")
    parser.add_argument("--deny", action="append", default=[], help="a path no tool may read (repeatable)")
    args = parser.parse_args(argv)
    out = sys.stdout.buffer
    try:
        service = Service(args.root, args.work or args.root / "gdk" / "work", args.mode, args.card_budget,
                          args.read_budget, args.read_only, args.deny)
    except StoryworldError as exc:
        print(f"storyworld server: {exc}", file=sys.stderr)
        return 2
    serve(service, sys.stdin.buffer, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

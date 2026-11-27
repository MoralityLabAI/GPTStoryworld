"""Convert Camelot's Reckoning (outline.json + encounters.jsonl) into the repo's standard
SweepWeave storyworld JSON schema (see GPTStoryworld/storyworld_format_guide.md), so it can run
through json_to_swmd.py and the rest of the storyworld-conveyor tooling instead of living in a
one-off format. No narrative text is added or changed here: every text_script value is copied
verbatim from what Inky Mini wrote; only ids, titles and structural plumbing are authored here.
"""
import json
import re
import time
from pathlib import Path

RUN = Path(__file__).parent
OUTLINE = json.loads((RUN / "outline.json").read_text(encoding="utf-8"))
ENCOUNTERS = [json.loads(line) for line in (RUN / "encounters.jsonl").read_text(encoding="utf-8").splitlines()]
OUT = RUN / "storyworld.json"

CREATED = 1796198400.0  # 2026-11-26T00:00:00Z, the campaign's generation date


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def string_const(value: str) -> dict:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bool_const(value: bool) -> dict:
    return {"pointer_type": "Boolean Constant", "script_element_type": "Pointer", "value": value}


def number_const(value: float) -> dict:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def build_characters() -> list:
    return [{"id": f"char_{slugify(c['name'])}", "name": c["name"], "bnumber_properties": {}} for c in OUTLINE["cast"]]


def build_spools() -> list:
    spools = [{"id": "spool_trunk", "spool_type": "General", "creation_index": 0,
               "creation_time": CREATED, "modified_time": CREATED}]
    for i, b in enumerate(OUTLINE["branch_outline"]["branches"]):
        spools.append({"id": f"spool_{b['ending_id']}", "spool_type": "General", "creation_index": i + 1,
                        "creation_time": CREATED, "modified_time": CREATED})
    return spools


def by_branch() -> dict:
    groups: dict[str, list[dict]] = {}
    for row in ENCOUNTERS:
        groups.setdefault(row["branch"], []).append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: r["index_in_branch"])
    return groups


def next_id(rows: list, i: int) -> str | None:
    return rows[i + 1]["encounter_id"] if i + 1 < len(rows) else None


def build_encounters(groups: dict) -> list:
    trunk = groups["trunk"]
    trunk_last_id = trunk[-1]["encounter_id"]
    branch_heads = {b["ending_id"]: groups[b["ending_id"]][0]["encounter_id"] for b in OUTLINE["branch_outline"]["branches"]}
    pages = []
    creation_index = 0
    for branch, rows in [("trunk", trunk)] + [(b["ending_id"], groups[b["ending_id"]]) for b in OUTLINE["branch_outline"]["branches"]]:
        spool_id = "spool_trunk" if branch == "trunk" else f"spool_{branch}"
        for i, row in enumerate(rows):
            text = row["scene"]
            if row.get("is_ending") and row.get("ending_text"):
                text = f"{text}\n\n{row['ending_text']}"
            options = []
            is_trunk_finale = row["encounter_id"] == trunk_last_id
            for oi, opt in enumerate(row.get("options", [])):
                opt_id = f"{row['encounter_id']}_opt{oi}"
                if is_trunk_finale:
                    reactions = [
                        {
                            "id": f"{opt_id}_r_{ending_id}",
                            "text_script": string_const(""),
                            "consequence_id": head_id,
                            "desirability_script": number_const(1.0),
                            "after_effects": [],
                        }
                        for ending_id, head_id in branch_heads.items()
                    ]
                else:
                    nxt = next_id(rows, i)
                    reactions = [{
                        "id": f"{opt_id}_r1",
                        "text_script": string_const(opt.get("consequence", "")),
                        "consequence_id": nxt,
                        "desirability_script": number_const(1.0),
                        "after_effects": [],
                    }] if nxt else []
                options.append({
                    "id": opt_id,
                    "text_script": string_const(opt["label"]),
                    "visibility_script": bool_const(True),
                    "performability_script": bool_const(True),
                    "reactions": reactions,
                })
            pages.append({
                "id": row["encounter_id"],
                "title": row.get("state_summary", row["encounter_id"])[:80],
                "connected_spools": [spool_id],
                "earliest_turn": 0,
                "latest_turn": 999,
                "text_script": string_const(text),
                "options": [] if row.get("is_ending") else options,
                "acceptability_script": bool_const(True),
                "desirability_script": number_const(0),
                "creation_index": creation_index,
                "creation_time": CREATED,
                "modified_time": CREATED,
                "characters_present": row.get("characters_present", []),
                "art_svg": row.get("canvas_art_svg", ""),
            })
            creation_index += 1
    return pages


def main():
    groups = by_branch()
    characters = build_characters()
    spools = build_spools()
    encounters = build_encounters(groups)
    world = {
        "IFID": "SW-INKY-CAMELOT-0001",
        "storyworld_title": "Camelot's Reckoning",
        "storyworld_author": "Inkling-2-Mini (via goblin-gdk teacher-generation)",
        "sweepweave_version": "0.1.9",
        "creation_time": CREATED,
        "modified_time": CREATED,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "dark",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": string_const(OUTLINE["setting"]),
        "characters": characters,
        "authored_properties": [],
        "spools": spools,
        "encounters": encounters,
        "unique_id_seeds": {
            "character": len(characters),
            "encounter": len(encounters),
            "option": sum(len(e["options"]) for e in encounters),
            "reaction": sum(len(o["reactions"]) for e in encounters for o in e["options"]),
            "spool": len(spools),
            "authored_property": 0,
        },
    }
    OUT.write_text(json.dumps(world, indent=2), encoding="utf-8")
    print(f"wrote {OUT} : {len(characters)} characters, {len(spools)} spools, {len(encounters)} encounters")


if __name__ == "__main__":
    main()

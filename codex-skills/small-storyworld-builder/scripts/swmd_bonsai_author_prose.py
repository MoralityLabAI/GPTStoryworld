#!/usr/bin/env python3
"""Bounded-context (<=8k) per-encounter SWMD-0 prose & reaction pass for Bonsai 27."""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List


def strip_wrappers(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    if "<think>" in cleaned:
        cleaned = cleaned.split("<think>", 1)[0]
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        return cleaned[start : end + 1]
    return cleaned.strip()


def call_bonsai(base_url: str, model_name: str, prompt: str, max_tokens: int, temperature: float) -> tuple[str, Dict[str, Any], int]:
    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Ternary-Bonsai-2-27B authoring one bounded encounter card at a time under the "
                    "small-storyworld-builder contract (<=8k context). Write sharp, tense crime-thriller dialogue "
                    "and chamber-drama prose inspired by Reservoir Dogs (Mr. White, Mr. Pink, Mr. Orange, Mr. Blonde, "
                    "Marvin Nash, Nice Guy Eddie, Joe Cabot). Output one valid JSON object only, with no markdown fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": int(max_tokens),
        "temperature": float(temperature),
        "top_p": 0.9,
        "seed": 7,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    last_err: Exception | None = None
    for attempt in range(24):
        t0 = time.time()
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            latency_ms = int((time.time() - t0) * 1000)
            choice = (body.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            content = str(msg.get("content") or "").strip()
            usage = body.get("usage") or {}
            return content, usage, latency_ms
        except Exception as exc:
            last_err = exc
            time.sleep(5.0)
    assert last_err is not None
    raise last_err


def word_count(s: str) -> int:
    return len(str(s or "").split())


def sptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def get_sval(node: Any) -> str:
    if isinstance(node, dict):
        return str(node.get("value", "") or "")
    return str(node or "")


def main() -> int:
    ap = argparse.ArgumentParser(description="Author bounded per-encounter scene/option/reaction prose via Bonsai 27.")
    ap.add_argument("--base-json", required=True, type=Path)
    ap.add_argument("--swmd-min", required=True, type=Path)
    ap.add_argument("--phase-state", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-trace-jsonl", required=True, type=Path)
    ap.add_argument("--base-url", default="http://127.0.0.1:18080/v1")
    ap.add_argument("--model-name", default="Ternary-Bonsai-2-27B-PTQ1_0.gguf")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    source_json = args.out_json if (args.resume and args.out_json.exists()) else args.base_json
    world = json.loads(source_json.read_text(encoding="utf-8"))
    completed_ids: set[str] = set()
    if args.resume and args.out_trace_jsonl.exists():
        for raw_ln in args.out_trace_jsonl.read_text(encoding="utf-8").splitlines():
            if raw_ln.strip():
                try:
                    r_obj = json.loads(raw_ln)
                    if r_obj.get("parsed_ok") and r_obj.get("encounter_id"):
                        completed_ids.add(str(r_obj["encounter_id"]))
                except Exception:
                    pass
    phase_state: Dict[str, Any] = {}
    if args.phase_state.exists():
        phase_state = json.loads(args.phase_state.read_text(encoding="utf-8"))

    # Pull any option label updates already applied in SWMD-0-MIN during encounter_build / late_stage_holistic
    swmd_opt_labels: Dict[str, str] = {}
    if args.swmd_min.exists():
        for raw in args.swmd_min.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line.startswith("ORX "):
                continue
            m = re.match(r"^ORX\s+([^/]+)/([^\s]+)\s+->\s+[^|]+\|\s*O:([^|]+)\|", line)
            if m:
                opt_id = m.group(1).strip()
                opt_txt = m.group(3).strip()
                if opt_txt and opt_id not in swmd_opt_labels:
                    swmd_opt_labels[opt_id] = opt_txt

    encounters: List[Dict[str, Any]] = world.get("encounters", [])
    cast_summary = [
        {"id": c["id"], "name": c["name"], "role": c.get("description", "")}
        for c in world.get("characters", [])
    ]

    args.out_trace_jsonl.parent.mkdir(parents=True, exist_ok=True)
    trace_mode = "a" if (args.resume and args.out_trace_jsonl.exists()) else "w"
    with args.out_trace_jsonl.open(trace_mode, encoding="utf-8", newline="\n") as trace_f:
        for idx, enc in enumerate(encounters):
            enc_id = str(enc["id"])
            if enc_id in completed_ids:
                print(f"skip completed prose id={enc_id}", flush=True)
                continue
            options = enc.get("options") or []
            prev_title = encounters[idx - 1]["title"] if idx > 0 else "Opening Heist Escape"
            next_title = encounters[idx + 1]["title"] if idx + 1 < len(encounters) else "Terminal Verdict"
            notes = phase_state.get(enc_id, {})

            if options:
                opt_skeleton = []
                for opt in options:
                    oid = str(opt["id"])
                    cur_label = swmd_opt_labels.get(oid) or get_sval(opt.get("text_script"))
                    rxns = [
                        {
                            "rxn_id": str(r["id"]),
                            "consequence_id": str(r["consequence_id"]),
                        }
                        for r in (opt.get("reactions") or [])
                    ]
                    opt_skeleton.append(
                        {
                            "option_id": oid,
                            "seed_option_label": cur_label,
                            "reactions": rxns,
                        }
                    )

                prompt = (
                    "TASK: Author dramatic text for ONE Reservoir Dogs storyworld encounter card under an 8k context budget.\n"
                    "Keep all option_id and rxn_id strings IDENTICAL.\n"
                    "Requirements:\n"
                    "- title: punchy 3-7 word Reservoir Dogs scene title.\n"
                    "- scene_text: 65 to 110 words of taut warehouse chamber-drama prose + sharp dialogue.\n"
                    "- options: array matching the exact option_id order below.\n"
                    "  - option_text: 8 to 18 words, concrete action or spoken line.\n"
                    "  - reactions: array matching the exact rxn_id order below.\n"
                    "    - reaction_text: 24 to 42 words showing immediate character reaction, vocal tell, and shifting leverage toward consequence_id.\n\n"
                    f"CAST_CARD: {json.dumps(cast_summary, ensure_ascii=True)}\n"
                    f"NEIGHBOR_CONTEXT: prev='{prev_title}' -> current='{enc['title']}' ({enc_id}) -> next='{next_title}'\n"
                    f"SEED_SCENE: {get_sval(enc.get('text_script'))}\n"
                    f"MCP_PHASE_NOTES: {json.dumps(notes, ensure_ascii=True)[:1400]}\n"
                    f"OPTION_SKELETON: {json.dumps(opt_skeleton, ensure_ascii=True)}\n\n"
                    "Output JSON schema:\n"
                    '{"title":"...","scene_text":"...","options":[{"option_id":"...","option_text":"...","reactions":[{"rxn_id":"...","reaction_text":"..."}]}]}'
                )
                raw_out, usage, latency_ms = call_bonsai(
                    args.base_url,
                    args.model_name,
                    prompt,
                    max_tokens=1650,
                    temperature=args.temperature,
                )
                parsed_ok = False
                applied_fields = 0
                try:
                    data = json.loads(strip_wrappers(raw_out))
                    if isinstance(data, dict):
                        new_title = str(data.get("title") or "").strip()
                        new_scene = str(data.get("scene_text") or "").strip()
                        if new_title:
                            enc["title"] = new_title
                            applied_fields += 1
                        if word_count(new_scene) >= 52:
                            enc["text_script"] = sptr(new_scene)
                            applied_fields += 1
                        opt_map = {
                            str(o.get("option_id", "")): o
                            for o in (data.get("options") or [])
                            if isinstance(o, dict)
                        }
                        for opt in options:
                            oid = str(opt["id"])
                            cand_opt = opt_map.get(oid)
                            if cand_opt:
                                otxt = str(cand_opt.get("option_text") or "").strip()
                                if word_count(otxt) >= 4:
                                    opt["text_script"] = sptr(otxt)
                                    applied_fields += 1
                                rxn_map = {
                                    str(r.get("rxn_id", "")): str(r.get("reaction_text") or "").strip()
                                    for r in (cand_opt.get("reactions") or [])
                                    if isinstance(r, dict)
                                }
                                for rxn in opt.get("reactions") or []:
                                    rid = str(rxn["id"])
                                    rtxt = rxn_map.get(rid, "")
                                    if word_count(rtxt) >= 20:
                                        rxn["text_script"] = sptr(rtxt)
                                        applied_fields += 1
                        parsed_ok = applied_fields >= 4
                except Exception:
                    parsed_ok = False
                    # Still apply SWMD-0-MIN option label if present
                    for opt in options:
                        oid = str(opt["id"])
                        if oid in swmd_opt_labels and word_count(swmd_opt_labels[oid]) >= 4:
                            opt["text_script"] = sptr(swmd_opt_labels[oid])
            else:
                prompt = (
                    "TASK: Author dramatic terminal ending prose for ONE Reservoir Dogs ending card under an 8k context budget.\n"
                    "Requirements:\n"
                    "- title: evocative 3-8 word ending title (keep 'Secret Ending:' prefix if encounter_id starts with page_secret_).\n"
                    "- scene_text: 75 to 120 words resolving the mortuary warehouse standoff, the Karina diamond satchel, and the undercover cop revelation.\n\n"
                    f"CAST_CARD: {json.dumps(cast_summary, ensure_ascii=True)}\n"
                    f"ENDING_ID: {enc_id}\n"
                    f"SEED_TITLE: {enc['title']}\n"
                    f"SEED_ENDING: {get_sval(enc.get('text_script'))}\n\n"
                    'Output JSON schema:\n{"title":"...","scene_text":"..."}'
                )
                raw_out, usage, latency_ms = call_bonsai(
                    args.base_url,
                    args.model_name,
                    prompt,
                    max_tokens=420,
                    temperature=args.temperature,
                )
                parsed_ok = False
                applied_fields = 0
                try:
                    data = json.loads(strip_wrappers(raw_out))
                    if isinstance(data, dict):
                        new_title = str(data.get("title") or "").strip()
                        new_scene = str(data.get("scene_text") or "").strip()
                        if new_title:
                            if enc_id.startswith("page_secret_") and not new_title.lower().startswith("secret"):
                                new_title = f"Secret Ending: {new_title}"
                            enc["title"] = new_title
                            applied_fields += 1
                        if word_count(new_scene) >= 55:
                            enc["text_script"] = sptr(new_scene)
                            applied_fields += 1
                        parsed_ok = applied_fields >= 1
                except Exception:
                    parsed_ok = False

            row = {
                "encounter_id": enc_id,
                "is_terminal": len(options) == 0,
                "parsed_ok": parsed_ok,
                "applied_fields": applied_fields,
                "scene_words": word_count(get_sval(enc.get("text_script"))),
                "latency_ms": latency_ms,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
            }
            trace_f.write(json.dumps(row, ensure_ascii=True) + "\n")
            trace_f.flush()
            args.out_json.parent.mkdir(parents=True, exist_ok=True)
            tmp_json = args.out_json.with_suffix(args.out_json.suffix + ".tmp")
            tmp_json.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
            tmp_json.replace(args.out_json)
            print(
                f"prose id={enc_id} parsed_ok={parsed_ok} fields={applied_fields} "
                f"words={row['scene_words']} latency_ms={latency_ms}",
                flush=True,
            )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

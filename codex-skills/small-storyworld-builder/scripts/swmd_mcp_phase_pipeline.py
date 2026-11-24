from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


ORX_LINE_RE = re.compile(r"^ORX\s+[^/]+/[^\s]+\s+->\s+[^|]+\|.+$", re.M)
ENC_RE = re.compile(r"^ENC\s+(\S+)\s+turn=([^\s]+)\s*$", re.M)


def _load_swmd_tools() -> Any:
    module_dir = Path(__file__).resolve().parents[3] / "mcp-storyworld-encounter"
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))
    import swmd_store  # type: ignore

    return swmd_store


def _extract_replacement_block(text: str, encounter_id: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    start = -1
    for i, ln in enumerate(lines):
        if ln.startswith(f"ENC {encounter_id} "):
            start = i
            break
    if start < 0:
        return ""
    out = [lines[start]]
    for ln in lines[start + 1 :]:
        if ln.startswith("ENC "):
            break
        if ln.startswith("ORX "):
            out.append(ln)
    if len(out) < 2:
        return ""
    return "\n".join(out)


def _extract_any_enc_block(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    start = -1
    for i, ln in enumerate(lines):
        if ln.startswith("ENC "):
            start = i
            break
    if start < 0:
        return ""
    out = [lines[start]]
    for ln in lines[start + 1 :]:
        if ln.startswith("ENC "):
            break
        if ln.startswith("ORX "):
            out.append(ln)
    if len(out) < 2:
        return ""
    return "\n".join(out)


def _extract_orx_lines(text: str) -> List[str]:
    return [ln.rstrip() for ln in text.splitlines() if ln.strip().startswith("ORX ")]


def _parse_orx_id(line: str) -> str:
    parts = line.split()
    return parts[1] if len(parts) > 1 else ""


def _score_block_quality(block: str, target_block: str, encounter_id: str, turn_span: str) -> Dict[str, Any]:
    block_lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
    target_lines = [ln.rstrip() for ln in target_block.splitlines() if ln.strip()]
    header_ok = bool(block_lines and block_lines[0] == f"ENC {encounter_id} turn={turn_span}")
    target_orx = [ln for ln in target_lines if ln.startswith("ORX ")]
    block_orx = [ln for ln in block_lines if ln.startswith("ORX ")]
    target_ids = [_parse_orx_id(ln) for ln in target_orx]
    block_ids = [_parse_orx_id(ln) for ln in block_orx]
    matched_ids = [oid for oid in block_ids if oid in target_ids]
    coverage = (len(set(matched_ids)) / max(1, len(set(target_ids)))) if target_ids else 0.0
    changed_from_target = block.strip() != target_block.strip()
    word_count = len(re.findall(r"[A-Za-z0-9_'-]+", block))
    p_refs = len(re.findall(r"\bP\(", block))
    p2_refs = len(re.findall(r"\bP2\(", block))
    richness = min(1.0, word_count / 24.0)
    score = (
        0.35 * coverage
        + 0.15 * (1.0 if header_ok else 0.0)
        + 0.15 * (1.0 if changed_from_target else 0.0)
        + 0.15 * richness
        + 0.10 * min(1.0, p_refs / 2.0)
        + 0.10 * min(1.0, p2_refs / 1.0)
    )
    return {
        "score": round(score, 3),
        "header_ok": header_ok,
        "target_orx_count": len(target_orx),
        "block_orx_count": len(block_orx),
        "orx_coverage": round(coverage, 3),
        "changed_from_target": changed_from_target,
        "word_count": word_count,
        "p_refs": p_refs,
        "p2_refs": p2_refs,
    }


def _repair_replacement_block(text: str, encounter_id: str, turn_span: str, target_block: str) -> str:
    candidate = _extract_replacement_block(text, encounter_id) or _extract_any_enc_block(text) or text
    target_lines = [ln.rstrip() for ln in target_block.splitlines() if ln.strip()]
    target_orx = [ln for ln in target_lines if ln.startswith("ORX ")]
    if not target_orx:
        return ""
    target_ids = [_parse_orx_id(ln) for ln in target_orx]
    picked: Dict[str, str] = {}
    for ln in _extract_orx_lines(candidate):
        orx_id = _parse_orx_id(ln)
        if orx_id in target_ids and orx_id not in picked:
            picked[orx_id] = ln
    repaired_lines = [f"ENC {encounter_id} turn={turn_span}"]
    for fallback in target_orx:
        orx_id = _parse_orx_id(fallback)
        repaired_lines.append(picked.get(orx_id, fallback))
    if len(repaired_lines) < 2:
        return ""
    return "\n".join(repaired_lines)


def _packet_turn_span(packet: Dict[str, Any]) -> str:
    direct = str(packet.get("turn_span", "") or "").strip()
    if direct:
        return direct
    plan = packet.get("planning_card") or {}
    planned = str(plan.get("turn_span", "") or "").strip()
    if planned:
        return planned
    target = str(packet.get("target_block", "") or "")
    m = ENC_RE.search(target)
    if m:
        return str(m.group(2)).strip()
    return "0..0"


def _compact_block_view(block: str, max_formula_chars: int = 72) -> str:
    """Compact E:/D: formula tails for bounded prompt view while preserving exact ORX IDs, targets, and O: text."""
    out: List[str] = []
    for raw in block.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.startswith("ENC "):
            out.append(ln)
            continue
        if ln.startswith("ORX "):
            parts = [p.strip() for p in ln.split("|")]
            head = parts[0]
            o_part = next((p for p in parts[1:] if p.startswith("O:")), "O:")
            e_part = next((p for p in parts[1:] if p.startswith("E:")), "E:KEEP")
            d_part = next((p for p in parts[1:] if p.startswith("D:")), "D:KEEP")
            if len(e_part) > max_formula_chars:
                e_part = e_part[:max_formula_chars] + "..."
            if len(d_part) > max_formula_chars:
                d_part = d_part[:max_formula_chars] + "..."
            out.append(f"{head} | {o_part} | {e_part} | {d_part}")
    return "\n".join(out)


def _hydrate_formulas_from_target(candidate_block: str, target_block: str) -> str:
    """Restore full deterministic E: and D: expressions when model emits KEEP or truncated formula tails."""
    target_ed: Dict[str, tuple[str, str, str]] = {}
    for raw in target_block.splitlines():
        ln = raw.strip()
        if not ln.startswith("ORX "):
            continue
        oid = _parse_orx_id(ln)
        parts = [p.strip() for p in ln.split("|")]
        head = parts[0]
        e_part = next((p for p in parts[1:] if p.startswith("E:")), "E:SET none = C(0)")
        d_part = next((p for p in parts[1:] if p.startswith("D:")), "D:C(0)")
        target_ed[oid] = (head, e_part, d_part)

    out_lines: List[str] = []
    seen_orx: set[str] = set()
    for raw in candidate_block.splitlines():
        ln = raw.strip()
        if ln.startswith("ENC "):
            out_lines.append(ln)
            continue
        if ln.startswith("ORX "):
            oid = _parse_orx_id(ln)
            if oid not in target_ed or oid in seen_orx:
                continue
            seen_orx.add(oid)
            t_head, t_e, t_d = target_ed[oid]
            parts = [p.strip() for p in ln.split("|")]
            o_part = next((p for p in parts[1:] if p.startswith("O:")), "")
            e_part = next((p for p in parts[1:] if p.startswith("E:")), "")
            d_part = next((p for p in parts[1:] if p.startswith("D:")), "")
            if not o_part or len(o_part) < 4:
                continue
            if (not e_part) or ("..." in e_part) or (e_part == "E:KEEP"):
                e_part = t_e
            if (not d_part) or ("..." in d_part) or (d_part == "D:KEEP"):
                d_part = t_d
            out_lines.append(f"{t_head} | {o_part} | {e_part} | {d_part}")
    return "\n".join(out_lines)


def _phase_prompt(phase: str, packet: Dict[str, Any], act_label: str) -> str:
    plan = packet["planning_card"]
    poetics = packet.get("mathematical_poetics", {})
    neighbors = packet.get("neighbors", [])
    external_constraints = packet.get("external_constraints") or {}
    turn_span = _packet_turn_span(packet)
    neighbor_txt = "\n\n".join(
        [f"NEIGHBOR {n['encounter_id']}\n{_compact_block_view(n['block'], 48)}" for n in neighbors]
    )
    target = _compact_block_view(packet["target_block"], 64)
    constraint_txt = ""
    if external_constraints:
        constraint_txt = f"\nTRM_PACKET\n{json.dumps(external_constraints, ensure_ascii=True)}\n"

    if phase == "plan":
        return (
            "You are planning one encounter revision under 8k context constraints.\n"
            "Output compact single-object JSON only (<= 90 tokens) with keys: objective, constraints, risks, checks.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n{constraint_txt}\n{neighbor_txt}\n"
        )
    if phase in ("characterize", "recharacterize"):
        return (
            "You are producing compact characterization notes for this encounter.\n"
            "Output compact single-object JSON only (<= 90 tokens) with keys: voices, tensions, stance_shift, dialogue_style.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n{constraint_txt}\n{neighbor_txt}\n"
        )
    if phase == "act_complete":
        return (
            "You are auditing act-level coherence for this encounter's act segment.\n"
            "Output compact single-object JSON only (<= 90 tokens) with keys: act_status, continuity_risks, unresolved_threads, next_focus.\n"
            "Include numeric before/after where invariant values are available.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n{constraint_txt}\n{neighbor_txt}\n"
        )
    if phase in ("encounter_build", "late_stage_holistic"):
        # Deduplicate ORX view to one representative reaction per option if needed, or emit all ORX lines with E:KEEP | D:KEEP
        orx_template_lines = [f"ENC {packet['encounter_id']} turn={turn_span}"]
        for raw in packet["target_block"].splitlines():
            ln = raw.strip()
            if ln.startswith("ORX "):
                parts = [p.strip() for p in ln.split("|")]
                head = parts[0]
                o_part = next((p for p in parts[1:] if p.startswith("O:")), "O:")
                orx_template_lines.append(f"{head} | {o_part} | E:KEEP | D:KEEP")
        compact_target = "\n".join(orx_template_lines)
        return (
            "You are revising one SWMD-0-MIN encounter block for Reservoir Dogs.\n"
            "Output ONLY the revised SWMD-0-MIN block (no JSON, no fences, no commentary).\n"
            "Rules:\n"
            "1) First line must be exact: ENC <same id> turn=<same turn span>\n"
            "2) Emit every ORX line with exact same opt_id/rxn_id -> consequence_id\n"
            "3) Rewrite O:<option text> into sharp, distinct Reservoir Dogs character action/dialogue (6-14 words); options sharing the same opt_id should share the same O: text\n"
            "4) Leave | E:KEEP | D:KEEP at the end of each ORX line so invariant formulas stay preserved\n\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"TARGET_SWMD_BLOCK\n{compact_target}\n\n"
            f"{neighbor_txt}\n"
        )
    raise ValueError(f"unsupported phase: {phase}")


def _load_qlora_examples(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        try:
            row = json.loads(s)
        except Exception:
            continue
        if not isinstance(row, dict):
            continue
        if "instruction" in row and "output" in row:
            out = _extract_any_enc_block(str(row.get("output", ""))) or str(row.get("output", ""))
            rows.append({"instruction": row.get("instruction", ""), "output": out})
            continue
        messages = row.get("messages")
        if isinstance(messages, list):
            assistant_outputs = [
                _extract_any_enc_block(str(msg.get("content", "") or ""))
                for msg in messages
                if isinstance(msg, dict) and str(msg.get("role", "")) == "assistant"
            ]
            assistant_outputs = [x for x in assistant_outputs if x]
            user_inputs = [
                str(msg.get("content", "") or "")
                for msg in messages
                if isinstance(msg, dict) and str(msg.get("role", "")) == "user"
            ]
            if assistant_outputs:
                rows.append(
                    {
                        "instruction": user_inputs[-1] if user_inputs else "Rewrite this encounter block with stable SWMD structure.",
                        "output": assistant_outputs[-1],
                    }
                )
    return rows


def _load_external_constraints(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _fewshot_snippet(
    examples: List[Dict[str, Any]],
    phase: str,
    encounter_id: str,
    count: int,
    max_chars_each: int = 520,
) -> str:
    if not examples or count <= 0:
        return ""
    # Use compile/compression/repair/edit examples for build-like phases only.
    if phase not in ("encounter_build", "late_stage_holistic"):
        return ""
    salt = sum(ord(ch) for ch in encounter_id) + len(phase) * 17
    start = salt % len(examples)
    picked = [examples[(start + i) % len(examples)] for i in range(min(count, len(examples)))]
    lines = ["FEWSHOT_TRANSFORMS"]
    for i, ex in enumerate(picked, start=1):
        ins = str(ex.get("instruction", ""))[:max_chars_each]
        raw_out = str(ex.get("output", ""))
        out = (_compact_block_view(raw_out, 48) if "ORX " in raw_out else raw_out)[:max_chars_each]
        lines.append(f"[{i}] INSTRUCTION: {ins}")
        lines.append(f"[{i}] VALID_SWMD_BLOCK:")
        lines.append(out)
    return "\n".join(lines) + "\n"


def _load_model_hf(model_path: Path, adapter_path: Path | None):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        quantization_config=bnb,
        device_map="auto",
        low_cpu_mem_usage=True,
        torch_dtype=torch.float16,
        local_files_only=True,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, str(adapter_path), is_trainable=False) if adapter_path else base
    model.eval()
    tok = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok, model


def _generate_hf(tok, model, prompt: str, max_new_tokens: int, temperature: float) -> str:
    import torch

    if hasattr(tok, "apply_chat_template"):
        try:
            rendered = tok.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            rendered = prompt
    else:
        rendered = prompt
    inputs = tok(rendered, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0.0,
            temperature=max(0.01, temperature),
            top_p=0.9,
            eos_token_id=tok.eos_token_id,
            pad_token_id=tok.pad_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1] :]
    return tok.decode(new_tokens, skip_special_tokens=True).strip()


def _generate_mlx(
    model_path: Path,
    adapter_path: Path | None,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
) -> str:
    import subprocess

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "generate",
        "--model",
        str(model_path),
        "--prompt",
        prompt,
        "--max-tokens",
        str(max_new_tokens),
        "--temp",
        str(temperature),
        "--top-p",
        "0.9",
        "--seed",
        "7",
        "--ignore-chat-template",
        "--verbose",
        "false",
    ]
    if adapter_path and adapter_path.exists():
        cmd.extend(["--adapter-path", str(adapter_path)])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "mlx_lm generate failed").strip())
    text = (proc.stdout or "").strip()
    if not text:
        raise RuntimeError("mlx_lm returned empty output")
    return text


def _strip_think_tags(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    if "<think>" in cleaned:
        cleaned = cleaned.split("<think>", 1)[0]
    cleaned = re.sub(r"^```(?:json|markdown|swmd|text)?\s*", "", cleaned.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


def _generate_openai(
    base_url: str,
    model_name: str,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
) -> tuple[str, Dict[str, Any]]:
    import urllib.request

    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload: Dict[str, Any] = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a deterministic SWMD-0-MIN storyworld operation engine following the small-storyworld-builder contract. Follow output formatting instructions strictly with zero extra prose.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": int(max_new_tokens),
        "temperature": float(temperature),
        "top_p": 0.9,
        "seed": 7,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    choice = (body.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = str(msg.get("content") or "").strip()
    usage = body.get("usage") or {}
    return _strip_think_tags(content), {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "finish_reason": choice.get("finish_reason"),
    }


def _act_label(idx: int, total: int) -> str:
    if total <= 0:
        return "act2"
    cut1 = max(1, total // 3)
    cut2 = max(cut1 + 1, (2 * total) // 3)
    if idx < cut1:
        return "act1"
    if idx < cut2:
        return "act2"
    return "act3"


def main() -> int:
    p = argparse.ArgumentParser(description="Phased MCP pipeline for small-model storyworld iteration.")
    p.add_argument("--swmd", type=str, required=True)
    p.add_argument(
        "--model-path",
        type=str,
        default=r"D:\Research_Engine\Qwen_Storyworld\cache\models--Qwen--Qwen2.5-3B-Instruct\snapshots\aa8e72537993ba99e69dfaafa59ed015b17504d1",
    )
    p.add_argument(
        "--adapter-path",
        type=str,
        default="",
    )
    p.add_argument("--backend", type=str, default="auto", choices=("auto", "hf", "mlx", "openai"))
    p.add_argument("--base-url", type=str, default="http://127.0.0.1:18080/v1")
    p.add_argument("--model-name", type=str, default="Ternary-Bonsai-2-27B-PTQ1_0.gguf")
    p.add_argument(
        "--phases",
        type=str,
        default="plan,characterize,encounter_build,act_complete,recharacterize,late_stage_holistic",
    )
    p.add_argument("--max-encounters", type=int, default=20)
    p.add_argument("--start-index", type=int, default=0)
    p.add_argument("--neighbor-hops", type=int, default=1)
    p.add_argument("--context-budget-tokens", type=int, default=8192)
    p.add_argument("--reserve-output-tokens", type=int, default=1024)
    p.add_argument("--planning-card-tokens", type=int, default=900)
    p.add_argument("--max-new-tokens", type=int, default=220)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--out-jsonl", type=str, required=True)
    p.add_argument("--state-json", type=str, required=True)
    p.add_argument("--qlora-examples-jsonl", type=str, default="")
    p.add_argument("--fewshot-count", type=int, default=0)
    p.add_argument("--external-constraints-json", type=str, default="")
    p.add_argument("--repair-build-output", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    phases = [s.strip() for s in args.phases.split(",") if s.strip()]
    swmd_tools = _load_swmd_tools()
    swmd_path = Path(args.swmd)
    doc = swmd_tools.parse_swmd_min(swmd_path)
    ids = doc.encounter_order[args.start_index : args.start_index + args.max_encounters]
    qlora_examples = _load_qlora_examples(Path(args.qlora_examples_jsonl)) if args.qlora_examples_jsonl else []
    external_constraints = _load_external_constraints(Path(args.external_constraints_json)) if args.external_constraints_json else {}

    model_path = Path(args.model_path)
    adapter_raw = str(args.adapter_path or "").strip()
    adapter_path = Path(adapter_raw).expanduser() if adapter_raw else None
    if adapter_path is not None and not adapter_path.exists():
        adapter_path = None
    backend = args.backend
    if backend == "auto":
        backend = "mlx" if sys.platform == "darwin" else "hf"
    tok = None
    model = None
    if backend == "hf":
        tok, model = _load_model_hf(model_path, adapter_path)
    out_path = Path(args.out_jsonl)
    state_path = Path(args.state_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state: Dict[str, Dict[str, Any]] = {}
    completed_keys: set[tuple[str, str]] = set()
    if args.resume and state_path.exists():
        try:
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded_state, dict):
                state = loaded_state
        except Exception:
            pass
    if args.resume and out_path.exists():
        for raw_ln in out_path.read_text(encoding="utf-8").splitlines():
            s_ln = raw_ln.strip()
            if not s_ln:
                continue
            try:
                prev_row = json.loads(s_ln)
                ph = str(prev_row.get("phase", ""))
                eid = str(prev_row.get("encounter_id", ""))
                if ph and eid:
                    completed_keys.add((ph, eid))
                    if ph not in ("encounter_build", "late_stage_holistic") and prev_row.get("output_preview"):
                        state.setdefault(eid, {}).setdefault(ph, str(prev_row["output_preview"]))
            except Exception:
                continue

    open_mode = "a" if (args.resume and out_path.exists()) else "w"
    with out_path.open(open_mode, encoding="utf-8", newline="\n") as handle:
        for phase in phases:
            for i, encounter_id in enumerate(ids):
                if (phase, encounter_id) in completed_keys:
                    print(f"skip completed phase={phase} id={encounter_id}", flush=True)
                    continue
                packet = swmd_tools.iteration_packet(
                    path=swmd_path,
                    encounter_id=encounter_id,
                    neighbor_hops=args.neighbor_hops if phase != "late_stage_holistic" else max(2, args.neighbor_hops),
                    context_budget_tokens=args.context_budget_tokens,
                    reserve_output_tokens=args.reserve_output_tokens,
                    planning_card_tokens=args.planning_card_tokens,
                    include_poetics=True,
                )
                if external_constraints:
                    packet["external_constraints"] = external_constraints
                act = _act_label(i, len(ids))
                prompt = _phase_prompt(phase, packet, act)
                fewshot = _fewshot_snippet(qlora_examples, phase, encounter_id, args.fewshot_count)
                if fewshot:
                    prompt = f"{prompt}\n\n{fewshot}"
                t0 = time.time()
                provider_usage: Dict[str, Any] = {}
                phase_max_tokens = args.max_new_tokens if phase in ("encounter_build", "late_stage_holistic") else min(args.max_new_tokens, 220)
                if backend == "mlx":
                    output = _generate_mlx(model_path, adapter_path, prompt, phase_max_tokens, args.temperature)
                elif backend == "openai":
                    output, provider_usage = _generate_openai(
                        args.base_url,
                        args.model_name,
                        prompt,
                        phase_max_tokens,
                        args.temperature,
                    )
                else:
                    output = _generate_hf(tok, model, prompt, phase_max_tokens, args.temperature)
                latency_ms = int((time.time() - t0) * 1000)

                applied = False
                parse_ok = None
                model_parse_ok = None
                fallback_used = False
                repaired_used = False
                replacement = ""
                if phase in ("encounter_build", "late_stage_holistic"):
                    raw_extracted = _extract_replacement_block(output, encounter_id)
                    if raw_extracted:
                        replacement = _hydrate_formulas_from_target(raw_extracted, packet["target_block"])
                    model_parse_ok = bool(replacement and ORX_LINE_RE.search(replacement))
                    parse_ok = model_parse_ok
                    if not parse_ok and args.repair_build_output:
                        hydrated_any = _hydrate_formulas_from_target(output, packet["target_block"])
                        repaired = _repair_replacement_block(
                            hydrated_any or output,
                            encounter_id,
                            _packet_turn_span(packet),
                            packet["target_block"],
                        )
                        if repaired and ENC_RE.search(repaired) and ORX_LINE_RE.search(repaired):
                            replacement = repaired
                            parse_ok = True
                            repaired_used = True
                    if not parse_ok:
                        # Keep pipeline stable: fallback to the current target block when raw model output is malformed.
                        replacement = packet["target_block"]
                        parse_ok = bool(ENC_RE.search(replacement) and ORX_LINE_RE.search(replacement))
                        fallback_used = True
                    if args.apply and parse_ok:
                        swmd_tools.apply_encounter_block(swmd_path, encounter_id, replacement)
                        applied = True
                    block_quality = _score_block_quality(
                        replacement,
                        packet["target_block"],
                        encounter_id,
                        _packet_turn_span(packet),
                    )
                else:
                    state.setdefault(encounter_id, {})[phase] = output[:1800]
                    block_quality = None

                row = {
                    "phase": phase,
                    "encounter_id": encounter_id,
                    "act": act,
                    "latency_ms": latency_ms,
                    "budget": packet["budget"],
                    "backend": backend,
                    "model": args.model_name if backend == "openai" else Path(args.model_path).name,
                    "provider_usage": provider_usage,
                    "prompt_estimated_tokens": packet["budget"]["estimated_tokens_used"],
                    "external_constraints_loaded": bool(external_constraints),
                    "parse_ok": parse_ok,
                    "model_parse_ok": model_parse_ok,
                    "repaired_used": repaired_used,
                    "fallback_used": fallback_used,
                    "applied": applied,
                    "block_quality": block_quality,
                    "output_preview": (replacement if replacement else output)[:500],
                }
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
                handle.flush()
                state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
                print(f"phase={phase} id={encounter_id} parse_ok={parse_ok} latency_ms={latency_ms}", flush=True)

    state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
    print(str(out_path))
    print(str(state_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

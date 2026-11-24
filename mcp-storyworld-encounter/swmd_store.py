from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


ENC_RE = re.compile(r"^ENC\s+(\S+)\s+turn=([^\s]+)\s*$")


def _token_count(text: str) -> int:
    return max(1, len(re.findall(r"[A-Za-z0-9_'-]+", str(text))))


def _parse_blocks(text: str) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    lines = [line.rstrip() for line in text.splitlines()]
    current: List[str] = []
    current_id = ""
    current_turn = "0..0"
    in_swmd = False
    for line in lines:
        if line.strip() == "# SWMD-0-MIN":
            in_swmd = True
            continue
        if not in_swmd:
            continue
        match = ENC_RE.match(line.strip())
        if match:
            if current and current_id:
                blocks.append(
                    {
                        "encounter_id": current_id,
                        "turn_span": current_turn,
                        "block": "\n".join(current).strip(),
                    }
                )
            current = [line.strip()]
            current_id = match.group(1)
            current_turn = match.group(2)
            continue
        if current:
            if line.strip().startswith("ENC "):
                continue
            if line.strip() or current:
                current.append(line.rstrip())
    if current and current_id:
        blocks.append(
            {
                "encounter_id": current_id,
                "turn_span": current_turn,
                "block": "\n".join(current).strip(),
            }
        )
    return blocks


@dataclass
class SwmdDoc:
    path: Path
    text: str
    blocks: List[Dict[str, Any]]

    @property
    def encounter_order(self) -> List[str]:
        return [row["encounter_id"] for row in self.blocks]


def parse_swmd_min(path: str | Path) -> SwmdDoc:
    swmd_path = Path(path).expanduser().resolve()
    text = swmd_path.read_text(encoding="utf-8")
    blocks = _parse_blocks(text)
    return SwmdDoc(path=swmd_path, text=text, blocks=blocks)


def _index_blocks(doc: SwmdDoc) -> Dict[str, Dict[str, Any]]:
    return {row["encounter_id"]: row for row in doc.blocks}


def _neighbor_ids(order: List[str], encounter_id: str, hops: int) -> List[str]:
    if encounter_id not in order:
        return []
    idx = order.index(encounter_id)
    out: List[str] = []
    for offset in range(1, hops + 1):
        if idx - offset >= 0:
            out.append(order[idx - offset])
        if idx + offset < len(order):
            out.append(order[idx + offset])
    return out


def iteration_packet(
    *,
    path: str | Path,
    encounter_id: str,
    neighbor_hops: int,
    context_budget_tokens: int,
    reserve_output_tokens: int,
    planning_card_tokens: int,
    include_poetics: bool = True,
) -> Dict[str, Any]:
    doc = parse_swmd_min(path)
    by_id = _index_blocks(doc)
    encounter_id = str(encounter_id)
    target = by_id.get(encounter_id, {})
    neighbors: List[Dict[str, Any]] = []
    for neighbor_id in _neighbor_ids(doc.encounter_order, encounter_id, max(0, int(neighbor_hops))):
        neighbor = by_id.get(neighbor_id)
        if neighbor:
            neighbors.append(neighbor)

    target_block = str(target.get("block", "") or "")
    planning_card = {
        "encounter_id": encounter_id,
        "turn_span": str(target.get("turn_span", "0..0")),
        "target_word_count": _token_count(target_block),
        "neighbor_count": len(neighbors),
        "encounter_order_index": doc.encounter_order.index(encounter_id) if encounter_id in doc.encounter_order else -1,
    }
    mathematical_poetics = {
        "encounter_id": encounter_id,
        "block_word_count": _token_count(target_block),
        "neighbor_word_count": sum(_token_count(row["block"]) for row in neighbors),
        "symbolic_balance": round(min(1.0, (len(target_block) % 97) / 97.0), 3),
        "contrast": round(min(1.0, len(neighbors) / max(1, neighbor_hops * 2)), 3),
    }
    budget = {
        "context_budget_tokens": int(context_budget_tokens),
        "reserve_output_tokens": int(reserve_output_tokens),
        "planning_card_tokens": int(planning_card_tokens),
        "estimated_tokens_used": _token_count(target_block)
        + sum(_token_count(row["block"]) for row in neighbors)
        + int(planning_card_tokens),
    }
    packet = {
        "path": str(doc.path),
        "encounter_id": encounter_id,
        "turn_span": str(target.get("turn_span", "0..0")),
        "planning_card": planning_card,
        "target_block": target_block,
        "neighbors": neighbors,
        "budget": budget,
    }
    if include_poetics:
        packet["mathematical_poetics"] = mathematical_poetics
    return packet


def apply_encounter_block(path: str | Path, encounter_id: str, replacement: str) -> None:
    swmd_path = Path(path).expanduser().resolve()
    text = swmd_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = -1
    end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith(f"ENC {encounter_id} "):
            start = i
            break
    if start < 0:
        raise KeyError(encounter_id)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("ENC "):
            end = j
            break
    replacement_lines = [ln.rstrip() for ln in replacement.splitlines() if ln.strip()]
    new_lines = lines[:start] + replacement_lines + lines[end:]
    tmp_path = swmd_path.with_suffix(swmd_path.suffix + ".tmp")
    tmp_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8", newline="\n")
    tmp_path.replace(swmd_path)

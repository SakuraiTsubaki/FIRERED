#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "levelup_move_9bit_field": re.compile(r"\bu16\s+move\s*:\s*9\b"),
    "levelup_move_9bit_mask": re.compile(r"LEVEL_UP_MOVE_ID\s+0x01FF\b"),
    "species_abilities_u8_2": re.compile(r"\bu8\s+abilities\s*\[\s*2\s*\]"),
    "ability_slot_1bit": re.compile(r"\babilityNum\s*:\s*1\b"),
    "battle_ability_u8": re.compile(r"\bu8\s+ability\s*;"),
    "last_ability_u8": re.compile(r"\bu8\s+gLastUsedAbility\b"),
    "pokeball_4bit": re.compile(r"\bpokeball\s*:\s*4\b"),
    "met_game_4bit": re.compile(r"\bmetGame\s*:\s*4\b"),
    "met_location_u8": re.compile(r"\bu8\s+metLocation\b"),
    "battle_result_ball_4bit": re.compile(r"\bcaughtMonBall\s*:\s*4\b"),
}

SAFE_PATTERNS = {
    "persistent_species_u16": re.compile(r"\bu16\s+species\s*;"),
    "persistent_held_item_u16": re.compile(r"\bu16\s+heldItem\s*;"),
    "persistent_move_array_u16": re.compile(r"\bu16\s+moves\s*\["),
    "item_slot_u16": re.compile(r"\bu16\s+itemId\s*;"),
}


def scan(root: Path, patterns: dict[str, re.Pattern[str]]) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {name: [] for name in patterns}
    suffixes = {".c", ".h", ".inc"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel = str(path.relative_to(root))
        for line_no, line in enumerate(lines, 1):
            for name, pattern in patterns.items():
                if pattern.search(line):
                    results[name].append({
                        "path": rel,
                        "line": line_no,
                        "text": line.strip(),
                    })
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit pokefirered ID/metadata widths for the FIRERED Gen10 profile.")
    ap.add_argument("source", type=Path, help="pokefirered source tree")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    source = args.source.resolve()

    report = {
        "schema": 1,
        "source": str(source),
        "blockers": scan(source, PATTERNS),
        "safe_16bit_evidence": scan(source, SAFE_PATTERNS),
    }
    report["blocker_counts"] = {k: len(v) for k, v in report["blockers"].items()}
    report["safe_evidence_counts"] = {k: len(v) for k, v in report["safe_16bit_evidence"].items()}

    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

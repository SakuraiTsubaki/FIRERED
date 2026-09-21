#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SECTOR_SIZE = 0x1000
SECTOR_DATA_SIZE = 0xF80
SECTOR_SIGNATURE = 0x08012025
SECTION_SIZES = [
    0xF24,
    0xF80, 0xF80, 0xF80, 0xEE8,
    0xF80, 0xF80, 0xF80, 0xF80, 0xF80, 0xF80, 0xF80, 0xF80, 0x7D0,
]
EXTENSION_TAILS = {0: 0xF24, 4: 0xEE8, 13: 0x7D0}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gba_header_checksum(data: bytes) -> int:
    return (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF


def save_checksum(data: bytes) -> int:
    total = 0
    for offset in range(0, len(data) // 4 * 4, 4):
        total = (total + struct.unpack_from("<I", data, offset)[0]) & 0xFFFFFFFF
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def parse_rom(path: Path) -> dict:
    data = path.read_bytes()
    libs = []
    for match in re.finditer(rb"FLASH1M_V[0-9]+", data):
        libs.append({"offset": match.start(), "name": match.group().decode("ascii")})
    return {
        "kind": "rom",
        "file": path.name,
        "size": len(data),
        "sha256": sha256(data),
        "title": data[0xA0:0xAC].rstrip(b"\0").decode("ascii", "replace"),
        "game_code": data[0xAC:0xB0].decode("ascii", "replace"),
        "maker": data[0xB0:0xB2].decode("ascii", "replace"),
        "revision": data[0xBC],
        "header_checksum": data[0xBD],
        "calculated_header_checksum": gba_header_checksum(data),
        "header_checksum_valid": data[0xBD] == gba_header_checksum(data),
        "save_library": libs,
    }


def parse_save(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) % SECTOR_SIZE:
        raise ValueError(f"{path}: size is not a multiple of 0x1000")

    sections = []
    for physical in range(len(data) // SECTOR_SIZE):
        sector = data[physical * SECTOR_SIZE:(physical + 1) * SECTOR_SIZE]
        section_id, stored_checksum = struct.unpack_from("<HH", sector, 0xFF4)
        signature, counter = struct.unpack_from("<II", sector, 0xFF8)
        entry = {
            "physical_sector": physical,
            "section_id": section_id,
            "signature": f"0x{signature:08X}",
            "counter": counter,
        }
        if signature == SECTOR_SIGNATURE and section_id < len(SECTION_SIZES):
            calculated = save_checksum(sector[:SECTION_SIZES[section_id]])
            entry.update({
                "stored_checksum": stored_checksum,
                "calculated_checksum": calculated,
                "checksum_valid": stored_checksum == calculated,
            })
        sections.append(entry)

    normal = [
        x for x in sections
        if x["signature"] == f"0x{SECTOR_SIGNATURE:08X}" and x["section_id"] < 14
    ]
    counters = sorted({x["counter"] for x in normal})
    active = max(counters) if counters else None
    active_rows = [x for x in normal if x["counter"] == active]
    active_by_id = {x["section_id"]: x for x in active_rows}

    tails = []
    if active is not None and all(i in active_by_id for i in EXTENSION_TAILS):
        for section_id, used_size in EXTENSION_TAILS.items():
            physical = active_by_id[section_id]["physical_sector"]
            sector = data[physical * SECTOR_SIZE:(physical + 1) * SECTOR_SIZE]
            tail = sector[used_size:SECTOR_DATA_SIZE]
            tails.append({
                "section_id": section_id,
                "bytes": len(tail),
                "all_zero": all(value == 0 for value in tail),
            })

    return {
        "kind": "save",
        "file": path.name,
        "size": len(data),
        "sha256": sha256(data),
        "save_counters": counters,
        "active_counter": active,
        "valid_normal_sectors": len(normal),
        "all_normal_checksums_valid": all(x.get("checksum_valid", False) for x in normal),
        "extension_tails": tails,
        "special_sectors_28_31_blank": (
            len(data) >= 32 * SECTOR_SIZE
            and all(value == 0 for value in data[28 * SECTOR_SIZE:32 * SECTOR_SIZE])
        ),
        "sections": sections,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect FireRed GBA headers and retail 128 KiB save-sector structure."
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    results = []
    for path in args.inputs:
        suffix = path.suffix.lower()
        if suffix == ".gba":
            results.append(parse_rom(path))
        elif suffix == ".sav":
            results.append(parse_save(path))
        else:
            raise SystemExit(f"unsupported input: {path}")

    report = {
        "schema": 1,
        "section_sizes": SECTION_SIZES,
        "results": results,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

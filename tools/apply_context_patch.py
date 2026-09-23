#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


class PatchError(RuntimeError):
    pass


def parse_patch(text: str):
    current_path = None
    hunk = None
    hunks = []

    def finish_hunk():
        nonlocal hunk
        if hunk is not None:
            if not hunk["lines"]:
                raise PatchError(f"empty hunk for {hunk['path']}")
            hunks.append(hunk)
            hunk = None

    raw_lines = text.splitlines(keepends=True)
    for line_index, raw in enumerate(raw_lines):
        line = raw.rstrip("\n")
        if line.startswith("--- a/"):
            finish_hunk()
            current_path = line[6:]
            continue
        if line.startswith("+++ b/"):
            continue
        if line.startswith("@@"):
            finish_hunk()
            if current_path is None:
                raise PatchError("hunk before file header")
            hunk = {"path": current_path, "lines": []}
            continue
        if hunk is None:
            continue

        if raw.startswith("+"):
            hunk["lines"].append(("+", raw[1:]))
        elif raw.startswith("-"):
            hunk["lines"].append(("-", raw[1:]))
        elif raw.startswith(" "):
            # Most files use standard unified-diff context, where the first
            # space is a marker. Some early FIRERED project patches instead
            # stored indented source lines literally, with no extra marker.
            # Preserve both forms and resolve uniquely at apply time.
            hunk["lines"].append((" ", raw))
        elif line == "":
            next_line = raw_lines[line_index + 1] if line_index + 1 < len(raw_lines) else ""
            if next_line.startswith("@@") or next_line.startswith("--- a/") or next_line == "":
                finish_hunk()
            else:
                hunk["lines"].append((" ", raw))
        else:
            finish_hunk()

    finish_hunk()
    return hunks


def build_variant(lines, literal_context: bool):
    old_parts = []
    new_parts = []
    for op, raw in lines:
        if op == "+":
            new_parts.append(raw)
        elif op == "-":
            old_parts.append(raw)
        else:
            if raw == "\n":
                ctx = raw
            elif literal_context:
                ctx = raw
            else:
                ctx = raw[1:]
            old_parts.append(ctx)
            new_parts.append(ctx)
    return "".join(old_parts), "".join(new_parts)


def apply_hunks(root: Path, patch_path: Path, check_only: bool) -> None:
    hunks = parse_patch(patch_path.read_text(encoding="utf-8"))
    staged: dict[Path, str] = {}

    for hunk_no, hunk in enumerate(hunks, 1):
        path = root / hunk["path"]
        if path not in staged:
            staged[path] = path.read_text(encoding="utf-8")

        data = staged[path]
        candidates = []
        for literal_context in (False, True):
            old, new = build_variant(hunk["lines"], literal_context)
            pair = (old, new)
            if pair not in candidates:
                candidates.append(pair)

        chosen = None
        diagnostics = []
        for old, new in candidates:
            count = data.count(old)
            diagnostics.append((count, old))
            if count == 1:
                chosen = (old, new)
                break

        if chosen is None:
            detail = "; ".join(
                f"variant{n + 1} matched {count} times old={old[:220].replace(chr(10), '<NL>')!r}"
                for n, (count, old) in enumerate(diagnostics)
            )
            raise PatchError(
                f"{patch_path.name}: hunk {hunk_no} for {hunk['path']} "
                f"did not match uniquely; {detail}"
            )

        old, new = chosen
        staged[path] = data.replace(old, new, 1)

    if not check_only:
        for path, data in staged.items():
            path.write_text(data, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Apply FIRERED context patches whose @@ headers omit line ranges."
    )
    ap.add_argument("source", type=Path, help="target source tree")
    ap.add_argument("patches", nargs="+", type=Path)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    root = args.source.resolve()
    for patch in args.patches:
        apply_hunks(root, patch.resolve(), args.check)
        print(("checked" if args.check else "applied"), patch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

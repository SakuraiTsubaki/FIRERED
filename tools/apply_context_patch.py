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
            if not hunk["old"] and not hunk["new"]:
                raise PatchError(f"empty hunk for {hunk['path']}")
            hunks.append(hunk)
            hunk = None

    for raw in text.splitlines(keepends=True):
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
            hunk = {"path": current_path, "old": [], "new": []}
            continue
        if hunk is None:
            continue

        if raw.startswith("+"):
            hunk["new"].append(raw[1:])
        elif raw.startswith("-"):
            hunk["old"].append(raw[1:])
        elif raw.startswith(" "):
            hunk["old"].append(raw[1:])
            hunk["new"].append(raw[1:])
        elif line == "":
            # Bare blank lines in the project patch format are context lines.
            hunk["old"].append(raw)
            hunk["new"].append(raw)
        else:
            # Metadata between file blocks is ignored.
            finish_hunk()

    finish_hunk()
    return hunks


def apply_hunks(root: Path, patch_path: Path, check_only: bool) -> None:
    hunks = parse_patch(patch_path.read_text(encoding="utf-8"))
    staged: dict[Path, str] = {}

    for hunk_no, hunk in enumerate(hunks, 1):
        path = root / hunk["path"]
        if path not in staged:
            staged[path] = path.read_text(encoding="utf-8")

        old = "".join(hunk["old"])
        new = "".join(hunk["new"])
        data = staged[path]

        count = data.count(old)
        if count != 1:
            preview = old[:240].replace("\n", "\\n")
            raise PatchError(
                f"{patch_path.name}: hunk {hunk_no} for {hunk['path']} "
                f"matched {count} times; expected exactly once; old={preview!r}"
            )
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

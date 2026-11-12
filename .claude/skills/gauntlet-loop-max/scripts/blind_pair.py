#!/usr/bin/env python3
"""Build a blind pair for the gauntlet critic.

Usage: blind_pair.py <ours> <bar> <output_dir>

Copies both files to <output_dir>/A.<ext> and B.<ext> in random order and prints the key
(ours=A or ours=B) to stdout only, so the lead agent can keep it in its ledger. Nothing in the
output directory reveals the key, so the critic can't tell which version is ours.
"""
import secrets
import shutil
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: blind_pair.py <ours> <bar> <output_dir>", file=sys.stderr)
        return 2
    ours, bar, out = Path(argv[1]), Path(argv[2]), Path(argv[3])
    for p in (ours, bar):
        if not p.is_file():
            print(f"file not found: {p}", file=sys.stderr)
            return 2
    if ours.suffix.lower() != bar.suffix.lower():
        # Different extensions would give the origin away.
        print(
            f"different formats ({ours.suffix} and {bar.suffix}): convert both to the same format first "
            "(e.g. sips -s format png in.webp --out in.png on macOS)",
            file=sys.stderr,
        )
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("A.*")) + list(out.glob("B.*")):
        old.unlink()
    ours_is_a = secrets.randbelow(2) == 0
    first, second = (ours, bar) if ours_is_a else (bar, ours)
    ext = ours.suffix.lower()
    shutil.copyfile(first, out / f"A{ext}")
    shutil.copyfile(second, out / f"B{ext}")
    print(f"ours={'A' if ours_is_a else 'B'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""Cross-language metrics catalog sync check.

The backend catalog (catalog-backend.py) is the ingestion-time authority:
its METRIC_DIM_SPEC allowlist drops any counter whose metric name or dims
are not declared. The daemon (Go) and app (Dart) catalogs are the reporter
subsets. The lockstep invariant enforced here: every metric name string in
the Go and Dart catalogs appears BYTE-IDENTICAL in the backend catalog.
A single drifted string silently splits one logical counter into two, so
names are compared exactly, never fuzzily.

The companion guarantee (these copies match the code that actually ships)
is enforced by `make check-transparency` in each private repo, which
byte-diffs its live catalog file against the copy in this repo.

Exit 0 on sync, 1 with a diff report on drift.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

# A metric name is a dotted lowercase identifier like "chat.ttft_first".
_METRIC = r"([a-z][a-z0-9_]*\.[a-z0-9_.]+)"


def _extract(path: Path, quote: str) -> set[str]:
    names: set[str] = set()
    pattern = re.compile(r"=\s*" + quote + _METRIC + quote)
    for line in path.read_text().splitlines():
        m = pattern.search(line)
        if m:
            names.add(m.group(1))
    return names


def main() -> int:
    backend = _extract(HERE / "catalog-backend.py", '"')
    daemon = _extract(HERE / "catalog-daemon.go", '"')
    flutter = _extract(HERE / "catalog-flutter.dart", "'")

    if not backend or not daemon or not flutter:
        print("check_sync: FAILED to extract metric names from a catalog "
              f"(backend={len(backend)} daemon={len(daemon)} flutter={len(flutter)})")
        return 1

    ok = True
    for label, subset in (("daemon", daemon), ("flutter", flutter)):
        missing = sorted(subset - backend)
        if missing:
            ok = False
            print(f"check_sync: {label} metrics missing from backend catalog "
                  f"(name drift breaks aggregation): {missing}")

    if ok:
        print(f"check_sync: OK — backend={len(backend)} names; "
              f"daemon={len(daemon)} and flutter={len(flutter)} are exact subsets")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

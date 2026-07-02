"""heart/status.py — render cached Heart state with colour to stdout."""

from __future__ import annotations

import argparse
import datetime
import json
import sys

from heart import dashboard, readiness, state
from heart.heart_color import c_fail


def render(snapshot: dict, quiet: bool = False) -> None:
    """Print the full colour board.

    Thin wrapper over ``heart/dashboard.py`` — the ``fmt="term"`` projection IS
    the unified board, so ``status`` cannot drift from the web / mobile / venv
    surfaces (the "one renderer" invariant). ``status`` observes the full local
    snapshot, so no check family is marked unobserved here.
    """
    verdict = readiness.load_verdict()
    validation = snapshot.get("validation_report") or {}
    print(dashboard.render(snapshot, verdict, validation, fmt="term", quiet=quiet))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pyauto-heart status")
    ap.add_argument("--json", action="store_true", help="print raw state.json to stdout")
    ap.add_argument("--quiet", action="store_true", help="suppress drill-down details")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    ns = ap.parse_args(argv)
    if ns.no_color:
        import os
        os.environ["NO_COLOR"] = "1"

    snapshot = state.load()
    if snapshot is None:
        print(c_fail("no cache yet — run `pyauto-heart tick` first"), file=sys.stderr)
        return 2

    if ns.json:
        json.dump(snapshot, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    render(snapshot, quiet=ns.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())

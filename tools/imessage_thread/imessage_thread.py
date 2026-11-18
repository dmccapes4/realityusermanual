#!/usr/bin/env python3
"""imessage_thread CLI — v0.0.5 (see GAME_PLAN_v0.0.5.md)."""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parent.parent

if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

_env = REPO_ROOT / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(_env)
    except ImportError:
        pass

from pipeline import STAGES, VERSION, run_pipeline  # noqa: E402


def cmd_run(args: argparse.Namespace) -> int:
    images_dir = args.images.resolve()
    if not images_dir.is_dir():
        print(f"not a directory: {images_dir}", file=sys.stderr)
        return 1
    run_dir = run_pipeline(
        images_dir,
        args.out.resolve(),
        args.crop_profile.resolve(),
        slug=args.slug or images_dir.parent.name,
        process_date=args.process_date or datetime.date.today().isoformat(),
        tz=args.tz,
        model_mini=args.model_mini,
        model_41=args.model_41,
        model_4o=args.model_4o,
        stage=args.stage,
        run_dir=args.run_dir.resolve() if args.run_dir else None,
    )
    print(f"run_dir: {run_dir}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=f"imessage_thread v{VERSION}")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run")
    r.add_argument("--images", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--run-dir", type=Path, default=None, help="existing run dir (re-run a stage)")
    r.add_argument("--crop-profile", type=Path, default=TOOL_DIR / "crop_profiles" / "iphone_se_2022_imessage_dark.json")
    r.add_argument("--slug", default="")
    r.add_argument("--tz", default="America/Los_Angeles")
    r.add_argument("--process-date", default="", help="YYYY-MM-DD; default today (assumption 0b)")
    r.add_argument("--model-mini", default="gpt-4.1-mini")
    r.add_argument("--model-41", default="gpt-4.1")
    r.add_argument("--model-4o", default="gpt-4o")
    r.add_argument("--stage", default="all", choices=["all", *STAGES])
    r.set_defaults(func=cmd_run)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

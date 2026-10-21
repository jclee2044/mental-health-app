"""Print a checkpoint's scope; explicitly opt into staging with --stage.

Never commits. Refuses an already populated Git index to avoid mixing work.
"""
import argparse
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    scopes = json.loads((ROOT / "scripts/checkpoints.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", choices=scopes)
    parser.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    command = ["git", "add", "--", *scopes[args.checkpoint]]
    print(shlex.join(command))
    if not args.stage:
        print("Preview only. Add --stage to stage this scope; no commit will be created.")
        return
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True)
    if staged.strip():
        raise SystemExit("The index already contains staged work. Review/commit or unstage it yourself before staging a checkpoint.")
    prerequisites = {"interface": [], "emotion": ["frontend/src/features.js"], "breathing": ["frontend/src/features.js", "backend/app/features/emotion/routes.py"]}
    for path in prerequisites[args.checkpoint]:
        result = subprocess.run(["git", "cat-file", "-e", f"HEAD:{path}"], cwd=ROOT, capture_output=True)
        if result.returncode:
            raise SystemExit("Commit the preceding checkpoint first. Nothing was staged.")
    missing = [path for path in scopes[args.checkpoint] if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing checkpoint files: {', '.join(missing)}")
    subprocess.run(command, cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--stat"], cwd=ROOT, check=True)
    print("Review git diff --cached before committing. No commit was created.")


if __name__ == "__main__":
    main()

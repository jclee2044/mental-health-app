"""Build cumulative commit scopes without touching the real checkout or Git index.

Uses the recorded scaffold baseline, overlays only exact checkpoint scopes, and
borrows the existing project-owned environments. Outputs are ignored snapshots.
"""
import argparse
import io
import json
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPES = json.loads((ROOT / "scripts/checkpoints.json").read_text())


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    print(result.stdout, end="")
    if result.returncode:
        print(result.stderr, end="")
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["all", *SCOPES], default="all")
    args = parser.parse_args()
    output = ROOT / ".checkpoints" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output.mkdir(parents=True)
    baseline = (ROOT / "scripts/checkpoint-base.txt").read_text().strip()
    repository = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True).strip()
    archive = subprocess.check_output(["git", "archive", "--format=tar", baseline], cwd=repository)
    cumulative = []
    results = []
    for number, (stage, paths) in enumerate(SCOPES.items(), 1):
        cumulative.extend(paths)
        if args.stage not in ("all", stage):
            continue
        missing = [path for path in cumulative if not (ROOT / path).exists()]
        if missing:
            if args.stage == "all":
                print(f"Skipping {stage}: feature files are not present in this checkout.")
                continue
            raise SystemExit(f"Missing checkpoint files: {', '.join(missing)}")
        snapshot = output / f"{number:02d}-{stage}"
        snapshot.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(snapshot, filter="data")
        for relative in cumulative:
            source, destination = ROOT / relative, snapshot / relative
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "node_modules", "dist"))
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        (snapshot / "frontend/node_modules").symlink_to(ROOT / "frontend/node_modules", target_is_directory=True)
        print(f"Validating {stage}: {snapshot}", flush=True)
        run(["npm", "test"], snapshot / "frontend")
        # Snapshots are intentionally Git-ignored; lint explicit source roots.
        run(["npm", "exec", "--offline", "--", "oxlint", "--no-ignore", "src", "tests", "pwa", "vite.config.js", "eslint.config.js"], snapshot / "frontend")
        run(["npm", "exec", "--offline", "--", "eslint", ".", "--no-cache"], snapshot / "frontend")
        run(["npm", "run", "build"], snapshot / "frontend")
        if stage != "interface":
            run([str(ROOT / "backend/.venv/bin/python"), "-m", "pytest", "-q"], snapshot / "backend")
        results.append({"stage": stage, "path": str(snapshot), "result": "passed"})
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Checkpoint evidence: {output / 'results.json'}")


if __name__ == "__main__":
    main()

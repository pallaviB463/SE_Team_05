"""Run the complete APAS test suite, regenerate the deliverables and fill the team templates in ../testing/.

    python tools/run_all.py              # run all tests, then build deliverables/
    python tools/run_all.py --new-cycle  # archive the current results as cycle 1 first
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-cycle", action="store_true",
                        help="copy the current results/*.json to results/cycle1/ before running")
    args = parser.parse_args()
    results = ROOT / "results"
    if args.new_cycle and (results / "execution_results.json").exists():
        (results / "cycle1").mkdir(parents=True, exist_ok=True)
        for f in results.glob("*.json"):
            shutil.copy(f, results / "cycle1" / f.name)
    for f in results.glob("*.json"):
        f.unlink()
    code = subprocess.call([sys.executable, "-m", "pytest", "-p", "no:cacheprovider"], cwd=ROOT)
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "generate_reports.py")], cwd=ROOT)
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "fill_team_templates.py")], cwd=ROOT)
    return code


if __name__ == "__main__":
    sys.exit(main())

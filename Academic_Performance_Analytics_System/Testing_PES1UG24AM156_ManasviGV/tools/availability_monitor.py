"""Long-running availability monitor for APAS-NF-002 (>= 99% monthly availability).

Polls GET <base>/api/health at a fixed interval and appends each result to a CSV log.
Run it against the deployed instance for a full calendar month, then report:

    python tools/availability_monitor.py https://apas.example.edu --interval 60
    python tools/availability_monitor.py --report results/availability_log.csv \
        --maintenance 2026-11-08T02:00/2026-11-08T04:00

Scheduled maintenance windows are excluded from the calculation, as the SRS allows.
"""
import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_LOG = Path(__file__).resolve().parent.parent / "results" / "availability_log.csv"


def monitor(base, interval, log, verify):
    log.parent.mkdir(exist_ok=True)
    new = not log.exists()
    with log.open("a", newline="") as fh:
        writer = csv.writer(fh)
        if new:
            writer.writerow(["timestamp_utc", "status", "http_code", "latency_s"])
        while True:
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            start = time.perf_counter()
            try:
                r = requests.get(f"{base.rstrip('/')}/api/health", timeout=10, verify=verify)
                ok, code = r.status_code == 200 and r.json().get("status") == "ok", r.status_code
            except (requests.RequestException, ValueError):
                ok, code = False, ""
            writer.writerow([ts, "up" if ok else "down", code, round(time.perf_counter() - start, 3)])
            fh.flush()
            time.sleep(interval)


def report(log, maintenance):
    windows = [tuple(datetime.fromisoformat(p).replace(tzinfo=timezone.utc) for p in w.split("/")) for w in maintenance]
    up = total = 0
    with log.open() as fh:
        for row in csv.DictReader(fh):
            ts = datetime.fromisoformat(row["timestamp_utc"])
            if any(a <= ts <= b for a, b in windows):
                continue
            total += 1
            up += row["status"] == "up"
    pct = 100 * up / total if total else 0.0
    print(f"Probes (excluding maintenance): {total}; up: {up}; availability: {pct:.3f}% "
          f"-> {'MEETS' if pct >= 99 else 'DOES NOT MEET'} the 99% target (APAS-NF-002)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", nargs="?", help="base URL of the APAS deployment")
    parser.add_argument("--interval", type=int, default=60, help="seconds between probes")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--ca", help="CA bundle for self-signed test certificates")
    parser.add_argument("--report", type=Path, help="summarise an existing log instead of monitoring")
    parser.add_argument("--maintenance", nargs="*", default=[], help="ISO start/end windows to exclude")
    args = parser.parse_args()
    if args.report:
        report(args.report, args.maintenance)
    elif args.base:
        monitor(args.base, args.interval, args.log, args.ca or True)
    else:
        parser.error("give a base URL to monitor or --report <log>")


if __name__ == "__main__":
    main()

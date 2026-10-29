"""Run the APAS reference build locally for manual / exploratory testing.

    python run_app.py            # http://127.0.0.1:5000 (HTTPS enforcement off for local dev)
    python run_app.py --https    # https://127.0.0.1:5443 with a self-signed certificate
"""
import argparse
import subprocess
import sys
from pathlib import Path

from apas import create_app, make_ssl_context
from apas.db import connect
from apas.seed import add_synthetic_students, load_dataset

HERE = Path(__file__).resolve().parent
DB = HERE / "results" / "demo_apas.db"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--https", action="store_true")
    parser.add_argument("--reset", action="store_true", help="recreate the demo database")
    args = parser.parse_args()
    DB.parent.mkdir(exist_ok=True)
    if args.reset and DB.exists():
        DB.unlink()
    if not DB.exists():
        conn = connect(DB)
        load_dataset(conn)
        add_synthetic_students(conn, 50)
        conn.close()
    app = create_app({"DATABASE": str(DB), "ENFORCE_HTTPS": args.https})
    if args.https:
        cert, key = HERE / "results" / "dev_cert.pem", HERE / "results" / "dev_key.pem"
        if not cert.exists():
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "30",
                            "-subj", "/CN=localhost", "-keyout", str(key), "-out", str(cert)], check=True)
        app.run(port=5443, ssl_context=make_ssl_context(cert, key))
    else:
        app.run(port=5000)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Local reviewer desk (the same tree the live site serves).

A PDF cannot run this. This server can.

  .venv/bin/python tools/desk_browser.py
"""

from __future__ import annotations

import argparse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / "web"


class DeskHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()}  {args[0]}")

    def end_headers(self):
        path = self.path.split("?", 1)[0]
        if path.endswith(".pdf"):
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", "inline")
        super().end_headers()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    if not (WEB / "index.html").exists():
        raise SystemExit("web/ missing. Run tools/build_desks.py")
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), DeskHandler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Inbox {url}")
    print("  /m/how-to-fly/")
    print("  /m/glacial-cell/")
    print("  /m/plume-wave/")
    print("  /m/how-tos/")
    print("  /m/reality-user-manual/")
    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nclosed")


if __name__ == "__main__":
    main()

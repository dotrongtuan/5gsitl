from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from tools.common import append_jsonl, env_path, load_json


class Handler(BaseHTTPRequestHandler):
    def _send(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/state":
            self._send(load_json(env_path("STATE_FILE", "outputs/runtime/state.json"), {}))
            return
        if path == "/metrics":
            self._send(load_json(env_path("METRICS_FILE", "outputs/runtime/metrics.json"), {}))
            return
        if path == "/events":
            event_log = Path(env_path("EVENT_LOG", "outputs/runtime/events.jsonl"))
            payload = []
            if event_log.exists():
                payload = [json.loads(line) for line in event_log.read_text(encoding="utf-8").splitlines()[-50:]]
            self._send(payload)
            return
        self._send({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/publish":
            self._send({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or "{}")
        append_jsonl(env_path("EVENT_LOG", "outputs/runtime/events.jsonl"), payload)
        self._send({"status": "ok"})


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    serve_cmd = sub.add_parser("serve")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", default=18080, type=int)
    args = parser.parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()

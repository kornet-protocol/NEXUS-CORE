#!/usr/bin/env python3
# =====================================================================
# NEXUS KORNET ENGINE: Service Entrypoint
# Starts HTTP server for core engine API
# =====================================================================

from __future__ import annotations

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

try:
    from .genesis_protocol import GenesisProtocol
    from .production_config import ProductionConfig
except ImportError:
    from genesis_protocol import GenesisProtocol
    from production_config import ProductionConfig


class NexusHandler(BaseHTTPRequestHandler):
    protocol = GenesisProtocol()

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "environment": os.getenv("NEXUS_ENV", "unknown")})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/verify":
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))
            result = self.protocol.verify_and_mint_zkp(
                user_zk_proof=body.get("zk_proof"),
                action_type=body.get("action_type", "tree_planted"),
                hardware_signature=body.get("hardware_signature", ""),
                network_nodes=body.get("network_nodes", []),
                action_id=body.get("action_id"),
            )
            self.send_json(200, {"result": result})
        else:
            self.send_json(404, {"error": "Not found"})

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def main():
    config = ProductionConfig()
    port = int(os.getenv("NEXUS_PORT", "8080"))
    server = HTTPServer(("0.0.0.0", port), NexusHandler)
    print(f"NEXUS Core Engine listening on :{port} [{config.environment}]")
    server.serve_forever()


if __name__ == "__main__":
    main()

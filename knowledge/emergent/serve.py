#!/usr/bin/env python3
"""Simple static server for the NeXifyAI site artifact."""
import http.server, socketserver, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
DIR = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)
    
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"NeXifyAI site restored at http://localhost:{PORT}")
    httpd.serve_forever()

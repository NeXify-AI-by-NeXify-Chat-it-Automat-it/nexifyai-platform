#!/usr/bin/env python3
"""Check Open Notebook source status"""
import subprocess, json

SSH = ['ssh','-i','/opt/data/ssh_keys/hermes_vps_key','-o','StrictHostKeyChecking=no','root@72.62.152.47']

cmd = "curl -s -H 'Authorization: Bearer 1def!xO2022!!' 'http://localhost:32774/api/sources?notebook=notebook:h94klvy6b0uu3wtq6vby&limit=40'"
r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=15)
d = json.loads(r.stdout)

completed = sum(1 for s in d if s.get("status")=="completed")
pending = sum(1 for s in d if s.get("status")!="completed")
chunked = sum(1 for s in d if s.get("embedded_chunks",0)>0)
print(f"Total: {len(d)} sources")
print(f"Completed: {completed}, Pending: {pending}, Chunked: {chunked}")
for s in d:
    sid = s.get("id","?")[:8]
    title = s.get("title","?")
    status = s.get("status","?")
    chunks = s.get("embedded_chunks",0)
    print(f"  [{sid}] {title[:50]:50s} Status: {status:10s} Chunks: {chunks}")

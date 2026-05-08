import json, os, requests, glob

PORT = "32779"
BASE = f"http://localhost:{PORT}"
EXPORT_DIR = "/opt/nexifyai-website-sicherheitskopie/notebook_exports"

files = sorted(glob.glob(f"{EXPORT_DIR}/source_*.json"))[:36]
count = 0
errors = 0

for f in files:
    try:
        with open(f) as fh:
            data = json.load(fh)
        name = data.get("name", os.path.basename(f))[:200]
        stype = data.get("type", "url")
        url = data.get("url", "")
        content = data.get("content", data.get("text", url))[:5000]
        
        payload = {"name": name, "type": stype}
        if url: payload["url"] = url
        if content: payload["content"] = str(content)[:5000]
        payload["description"] = f"Importiert via NeXifyAI Sync: {name}"
        
        r = requests.post(f"{BASE}/api/sources", json=payload, timeout=15)
        if r.status_code in (200, 201):
            count += 1
        else:
            errors += 1
    except Exception as e:
        errors += 1

print(f"Importiert: {count}/{len(files)}, Fehler: {errors}")

r = requests.get(f"{BASE}/api/sources", timeout=10)
data = r.json()
total = len(data) if isinstance(data, list) else data.get("total", "?")
print(f"Quellen aktuell: {total}")

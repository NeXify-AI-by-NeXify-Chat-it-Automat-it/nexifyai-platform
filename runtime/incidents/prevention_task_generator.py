#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("prevention")
TPL = {"service_down":"Add health check for {s}","memory_pressure":"Set memory limit for {s}","disk_full":"Add disk alert at 80%","tls_expiry":"Add cert monitoring"}
def gen(inc=None):
    if not inc: inc = {"causes":["service_down"],"services":["backend"]}
    tasks = [{"title":TPL.get(c,"Review pattern").replace("{s}",inc.get("services",["unknown"])[0]),"priority":"P1"} for c in inc.get("causes",[])]
    if not tasks: tasks = [{"title":"Add monitoring for incident pattern","priority":"P2"}]
    return tasks
def main():
    inc = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {"causes":["service_down"],"services":["backend"]}
    print(json.dumps(gen(inc), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()

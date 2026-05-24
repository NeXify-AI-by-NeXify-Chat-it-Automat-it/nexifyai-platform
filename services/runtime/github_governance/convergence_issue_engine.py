#!/usr/bin/env python3
import json, logging, os, sys
log = logging.getLogger("conv-issue")
def gen(report: dict = None) -> list:
    if not report: report = {"checks":[{"check":"Temporal","passed":False}]}
    return [{"title":f"Converge fail: {c.get('check')}","severity":"warning","project":"Ops"} for c in report.get("checks",[]) if not c.get("passed")]
def main():
    r = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    print(json.dumps(gen(r), indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()

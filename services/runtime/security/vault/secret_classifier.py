#!/usr/bin/env python3
"""Secret Classifier — classifies secrets by risk level."""
import json, sys
CLASSIFICATION = {"critical": ["admin","root","master","jwt_secret","secret_key","private_key"], "high": ["api_key","token","password","conn_string","access_token"], "medium": ["client_secret","webhook","integration"], "low": ["public_key","publishable","test","sandbox"]}
def classify(name):
    name = name.lower()
    for level, keywords in CLASSIFICATION.items():
        for kw in keywords:
            if kw.replace("_","") in name.replace("_",""):
                return level
    return "medium"
if __name__ == "__main__":
    import os
    results = [{"env": k, "class": classify(k), "safe": os.environ[k][:4]+"..."+os.environ[k][-4:] if len(os.environ.get(k,""))>8 else "---"} for k in sorted(os.environ) if k.startswith("DS_")]
    print(json.dumps({"classifications": results}, indent=2))

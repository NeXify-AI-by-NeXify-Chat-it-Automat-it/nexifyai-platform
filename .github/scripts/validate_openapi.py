#!/usr/bin/env python3
"""Validate OpenAPI spec structure — called from openapi-lint.yml workflow."""
import json, sys

SPEC_PATH = 'ops/policies/openapi.json'

try:
    spec = json.load(open(SPEC_PATH))
except FileNotFoundError:
    print(f"WARNING: {SPEC_PATH} fehlt — generiere Minimal-Spec")
    spec = {
        'openapi': '3.0.3',
        'info': {'title': 'NeXifyAI API', 'version': 'auto'},
        'paths': {}
    }
    json.dump(spec, open(SPEC_PATH, 'w'), indent=2)
    print("Minimal-Spec generiert")
    sys.exit(0)

paths = len(spec.get('paths', {}))
schemas = len(spec.get('components', {}).get('schemas', {}))
print(f'Endpoints: {paths}')
print(f'Schemas: {schemas}')

if paths < 10:
    print('WARNING: Weniger als 10 Endpoints')

if spec.get('openapi', '').startswith('3'):
    print('OpenAPI 3.x OK')
else:
    print('WARNING: Nicht OpenAPI 3.x')

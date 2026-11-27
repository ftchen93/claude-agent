#!/usr/bin/env python3
"""Validate a handoff file against its schema.

Usage: validate.py <schema-name> <file.json>
  schema-name: quality-report | dor-result | test-cases | feasibility | triage | defect | dod-result
Exit 0 if valid, 1 if not.
"""
import sys

from qe_common import PLUGIN_ROOT, load_json, validate


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    schema = load_json(PLUGIN_ROOT / "shared" / "schemas" / f"{sys.argv[1]}.schema.json")
    errors = validate(load_json(sys.argv[2]), schema)
    if errors:
        print("INVALID")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())

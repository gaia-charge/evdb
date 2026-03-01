#!/usr/bin/env python3
"""Apply verified field extractions to data/ YAML files.

Reads a proposal JSON (one per brand, written by the extraction agents and
filtered to verifier-confirmed entries) and edits the target YAML files
surgically - existing formatting and comments are preserved, only the
affected lines change.

Guard rails:
  - never overwrites a field that already has a value (unless --overwrite)
  - every update must carry a source_url; it is added to metadata.sources
  - the file is re-parsed and re-validated against its JSON Schema after
    editing; on any failure the original text is restored
  - list-valued fields (e.g. performance.motors) are rejected - those need
    hand-written YAML, not mechanical insertion

Proposal format:
{
  "brand": "lexus",
  "updates": [
    {"target": "vehicle-variants/lexus-rz-350e-2025",
     "field": "charging.time_10_to_80_min",
     "value": 30,
     "source_url": "https://...",
     "evidence": "Ladezeit DC 10-80 % (Std./Min.) 00:30"}
  ]
}

Usage:
    python scripts/apply-extraction.py proposals/*.json          # apply
    python scripts/apply-extraction.py --dry-run proposals/*.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas"

SCHEMA_FOR_DIR = {
    "vehicle-variants": "vehicle-variant.schema.json",
    "vehicle-models": "vehicle-model.schema.json",
    "market-availability": "market-availability.schema.json",
    "manufacturers": "manufacturer.schema.json",
}


def fmt_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    # quote anything YAML would coerce away from a plain string: booleans,
    # nulls, dates (2026-03-01 becomes a date object otherwise), numerics
    if (
        s.lower() in {"true", "false", "null", "yes", "no", "on", "off", "~"}
        or re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", s)
        or re.fullmatch(r"[-+]?[\d_]*\.?\d+([eE][-+]?\d+)?", s)
        or any(c in s for c in ':#{}[]&*!|>%@`"\'')
        or s.strip() != s
        or s == ""
    ):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def get_path(d, path):
    for k in path.split("."):
        if not isinstance(d, dict) or d.get(k) is None:
            return None
        d = d[k]
    return d


def block_bounds(lines, header_idx):
    """Return (start, end) line indices of the block body under a header."""
    base = len(lines[header_idx]) - len(lines[header_idx].lstrip())
    i = header_idx + 1
    end = i
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "" or ln.lstrip().startswith("#"):
            i += 1
            continue
        ind = len(ln) - len(ln.lstrip())
        if ind <= base:
            break
        end = i + 1
        i += 1
    return header_idx + 1, end


def find_key(lines, key, start, end, indent):
    pref = " " * indent + key + ":"
    for i in range(start, min(end, len(lines))):
        if lines[i].startswith(pref):
            return i
    return None


def set_field(text, field, value):
    """Insert or replace `field` (dotted, max 2 levels) in YAML text."""
    parts = field.split(".")
    lines = text.splitlines(keepends=True)

    if len(parts) == 1:
        idx = find_key(lines, parts[0], 0, len(lines), 0)
        newline = f"{parts[0]}: {fmt_value(value)}\n"
        if idx is not None:
            lines[idx] = newline
        else:
            meta = find_key(lines, "metadata", 0, len(lines), 0)
            at = meta if meta is not None else len(lines)
            lines.insert(at, newline)
        return "".join(lines)

    if len(parts) != 2:
        raise ValueError(f"unsupported field depth: {field}")

    parent, leaf = parts
    pidx = find_key(lines, parent, 0, len(lines), 0)
    if pidx is None:
        # create the parent block just before metadata (or at EOF)
        meta = find_key(lines, "metadata", 0, len(lines), 0)
        at = meta if meta is not None else len(lines)
        blk = f"{parent}:\n  {leaf}: {fmt_value(value)}\n"
        if at > 0 and lines[at - 1].strip() != "":
            blk = "\n" + blk
        lines.insert(at, blk)
        return "".join(lines)

    # parent must be a block, not an inline value
    if lines[pidx].split(":", 1)[1].strip() not in ("", "|", ">"):
        raise ValueError(f"{parent} is not a block mapping")

    start, end = block_bounds(lines, pidx)
    body = [l for l in lines[start:end] if l.strip()]
    indent = (len(body[0]) - len(body[0].lstrip())) if body else 2
    lidx = find_key(lines, leaf, start, end, indent)
    newline = " " * indent + f"{leaf}: {fmt_value(value)}\n"
    if lidx is not None:
        lines[lidx] = newline
    else:
        lines.insert(end, newline)
    return "".join(lines)


def add_source(text, url):
    doc = yaml.safe_load(text) or {}
    md = doc.get("metadata") or {}
    existing = md.get("sources") or []
    if url in existing:
        return text
    lines = text.splitlines(keepends=True)
    midx = find_key(lines, "metadata", 0, len(lines), 0)
    if midx is None:
        tail = "" if text.endswith("\n") else "\n"
        return text + f'{tail}\nmetadata:\n  sources:\n    - {url}\n'
    start, end = block_bounds(lines, midx)
    body = [l for l in lines[start:end] if l.strip()]
    indent = (len(body[0]) - len(body[0].lstrip())) if body else 2
    sidx = find_key(lines, "sources", start, end, indent)
    if sidx is None:
        lines.insert(end, " " * indent + "sources:\n" + " " * indent + f"  - {url}\n")
    else:
        if lines[sidx].split(":", 1)[1].strip() in ("[]", ""):
            lines[sidx] = " " * indent + "sources:\n"
        # list items may sit at the same indent as the key or deeper; walk to
        # the last one so the new URL is appended rather than prepended
        item_indent, after = indent + 2, sidx + 1
        i = sidx + 1
        while i < len(lines):
            ln = lines[i]
            if ln.strip() == "":
                i += 1
                continue
            ind = len(ln) - len(ln.lstrip())
            if ln.lstrip().startswith("- ") and ind >= indent:
                item_indent, after = ind, i + 1
                i += 1
                continue
            if ind > item_indent:  # continuation of the current item
                after = i + 1
                i += 1
                continue
            break
        lines.insert(after, " " * item_indent + f"- {url}\n")
    return "".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proposals", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true",
                    help="also replace fields that already have a value")
    ap.add_argument("--date", default="2026-03-01", help="metadata.updated_at value")
    args = ap.parse_args()

    validators = {
        d: Draft7Validator(json.loads((SCHEMAS / s).read_text()))
        for d, s in SCHEMA_FOR_DIR.items()
    }

    applied = skipped = failed = 0
    reasons = {}
    touched = {}

    for pf in args.proposals:
        prop = json.loads(Path(pf).read_text())
        for u in prop.get("updates", []):
            target, field = u["target"], u["field"]
            path = DATA / f"{target}.yaml"
            key = f"{target}:{field}"
            if not path.exists():
                failed += 1
                reasons[key] = "target file not found"
                continue
            if not u.get("source_url"):
                failed += 1
                reasons[key] = "no source_url"
                continue
            if isinstance(u["value"], (list, dict)):
                failed += 1
                reasons[key] = "list/dict values need hand-written YAML"
                continue

            original = path.read_text()
            doc = yaml.safe_load(original) or {}
            if get_path(doc, field) is not None and not args.overwrite:
                skipped += 1
                reasons[key] = "already has a value"
                continue

            try:
                text = set_field(original, field, u["value"])
                text = add_source(text, u["source_url"])
                text = set_field(text, "metadata.updated_at", args.date)
                new_doc = yaml.safe_load(text)
                if get_path(new_doc, field) != u["value"]:
                    raise ValueError(
                        f"post-parse mismatch: {get_path(new_doc, field)!r} != {u['value']!r}")
                errs = list(validators[target.split("/")[0]].iter_errors(new_doc))
                if errs:
                    raise ValueError("; ".join(e.message[:90] for e in errs[:2]))
            except Exception as e:
                failed += 1
                reasons[key] = str(e)[:110]
                continue

            if not args.dry_run:
                path.write_text(text)
            applied += 1
            touched[target] = touched.get(target, 0) + 1

    print(f"applied {applied} | skipped {skipped} | failed {failed} "
          f"| files touched {len(touched)}{' (DRY RUN)' if args.dry_run else ''}")
    if failed:
        print("\nfailures:")
        for k, v in list(reasons.items()):
            if "already has a value" not in v:
                print(f"  {k}: {v}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

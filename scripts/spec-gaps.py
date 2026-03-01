#!/usr/bin/env python3
"""Report missing spec fields per brand/model as a fetch work-queue.

Outputs JSON grouped brand -> model -> {model_gaps, variants: {id: [missing]}},
sorted by total gap count, so fetch agents can work brand-by-brand.

Usage:
    python scripts/spec-gaps.py                  # summary table
    python scripts/spec-gaps.py --json out.json  # full queue for agents
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "data"

# Variant fields fillable from official manufacturer sources.
# EPA range deliberately excluded (US-market figure, out of scope).
VARIANT_FIELDS = [
    "charging.time_10_to_80_min",
    "charging.time_0_to_80_min",
    "charging.charging_speed_kmh",  # derivable once charge time is known
    "performance.drive_type",
    "performance.motors",
    "performance.total_torque_nm",
    "performance.acceleration_0_100_sec",
    "features.heat_pump",
    "bidirectional.v2l",
    "efficiency.wltp_kwh_per_100km",
    "range.wltp_city_km",
    "battery.total_kwh",
    "battery.chemistry",
]
# Either 10-80 or 0-80 satisfies the charge-time gap.
CHARGE_TIME_ALTERNATIVES = {
    "charging.time_10_to_80_min",
    "charging.time_0_to_80_min",
}

MODEL_FIELDS = [
    "seating.seats",
    "production_status",
    "platform",
    "dimensions.length_mm",
    "dimensions.wheelbase_mm",
]


def get(d, path):
    for k in path.split("."):
        if not isinstance(d, dict) or d.get(k) is None:
            return None
        d = d[k]
    return d


def load_dir(name):
    out = {}
    for f in sorted((DATA / name).glob("*.yaml")):
        out[f.stem] = yaml.safe_load(f.read_text())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="FILE", help="write full queue as JSON")
    args = ap.parse_args()

    manufacturers = load_dir("manufacturers")
    models = load_dir("vehicle-models")
    variants = load_dir("vehicle-variants")

    queue = defaultdict(lambda: {"website": None, "models": {}})

    for mid, m in models.items():
        brand = (m.get("brand") or m.get("manufacturer_id") or "unknown").lower()
        mfr = manufacturers.get(m.get("manufacturer_id") or "")
        entry = queue[brand]
        if mfr and not entry["website"]:
            entry["website"] = mfr.get("website")
        model_gaps = [f for f in MODEL_FIELDS if get(m, f) is None]
        entry["models"][mid] = {
            "name": m.get("name"),
            "model_gaps": model_gaps,
            "variants": {},
        }

    for vid, v in variants.items():
        m = models.get(v.get("model_id") or "")
        brand = ((m or {}).get("brand") or "unknown").lower()
        model_entry = queue[brand]["models"].setdefault(
            v.get("model_id") or "orphan",
            {"name": v.get("model_id"), "model_gaps": [], "variants": {}},
        )
        missing = [f for f in VARIANT_FIELDS if get(v, f) is None]
        # one charge-time figure is enough
        if CHARGE_TIME_ALTERNATIVES - set(missing):
            missing = [f for f in missing if f not in CHARGE_TIME_ALTERNATIVES]
        if missing:
            model_entry["variants"][vid] = {
                "name": v.get("name"),
                "model_year": v.get("model_year"),
                "missing": missing,
            }

    # prune models with nothing missing, count gaps
    report = {}
    for brand, e in queue.items():
        models_out = {
            mid: me
            for mid, me in e["models"].items()
            if me["model_gaps"] or me["variants"]
        }
        if not models_out:
            continue
        total = sum(
            len(me["model_gaps"])
            + sum(len(v["missing"]) for v in me["variants"].values())
            for me in models_out.values()
        )
        report[brand] = {
            "website": e["website"],
            "total_gaps": total,
            "models": models_out,
        }

    ordered = dict(sorted(report.items(), key=lambda kv: -kv[1]["total_gaps"]))

    if args.json:
        Path(args.json).write_text(json.dumps(ordered, indent=2, ensure_ascii=False))
        print(f"wrote {args.json}: {len(ordered)} brands")

    print(f"{'brand':22s} {'models':>6s} {'variants':>8s} {'gaps':>6s}")
    for brand, e in ordered.items():
        nvar = sum(len(m['variants']) for m in e['models'].values())
        print(f"{brand:22s} {len(e['models']):6d} {nvar:8d} {e['total_gaps']:6d}")
    total = sum(e['total_gaps'] for e in ordered.values())
    print(f"{'TOTAL':22s} {'':6s} {'':8s} {total:6d}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate static JSON API files from the EVDB SQLite database.

Produces a directory structure that mimics a REST API, suitable for
deployment to GitHub Pages or any static file host.

Output structure:
  api/
    v1/
      manufacturers.json          - All manufacturers
      manufacturers/{id}.json     - Single manufacturer
      vehicles.json               - All vehicles (summary)
      vehicles/{id}.json          - Single vehicle with full specs
      markets.json                - All market availability
      markets/{code}/vehicles.json - Vehicles available in a market
      queries/
        long-range.json           - Long range EVs (500km+)
        budget.json               - Budget EVs under €40k
        performance.json          - Performance EVs
        most-efficient.json       - Most efficient EVs
        fastest-charging.json     - Fastest charging EVs
      stats.json                  - Database statistics
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def dict_factory(cursor, row):
    """Convert sqlite3 rows to dicts."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def clean_none(obj):
    """Recursively remove None values from dicts for cleaner JSON."""
    if isinstance(obj, dict):
        return {k: clean_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [clean_none(i) for i in obj]
    return obj


def write_json(path: Path, data: dict):
    """Write JSON file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
    print(f"  ✓ {path}")


def generate_api(db_path: str, output_dir: str = "api"):
    """Generate all static API files."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    c = conn.cursor()

    base = Path(output_dir) / "v1"
    now = datetime.now(timezone.utc).isoformat()

    print("Generating static API files...")

    # --- Stats ---
    stats = {}
    for table in ['manufacturers', 'vehicle_models', 'vehicle_variants', 'market_availability']:
        c.execute(f"SELECT COUNT(*) as count FROM {table}")
        stats[table] = c.fetchone()['count']

    c.execute("SELECT DISTINCT market_code FROM market_availability ORDER BY market_code")
    stats['markets'] = [r['market_code'] for r in c.fetchall()]

    write_json(base / "stats.json", {
        "generated_at": now,
        "counts": stats,
    })

    # --- Manufacturers ---
    c.execute("SELECT * FROM manufacturers ORDER BY name")
    manufacturers = c.fetchall()
    write_json(base / "manufacturers.json", {
        "count": len(manufacturers),
        "results": [clean_none(m) for m in manufacturers],
    })

    for mfr in manufacturers:
        c.execute("""
            SELECT vm.*, COUNT(vv.id) as variant_count
            FROM vehicle_models vm
            LEFT JOIN vehicle_variants vv ON vv.model_id = vm.id
            WHERE vm.manufacturer_id = ?
            GROUP BY vm.id
            ORDER BY vm.name
        """, (mfr['id'],))
        models = c.fetchall()
        write_json(base / "manufacturers" / f"{mfr['id']}.json", {
            **clean_none(mfr),
            "models": [clean_none(m) for m in models],
        })

    # --- Vehicles (summary) ---
    c.execute("""
        SELECT 
            v.id, m.brand, m.name as model, v.variant_name, v.model_year,
            m.body_style, v.battery_usable_kwh, v.range_wltp_km,
            v.range_real_world_km, v.total_power_kw, v.dc_charge_power_kw,
            v.drive_type, v.acceleration_0_100_sec, v.top_speed_kph,
            v.weight_curb_kg, v.trunk_capacity_liters,
            v.length_mm, v.width_mm, v.height_mm
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        ORDER BY m.brand, m.name, v.variant_name
    """)
    vehicles_summary = c.fetchall()
    write_json(base / "vehicles.json", {
        "count": len(vehicles_summary),
        "results": [clean_none(v) for v in vehicles_summary],
    })

    # --- Individual vehicles (full specs + market data) ---
    c.execute("SELECT * FROM vehicle_variants ORDER BY id")
    all_variants = c.fetchall()

    for variant in all_variants:
        # Get model info
        c.execute("SELECT * FROM vehicle_models WHERE id = ?", (variant['model_id'],))
        model = c.fetchone() or {}

        # Get market data
        c.execute("""
            SELECT market_code, currency, price_base, price_including_vat,
                   price_after_incentives, available_from, available_until,
                   availability_status, notes
            FROM market_availability
            WHERE variant_id = ?
            ORDER BY market_code
        """, (variant['id'],))
        markets = c.fetchall()

        write_json(base / "vehicles" / f"{variant['id']}.json", {
            **clean_none(variant),
            "brand": model.get('brand'),
            "model_name": model.get('name'),
            "body_style": model.get('body_style'),
            "segment": model.get('segment'),
            "markets": [clean_none(m) for m in markets],
        })

    # --- Markets ---
    c.execute("""
        SELECT market_code, COUNT(*) as vehicle_count, 
               MIN(price_base) as min_price, MAX(price_base) as max_price,
               currency
        FROM market_availability
        GROUP BY market_code
        ORDER BY vehicle_count DESC
    """)
    market_summary = c.fetchall()
    write_json(base / "markets.json", {
        "count": len(market_summary),
        "results": [clean_none(m) for m in market_summary],
    })

    # Per-market vehicle lists
    for market in market_summary:
        code = market['market_code']
        c.execute("""
            SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                   ma.price_base, ma.price_including_vat, ma.currency,
                   ma.price_after_incentives, ma.available_from
            FROM market_availability ma
            JOIN vehicle_variants v ON ma.variant_id = v.id
            JOIN vehicle_models m ON v.model_id = m.id
            WHERE ma.market_code = ?
            ORDER BY m.brand, m.name, v.variant_name
        """, (code,))
        market_vehicles = c.fetchall()
        write_json(base / "markets" / f"{code.lower()}" / "vehicles.json", {
            "market_code": code,
            "count": len(market_vehicles),
            "results": [clean_none(v) for v in market_vehicles],
        })

    # --- Canned queries ---
    queries = {
        "long-range": {
            "title": "Long Range EVs (500km+)",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.range_wltp_km, v.range_real_world_km, v.battery_usable_kwh,
                       v.consumption_real_world_kwh_100km, v.drive_type
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.range_wltp_km >= 500
                ORDER BY v.range_wltp_km DESC
            """,
        },
        "budget": {
            "title": "Budget EVs (under €40,000)",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       ma.price_base as price_eur, v.range_wltp_km, v.battery_usable_kwh,
                       v.dc_charge_power_kw, v.drive_type
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
                WHERE ma.price_base < 40000
                ORDER BY ma.price_base ASC
            """,
        },
        "performance": {
            "title": "Performance EVs (0-100 under 5s)",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.acceleration_0_100_sec, v.total_power_kw, v.top_speed_kph,
                       v.drive_type, v.battery_usable_kwh
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.acceleration_0_100_sec < 5.0 AND v.acceleration_0_100_sec > 0
                ORDER BY v.acceleration_0_100_sec ASC
            """,
        },
        "most-efficient": {
            "title": "Most Efficient EVs",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.consumption_real_world_kwh_100km, v.range_wltp_km,
                       v.range_real_world_km, v.battery_usable_kwh, v.weight_curb_kg
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.consumption_real_world_kwh_100km > 0
                ORDER BY v.consumption_real_world_kwh_100km ASC
                LIMIT 50
            """,
        },
        "fastest-charging": {
            "title": "Fastest Charging EVs",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.dc_charge_power_kw, v.dc_charge_time_10_80_min,
                       v.battery_usable_kwh, v.battery_voltage,
                       CASE WHEN v.battery_voltage >= 700 THEN '800V' ELSE '400V' END as architecture
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.dc_charge_power_kw > 0
                ORDER BY v.dc_charge_power_kw DESC
                LIMIT 50
            """,
        },
        "best-value": {
            "title": "Best Value EVs (lowest €/kWh)",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       ma.price_base as price_eur, v.battery_usable_kwh,
                       ROUND(ma.price_base / v.battery_usable_kwh, 0) as eur_per_kwh,
                       v.range_wltp_km, v.dc_charge_power_kw
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
                WHERE v.battery_usable_kwh > 0 AND ma.price_base > 0
                ORDER BY eur_per_kwh ASC
                LIMIT 50
            """,
        },
        "largest-cargo": {
            "title": "Largest Cargo Capacity",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.trunk_capacity_liters, v.trunk_max_liters, v.frunk_capacity_liters,
                       m.body_style, v.length_mm
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.trunk_capacity_liters > 0
                ORDER BY v.trunk_capacity_liters DESC
                LIMIT 50
            """,
        },
        "best-towing": {
            "title": "Best Towing Capacity",
            "sql": """
                SELECT v.id, m.brand, m.name as model, v.variant_name, v.model_year,
                       v.towing_capacity_braked_kg, v.weight_curb_kg,
                       v.total_power_kw, m.body_style, v.drive_type
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                WHERE v.towing_capacity_braked_kg > 0
                ORDER BY v.towing_capacity_braked_kg DESC
                LIMIT 50
            """,
        },
    }

    for name, query in queries.items():
        c.execute(query['sql'])
        results = c.fetchall()
        write_json(base / "queries" / f"{name}.json", {
            "title": query['title'],
            "count": len(results),
            "results": [clean_none(r) for r in results],
        })

    # --- Index page ---
    write_json(base / "index.json", {
        "name": "EVDB API",
        "version": "1.0",
        "description": "Electric Vehicle Database - Static JSON API",
        "generated_at": now,
        "license": "CC BY-SA 4.0",
        "source": "https://github.com/gaia-charge/evdb",
        "endpoints": {
            "stats": "/v1/stats.json",
            "manufacturers": "/v1/manufacturers.json",
            "manufacturer": "/v1/manufacturers/{id}.json",
            "vehicles": "/v1/vehicles.json",
            "vehicle": "/v1/vehicles/{id}.json",
            "markets": "/v1/markets.json",
            "market_vehicles": "/v1/markets/{code}/vehicles.json",
            "queries": {
                "long_range": "/v1/queries/long-range.json",
                "budget": "/v1/queries/budget.json",
                "performance": "/v1/queries/performance.json",
                "most_efficient": "/v1/queries/most-efficient.json",
                "fastest_charging": "/v1/queries/fastest-charging.json",
                "best_value": "/v1/queries/best-value.json",
                "largest_cargo": "/v1/queries/largest-cargo.json",
                "best_towing": "/v1/queries/best-towing.json",
            },
        },
        "database_download": "https://github.com/gaia-charge/evdb/releases/latest/download/evdb.db",
    })

    conn.close()

    # Count generated files
    total = sum(1 for _ in Path(output_dir).rglob("*.json"))
    print(f"\n✨ Generated {total} API files in {output_dir}/")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "evdb.db"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "api"
    generate_api(db_path, output_dir)

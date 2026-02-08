#!/usr/bin/env python3
"""
EVDB Data Integrity Checker
Validates database relationships and data quality
"""

import sqlite3
from datetime import datetime

def check_integrity():
    print("╭─────────────────────────────────╮")
    print("│ EVDB Data Integrity Check       │")
    print("╰─────────────────────────────────╯")
    print()
    
    conn = sqlite3.connect('evdb.db')
    c = conn.cursor()
    
    issues = []
    
    # Check 1: Orphaned variants (variants without models)
    orphaned = c.execute("""
        SELECT v.id FROM vehicle_variants v
        LEFT JOIN vehicle_models m ON v.model_id = m.id
        WHERE m.id IS NULL
    """).fetchall()
    if orphaned:
        issues.append(f"❌ {len(orphaned)} orphaned variants found")
    else:
        print("✓ No orphaned variants")
    
    # Check 2: Variants without market data
    no_market = c.execute("""
        SELECT v.id, m.name FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        WHERE v.id NOT IN (SELECT DISTINCT variant_id FROM market_availability)
    """).fetchall()
    if no_market:
        issues.append(f"⚠ {len(no_market)} variants without any market data")
        for vid, model in no_market[:5]:
            print(f"  - {model}: {vid}")
    else:
        print("✓ All variants have market data")
    
    # Check 3: Missing critical specs
    missing_range = c.execute("""
        SELECT COUNT(*) FROM vehicle_variants
        WHERE range_wltp_km IS NULL AND range_epa_km IS NULL
    """).fetchone()[0]
    if missing_range > 0:
        issues.append(f"⚠ {missing_range} variants missing range data")
    else:
        print("✓ All variants have range data")
    
    missing_battery = c.execute("""
        SELECT COUNT(*) FROM vehicle_variants
        WHERE battery_usable_kwh IS NULL
    """).fetchone()[0]
    if missing_battery > 0:
        issues.append(f"⚠ {missing_battery} variants missing battery capacity")
    else:
        print("✓ All variants have battery capacity")
    
    missing_power = c.execute("""
        SELECT COUNT(*) FROM vehicle_variants
        WHERE total_power_kw IS NULL
    """).fetchone()[0]
    if missing_power > 0:
        issues.append(f"⚠ {missing_power} variants missing power data")
    else:
        print("✓ All variants have power data")
    
    # Check 4: Germany market coverage
    total_variants = c.execute("SELECT COUNT(*) FROM vehicle_variants").fetchone()[0]
    de_coverage = c.execute("""
        SELECT COUNT(DISTINCT variant_id) FROM market_availability
        WHERE market_code = 'DE'
    """).fetchone()[0]
    
    coverage_pct = 100 * de_coverage / total_variants if total_variants > 0 else 0
    print(f"✓ Germany market coverage: {de_coverage}/{total_variants} ({coverage_pct:.1f}%)")
    
    # Check 5: Price data quality
    prices_in_de = c.execute("""
        SELECT COUNT(*) FROM market_availability
        WHERE market_code = 'DE' AND price_base IS NOT NULL
    """).fetchone()[0]
    price_pct = 100 * prices_in_de / de_coverage if de_coverage > 0 else 0
    print(f"✓ DE market with prices: {prices_in_de}/{de_coverage} ({price_pct:.1f}%)")
    
    # Summary
    print()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("╭────────────────────────────────╮")
        print("│ ✅ All integrity checks passed │")
        print("╰────────────────────────────────╯")
        return 0
    
    conn.close()

if __name__ == "__main__":
    exit(check_integrity())

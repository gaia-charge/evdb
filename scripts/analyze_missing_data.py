#!/usr/bin/env python3
"""
Analyze EVDB for missing data and generate prioritized recommendations.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def load_yaml(file_path: Path) -> dict:
    """Load a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return {}

def check_nested_field(data: dict, path: str) -> bool:
    """Check if a nested field exists and has a value."""
    keys = path.split('.')
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return current is not None and current != ""

def analyze_variant(file_path: Path) -> Dict[str, List[str]]:
    """Analyze a single vehicle variant for missing data."""
    data = load_yaml(file_path)
    missing = defaultdict(list)
    variant_id = data.get('id', file_path.stem)
    
    # Critical fields that should always be present
    critical_fields = {
        'battery.usable_capacity_kwh': 'Battery usable capacity',
        'battery.total_capacity_kwh': 'Battery total capacity',
        'range.wltp_combined_km': 'WLTP range',
        'charging.ac_charging.max_power_kw': 'AC charging power',
        'charging.dc_charging.max_power_kw': 'DC charging power',
        'performance.acceleration_0_100_kmh_sec': 'Acceleration 0-100',
        'performance.top_speed_kmh': 'Top speed',
        'motor.total_power_kw': 'Motor power',
        'motor.total_torque_nm': 'Motor torque',
    }
    
    # Important fields (nice to have)
    important_fields = {
        'range.wltp_city_km': 'WLTP city range',
        'range.wltp_highway_km': 'WLTP highway range',
        'range.real_world_mixed_km': 'Real-world range',
        'consumption.wltp_combined_kwh_100km': 'WLTP consumption',
        'consumption.real_world_mixed_kwh_100km': 'Real-world consumption',
        'charging.dc_charging.time_10_80_min': 'DC charging time 10-80%',
        'charging.ac_charging.time_0_100_hours': 'AC charging time 0-100%',
        'dimensions.length_mm': 'Length',
        'dimensions.width_mm': 'Width',
        'dimensions.height_mm': 'Height',
        'dimensions.wheelbase_mm': 'Wheelbase',
        'cargo.trunk_capacity_liters': 'Trunk capacity',
        'weight.curb_weight_kg': 'Curb weight',
        'weight.towing_capacity_braked_kg': 'Towing capacity (braked)',
    }
    
    # Optional/advanced fields
    optional_fields = {
        'dimensions.ground_clearance_mm': 'Ground clearance',
        'cargo.trunk_max_liters': 'Trunk max (seats down)',
        'cargo.frunk_capacity_liters': 'Frunk capacity',
        'weight.gross_vehicle_weight_kg': 'Gross vehicle weight',
        'weight.payload_kg': 'Payload',
        'weight.towing_capacity_unbraked_kg': 'Towing capacity (unbraked)',
        'battery.architecture_voltage': 'Battery voltage',
        'battery.chemistry': 'Battery chemistry',
        'charging.dc_charging.curve_description': 'DC charging curve',
        'efficiency.heat_pump': 'Heat pump availability',
        'efficiency.recuperation_power_max_kw': 'Max recuperation power',
    }
    
    # Check each category
    for field, description in critical_fields.items():
        if not check_nested_field(data, field):
            missing['critical'].append(f"{description} ({field})")
    
    for field, description in important_fields.items():
        if not check_nested_field(data, field):
            missing['important'].append(f"{description} ({field})")
    
    for field, description in optional_fields.items():
        if not check_nested_field(data, field):
            missing['optional'].append(f"{description} ({field})")
    
    return {
        'variant_id': variant_id,
        'file': str(file_path.name),
        'missing': dict(missing)
    }

def analyze_market_coverage(data_dir: Path) -> Dict:
    """Analyze market availability coverage."""
    variants_dir = data_dir / 'vehicle-variants'
    market_dir = data_dir / 'market-availability'
    
    # Get all variant IDs
    all_variants = set()
    for variant_file in variants_dir.glob('*.yaml'):
        data = load_yaml(variant_file)
        if 'id' in data:
            all_variants.add(data['id'])
    
    # Get market coverage per country
    market_coverage = defaultdict(set)
    for market_file in market_dir.glob('*.yaml'):
        name = market_file.stem
        # Format: variant-id-country
        parts = name.split('-')
        if len(parts) >= 2:
            country = parts[-1].lower()
            variant_id = '-'.join(parts[:-1])
            market_coverage[country].add(variant_id)
    
    # Calculate coverage percentages
    total_variants = len(all_variants)
    coverage_stats = {}
    for country, variants in market_coverage.items():
        coverage_pct = (len(variants) / total_variants * 100) if total_variants > 0 else 0
        missing_count = total_variants - len(variants)
        coverage_stats[country] = {
            'covered': len(variants),
            'missing': missing_count,
            'total': total_variants,
            'percentage': round(coverage_pct, 1)
        }
    
    return coverage_stats

def main():
    # Determine data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}", file=sys.stderr)
        sys.exit(1)
    
    variants_dir = data_dir / 'vehicle-variants'
    
    print("=" * 80)
    print("EVDB Missing Data Analysis")
    print("=" * 80)
    print()
    
    # Analyze all variants
    all_missing = []
    critical_count = 0
    important_count = 0
    optional_count = 0
    
    for variant_file in sorted(variants_dir.glob('*.yaml')):
        result = analyze_variant(variant_file)
        missing = result['missing']
        
        if missing.get('critical') or missing.get('important'):
            all_missing.append(result)
            critical_count += len(missing.get('critical', []))
            important_count += len(missing.get('important', []))
            optional_count += len(missing.get('optional', []))
    
    # Summary statistics
    total_variants = len(list(variants_dir.glob('*.yaml')))
    variants_with_missing = len(all_missing)
    
    print(f"📊 SUMMARY")
    print(f"{'─' * 80}")
    print(f"Total variants analyzed: {total_variants}")
    print(f"Variants with missing data: {variants_with_missing} ({variants_with_missing/total_variants*100:.1f}%)")
    print(f"")
    print(f"Missing fields by priority:")
    print(f"  🔴 Critical:  {critical_count} fields")
    print(f"  🟡 Important: {important_count} fields")
    print(f"  ⚪ Optional:  {optional_count} fields")
    print()
    
    # Market coverage analysis
    print(f"📍 MARKET COVERAGE")
    print(f"{'─' * 80}")
    coverage_stats = analyze_market_coverage(data_dir)
    
    # Sort by coverage percentage
    sorted_markets = sorted(coverage_stats.items(), key=lambda x: x[1]['percentage'], reverse=True)
    
    for country, stats in sorted_markets:
        bar_length = int(stats['percentage'] / 2)  # Scale to 50 chars max
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"{country.upper():3s} {bar} {stats['percentage']:5.1f}% ({stats['covered']}/{stats['total']} variants)")
    
    print()
    print(f"💡 Market expansion priority:")
    for country, stats in sorted_markets:
        if stats['percentage'] < 100:
            print(f"  • {country.upper()}: Add {stats['missing']} market entries to reach 100%")
    print()
    
    # Top variants with most missing critical/important data
    if all_missing:
        print(f"🎯 TOP 20 VARIANTS WITH MISSING DATA")
        print(f"{'─' * 80}")
        
        # Sort by number of critical + important missing fields
        all_missing.sort(
            key=lambda x: len(x['missing'].get('critical', [])) * 10 + len(x['missing'].get('important', [])),
            reverse=True
        )
        
        for i, result in enumerate(all_missing[:20], 1):
            missing = result['missing']
            critical = missing.get('critical', [])
            important = missing.get('important', [])
            
            if critical or important:
                total_missing = len(critical) + len(important)
                print(f"\n{i}. {result['variant_id']}")
                print(f"   File: {result['file']}")
                print(f"   Missing: {len(critical)} critical, {len(important)} important")
                
                if critical:
                    print(f"   🔴 Critical:")
                    for field in critical[:3]:  # Show first 3
                        print(f"      - {field}")
                    if len(critical) > 3:
                        print(f"      ... and {len(critical) - 3} more")
                
                if important:
                    print(f"   🟡 Important:")
                    for field in important[:3]:  # Show first 3
                        print(f"      - {field}")
                    if len(important) > 3:
                        print(f"      ... and {len(important) - 3} more")
    
    print()
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    if critical_count > 0:
        print(f"1. 🔴 CRITICAL: Fill {critical_count} critical missing fields first")
        print(f"   These are essential specs (battery, range, charging, performance)")
    
    if important_count > 0:
        print(f"2. 🟡 IMPORTANT: Fill {important_count} important fields")
        print(f"   These enhance usability (consumption, dimensions, cargo, weight)")
    
    # Market recommendations
    under_80 = [c for c, s in coverage_stats.items() if s['percentage'] < 80]
    if under_80:
        print(f"3. 📍 MARKET EXPANSION: Focus on {', '.join(c.upper() for c in under_80)}")
        print(f"   These markets are under 80% coverage")
    
    print()
    print("Run with variant file path to see detailed missing fields:")
    print(f"  python3 {Path(__file__).name} <variant-file.yaml>")
    print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Detailed analysis of a single variant
        variant_path = Path(sys.argv[1])
        if not variant_path.exists():
            print(f"Error: File not found: {variant_path}", file=sys.stderr)
            sys.exit(1)
        
        result = analyze_variant(variant_path)
        print(f"Variant: {result['variant_id']}")
        print(f"File: {result['file']}")
        print()
        
        missing = result['missing']
        if missing.get('critical'):
            print("🔴 Missing critical fields:")
            for field in missing['critical']:
                print(f"  - {field}")
            print()
        
        if missing.get('important'):
            print("🟡 Missing important fields:")
            for field in missing['important']:
                print(f"  - {field}")
            print()
        
        if missing.get('optional'):
            print("⚪ Missing optional fields:")
            for field in missing['optional']:
                print(f"  - {field}")
    else:
        main()

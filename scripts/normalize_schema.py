#!/usr/bin/env python3
"""
Normalize EVDB schema from nested to flat canonical format.

Transformations:
- charging.ac.max_power_kw → charging.ac_max_kw
- charging.dc.max_power_kw → charging.dc_max_kw
- motors.combined.power_kw → performance.total_power_kw
- motors.combined.power_hp → performance.total_power_hp
- motors.combined.torque_nm → performance.total_torque_nm
- performance.acceleration_0_100_kph → performance.acceleration_0_100_sec
- performance.acceleration_0_100_kph_sec → performance.acceleration_0_100_sec
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
import shutil
from datetime import datetime

def load_yaml(file_path: Path) -> dict:
    """Load a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return {}

def save_yaml(file_path: Path, data: dict):
    """Save data to YAML file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def normalize_variant(data: dict) -> tuple[dict, List[str]]:
    """
    Normalize a variant dictionary to canonical flat schema.
    Returns (normalized_data, changes_list)
    """
    changes = []
    
    # 1. Normalize charging fields
    if 'charging' in data:
        charging = data['charging']
        
        # AC charging: charging.ac.max_power_kw → charging.ac_max_kw
        if 'ac' in charging and isinstance(charging['ac'], dict):
            if 'max_power_kw' in charging['ac']:
                if 'ac_max_kw' not in charging:
                    charging['ac_max_kw'] = charging['ac']['max_power_kw']
                    changes.append(f"charging.ac.max_power_kw ({charging['ac']['max_power_kw']}) → charging.ac_max_kw")
                del charging['ac']['max_power_kw']
            
            # Flatten other AC fields if empty object remains
            if not charging['ac'] or not any(charging['ac'].values()):
                del charging['ac']
        
        # AC charging (alternative structure): charging.ac_charging.max_power_kw → charging.ac_max_kw
        if 'ac_charging' in charging and isinstance(charging['ac_charging'], dict):
            if 'max_power_kw' in charging['ac_charging']:
                if 'ac_max_kw' not in charging:
                    charging['ac_max_kw'] = charging['ac_charging']['max_power_kw']
                    changes.append(f"charging.ac_charging.max_power_kw ({charging['ac_charging']['max_power_kw']}) → charging.ac_max_kw")
            # Keep ac_charging section for other fields (time_0_100_hours, etc.)
        
        # DC charging: charging.dc.max_power_kw → charging.dc_max_kw  
        if 'dc' in charging and isinstance(charging['dc'], dict):
            if 'max_power_kw' in charging['dc']:
                if 'dc_max_kw' not in charging:
                    charging['dc_max_kw'] = charging['dc']['max_power_kw']
                    changes.append(f"charging.dc.max_power_kw ({charging['dc']['max_power_kw']}) → charging.dc_max_kw")
                del charging['dc']['max_power_kw']
            
            # Flatten other DC fields if empty object remains
            if not charging['dc'] or not any(charging['dc'].values()):
                del charging['dc']
        
        # DC charging (alternative structure): charging.dc_charging.max_power_kw → charging.dc_max_kw
        if 'dc_charging' in charging and isinstance(charging['dc_charging'], dict):
            if 'max_power_kw' in charging['dc_charging']:
                if 'dc_max_kw' not in charging:
                    charging['dc_max_kw'] = charging['dc_charging']['max_power_kw']
                    changes.append(f"charging.dc_charging.max_power_kw ({charging['dc_charging']['max_power_kw']}) → charging.dc_max_kw")
            # Keep dc_charging section for other fields (charge_time_10_80_minutes, etc.)
    
    # 1b. Handle top-level charging_ac and charging_dc sections (move to charging.*)
    # Ensure charging section exists
    if 'charging' not in data:
        data['charging'] = {}
    charging = data['charging']
    
    # Top-level charging_ac → charging.ac_max_kw
    if 'charging_ac' in data and isinstance(data['charging_ac'], dict):
        ac_section = data['charging_ac']
        if 'max_power_kw' in ac_section and 'ac_max_kw' not in charging:
            charging['ac_max_kw'] = ac_section['max_power_kw']
            changes.append(f"charging_ac.max_power_kw ({ac_section['max_power_kw']}) → charging.ac_max_kw")
        # Keep charging_ac section for other fields
    
    # Top-level charging_dc → charging.dc_max_kw
    if 'charging_dc' in data and isinstance(data['charging_dc'], dict):
        dc_section = data['charging_dc']
        if 'max_power_kw' in dc_section and 'dc_max_kw' not in charging:
            charging['dc_max_kw'] = dc_section['max_power_kw']
            changes.append(f"charging_dc.max_power_kw ({dc_section['max_power_kw']}) → charging.dc_max_kw")
        # Keep charging_dc section for other fields
    
    # 2. Normalize motor/performance fields
    if 'motors' in data and isinstance(data['motors'], dict):
        motors = data['motors']
        
        # Ensure performance section exists
        if 'performance' not in data:
            data['performance'] = {}
        perf = data['performance']
        
        # motors.total_power_kw → performance.total_power_kw
        if 'total_power_kw' in motors and 'total_power_kw' not in perf:
            perf['total_power_kw'] = motors['total_power_kw']
            changes.append(f"motors.total_power_kw ({motors['total_power_kw']}) → performance.total_power_kw")
        
        # motors.total_power_hp → performance.total_power_hp
        if 'total_power_hp' in motors and 'total_power_hp' not in perf:
            perf['total_power_hp'] = motors['total_power_hp']
            changes.append(f"motors.total_power_hp ({motors['total_power_hp']}) → performance.total_power_hp")
        
        # motors.total_torque_nm → performance.total_torque_nm
        if 'total_torque_nm' in motors and 'total_torque_nm' not in perf:
            perf['total_torque_nm'] = motors['total_torque_nm']
            changes.append(f"motors.total_torque_nm ({motors['total_torque_nm']}) → performance.total_torque_nm")
        
        # motors.combined.power_kw → performance.total_power_kw
        if 'combined' in motors and isinstance(motors['combined'], dict):
            combined = motors['combined']
            
            if 'power_kw' in combined and 'total_power_kw' not in perf:
                perf['total_power_kw'] = combined['power_kw']
                changes.append(f"motors.combined.power_kw ({combined['power_kw']}) → performance.total_power_kw")
            
            # motors.combined.max_power_kw → performance.total_power_kw (alternative naming)
            if 'max_power_kw' in combined and 'total_power_kw' not in perf:
                perf['total_power_kw'] = combined['max_power_kw']
                changes.append(f"motors.combined.max_power_kw ({combined['max_power_kw']}) → performance.total_power_kw")
            
            if 'power_hp' in combined and 'total_power_hp' not in perf:
                perf['total_power_hp'] = combined['power_hp']
                changes.append(f"motors.combined.power_hp ({combined['power_hp']}) → performance.total_power_hp")
            
            # motors.combined.max_power_hp → performance.total_power_hp (alternative naming)
            if 'max_power_hp' in combined and 'total_power_hp' not in perf:
                perf['total_power_hp'] = combined['max_power_hp']
                changes.append(f"motors.combined.max_power_hp ({combined['max_power_hp']}) → performance.total_power_hp")
            
            if 'torque_nm' in combined and 'total_torque_nm' not in perf:
                perf['total_torque_nm'] = combined['torque_nm']
                changes.append(f"motors.combined.torque_nm ({combined['torque_nm']}) → performance.total_torque_nm")
            
            # motors.combined.max_torque_nm → performance.total_torque_nm (alternative naming)
            if 'max_torque_nm' in combined and 'total_torque_nm' not in perf:
                perf['total_torque_nm'] = combined['max_torque_nm']
                changes.append(f"motors.combined.max_torque_nm ({combined['max_torque_nm']}) → performance.total_torque_nm")
            
            # Remove combined section if it's now empty
            if not combined or not any(combined.values()):
                del motors['combined']
    
    # 3. Normalize performance fields
    if 'performance' in data and isinstance(data['performance'], dict):
        perf = data['performance']
        
        # acceleration_0_100_kph → acceleration_0_100_sec
        if 'acceleration_0_100_kph' in perf and 'acceleration_0_100_sec' not in perf:
            perf['acceleration_0_100_sec'] = perf['acceleration_0_100_kph']
            changes.append(f"performance.acceleration_0_100_kph ({perf['acceleration_0_100_kph']}) → performance.acceleration_0_100_sec")
            del perf['acceleration_0_100_kph']
        
        # acceleration_0_100_kph_sec → acceleration_0_100_sec
        if 'acceleration_0_100_kph_sec' in perf and 'acceleration_0_100_sec' not in perf:
            perf['acceleration_0_100_sec'] = perf['acceleration_0_100_kph_sec']
            changes.append(f"performance.acceleration_0_100_kph_sec ({perf['acceleration_0_100_kph_sec']}) → performance.acceleration_0_100_sec")
            del perf['acceleration_0_100_kph_sec']
        
        # acceleration_0_100_kmh_seconds → acceleration_0_100_sec
        if 'acceleration_0_100_kmh_seconds' in perf and 'acceleration_0_100_sec' not in perf:
            perf['acceleration_0_100_sec'] = perf['acceleration_0_100_kmh_seconds']
            changes.append(f"performance.acceleration_0_100_kmh_seconds ({perf['acceleration_0_100_kmh_seconds']}) → performance.acceleration_0_100_sec")
            del perf['acceleration_0_100_kmh_seconds']
        
        # acceleration_0_100_kmh_s → acceleration_0_100_sec
        if 'acceleration_0_100_kmh_s' in perf and 'acceleration_0_100_sec' not in perf:
            perf['acceleration_0_100_sec'] = perf['acceleration_0_100_kmh_s']
            changes.append(f"performance.acceleration_0_100_kmh_s ({perf['acceleration_0_100_kmh_s']}) → performance.acceleration_0_100_sec")
            del perf['acceleration_0_100_kmh_s']
    
    return data, changes

def backup_file(file_path: Path, backup_dir: Path):
    """Create a backup of the file."""
    backup_path = backup_dir / file_path.name
    shutil.copy2(file_path, backup_path)

def normalize_all_variants(data_dir: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Normalize all variant files in the database.
    
    Args:
        data_dir: Path to data directory
        dry_run: If True, only show what would be changed
    
    Returns:
        Dictionary with statistics
    """
    variants_dir = data_dir / 'vehicle-variants'
    backup_dir = data_dir.parent / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created backup directory: {backup_dir}")
    
    stats = {
        'total_files': 0,
        'files_changed': 0,
        'files_unchanged': 0,
        'total_changes': 0,
        'errors': []
    }
    
    all_variant_files = sorted(variants_dir.glob('*.yaml'))
    
    print(f"Processing {len(all_variant_files)} variant files...")
    print()
    
    for variant_file in all_variant_files:
        stats['total_files'] += 1
        
        try:
            # Load original data
            original_data = load_yaml(variant_file)
            if not original_data:
                continue
            
            # Normalize
            normalized_data, changes = normalize_variant(original_data)
            
            if changes:
                stats['files_changed'] += 1
                stats['total_changes'] += len(changes)
                
                print(f"{'[DRY RUN] ' if dry_run else ''}📝 {variant_file.name}")
                for change in changes:
                    print(f"   • {change}")
                print()
                
                if not dry_run:
                    # Backup original
                    backup_file(variant_file, backup_dir)
                    
                    # Save normalized version
                    save_yaml(variant_file, normalized_data)
            else:
                stats['files_unchanged'] += 1
        
        except Exception as e:
            error_msg = f"Error processing {variant_file.name}: {e}"
            print(f"❌ {error_msg}", file=sys.stderr)
            stats['errors'].append(error_msg)
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Normalize EVDB schema from nested to flat canonical format'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=None,
        help='Path to data directory (default: ../data relative to script)'
    )
    
    args = parser.parse_args()
    
    # Determine data directory
    if args.data_dir:
        data_dir = args.data_dir
    else:
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 80)
    print("EVDB Schema Normalization")
    if args.dry_run:
        print("MODE: DRY RUN (no files will be modified)")
    print("=" * 80)
    print()
    
    # Run normalization
    stats = normalize_all_variants(data_dir, dry_run=args.dry_run)
    
    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Files changed: {stats['files_changed']}")
    print(f"Files unchanged: {stats['files_unchanged']}")
    print(f"Total transformations: {stats['total_changes']}")
    
    if stats['errors']:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"   • {error}")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ Schema normalization complete!")
        print(f"   Backups saved to: {data_dir.parent}/backups/")
        print("\n📋 Next steps:")
        print("   1. Validate: python3 scripts/validate.py --directory data/")
        print("   2. Review changes: git diff data/vehicle-variants/")
        print("   3. Commit: git add data/ && git commit -m 'Normalize schema to canonical flat format'")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Normalize EVDB schema from nested to flat canonical format.

Canonical field names:
- charging.ac_max_kw (max AC charging power)
- charging.dc_max_kw (max DC charging power)
- performance.total_power_kw (total system power)
- performance.total_power_hp (total system power in HP)
- performance.total_torque_nm (total system torque)
- performance.acceleration_0_100_sec (0-100 km/h time)
- performance.top_speed_kmh (top speed)

Source field patterns handled:
- charging.ac.max_power_kw, charging.ac_charging.max_power_kw,
  charging.ac_max_power_kw, charging_ac.max_power_kw → charging.ac_max_kw
- charging.dc.max_power_kw, charging.dc_charging.max_power_kw,
  charging.dc_max_power_kw, charging_dc.max_power_kw → charging.dc_max_kw
- motors.combined.power_kw, motors.combined.max_power_kw,
  motors.combined_power_kw, motors.total_power_kw,
  motor.power_kw, performance.power_kw, performance.system_power_kw,
  top-level total_power_kw → performance.total_power_kw
- (same patterns for torque_nm and power_hp)
- performance.acceleration_0_100_kph, _kph_sec, _kmh, _kmh_s, _kmh_seconds,
  performance.acceleration.zero_to_100_kmh_sec → performance.acceleration_0_100_sec
- performance.top_speed_kph → performance.top_speed_kmh
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
    
    # 2. Charging field name fixes (ac_max_power_kw → ac_max_kw)
    if 'charging' in data and isinstance(data['charging'], dict):
        charging = data['charging']
        if 'ac_max_power_kw' in charging and 'ac_max_kw' not in charging:
            charging['ac_max_kw'] = charging['ac_max_power_kw']
            changes.append(f"charging.ac_max_power_kw ({charging['ac_max_power_kw']}) → charging.ac_max_kw")
        if 'dc_max_power_kw' in charging and 'dc_max_kw' not in charging:
            charging['dc_max_kw'] = charging['dc_max_power_kw']
            changes.append(f"charging.dc_max_power_kw ({charging['dc_max_power_kw']}) → charging.dc_max_kw")
    
    # 3. Ensure performance section exists for motor/perf migrations
    if 'performance' not in data:
        data['performance'] = {}
    perf = data['performance']
    
    # 4. Normalize motor fields → performance.total_*
    # Source: motors section (various structures)
    if 'motors' in data and isinstance(data['motors'], dict):
        motors = data['motors']
        
        # motors.total_power_kw / motors.total_torque_nm
        for src, dst in [('total_power_kw', 'total_power_kw'), ('total_power_hp', 'total_power_hp'), ('total_torque_nm', 'total_torque_nm')]:
            if src in motors and dst not in perf:
                perf[dst] = motors[src]
                changes.append(f"motors.{src} ({motors[src]}) → performance.{dst}")
        
        # motors.combined_power_kw (underscore variant)
        for src, dst in [('combined_power_kw', 'total_power_kw'), ('combined_torque_nm', 'total_torque_nm')]:
            if src in motors and dst not in perf:
                perf[dst] = motors[src]
                changes.append(f"motors.{src} ({motors[src]}) → performance.{dst}")
        
        # motors.max_power_kw / motors.max_torque_nm
        for src, dst in [('max_power_kw', 'total_power_kw'), ('max_torque_nm', 'total_torque_nm')]:
            if src in motors and dst not in perf:
                perf[dst] = motors[src]
                changes.append(f"motors.{src} ({motors[src]}) → performance.{dst}")
        
        # motors.combined.* (nested dict)
        if 'combined' in motors and isinstance(motors['combined'], dict):
            combined = motors['combined']
            for src, dst in [
                ('power_kw', 'total_power_kw'), ('max_power_kw', 'total_power_kw'),
                ('total_power_kw', 'total_power_kw'),
                ('power_hp', 'total_power_hp'), ('max_power_hp', 'total_power_hp'),
                ('total_power_hp', 'total_power_hp'),
                ('torque_nm', 'total_torque_nm'), ('max_torque_nm', 'total_torque_nm'),
                ('total_torque_nm', 'total_torque_nm'),
            ]:
                if src in combined and dst not in perf:
                    perf[dst] = combined[src]
                    changes.append(f"motors.combined.{src} ({combined[src]}) → performance.{dst}")
    
    # Single-motor vehicles: if only one motor defined (front OR rear, not both),
    # use its values as total system power/torque
    if 'motors' in data and isinstance(data['motors'], dict):
        motors = data['motors']
        motor_sections = [k for k in motors if isinstance(motors.get(k), dict) and k not in ('combined',)]
        # Only derive from single motor if there's exactly one motor and no combined
        if len(motor_sections) == 1 and 'combined' not in motors:
            single = motors[motor_sections[0]]
            section_name = motor_sections[0]
            for src, dst in [
                ('power_kw', 'total_power_kw'), ('max_power_kw', 'total_power_kw'),
                ('power_hp', 'total_power_hp'), ('max_power_hp', 'total_power_hp'),
                ('torque_nm', 'total_torque_nm'), ('max_torque_nm', 'total_torque_nm'),
            ]:
                if src in single and dst not in perf:
                    perf[dst] = single[src]
                    changes.append(f"motors.{section_name}.{src} ({single[src]}) → performance.{dst} (single motor)")
    
    # Source: drivetrain.motors section
    dt = data.get('drivetrain', {})
    if isinstance(dt, dict) and 'motors' in dt and isinstance(dt['motors'], dict):
        dt_motors = dt['motors']
        # Check for combined section
        if 'combined' in dt_motors and isinstance(dt_motors['combined'], dict):
            combined = dt_motors['combined']
            for src, dst in [
                ('power_kw', 'total_power_kw'), ('total_power_kw', 'total_power_kw'),
                ('power_hp', 'total_power_hp'), ('total_power_hp', 'total_power_hp'),
                ('torque_nm', 'total_torque_nm'), ('total_torque_nm', 'total_torque_nm'),
            ]:
                if src in combined and dst not in perf:
                    perf[dst] = combined[src]
                    changes.append(f"drivetrain.motors.combined.{src} ({combined[src]}) → performance.{dst}")
        # Single motor derivation from drivetrain.motors
        dt_motor_sections = [k for k in dt_motors if isinstance(dt_motors.get(k), dict)]
        active_motors = [k for k in dt_motor_sections if dt_motors[k] is not None and dt_motors[k].get('power_kw')]
        if len(active_motors) == 1:
            single = dt_motors[active_motors[0]]
            sname = active_motors[0]
            for src, dst in [
                ('power_kw', 'total_power_kw'), ('power_hp', 'total_power_hp'),
                ('torque_nm', 'total_torque_nm'),
            ]:
                if src in single and dst not in perf:
                    perf[dst] = single[src]
                    changes.append(f"drivetrain.motors.{sname}.{src} ({single[src]}) → performance.{dst} (single motor)")
    
    # Source: singular motor section
    if 'motor' in data and isinstance(data['motor'], dict):
        motor = data['motor']
        for src, dst in [
            ('power_kw', 'total_power_kw'), ('max_power_kw', 'total_power_kw'),
            ('total_power_kw', 'total_power_kw'),
            ('power_hp', 'total_power_hp'), ('max_power_hp', 'total_power_hp'),
            ('total_power_hp', 'total_power_hp'),
            ('torque_nm', 'total_torque_nm'), ('max_torque_nm', 'total_torque_nm'),
            ('total_torque_nm', 'total_torque_nm'),
        ]:
            if src in motor and dst not in perf:
                perf[dst] = motor[src]
                changes.append(f"motor.{src} ({motor[src]}) → performance.{dst}")
    
    # Source: top-level total_power_kw / total_torque_nm
    for src, dst in [('total_power_kw', 'total_power_kw'), ('total_power_hp', 'total_power_hp'), ('total_torque_nm', 'total_torque_nm')]:
        if src in data and dst not in perf:
            perf[dst] = data[src]
            changes.append(f"(top-level) {src} ({data[src]}) → performance.{dst}")
    
    # Source: performance section non-canonical names
    for src, dst in [
        ('power_kw', 'total_power_kw'), ('system_power_kw', 'total_power_kw'),
        ('torque_nm', 'total_torque_nm'),
        ('power_hp', 'total_power_hp'),
    ]:
        if src in perf and dst not in perf:
            perf[dst] = perf[src]
            changes.append(f"performance.{src} ({perf[src]}) → performance.{dst}")
    
    # 5. Normalize acceleration fields
    # Nested: performance.acceleration.zero_to_100_kmh_sec
    if 'acceleration' in perf and isinstance(perf['acceleration'], dict):
        accel = perf['acceleration']
        for key in ['zero_to_100_kmh_sec', 'zero_to_100_kmh_launch_control_sec']:
            if key == 'zero_to_100_kmh_sec' and key in accel and 'acceleration_0_100_sec' not in perf:
                perf['acceleration_0_100_sec'] = accel[key]
                changes.append(f"performance.acceleration.{key} ({accel[key]}) → performance.acceleration_0_100_sec")
    
    # Flat variants
    accel_variants = [
        'acceleration_0_100_kph', 'acceleration_0_100_kph_sec',
        'acceleration_0_100_kmh', 'acceleration_0_100_kmh_s',
        'acceleration_0_100_kmh_seconds', 'acceleration_0_100_kmh_sec',
    ]
    for src in accel_variants:
        if src in perf and 'acceleration_0_100_sec' not in perf:
            perf['acceleration_0_100_sec'] = perf[src]
            changes.append(f"performance.{src} ({perf[src]}) → performance.acceleration_0_100_sec")
    
    # 6. Normalize top_speed_kph → top_speed_kmh
    if 'top_speed_kph' in perf and 'top_speed_kmh' not in perf:
        perf['top_speed_kmh'] = perf['top_speed_kph']
        changes.append(f"performance.top_speed_kph ({perf['top_speed_kph']}) → performance.top_speed_kmh")
    
    # Clean up empty performance section
    if not perf:
        del data['performance']
    
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

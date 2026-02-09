#!/usr/bin/env python3
"""
Fix variant names that duplicate the model name.
E.g. model="Q6 e-tron", variant="Q6 e-tron RWD" → variant="RWD"
"""

import yaml
import sqlite3
import subprocess
import os
from pathlib import Path

def get_fixes():
    """Query database to find variants where name starts with model name."""
    # Build fresh database
    subprocess.run(['python3', 'scripts/build-sqlite.py', '--clean'], 
                   capture_output=True, cwd=Path(__file__).resolve().parent.parent)
    
    db_path = Path(__file__).resolve().parent.parent / 'evdb.db'
    conn = sqlite3.connect(str(db_path))
    
    rows = conn.execute('''
        SELECT v.id, m.name as model, v.variant_name
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        ORDER BY v.id
    ''').fetchall()
    
    fixes = []
    for vid, model, variant in rows:
        if variant.lower().startswith(model.lower()) and variant != model[:len(variant)]:
            new_name = variant[len(model):].strip()
            if not new_name:
                new_name = "Base"
            fixes.append((vid, model, variant, new_name))
    
    conn.close()
    return fixes

def fix_variant_file(variant_id, old_name, new_name):
    """Fix the name field in a variant YAML file."""
    data_dir = Path(__file__).resolve().parent.parent / 'data' / 'vehicle-variants'
    file_path = data_dir / f'{variant_id}.yaml'
    
    if not file_path.exists():
        print(f"  ❌ File not found: {file_path.name}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Try different quoting styles for the name field
    replacements = [
        (f'name: "{old_name}"', f'name: "{new_name}"'),
        (f"name: '{old_name}'", f'name: "{new_name}"'),
        (f'name: {old_name}\n', f'name: "{new_name}"\n'),
    ]
    
    replaced = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
            replaced = True
            break
    
    if not replaced:
        print(f"  ⚠️  Could not find name field for: {variant_id} (looking for '{old_name}')")
        return False
    
    file_path.write_text(content, encoding='utf-8')
    return True

def main():
    print("=" * 70)
    print("Fixing variant names (removing model name prefix)")
    print("=" * 70)
    
    fixes = get_fixes()
    print(f"\nFound {len(fixes)} variants to fix:\n")
    
    success = 0
    failed = 0
    
    for vid, model, old_name, new_name in fixes:
        result = fix_variant_file(vid, old_name, new_name)
        if result:
            print(f"  ✓ {vid}: \"{old_name}\" → \"{new_name}\"")
            success += 1
        else:
            failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"✅ Fixed: {success}")
    if failed:
        print(f"❌ Failed: {failed}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()

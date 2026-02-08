#!/usr/bin/env python3
"""
Fix model names to remove brand prefixes.
Brand should be in the 'brand' field, not duplicated in the 'name' field.
"""

import yaml
from pathlib import Path
from typing import List, Tuple

# Models to fix: (file_id, old_name, new_name)
FIXES: List[Tuple[str, str, str]] = [
    ("audi-q8-e-tron", "Audi Q8 e-tron", "Q8 e-tron"),
    ("dacia-spring", "Dacia Spring", "Spring"),
    ("fiat-500e", "Fiat 500e", "500e"),
    ("genesis-electrified-gv70", "Genesis Electrified GV70", "Electrified GV70"),
    ("mg-zs-ev", "MG ZS EV", "ZS EV"),
    ("mg4-electric", "MG4 Electric", "4 Electric"),
    ("mg5-electric", "MG5 Electric", "5 Electric"),
    ("mercedes-benz-eqa", "Mercedes-Benz EQA", "EQA"),
    ("mercedes-benz-eqb", "Mercedes-Benz EQB", "EQB"),
    ("mercedes-benz-eqe", "Mercedes-Benz EQE", "EQE"),
    ("mercedes-benz-eqe-suv", "Mercedes-Benz EQE SUV", "EQE SUV"),
    ("mercedes-benz-eqs", "Mercedes-Benz EQS", "EQS"),
    ("mercedes-benz-eqs-suv", "Mercedes-Benz EQS SUV", "EQS SUV"),
    ("polestar-2", "Polestar 2", "2"),
    ("polestar-3", "Polestar 3", "3"),
    ("renault-zoe", "Renault Zoe", "Zoe"),
    ("smart-1", "Smart #1", "#1"),
    ("volkswagen-id-buzz", "Volkswagen ID.Buzz", "ID.Buzz"),
]

def fix_model_file(file_id: str, old_name: str, new_name: str) -> bool:
    """Fix a single model YAML file"""
    file_path = Path(f"data/vehicle-models/{file_id}.yaml")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if old name exists
    if f'name: "{old_name}"' not in content and f"name: {old_name}" not in content:
        # Try with single quotes
        if f"name: '{old_name}'" not in content:
            print(f"⚠️  {file_id}: Name '{old_name}' not found in file")
            return False
    
    # Replace old name with new name (handle both quoted and unquoted)
    if f'name: "{old_name}"' in content:
        content = content.replace(f'name: "{old_name}"', f'name: "{new_name}"')
    elif f"name: '{old_name}'" in content:
        content = content.replace(f"name: '{old_name}'", f'name: "{new_name}"')
    else:
        content = content.replace(f'name: {old_name}', f'name: "{new_name}"')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ {file_id}: '{old_name}' → '{new_name}'")
    return True

def main():
    print("=" * 60)
    print("Fixing model names (removing brand prefixes)")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for file_id, old_name, new_name in FIXES:
        if fix_model_file(file_id, old_name, new_name):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed: {success_count} files")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count} files")
    print("=" * 60)

if __name__ == "__main__":
    main()

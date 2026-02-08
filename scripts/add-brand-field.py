#!/usr/bin/env python3
"""
Add 'brand' field to all vehicle-model YAML files.

For multi-brand manufacturers (Stellantis, VW Group), extract brand from model ID/name.
For single-brand manufacturers, use manufacturer name as brand.
"""

import yaml
from pathlib import Path
import re

# Brand mappings for multi-brand manufacturers
BRAND_MAPPING = {
    # Stellantis brands
    'fiat': 'Fiat',
    'peugeot': 'Peugeot',
    'opel': 'Opel',
    'citroen': 'Citroën',
    'jeep': 'Jeep',
    'cupra': 'Cupra',
    
    # VW Group brands
    'volkswagen': 'Volkswagen',
    'audi': 'Audi',
    'skoda': 'Škoda',
    'porsche': 'Porsche',
    
    # Mercedes-Benz variations
    'mercedes-benz': 'Mercedes-Benz',
    'mercedes-amg': 'Mercedes-AMG',
    
    # BMW Group
    'bmw': 'BMW',
    'mini': 'Mini',
    
    # Hyundai Motor Group
    'hyundai': 'Hyundai',
    'kia': 'Kia',
    'genesis': 'Genesis',
    
    # Other brands
    'tesla': 'Tesla',
    'ford': 'Ford',
    'nissan': 'Nissan',
    'renault': 'Renault',
    'volvo': 'Volvo',
    'polestar': 'Polestar',
    'mg': 'MG',
    'byd': 'BYD',
    'smart': 'Smart',
}

def extract_brand_from_id(model_id: str) -> str:
    """Extract brand from model ID (e.g., 'fiat-500e' -> 'Fiat')"""
    # Try to match known brand prefixes
    for brand_key, brand_name in BRAND_MAPPING.items():
        if model_id.startswith(brand_key + '-'):
            return brand_name
    
    # Fallback: capitalize first word
    first_word = model_id.split('-')[0]
    return first_word.capitalize()

def add_brand_to_model(file_path: Path):
    """Add brand field to a vehicle-model YAML file"""
    print(f"Processing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Skip if brand already exists
    if 'brand' in data:
        print(f"  ✓ Already has brand: {data['brand']}")
        return False
    
    # Extract brand from model ID
    model_id = data.get('id', '')
    brand = extract_brand_from_id(model_id)
    
    print(f"  + Adding brand: {brand}")
    
    # Read file content to preserve formatting and comments
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find manufacturer_id line and insert brand after it
    new_lines = []
    inserted = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Insert brand after manufacturer_id
        if not inserted and line.startswith('manufacturer_id:'):
            indent = len(line) - len(line.lstrip())
            brand_line = f"{' ' * indent}brand: \"{brand}\"\n"
            new_lines.append(brand_line)
            inserted = True
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

def main():
    """Process all vehicle-model files"""
    models_dir = Path('data/vehicle-models')
    
    if not models_dir.exists():
        print(f"Error: {models_dir} not found")
        return
    
    model_files = sorted(models_dir.glob('*.yaml'))
    
    print(f"Found {len(model_files)} model files\n")
    
    updated = 0
    skipped = 0
    
    for model_file in model_files:
        if add_brand_to_model(model_file):
            updated += 1
        else:
            skipped += 1
    
    print(f"\n✅ Done!")
    print(f"  Updated: {updated} files")
    print(f"  Skipped: {skipped} files (already had brand)")

if __name__ == '__main__':
    main()

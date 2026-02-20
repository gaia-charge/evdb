#!/usr/bin/env python3
"""Strip all fields not defined in the schema from YAML files."""

import yaml, json, jsonschema, glob, os, sys
from collections import Counter

def get_allowed_keys(schema_obj):
    """Get allowed property names from a schema object."""
    return set(schema_obj.get('properties', {}).keys())

def get_nested_schema(schema, path):
    """Get schema for a nested path."""
    current = schema
    for key in path:
        if isinstance(key, int):
            current = current.get('items', {})
        else:
            props = current.get('properties', {})
            current = props.get(key, {})
    return current

def strip_extras(data, schema, path="root"):
    """Recursively strip fields not in schema. Returns (cleaned_data, removed_fields)."""
    removed = []
    
    if not isinstance(data, dict):
        return data, removed
    
    schema_type = schema.get('type', 'object')
    if isinstance(schema_type, list):
        if 'object' not in schema_type:
            return data, removed
    elif schema_type != 'object':
        return data, removed
    
    allowed = get_allowed_keys(schema)
    if not allowed:
        return data, removed
    
    # Remove extra keys
    extras = set(data.keys()) - allowed
    for key in extras:
        removed.append(f"{path}.{key}")
        del data[key]
    
    # Recurse into allowed object/array properties
    props = schema.get('properties', {})
    for key, val in list(data.items()):
        if key in props:
            sub_schema = props[key]
            sub_type = sub_schema.get('type', '')
            
            if isinstance(val, dict):
                _, sub_removed = strip_extras(val, sub_schema, f"{path}.{key}")
                removed.extend(sub_removed)
                # Remove empty dicts after stripping
                if not val:
                    del data[key]
                    
            elif isinstance(val, list):
                items_schema = sub_schema.get('items', {})
                for i, item in enumerate(val):
                    if isinstance(item, dict):
                        _, sub_removed = strip_extras(item, items_schema, f"{path}.{key}[{i}]")
                        removed.extend(sub_removed)
    
    return data, removed


def main():
    dry_run = '--dry-run' in sys.argv
    
    with open('schemas/vehicle-variant.schema.json') as f:
        schema = json.load(f)
    
    total_removed = Counter()
    files_modified = 0
    
    for path in sorted(glob.glob('data/vehicle-variants/*.yaml')):
        fname = os.path.basename(path)
        with open(path) as f:
            raw = f.read()
            
        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            continue
            
        _, removed = strip_extras(data, schema)
        
        if removed:
            files_modified += 1
            for r in removed:
                total_removed[r.split('.', 1)[1] if '.' in r else r] += 1
            
            if not dry_run:
                with open(path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            if dry_run:
                print(f"\n{fname}:")
                for r in removed:
                    print(f"  - {r}")
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Files modified: {files_modified}")
    print(f"  Total fields removed: {sum(total_removed.values())}")
    print(f"\n  Top removed fields:")
    for field, count in total_removed.most_common(30):
        print(f"    {count:4d}x  {field}")


if __name__ == '__main__':
    main()

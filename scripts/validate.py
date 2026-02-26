#!/usr/bin/env python3
"""
EVDB Data Validation Script

Validates YAML files against JSON Schema and performs additional checks.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml
import jsonschema
from jsonschema import Draft7Validator, validators
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


class ValidationError:
    """Represents a validation error"""
    
    def __init__(self, file_path: str, error_type: str, message: str, severity: str = "error"):
        self.file_path = file_path
        self.error_type = error_type
        self.message = message
        self.severity = severity  # error, warning
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.file_path}: {self.error_type} - {self.message}"


class Validator:
    """Main validation class"""
    
    def __init__(self, schemas_dir: Path):
        self.schemas_dir = schemas_dir
        self.schemas = {}
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.load_schemas()
    
    def load_schemas(self):
        """Load all JSON schemas"""
        if not self.schemas_dir.exists():
            console.print(f"[red]Schemas directory not found: {self.schemas_dir}[/red]")
            sys.exit(1)
        
        schema_files = list(self.schemas_dir.glob("*.schema.json"))
        if not schema_files:
            console.print(f"[yellow]No schema files found in {self.schemas_dir}[/yellow]")
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema = yaml.safe_load(f)
                    # Extract schema type from filename (e.g., manufacturer.schema.json -> manufacturer)
                    schema_type = schema_file.stem.replace('.schema', '')
                    self.schemas[schema_type] = schema
                    console.print(f"[dim]Loaded schema: {schema_type}[/dim]")
            except Exception as e:
                console.print(f"[red]Failed to load schema {schema_file}: {e}[/red]")
                sys.exit(1)
    
    def load_yaml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    self.errors.append(ValidationError(
                        str(file_path),
                        "EmptyFile",
                        "File is empty or contains no data"
                    ))
                    return None
                return data
        except yaml.YAMLError as e:
            self.errors.append(ValidationError(
                str(file_path),
                "YAMLSyntaxError",
                f"Invalid YAML syntax: {e}"
            ))
            return None
        except Exception as e:
            self.errors.append(ValidationError(
                str(file_path),
                "FileReadError",
                f"Failed to read file: {e}"
            ))
            return None
    
    def detect_schema_type(self, file_path: Path) -> Optional[str]:
        """Detect which schema to use based on file location"""
        parts = file_path.parts
        
        # Map directory names to schema types
        dir_to_schema = {
            'manufacturers': 'manufacturer',
            'vehicle-models': 'vehicle-model',
            'vehicle-variants': 'vehicle-variant',
            'market-availability': 'market-availability'
        }
        
        for part in parts:
            if part in dir_to_schema:
                return dir_to_schema[part]
        
        return None
    
    def validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any], file_path: str) -> List[ValidationError]:
        """Validate data against JSON schema"""
        errors = []
        
        try:
            validator = Draft7Validator(schema)
            for error in validator.iter_errors(data):
                # Build a readable error message
                path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                errors.append(ValidationError(
                    file_path,
                    "SchemaValidation",
                    f"At '{path}': {error.message}"
                ))
        except Exception as e:
            errors.append(ValidationError(
                file_path,
                "ValidationError",
                f"Schema validation failed: {e}"
            ))
        
        return errors
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single YAML file"""
        # Load file
        data = self.load_yaml_file(file_path)
        if data is None:
            return False
        
        # Detect schema type
        schema_type = self.detect_schema_type(file_path)
        if schema_type is None:
            self.warnings.append(ValidationError(
                str(file_path),
                "UnknownSchemaType",
                "Could not determine schema type from file path",
                severity="warning"
            ))
            return True  # Not an error, just skip schema validation
        
        # Check if schema exists
        if schema_type not in self.schemas:
            self.warnings.append(ValidationError(
                str(file_path),
                "SchemaNotFound",
                f"Schema '{schema_type}' not found",
                severity="warning"
            ))
            return True
        
        # Validate against schema
        schema = self.schemas[schema_type]
        schema_errors = self.validate_against_schema(data, schema, str(file_path))
        self.errors.extend(schema_errors)
        
        return len(schema_errors) == 0
    
    def validate_directory(self, directory: Path, recursive: bool = True) -> Tuple[int, int]:
        """
        Validate all YAML files in a directory
        
        Returns: (success_count, total_count)
        """
        if not directory.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            return 0, 0
        
        # Find all YAML files
        pattern = "**/*.yaml" if recursive else "*.yaml"
        yaml_files = list(directory.glob(pattern))
        
        if not yaml_files:
            console.print(f"[yellow]No YAML files found in {directory}[/yellow]")
            return 0, 0
        
        console.print(f"\n[bold]Validating {len(yaml_files)} file(s)...[/bold]\n")
        
        success_count = 0
        for yaml_file in yaml_files:
            # Show progress
            console.print(f"[dim]Validating {yaml_file.relative_to(directory)}...[/dim]", end="")
            
            if self.validate_file(yaml_file):
                console.print(" [green]✓[/green]")
                success_count += 1
            else:
                console.print(" [red]✗[/red]")
        
        return success_count, len(yaml_files)
    
    # Approximate FX rates for cross-market price comparison only (not stored)
    EUR_RATES = {'EUR': 1.0, 'PLN': 4.3, 'GBP': 0.85, 'USD': 1.08, 'CHF': 0.94,
                 'SEK': 11.3, 'NOK': 11.6, 'DKK': 7.46, 'CZK': 25.2}
    MARKET_CURRENCY = {'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR', 'ES': 'EUR', 'NL': 'EUR',
                       'AT': 'EUR', 'BE': 'EUR', 'PT': 'EUR', 'IE': 'EUR', 'FI': 'EUR',
                       'PL': 'PLN', 'GB': 'GBP', 'UK': 'GBP', 'US': 'USD', 'CH': 'CHF',
                       'SE': 'SEK', 'NO': 'NOK', 'DK': 'DKK', 'CZ': 'CZK'}
    # Sanity bands for base prices, in EUR
    PRICE_BAND_EUR = (8000, 500000)
    # Plausible efficiency band: km of WLTP range per kWh of usable battery
    KM_PER_KWH_BAND = (2.5, 10.0)

    def cross_validate(self, directory: Path):
        """Cross-file checks: referential integrity, duplicates, plausibility."""
        def load_dir(sub):
            out = {}
            d = directory / sub
            if not d.exists():
                return out
            for f in sorted(d.glob('*.yaml')):
                data = self.load_yaml_file(f)
                if data and isinstance(data, dict) and 'id' in data:
                    out[data['id']] = (f, data)
            return out

        manufacturers = load_dir('manufacturers')
        models = load_dir('vehicle-models')
        variants = load_dir('vehicle-variants')
        markets = load_dir('market-availability')

        def err(f, etype, msg, severity="error"):
            target = self.errors if severity == "error" else self.warnings
            target.append(ValidationError(str(f), etype, msg, severity=severity))

        # 1. Filename must equal id
        for coll in (manufacturers, models, variants, markets):
            for rid, (f, _) in coll.items():
                if f.stem != rid:
                    err(f, "FilenameIdMismatch",
                        f"File name '{f.stem}' != id '{rid}'")

        # 2. Referential integrity
        for rid, (f, d) in models.items():
            if d.get('manufacturer_id') not in manufacturers:
                err(f, "BrokenReference",
                    f"manufacturer_id '{d.get('manufacturer_id')}' does not exist")
        for rid, (f, d) in variants.items():
            if d.get('model_id') not in models:
                err(f, "BrokenReference", f"model_id '{d.get('model_id')}' does not exist")
        for rid, (f, d) in markets.items():
            if d.get('variant_id') not in variants:
                err(f, "BrokenReference",
                    f"variant_id '{d.get('variant_id')}' does not exist")

        # 3. (variant_id, market) uniqueness
        seen_vm: Dict[Tuple[str, str], str] = {}
        for rid, (f, d) in markets.items():
            key = (str(d.get('variant_id')), str(d.get('market', '')).upper())
            if key in seen_vm:
                err(f, "DuplicateMarketEntry",
                    f"variant '{key[0]}' already has a {key[1]} entry in {seen_vm[key]}")
            else:
                seen_vm[key] = f.name

        # 4. Semantic duplicate variants: same model, name, year under different ids
        seen_variant: Dict[Tuple[str, str, Any], str] = {}
        for rid, (f, d) in variants.items():
            key = (str(d.get('model_id')), str(d.get('name', '')).strip().lower(),
                   d.get('model_year'))
            if key in seen_variant:
                err(f, "DuplicateVariant",
                    f"same (model_id, name, model_year) as {seen_variant[key]} - "
                    f"one of the two ids is redundant")
            else:
                seen_variant[key] = f.name

        # 5. Variant plausibility
        for rid, (f, d) in variants.items():
            battery = d.get('battery') or {}
            usable = battery.get('usable_kwh')
            total = battery.get('total_kwh')
            if usable and total and usable > total + 0.5:
                err(f, "Plausibility", f"usable_kwh {usable} > total_kwh {total}")
            wltp = (d.get('range') or {}).get('wltp_km')
            if usable and wltp:
                ratio = wltp / usable
                lo, hi = self.KM_PER_KWH_BAND
                if not (lo <= ratio <= hi):
                    err(f, "Plausibility",
                        f"range {wltp} km / {usable} kWh = {ratio:.1f} km/kWh "
                        f"outside plausible band {lo}-{hi}")
            dc = (d.get('charging') or {}).get('dc_max_kw')
            if dc is not None and not (10 <= dc <= 1000):
                err(f, "Plausibility", f"dc_max_kw {dc} outside 10-1000")
            acc = (d.get('performance') or {}).get('acceleration_0_100_sec')
            if acc is not None and not (1.5 <= acc <= 25):
                err(f, "Plausibility", f"acceleration_0_100_sec {acc} outside 1.5-25")

        # 6. Market plausibility: currency map + price band + VAT arithmetic
        for rid, (f, d) in markets.items():
            market = str(d.get('market', '')).upper()
            currency = d.get('currency')
            expected = self.MARKET_CURRENCY.get(market)
            if expected and currency != expected:
                err(f, "CurrencyMismatch",
                    f"market {market} expects {expected}, file says {currency}")
            pricing = d.get('pricing') or {}
            base = pricing.get('base_price')
            rate = self.EUR_RATES.get(currency)
            if base and rate:
                eur = base / rate
                lo, hi = self.PRICE_BAND_EUR
                if not (lo <= eur <= hi):
                    err(f, "Plausibility",
                        f"base_price {base} {currency} (~EUR {eur:,.0f}) outside {lo}-{hi}")
            incl = pricing.get('price_including_vat')
            if base and incl and incl < base * 0.99:
                err(f, "Plausibility",
                    f"price_including_vat {incl} < base_price {base}")

        # 7. Cross-market spread per variant (warning; verify prices when it fires)
        by_variant: Dict[str, List[Tuple[str, float, str]]] = {}
        for rid, (f, d) in markets.items():
            base = (d.get('pricing') or {}).get('base_price')
            rate = self.EUR_RATES.get(d.get('currency'))
            if base and rate:
                by_variant.setdefault(str(d.get('variant_id')), []).append(
                    (str(d.get('market')), base / rate, f.name))
        for vid, entries in by_variant.items():
            if len(entries) < 2:
                continue
            entries.sort(key=lambda e: e[1])
            low, high = entries[0], entries[-1]
            if low[1] > 0 and high[1] / low[1] > 1.5:
                err(high[2], "CrossMarketSpread",
                    f"variant '{vid}': {high[0]} ~EUR {high[1]:,.0f} vs "
                    f"{low[0]} ~EUR {low[1]:,.0f} ({high[1]/low[1]:.2f}x) - "
                    f"verify both prices", severity="warning")

    def check_duplicate_ids(self, directory: Path) -> List[ValidationError]:
        """Check for duplicate IDs across files"""
        errors = []
        id_map: Dict[str, List[str]] = {}
        
        for yaml_file in directory.rglob("*.yaml"):
            data = self.load_yaml_file(yaml_file)
            if data and 'id' in data:
                file_id = data['id']
                if file_id not in id_map:
                    id_map[file_id] = []
                id_map[file_id].append(str(yaml_file))
        
        # Find duplicates
        for file_id, files in id_map.items():
            if len(files) > 1:
                errors.append(ValidationError(
                    ", ".join(files),
                    "DuplicateID",
                    f"ID '{file_id}' is used in multiple files"
                ))
        
        return errors
    
    def print_summary(self, success_count: int, total_count: int):
        """Print validation summary"""
        # Summary table
        table = Table(title="Validation Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Files", str(total_count))
        table.add_row("Passed", f"[green]{success_count}[/green]")
        table.add_row("Failed", f"[red]{total_count - success_count}[/red]")
        table.add_row("Errors", f"[red]{len(self.errors)}[/red]")
        table.add_row("Warnings", f"[yellow]{len(self.warnings)}[/yellow]")
        
        console.print()
        console.print(table)
        console.print()
        
        # Show errors
        if self.errors:
            console.print("[bold red]Errors:[/bold red]")
            for error in self.errors:
                console.print(f"  [red]✗[/red] {error}")
            console.print()
        
        # Show warnings
        if self.warnings:
            console.print("[bold yellow]Warnings:[/bold yellow]")
            for warning in self.warnings:
                console.print(f"  [yellow]⚠[/yellow] {warning}")
            console.print()
        
        # Final verdict
        if len(self.errors) == 0:
            console.print(Panel.fit(
                "[bold green]✓ All validations passed![/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                f"[bold red]✗ Validation failed with {len(self.errors)} error(s)[/bold red]",
                border_style="red"
            ))


@click.command()
@click.option('--file', '-f', 'file_path', type=click.Path(exists=True, path_type=Path),
              help='Validate a single file')
@click.option('--directory', '-d', 'directory_path', type=click.Path(exists=True, path_type=Path),
              help='Validate all YAML files in directory')
@click.option('--schemas', '-s', 'schemas_dir', type=click.Path(exists=True, path_type=Path),
              default='schemas', help='Directory containing JSON schemas')
@click.option('--check-duplicates/--no-check-duplicates', default=True,
              help='Check for duplicate IDs')
@click.option('--cross-checks/--no-cross-checks', default=True,
              help='Cross-file referential integrity, duplicate and plausibility checks')
@click.option('--recursive/--no-recursive', default=True,
              help='Recursively search for YAML files')
def main(file_path: Optional[Path], directory_path: Optional[Path], schemas_dir: Path,
         check_duplicates: bool, cross_checks: bool, recursive: bool):
    """
    Validate EVDB YAML files against JSON schemas.
    
    Examples:
    
        # Validate single file
        python validate.py --file data/manufacturers/tesla.yaml
        
        # Validate all files in directory
        python validate.py --directory data/
        
        # Validate with custom schemas directory
        python validate.py --directory data/ --schemas custom-schemas/
    """
    console.print(Panel.fit(
        "[bold cyan]EVDB Data Validator[/bold cyan]",
        border_style="cyan"
    ))
    
    validator = Validator(schemas_dir)
    
    if file_path:
        # Validate single file
        console.print(f"\n[bold]Validating file: {file_path}[/bold]\n")
        success = validator.validate_file(file_path)
        validator.print_summary(1 if success else 0, 1)
        sys.exit(0 if len(validator.errors) == 0 else 1)
    
    elif directory_path:
        # Validate directory
        success_count, total_count = validator.validate_directory(directory_path, recursive)
        
        # Check for duplicate IDs
        if check_duplicates:
            console.print("\n[bold]Checking for duplicate IDs...[/bold]")
            duplicate_errors = validator.check_duplicate_ids(directory_path)
            validator.errors.extend(duplicate_errors)

        # Cross-file checks (referential integrity, duplicates, plausibility)
        if cross_checks:
            console.print("\n[bold]Running cross-file checks...[/bold]")
            validator.cross_validate(directory_path)

        validator.print_summary(success_count, total_count)
        sys.exit(0 if len(validator.errors) == 0 else 1)
    
    else:
        console.print("[red]Error: Either --file or --directory must be specified[/red]")
        console.print("Run with --help for usage information")
        sys.exit(1)


if __name__ == '__main__':
    main()

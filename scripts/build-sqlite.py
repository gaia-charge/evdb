#!/usr/bin/env python3
"""
EVDB SQLite Database Builder

Converts YAML files into a SQLite database with proper relational structure.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import sqlite3
import json
from datetime import datetime
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DatabaseBuilder:
    """Main database builder class"""
    
    def __init__(self, data_dir: Path, output_path: Path, clean: bool = False):
        self.data_dir = data_dir
        self.output_path = output_path
        self.clean = clean
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.stats = {
            'manufacturers': 0,
            'vehicle_models': 0,
            'vehicle_variants': 0,
            'market_availability': 0,
            'connectors': 0,
            'platforms': 0,
        }
    
    def connect(self):
        """Connect to SQLite database"""
        if self.clean and self.output_path.exists():
            console.print(f"[yellow]Removing existing database: {self.output_path}[/yellow]")
            self.output_path.unlink()
        
        self.conn = sqlite3.connect(str(self.output_path))
        self.cursor = self.conn.cursor()
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        console.print(f"[green]Connected to database: {self.output_path}[/green]")
    
    def create_schema(self):
        """Create database schema"""
        console.print("[cyan]Creating database schema...[/cyan]")
        
        # Manufacturers table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS manufacturers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                website TEXT,
                founded_year INTEGER,
                headquarters TEXT,
                parent_company TEXT,
                brands TEXT,  -- JSON array
                logo_url TEXT,
                description TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Vehicle models table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_models (
                id TEXT PRIMARY KEY,
                manufacturer_id TEXT NOT NULL,
                name TEXT NOT NULL,
                marketing_name TEXT,
                body_style TEXT NOT NULL,
                segment TEXT NOT NULL,
                platform_id TEXT,
                production_start TEXT,
                production_end TEXT,
                seating_capacity INTEGER,
                seating_configuration TEXT,
                length_mm INTEGER,
                width_mm INTEGER,
                height_mm INTEGER,
                wheelbase_mm INTEGER,
                ground_clearance_mm INTEGER,
                drag_coefficient REAL,
                cargo_volume_liters INTEGER,
                frunk_volume_liters INTEGER,
                towing_capacity_kg INTEGER,
                roof_load_kg INTEGER,
                image_url TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id)
            )
        """)
        
        # Vehicle variants table (most detailed)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_variants (
                id TEXT PRIMARY KEY,
                model_id TEXT NOT NULL,
                variant_name TEXT NOT NULL,
                model_year INTEGER NOT NULL,
                trim_level TEXT,
                battery_capacity_kwh REAL NOT NULL,
                battery_usable_kwh REAL NOT NULL,
                battery_chemistry TEXT,
                battery_voltage REAL,
                battery_cells INTEGER,
                battery_modules INTEGER,
                battery_warranty_years INTEGER,
                battery_warranty_km INTEGER,
                range_wltp_km INTEGER,
                range_epa_km INTEGER,
                range_real_world_km INTEGER,
                consumption_wltp_kwh_100km REAL,
                consumption_real_world_kwh_100km REAL,
                efficiency_wh_km REAL,
                ac_charge_power_kw REAL,
                ac_charge_phase INTEGER,
                ac_onboard_charger_kw REAL,
                dc_charge_power_kw REAL,
                dc_charge_time_10_80_min INTEGER,
                dc_charge_time_0_100_min INTEGER,
                dc_peak_power_kw REAL,
                connector_types TEXT,  -- JSON array
                bidirectional_charging TEXT,  -- JSON array (V2L, V2H, V2G)
                bidirectional_power_kw REAL,
                motor_type TEXT,
                motor_count INTEGER,
                drive_type TEXT,
                total_power_kw REAL,
                total_torque_nm REAL,
                acceleration_0_100_sec REAL,
                top_speed_kph INTEGER,
                weight_curb_kg INTEGER,
                weight_gross_kg INTEGER,
                price_base_eur INTEGER,
                data_quality TEXT,
                sources TEXT,  -- JSON array
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (model_id) REFERENCES vehicle_models (id)
            )
        """)
        
        # Market availability table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_availability (
                id TEXT PRIMARY KEY,
                variant_id TEXT NOT NULL,
                market_code TEXT NOT NULL,
                currency TEXT NOT NULL,
                price_base INTEGER,
                price_including_vat INTEGER,
                price_after_incentives INTEGER,
                available_from TEXT,
                available_until TEXT,
                availability_status TEXT,
                delivery_time_weeks INTEGER,
                pre_order_available INTEGER,
                order_book_open INTEGER,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (variant_id) REFERENCES vehicle_variants (id)
            )
        """)
        
        # Market incentives table (normalized from market_availability)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_incentives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_availability_id TEXT NOT NULL,
                incentive_type TEXT NOT NULL,
                name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                conditions TEXT,
                FOREIGN KEY (market_availability_id) REFERENCES market_availability (id)
            )
        """)
        
        # Market colors (normalized)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_colors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_availability_id TEXT NOT NULL,
                name TEXT NOT NULL,
                code TEXT,
                price INTEGER NOT NULL,
                is_default INTEGER,
                FOREIGN KEY (market_availability_id) REFERENCES market_availability (id)
            )
        """)
        
        # Market wheels (normalized)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_wheels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_availability_id TEXT NOT NULL,
                name TEXT NOT NULL,
                size_inches REAL NOT NULL,
                price INTEGER NOT NULL,
                is_default INTEGER,
                FOREIGN KEY (market_availability_id) REFERENCES market_availability (id)
            )
        """)
        
        # Market interiors (normalized)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_interiors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_availability_id TEXT NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                is_default INTEGER,
                FOREIGN KEY (market_availability_id) REFERENCES market_availability (id)
            )
        """)
        
        # Reference: Connectors
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS connectors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                max_power_kw REAL,
                max_voltage_v REAL,
                max_current_a REAL,
                regions TEXT,  -- JSON array
                description TEXT
            )
        """)
        
        # Reference: Platforms
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS platforms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                type TEXT NOT NULL,
                voltage_nominal_v INTEGER,
                architecture TEXT,
                battery_supplier TEXT,
                first_used INTEGER,
                description TEXT,
                notes TEXT
            )
        """)
        
        # Create indexes for better query performance
        console.print("[cyan]Creating indexes...[/cyan]")
        
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_manufacturer ON vehicle_models(manufacturer_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_variants_model ON vehicle_variants(model_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_variants_year ON vehicle_variants(model_year)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_variant ON market_availability(variant_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_code ON market_availability(market_code)")
        
        self.conn.commit()
        console.print("[green]✓ Schema created successfully[/green]")
    
    def load_yaml_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file"""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            console.print(f"[red]Error loading {file_path}: {e}[/red]")
            return None
    
    def import_manufacturers(self):
        """Import manufacturers from YAML files"""
        manufacturers_dir = self.data_dir / 'manufacturers'
        if not manufacturers_dir.exists():
            console.print("[yellow]No manufacturers directory found[/yellow]")
            return
        
        files = list(manufacturers_dir.glob('*.yaml'))
        console.print(f"[cyan]Importing {len(files)} manufacturers...[/cyan]")
        
        for file_path in files:
            data = self.load_yaml_file(file_path)
            if not data:
                continue
            
            # Handle headquarters - can be dict or string
            headquarters = data.get('headquarters')
            if isinstance(headquarters, dict):
                headquarters = f"{headquarters.get('city', '')}, {headquarters.get('country', '')}"
            
            # Get founded year from either founded_year or founded
            founded_year = data.get('founded_year') or data.get('founded')
            
            # Get updated_at with proper null handling
            metadata = data.get('metadata', {})
            updated_at = metadata.get('updated_at')
            if not updated_at:
                updated_at = metadata.get('created_at', datetime.now().isoformat())
            
            self.cursor.execute("""
                INSERT INTO manufacturers (
                    id, name, country, website, founded_year, headquarters,
                    parent_company, brands, logo_url, description, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['name'],
                data['country'],
                data.get('website'),
                founded_year,
                headquarters,
                data.get('parent_company'),
                json.dumps(data.get('brands', [])),
                data.get('logo_url'),
                data.get('description'),
                data.get('notes'),
                metadata.get('created_at', datetime.now().isoformat()),
                updated_at
            ))
            self.stats['manufacturers'] += 1
        
        self.conn.commit()
        console.print(f"[green]✓ Imported {self.stats['manufacturers']} manufacturers[/green]")
    
    def import_vehicle_models(self):
        """Import vehicle models from YAML files"""
        models_dir = self.data_dir / 'vehicle-models'
        if not models_dir.exists():
            console.print("[yellow]No vehicle-models directory found[/yellow]")
            return
        
        files = list(models_dir.glob('*.yaml'))
        console.print(f"[cyan]Importing {len(files)} vehicle models...[/cyan]")
        
        for file_path in files:
            data = self.load_yaml_file(file_path)
            if not data:
                continue
            
            dims = data.get('dimensions', {})
            cargo = data.get('cargo', {})
            capacity = data.get('capacity', {})
            seating = data.get('seating', {})
            towing = data.get('towing', {})
            
            # Handle production dates - can be in different formats
            production = data.get('production', {})
            if isinstance(production, dict):
                production_start = production.get('start_date') or production.get('start')
                production_end = production.get('end_date') or production.get('end')
            else:
                production_start = data.get('production_start')
                production_end = data.get('production_end')
            
            # Handle seating capacity - can be in different locations
            seating_capacity = (seating.get('seats') or 
                              capacity.get('seating') or 
                              dims.get('seating_capacity'))
            
            # Handle cargo volumes
            trunk_liters = (cargo.get('trunk_capacity_liters') or 
                          cargo.get('trunk_liters') or 
                          dims.get('cargo_volume_l'))
            frunk_liters = (cargo.get('frunk_capacity_liters') or 
                          cargo.get('frunk_liters'))
            
            # Handle towing capacity
            towing_capacity_kg = (towing.get('max_towing_capacity_kg') or 
                                capacity.get('towing_capacity_kg'))
            
            # Get updated_at with proper null handling
            metadata = data.get('metadata', {})
            updated_at = metadata.get('updated_at')
            if not updated_at:
                updated_at = metadata.get('created_at', datetime.now().isoformat())
            
            self.cursor.execute("""
                INSERT INTO vehicle_models (
                    id, manufacturer_id, name, marketing_name, body_style, segment,
                    platform_id, production_start, production_end, seating_capacity,
                    seating_configuration, length_mm, width_mm, height_mm, wheelbase_mm,
                    ground_clearance_mm, drag_coefficient, cargo_volume_liters,
                    frunk_volume_liters, towing_capacity_kg, roof_load_kg,
                    image_url, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['manufacturer_id'],
                data['name'],
                data.get('marketing_name') or data.get('full_name'),
                data['body_style'],
                data['segment'],
                data.get('platform_id') or data.get('platform'),
                production_start,
                production_end,
                seating_capacity,
                json.dumps(seating.get('seating_configurations', [])),
                dims.get('length_mm'),
                dims.get('width_mm'),
                dims.get('height_mm'),
                dims.get('wheelbase_mm'),
                dims.get('ground_clearance_mm'),
                dims.get('drag_coefficient'),
                trunk_liters,
                frunk_liters,
                towing_capacity_kg,
                capacity.get('roof_load_kg'),
                data.get('image_url'),
                data.get('notes'),
                metadata.get('created_at', datetime.now().isoformat()),
                updated_at
            ))
            self.stats['vehicle_models'] += 1
        
        self.conn.commit()
        console.print(f"[green]✓ Imported {self.stats['vehicle_models']} vehicle models[/green]")
    
    def import_vehicle_variants(self):
        """Import vehicle variants from YAML files"""
        variants_dir = self.data_dir / 'vehicle-variants'
        if not variants_dir.exists():
            console.print("[yellow]No vehicle-variants directory found[/yellow]")
            return
        
        files = list(variants_dir.glob('*.yaml'))
        console.print(f"[cyan]Importing {len(files)} vehicle variants...[/cyan]")
        
        for file_path in files:
            data = self.load_yaml_file(file_path)
            if not data:
                continue
            
            battery = data.get('battery', {})
            range_data = data.get('range', {})
            consumption = data.get('consumption', {})
            charging = data.get('charging', {})
            ac = charging.get('ac', {})
            dc = charging.get('dc', {})
            bidir = charging.get('bidirectional', {})
            motor = data.get('motor', {})
            performance = data.get('performance', {})
            weight = data.get('weight', {})
            pricing = data.get('pricing', {})
            metadata = data.get('metadata', {})
            
            # Get updated_at with proper null handling
            updated_at = metadata.get('updated_at')
            if not updated_at:
                updated_at = metadata.get('created_at', datetime.now().isoformat())
            
            self.cursor.execute("""
                INSERT INTO vehicle_variants (
                    id, model_id, variant_name, model_year, trim_level,
                    battery_capacity_kwh, battery_usable_kwh, battery_chemistry,
                    battery_voltage, battery_cells, battery_modules,
                    battery_warranty_years, battery_warranty_km,
                    range_wltp_km, range_epa_km, range_real_world_km,
                    consumption_wltp_kwh_100km, consumption_real_world_kwh_100km,
                    efficiency_wh_km,
                    ac_charge_power_kw, ac_charge_phase, ac_onboard_charger_kw,
                    dc_charge_power_kw, dc_charge_time_10_80_min, dc_charge_time_0_100_min,
                    dc_peak_power_kw, connector_types, bidirectional_charging,
                    bidirectional_power_kw,
                    motor_type, motor_count, drive_type, total_power_kw, total_torque_nm,
                    acceleration_0_100_sec, top_speed_kph,
                    weight_curb_kg, weight_gross_kg,
                    price_base_eur, data_quality, sources, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['model_id'],
                data.get('variant_name') or data.get('name'),
                data['model_year'],
                data.get('trim_level'),
                battery.get('capacity_kwh') or battery.get('total_kwh'),
                battery.get('usable_kwh'),
                battery.get('chemistry'),
                battery.get('voltage'),
                battery.get('cells'),
                battery.get('modules'),
                battery.get('warranty', {}).get('years'),
                battery.get('warranty', {}).get('km'),
                range_data.get('wltp_km'),
                range_data.get('epa_km'),
                range_data.get('real_world_km'),
                consumption.get('wltp_kwh_100km'),
                consumption.get('real_world_kwh_100km'),
                consumption.get('efficiency_wh_km'),
                ac.get('max_power_kw'),
                ac.get('phases'),
                ac.get('onboard_charger_kw'),
                dc.get('max_power_kw'),
                dc.get('time_10_80_min'),
                dc.get('time_0_100_min'),
                dc.get('peak_power_kw'),
                json.dumps(charging.get('connectors', [])),
                json.dumps(bidir.get('capabilities', [])),
                bidir.get('max_power_kw'),
                motor.get('type'),
                motor.get('count'),
                motor.get('drive_type'),
                motor.get('total_power_kw'),
                motor.get('total_torque_nm'),
                performance.get('acceleration_0_100_kph_sec'),
                performance.get('top_speed_kph'),
                weight.get('curb_kg'),
                weight.get('gross_vehicle_kg'),
                pricing.get('base_price_eur'),
                metadata.get('data_quality'),
                json.dumps(metadata.get('sources', [])),
                data.get('notes'),
                metadata.get('created_at', datetime.now().isoformat()),
                updated_at
            ))
            self.stats['vehicle_variants'] += 1
        
        self.conn.commit()
        console.print(f"[green]✓ Imported {self.stats['vehicle_variants']} vehicle variants[/green]")
    
    def import_market_availability(self):
        """Import market availability from YAML files"""
        market_dir = self.data_dir / 'market-availability'
        if not market_dir.exists():
            console.print("[yellow]No market-availability directory found[/yellow]")
            return
        
        files = list(market_dir.glob('*.yaml'))
        console.print(f"[cyan]Importing {len(files)} market availability records...[/cyan]")
        
        for file_path in files:
            data = self.load_yaml_file(file_path)
            if not data:
                continue
            
            pricing = data.get('pricing', {})
            availability = data.get('availability', {})
            metadata = data.get('metadata', {})
            
            # Get updated_at with proper null handling
            updated_at = metadata.get('updated_at')
            if not updated_at:
                updated_at = metadata.get('created_at', datetime.now().isoformat())
            
            # Insert main market availability record
            self.cursor.execute("""
                INSERT INTO market_availability (
                    id, variant_id, market_code, currency,
                    price_base, price_including_vat, price_after_incentives,
                    available_from, available_until, availability_status,
                    delivery_time_weeks, pre_order_available, order_book_open,
                    notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'],
                data['variant_id'],
                data['market'],
                data['currency'],
                pricing.get('base'),
                pricing.get('including_vat'),
                pricing.get('after_incentives'),
                availability.get('available_from'),
                availability.get('available_until'),
                availability.get('status'),
                availability.get('delivery_time_weeks'),
                1 if availability.get('pre_order_available') else 0,
                1 if availability.get('order_book_open') else 0,
                data.get('notes'),
                metadata.get('created_at', datetime.now().isoformat()),
                updated_at
            ))
            
            # Import incentives
            for incentive in data.get('incentives', []):
                conditions = incentive.get('conditions')
                if isinstance(conditions, list):
                    conditions = json.dumps(conditions)
                
                self.cursor.execute("""
                    INSERT INTO market_incentives (
                        market_availability_id, incentive_type, name, amount,
                        currency, valid_from, valid_until, conditions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['id'],
                    incentive.get('type'),
                    incentive.get('name'),
                    incentive.get('amount'),
                    data['currency'],
                    incentive.get('valid_from'),
                    incentive.get('valid_until'),
                    conditions
                ))
            
            # Import colors
            for color in data.get('options', {}).get('colors', []):
                self.cursor.execute("""
                    INSERT INTO market_colors (
                        market_availability_id, name, code, price, is_default
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    data['id'],
                    color.get('name'),
                    color.get('code'),
                    color.get('price', 0),
                    1 if color.get('default') else 0
                ))
            
            # Import wheels
            for wheel in data.get('options', {}).get('wheels', []):
                self.cursor.execute("""
                    INSERT INTO market_wheels (
                        market_availability_id, name, size_inches, price, is_default
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    data['id'],
                    wheel.get('name'),
                    wheel.get('size_inches'),
                    wheel.get('price', 0),
                    1 if wheel.get('default') else 0
                ))
            
            # Import interiors
            for interior in data.get('options', {}).get('interiors', []):
                self.cursor.execute("""
                    INSERT INTO market_interiors (
                        market_availability_id, name, price, is_default
                    ) VALUES (?, ?, ?, ?)
                """, (
                    data['id'],
                    interior.get('name'),
                    interior.get('price', 0),
                    1 if interior.get('default') else 0
                ))
            
            self.stats['market_availability'] += 1
        
        self.conn.commit()
        console.print(f"[green]✓ Imported {self.stats['market_availability']} market availability records[/green]")
    
    def import_reference_data(self):
        """Import reference data (connectors, platforms)"""
        reference_dir = self.data_dir / 'reference'
        if not reference_dir.exists():
            console.print("[yellow]No reference directory found[/yellow]")
            return
        
        # Import connectors
        connectors_file = reference_dir / 'connectors.yaml'
        if connectors_file.exists():
            data = self.load_yaml_file(connectors_file)
            if data and 'connectors' in data:
                console.print(f"[cyan]Importing {len(data['connectors'])} connectors...[/cyan]")
                for connector in data['connectors']:
                    self.cursor.execute("""
                        INSERT INTO connectors (
                            id, name, type, max_power_kw, max_voltage_v,
                            max_current_a, regions, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        connector['id'],
                        connector['name'],
                        connector['type'],
                        connector.get('max_power_kw'),
                        connector.get('max_voltage_v'),
                        connector.get('max_current_a'),
                        json.dumps(connector.get('regions', [])),
                        connector.get('description')
                    ))
                    self.stats['connectors'] += 1
                console.print(f"[green]✓ Imported {self.stats['connectors']} connectors[/green]")
        
        # Import platforms
        platforms_file = reference_dir / 'platforms.yaml'
        if platforms_file.exists():
            data = self.load_yaml_file(platforms_file)
            if data and 'platforms' in data:
                console.print(f"[cyan]Importing {len(data['platforms'])} platforms...[/cyan]")
                for platform in data['platforms']:
                    self.cursor.execute("""
                        INSERT INTO platforms (
                            id, name, manufacturer, type, voltage_nominal_v,
                            architecture, battery_supplier, first_used,
                            description, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        platform['id'],
                        platform['name'],
                        platform['manufacturer'],
                        platform.get('architecture', 'dedicated'),  # Use architecture instead of type
                        platform.get('typical_voltage_v'),
                        platform.get('architecture'),
                        platform.get('battery_supplier'),
                        platform.get('introduced'),
                        platform.get('description'),
                        platform.get('notes')
                    ))
                    self.stats['platforms'] += 1
                console.print(f"[green]✓ Imported {self.stats['platforms']} platforms[/green]")
        
        self.conn.commit()
    
    def create_views(self):
        """Create useful database views"""
        console.print("[cyan]Creating database views...[/cyan]")
        
        # Full vehicle view with all data joined
        self.cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_vehicles_full AS
            SELECT 
                v.id as variant_id,
                v.variant_name,
                v.model_year,
                m.id as model_id,
                m.name as model_name,
                m.body_style,
                m.segment,
                mfr.id as manufacturer_id,
                mfr.name as manufacturer_name,
                mfr.country as manufacturer_country,
                v.battery_usable_kwh,
                v.battery_chemistry,
                v.range_wltp_km,
                v.range_real_world_km,
                v.consumption_real_world_kwh_100km,
                v.dc_charge_power_kw,
                v.dc_charge_time_10_80_min,
                v.total_power_kw,
                v.acceleration_0_100_sec,
                v.drive_type,
                v.price_base_eur
            FROM vehicle_variants v
            JOIN vehicle_models m ON v.model_id = m.id
            JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
        """)
        
        # Latest model year variants
        self.cursor.execute("""
            CREATE VIEW IF NOT EXISTS view_vehicles_latest AS
            SELECT * FROM view_vehicles_full
            WHERE model_year = (
                SELECT MAX(model_year) 
                FROM vehicle_variants v2 
                WHERE v2.model_id = model_id
            )
        """)
        
        self.conn.commit()
        console.print("[green]✓ Created database views[/green]")
    
    def print_stats(self):
        """Print import statistics"""
        table = Table(title="Import Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        for category, count in self.stats.items():
            table.add_row(category.replace('_', ' ').title(), str(count))
        
        console.print(table)
        
        # Print database size
        size_bytes = self.output_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        console.print(f"\n[cyan]Database size:[/cyan] {size_mb:.2f} MB")
    
    def build(self):
        """Main build process"""
        try:
            self.connect()
            self.create_schema()
            self.import_reference_data()
            self.import_manufacturers()
            self.import_vehicle_models()
            self.import_vehicle_variants()
            self.import_market_availability()
            self.create_views()
            self.print_stats()
            
            console.print("\n[green]✨ Database build complete![/green]")
            console.print(f"[cyan]Output:[/cyan] {self.output_path}")
            
        except Exception as e:
            console.print(f"\n[red]Error during build: {e}[/red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            if self.conn:
                self.conn.close()


@click.command()
@click.option('--input-dir', '-i', type=click.Path(exists=True, path_type=Path), 
              default=Path('data'), help='Input directory with YAML files')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              default=Path('evdb.db'), help='Output SQLite database file')
@click.option('--clean', is_flag=True, help='Remove existing database before building')
def main(input_dir: Path, output: Path, clean: bool):
    """
    Build SQLite database from YAML files
    
    Example:
        python build-sqlite.py --input-dir data --output evdb.db --clean
    """
    console.print(Panel.fit(
        "[bold cyan]EVDB SQLite Database Builder[/bold cyan]\n"
        "Converting YAML files to SQLite database",
        border_style="cyan"
    ))
    
    builder = DatabaseBuilder(input_dir, output, clean)
    builder.build()


if __name__ == '__main__':
    main()

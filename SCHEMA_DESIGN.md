# EVDB Schema Design

## Overview

Based on analysis of comprehensive EV databases (like ev-database.org), this document defines a flexible schema that handles:
- Multiple vehicle versions/trims
- Market-specific variants
- Changes over time (model years, updates)
- Optional equipment variations
- Missing/incomplete data
- Both manufacturer-claimed and real-world measurements

---

## Core Principles

### 1. Separation of Concerns
```
Manufacturer → Vehicle Model → Vehicle Variant → Market Availability → Specs
```

### 2. Versioning Strategy
- **Model** = Basic vehicle (e.g., "Tesla Model 3")
- **Variant** = Specific trim/version (e.g., "Long Range AWD")
- **Model Year** = Year-specific specs (2024 model may differ from 2023)
- **Market** = Region-specific availability and pricing

### 3. Data Quality Indicators
- Mark estimated vs. measured values
- Track data source (manufacturer, test, community)
- Support "unknown" fields without breaking validation

---

## Entity Relationship

```
manufacturers/
  └─ tesla.yaml

vehicle-models/
  └─ tesla-model-3.yaml (base model info)

vehicle-variants/
  ├─ tesla-model-3-rwd-2024.yaml
  ├─ tesla-model-3-long-range-awd-2024.yaml
  └─ tesla-model-3-performance-2024.yaml

market-availability/
  ├─ tesla-model-3-rwd-2024-europe.yaml
  ├─ tesla-model-3-rwd-2024-usa.yaml
  └─ tesla-model-3-long-range-awd-2024-china.yaml

connectors.yaml (shared reference data)
platforms.yaml (shared reference data)
```

---

## Schema Definitions

### 1. Manufacturer Schema

```yaml
# manufacturers/mercedes-benz.yaml
id: mercedes-benz
name: Mercedes-Benz
parent_company: Daimler AG
country: Germany
founded_year: 1926
website: https://www.mercedes-benz.com
logo_url: https://example.com/logos/mercedes-benz.svg

brands:
  - Mercedes-Benz
  - Mercedes-EQ
  - EQ (legacy)

markets:
  - europe
  - north-america
  - china
  - japan

social:
  twitter: "@MercedesBenz"
  linkedin: mercedes-benz

notes: |
  Mercedes-Benz is transitioning all EVs under the Mercedes-EQ sub-brand.
  
metadata:
  created_at: "2024-01-15"
  updated_at: "2024-01-15"
  data_quality: verified
  sources:
    - https://www.mercedes-benz.com/about
```

---

### 2. Vehicle Model Schema (Base Information)

```yaml
# vehicle-models/mercedes-eqs-suv.yaml
id: mercedes-eqs-suv
name: EQS SUV
manufacturer_id: mercedes-benz
full_name: Mercedes-Benz EQS SUV

body_style: suv
segment: luxury-suv  # JF segment
ev_dedicated_platform: true
platform: mercedes-eva2

production:
  start_date: "2022-01"
  end_date: null  # Still in production
  status: active  # active, discontinued, upcoming

seating:
  seats: 7
  rows: 3
  isofix_positions: 2

dimensions:
  length_mm: 5125
  width_mm: 1959
  width_with_mirrors_mm: 2157
  height_mm: 1718
  wheelbase_mm: 3210
  turning_circle_m: 11.0
  ground_clearance_mm: null  # Unknown

cargo:
  trunk_volume_l: 645
  trunk_volume_max_l: 2100  # Seats folded
  frunk_volume_l: 0
  roof_load_kg: 100

towing:
  hitch_available: true
  max_weight_braked_kg: 750
  max_weight_unbraked_kg: 750
  tongue_weight_kg: 100

features:
  heat_pump:
    available: true
    standard: true
  roof_rails: false
  panoramic_roof: true
  air_suspension: true

predecessor_id: null
successor_id: null

external_ids:
  wikipedia_slug: Mercedes-Benz_EQS

metadata:
  created_at: "2024-01-15"
  updated_at: "2024-01-15"
  data_quality: verified
  sources:
    - https://www.mercedes-benz.com/eqs-suv
```

---

### 3. Vehicle Variant Schema (Trim/Version-Specific)

This is the most detailed entity with all technical specifications.

```yaml
# vehicle-variants/mercedes-eqs-suv-450plus-2024.yaml
id: mercedes-eqs-suv-450plus-2024
vehicle_model_id: mercedes-eqs-suv
variant_name: "450+"
model_year: 2024

# Alternative names for this variant
aliases:
  - "EQS 450+"
  - "EQS SUV 450 4MATIC"

# Variant type
variant_type: standard  # standard, performance, long-range, etc.

# --- BATTERY ---
battery:
  # Capacity
  nominal_capacity_kwh: 125.0
  usable_capacity_kwh: 118.0
  capacity_data_source: measured  # measured, manufacturer, estimated
  
  # Chemistry
  chemistry: NMC  # NMC, LFP, NCA, LTO
  cathode_material: null  # NCM811, NCM622, LFP, etc.
  
  # Architecture
  voltage_architecture: 400  # 400, 800, etc.
  nominal_voltage_v: null
  pack_configuration: null  # e.g., "108s4p" 
  number_of_cells: null
  cell_form_factor: null  # pouch, cylindrical-2170, prismatic, etc.
  
  # Supplier
  battery_supplier: null  # CATL, LG Energy Solution, etc.
  
  # Warranty
  warranty_years: 10
  warranty_km: 250000
  warranty_capacity_percent: 70  # Guaranteed % after warranty period

# --- RANGE ---
range:
  # WLTP ratings
  wltp:
    - test_variant: TEL  # Test Energy Low
      range_km: 720
      rated_consumption_whkm: 188
      vehicle_consumption_whkm: 164
      fuel_equivalent_l100km: 2.1
      
    - test_variant: TEH  # Test Energy High
      range_km: 605
      rated_consumption_whkm: 225
      vehicle_consumption_whkm: 195
      fuel_equivalent_l100km: 2.5
  
  # EPA rating (for US market)
  epa:
    combined_miles: null  # Not rated for this market
    city_miles: null
    highway_miles: null
    consumption_mpge: null

# --- ENERGY CONSUMPTION ---
consumption:
  # Real-world measured
  real_world:
    combined_whkm: 219
    combined_data_source: calculated
    
    conditions:
      - condition_name: "City - Mild Weather"
        consumption_whkm: 152
        temperature_c: 23
        
      - condition_name: "Highway - Mild Weather"
        consumption_whkm: 238
        temperature_c: 23
        speed_kmh: 110
        
      - condition_name: "City - Cold Weather"
        consumption_whkm: 217
        temperature_c: -10
        
      - condition_name: "Highway - Cold Weather"
        consumption_whkm: 303
        temperature_c: -10
        speed_kmh: 110

  # Emissions
  co2_gkm: 0

# --- CHARGING ---
charging:
  # AC Charging (Home/Destination)
  ac:
    port_type: Type2  # Type2, Type1, etc.
    port_location: right-rear
    
    # Standard equipment
    onboard_charger_kw: 11
    
    # Optional equipment
    optional_chargers:
      - power_kw: 22
        option_name: "22kW On-Board Charger"
        cost_eur: 1200
    
    # Charging times
    charge_times:
      - charger_power_kw: 11
        time_0_100_minutes: 765  # 12h 45m
        charge_speed_kmh: 43
        
      - charger_power_kw: 22
        time_0_100_minutes: 390  # 6h 30m
        charge_speed_kmh: 83
    
    # Detailed charge curve (optional)
    charge_curve: null
  
  # DC Fast Charging
  dc:
    port_type: CCS2  # CCS2, CCS1, CHAdeMO, GB/T
    port_location: right-rear
    
    # Power specs
    max_charge_power_kw: 200
    avg_charge_power_10_80_kw: 160
    charge_time_10_80_minutes: 33
    charge_speed_kmh: 680
    
    # Manufacturer claimed specs
    manufacturer_claimed:
      max_power_kw: 200
      charge_from_percent: 10
      charge_to_percent: 80
      time_minutes: 31
    
    # Detailed charge curve (optional)
    charge_curve:
      - soc_percent: 10
        power_kw: 200
      - soc_percent: 20
        power_kw: 200
      - soc_percent: 50
        power_kw: 180
      - soc_percent: 80
        power_kw: 100
      # ... more data points
  
  # Smart charging features
  smart_features:
    autocharge: true  # Automatic payment
    plug_and_charge: true
    plug_and_charge_protocol: ISO-15118-2
    preconditioning: true
    preconditioning_auto_nav: true  # Automatic via navigation

# --- BIDIRECTIONAL CHARGING (V2X) ---
bidirectional:
  v2l:  # Vehicle-to-Load (powering devices)
    supported: false
    max_output_kw: null
    outlets_exterior: 0
    outlets_interior: 0
  
  v2h_ac:  # Vehicle-to-Home (AC)
    supported: false
    max_output_kw: null
  
  v2h_dc:  # Vehicle-to-Home (DC)
    supported: false
    max_output_kw: null
  
  v2g_ac:  # Vehicle-to-Grid (AC)
    supported: false
    max_output_kw: null
  
  v2g_dc:  # Vehicle-to-Grid (DC)
    supported: false
    max_output_kw: null

# --- PERFORMANCE ---
performance:
  # Acceleration
  acceleration_0_100_kmh_s: 6.8
  acceleration_0_60_mph_s: null
  
  # Top speed
  top_speed_kmh: 210
  top_speed_limited: true  # Electronic limiter
  
  # Power
  total_power_kw: 265
  total_power_hp: 360
  total_power_ps: 360
  
  # Torque
  total_torque_nm: 568
  
  # Drivetrain
  drive_type: RWD  # RWD, FWD, AWD
  motor_count: 1
  motor_layout: rear  # front, rear, front+rear
  
  # Motor details (optional)
  motors:
    - position: rear
      type: PSM  # PSM (Permanent Magnet Synchronous), ASM (Asynchronous), etc.
      power_kw: 265
      torque_nm: 568

# --- WEIGHT ---
weight:
  unladen_eu_kg: 2730  # EU unladen weight
  curb_weight_kg: 2730  # Alternative naming
  gross_vehicle_weight_kg: 3300  # GVWR
  max_payload_kg: 645
  
  # Distribution
  weight_distribution_front_percent: null
  weight_distribution_rear_percent: null

# --- EFFICIENCY RATING ---
efficiency:
  # Long-distance suitability (1-Stop Range benchmark)
  long_distance_rating: 3.5  # Out of 5.0
  one_stop_range_km: 559
  one_stop_range_conditions:
    - weather: mild
      range_km: 636
      first_leg_km: 446
      charging_time_min: 15
      second_leg_km: 190
      
    - weather: average
      range_km: 559
      first_leg_km: 393
      charging_time_min: 15
      second_leg_km: 167
      
    - weather: cold
      range_km: 499
      first_leg_km: 350
      charging_time_min: 15
      second_leg_km: 149

# --- AVAILABILITY ---
availability:
  production_status: active  # active, discontinued, announced, pre-production
  order_start_date: "2023-10"
  order_end_date: null
  delivery_start_date: "2024-01"
  
  markets:
    - europe
    - middle-east
    # (Market-specific pricing in separate files)

# --- VERSIONING ---
versioning:
  generation: 1  # Which generation of this model
  facelift: false  # Mid-cycle refresh
  
  predecessor_variant_id: mercedes-eqs-suv-450plus-2023
  successor_variant_id: null
  
  changes_from_predecessor:
    - "+40 km WLTP range"
    - "Updated interior trim options"
    - "New battery management software"

# --- EXTERNAL REFERENCES ---
external_ids:
  vin_pattern: "W1K*"  # Partial VIN pattern
  model_code: "X296"

# --- METADATA ---
metadata:
  created_at: "2024-01-15"
  updated_at: "2024-02-01"
  created_by: contributor_name
  
  data_quality: verified  # verified, unverified, estimated, partial
  verification_date: "2024-02-01"
  verification_method: manufacturer_spec_sheet
  
  sources:
    - url: https://www.mercedes-benz.com/eqs-suv/specifications
      type: manufacturer
      accessed_date: "2024-01-15"
  
  notes: |
    This variant replaced the 2023 model with improved range.
    Battery supplier changed from SK to CATL mid-2024.

# --- OPTIONAL: MULTIMEDIA ---
media:
  images:
    - url: https://example.com/eqs-suv-450-front.jpg
      type: exterior
      angle: front
    - url: https://example.com/eqs-suv-450-interior.jpg
      type: interior
      
  videos:
    - url: https://youtube.com/watch?v=xxxxx
      type: review
      title: "EQS SUV 450+ Full Review"
```

---

### 4. Market Availability Schema

Separates market-specific information (pricing, options, availability).

```yaml
# market-availability/mercedes-eqs-suv-450plus-2024-germany.yaml
id: mercedes-eqs-suv-450plus-2024-germany
variant_id: mercedes-eqs-suv-450plus-2024
market: germany
market_region: europe

# Pricing
pricing:
  base_price: 109000
  currency: EUR
  price_includes_vat: true
  
  # Incentives
  incentives:
    - name: "Federal EV Subsidy"
      amount: 6750
      currency: EUR
      end_date: "2024-12-31"
      
  price_as_of: "2024-01-15"

# Market-specific specs (if different)
market_specifications:
  # Some markets have different battery/power specs
  battery_usable_kwh: 118.0  # Could differ by market
  
  # Equipment that's standard vs optional varies by market
  standard_equipment:
    - heat_pump
    - led_headlights
    - parking_sensors
    
  optional_packages:
    - name: "Premium Plus Package"
      price: 5000
      currency: EUR
      includes:
        - air_suspension
        - 22kw_onboard_charger
        - massage_seats

# Availability
availability:
  available: true
  order_start_date: "2023-10-15"
  estimated_delivery_months: 3-6
  
# Competitors (market-specific)
competitors:
  - bmw-ix-xdrive50-2024
  - audi-q8-etron-55-2024

# Market-specific notes
notes: |
  Price includes 19% VAT.
  Federal EV subsidy reduces net price to €102,250.

metadata:
  updated_at: "2024-01-15"
  data_quality: verified
  source: https://www.mercedes-benz.de/konfigurator
```

---

### 5. Shared Reference Data

#### Connectors

```yaml
# connectors.yaml
connectors:
  - id: type2
    name: Type 2
    other_names:
      - IEC 62196-2
      - Mennekes
    current_types:
      - AC-single-phase
      - AC-three-phase
    max_current_a: 80
    max_voltage_v: 480
    max_power_kw: 43
    regions:
      - europe
      - australia
    
  - id: ccs2
    name: CCS Combo 2
    other_names:
      - Combined Charging System
      - Combo 2
    current_types:
      - DC
    max_current_a: 500
    max_voltage_v: 1000
    max_power_kw: 350
    regions:
      - europe
      - australia
```

#### Platforms

```yaml
# platforms.yaml
platforms:
  - id: mercedes-eva2
    name: Mercedes-Benz EVA2
    manufacturer: mercedes-benz
    full_name: Electric Vehicle Architecture 2
    ev_dedicated: true
    voltage: 400
    launch_year: 2021
    vehicles:
      - mercedes-eqs-sedan
      - mercedes-eqs-suv
      - mercedes-eqe-sedan
```

---

## Schema Validation Rules

### JSON Schema Fragments

#### Required Fields
```json
{
  "required": [
    "id",
    "vehicle_model_id",
    "variant_name",
    "model_year",
    "battery",
    "charging",
    "metadata"
  ]
}
```

#### Conditional Requirements
```json
{
  "if": {
    "properties": { "availability.production_status": { "const": "active" } }
  },
  "then": {
    "required": ["availability.order_start_date"]
  }
}
```

#### Enum Constraints
```json
{
  "properties": {
    "battery.chemistry": {
      "enum": ["NMC", "NCA", "LFP", "LTO", "LMO", "NCM", null]
    },
    "performance.drive_type": {
      "enum": ["RWD", "FWD", "AWD"]
    }
  }
}
```

---

## Handling Evolution & Variants

### Example: Tesla Model 3 Over Time

```
vehicle-models/
  tesla-model-3.yaml (base info, doesn't change much)

vehicle-variants/
  # 2024 Model Year
  tesla-model-3-rwd-2024.yaml (54 kWh, LFP, 272 mi EPA)
  tesla-model-3-long-range-awd-2024.yaml (82 kWh, NCA, 341 mi EPA)
  tesla-model-3-performance-2024.yaml (82 kWh, 162 mph top speed)
  
  # 2025 Model Year (Highland refresh)
  tesla-model-3-rwd-2025.yaml (60 kWh, new design)
  tesla-model-3-long-range-awd-2025.yaml (80 kWh, new interior)
  tesla-model-3-performance-2025.yaml (discontinued)

market-availability/
  # US Market
  tesla-model-3-rwd-2024-usa.yaml ($38,990)
  tesla-model-3-long-range-awd-2024-usa.yaml ($45,990)
  
  # EU Market  
  tesla-model-3-rwd-2024-europe.yaml (€42,990)
  tesla-model-3-long-range-awd-2024-europe.yaml (€52,990)
  
  # China Market (different specs!)
  tesla-model-3-rwd-2024-china.yaml (Made in Shanghai, different range)
```

### Linking Between Versions

```yaml
# tesla-model-3-rwd-2025.yaml
versioning:
  generation: 2  # Highland = generation 2
  facelift: false
  predecessor_variant_id: tesla-model-3-rwd-2024
  changes_from_predecessor:
    - "New exterior design (Project Highland)"
    - "Updated interior with 8-inch rear display"
    - "Improved suspension"
    - "+6 kWh battery capacity"
    - "+10 mi EPA range"
```

---

## Data Quality Indicators

Every measurement should indicate its source:

```yaml
battery:
  usable_capacity_kwh: 118.0
  capacity_data_source: measured  # measured, manufacturer, calculated, estimated, community

range:
  wltp:
    - range_km: 720
      data_source: manufacturer  # From official spec sheet
  
  real_world:
    combined_km: 540
    data_source: calculated  # EVDB methodology from test data
```

---

## Datasette Integration

### SQLite Schema (Generated from YAML)

The build script flattens the YAML into relational tables:

```sql
-- Core tables
CREATE TABLE manufacturers (...);
CREATE TABLE vehicle_models (...);
CREATE TABLE vehicle_variants (...);  -- Main table with most specs
CREATE TABLE market_availability (...);

-- Normalized tables for complex data
CREATE TABLE variant_range_conditions (...);
CREATE TABLE variant_consumption_conditions (...);
CREATE TABLE variant_charge_times (...);
CREATE TABLE variant_optional_equipment (...);
CREATE TABLE variant_motors (...);
CREATE TABLE variant_sources (...);

-- Reference tables
CREATE TABLE connectors (...);
CREATE TABLE platforms (...);
```

### Datasette Facets

```json
{
  "databases": {
    "evdb": {
      "tables": {
        "vehicle_variants": {
          "facets": [
            "manufacturer",
            "model_year",
            "body_style",
            "battery_chemistry",
            "drive_type",
            "charging_dc_max_power_kw"
          ]
        }
      }
    }
  }
}
```

---

## Example Queries (via Datasette SQL)

### Find all AWD vehicles with >500km range
```sql
SELECT 
  m.name as manufacturer,
  vm.name as model,
  vv.variant_name,
  vv.model_year,
  vv.performance_drive_type,
  vv.range_real_world_combined_km
FROM vehicle_variants vv
JOIN vehicle_models vm ON vv.vehicle_model_id = vm.id
JOIN manufacturers m ON vm.manufacturer_id = m.id
WHERE vv.performance_drive_type = 'AWD'
  AND vv.range_real_world_combined_km > 500
ORDER BY vv.range_real_world_combined_km DESC;
```

### Compare charging speeds
```sql
SELECT 
  m.name as manufacturer,
  vm.name as model,
  vv.variant_name,
  vv.battery_usable_capacity_kwh as battery,
  vv.charging_dc_max_charge_power_kw as max_dc,
  vv.charging_dc_charge_time_10_80_minutes as charge_time,
  vv.charging_dc_charge_speed_kmh as km_per_hour
FROM vehicle_variants vv
JOIN vehicle_models vm ON vv.vehicle_model_id = vm.id
JOIN manufacturers m ON vm.manufacturer_id = m.id
WHERE vv.charging_dc_max_charge_power_kw >= 150
ORDER BY vv.charging_dc_charge_speed_kmh DESC
LIMIT 20;
```

---

## Streamlit Integration

### Example Dashboard Queries

```python
import streamlit as st
import pandas as pd
import sqlite3

# Connect to Datasette SQLite
conn = sqlite3.connect('evdb.db')

# Load data
df = pd.read_sql_query("""
    SELECT 
        m.name as manufacturer,
        vm.name as model,
        vv.variant_name,
        vv.battery_usable_capacity_kwh,
        vv.range_real_world_combined_km,
        vv.charging_dc_max_charge_power_kw
    FROM vehicle_variants vv
    JOIN vehicle_models vm ON vv.vehicle_model_id = vm.id
    JOIN manufacturers m ON vm.manufacturer_id = m.id
    WHERE vv.model_year = 2024
""", conn)

# Streamlit UI
st.title("EV Comparison Dashboard")

# Filters
manufacturers = st.multiselect("Manufacturer", df['manufacturer'].unique())
min_range = st.slider("Minimum Range (km)", 200, 800, 400)

# Filter data
filtered = df[
    (df['manufacturer'].isin(manufacturers) if manufacturers else True) &
    (df['range_real_world_combined_km'] >= min_range)
]

# Display
st.scatter_chart(
    filtered,
    x='battery_usable_capacity_kwh',
    y='range_real_world_combined_km',
    color='manufacturer'
)
```

---

## Migration Path from Current Hugo Structure

1. **Extract existing data** from markdown front matter
2. **Split into new structure** (model → variant → market)
3. **Enrich** with missing fields (mark as `null` or `data_quality: partial`)
4. **Validate** against JSON schemas
5. **Import** to SQLite
6. **Deploy** Datasette

---

## Next Steps

1. Finalize JSON schemas for each entity
2. Create example YAML files (5-10 popular EVs)
3. Build validation script
4. Build SQLite import script
5. Configure Datasette metadata
6. Create contribution templates
7. Document data entry guide

---

## Summary

This schema design:
✅ **Handles complexity** (multiple variants, markets, changes over time)  
✅ **Prevents duplication** (shared models, connectors, platforms)  
✅ **Supports incomplete data** (nullable fields, data quality markers)  
✅ **Enables versioning** (predecessor/successor links)  
✅ **Git-friendly** (YAML files, one variant per file)  
✅ **Datasette-ready** (flattens to relational tables)  
✅ **Streamlit-compatible** (SQL queries, pandas DataFrames)  
✅ **Extensible** (add new fields without breaking existing data)

---

*Schema Design Date: February 6, 2026*

# Contributing to EVDB

Thank you for your interest in contributing to the Open Electric Vehicle Database! This guide will help you add vehicle data, fix errors, or improve the database structure.

## 🎯 What We Need

We welcome contributions of:

- **Vehicle specifications** - Battery, range, charging, performance data
- **Market pricing** - Regional pricing and available options
- **Real-world data** - Actual consumption, range, charging speeds
- **Corrections** - Fix errors or outdated information
- **Translations** - Help internationalize the database
- **Code improvements** - Scripts, validation, documentation

## 🚀 Quick Start

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/evdb.git
cd evdb

# Add upstream remote
git remote add upstream https://github.com/gaia-charge/evdb.git
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create a Branch

```bash
git checkout -b add-vehicle-name
# Example: add-nissan-ariya-2024
```

## 📝 Adding a Vehicle

### Step 1: Check if Manufacturer Exists

Look in `data/manufacturers/` for the manufacturer. If it doesn't exist, create it first.

**Example:** `data/manufacturers/nissan.yaml`

```yaml
id: nissan
name: Nissan Motor Corporation
name_short: Nissan
country: Japan
headquarters: Yokohama, Japan
founded_year: 1933
website: https://www.nissan-global.com/
logo_url: https://www.nissan-global.com/EN/LOGO/logo.png

metadata:
  data_source: "Official Nissan website"
  data_source_url: https://www.nissan-global.com/
  last_updated: "2024-02-07"
  verified: true
  notes: "Major Japanese automaker"
```

### Step 2: Create Vehicle Model

**Example:** `data/vehicle-models/nissan-ariya.yaml`

```yaml
id: nissan-ariya
manufacturer_id: nissan
name: Ariya
model_code: FE0
body_style: suv
segment: compact_suv
first_production_year: 2022
production_status: current

dimensions:
  length_mm: 4595
  width_mm: 1850
  height_mm: 1660
  wheelbase_mm: 2775
  curb_weight_min_kg: 1900
  curb_weight_max_kg: 2300
  cargo_capacity_seats_up_l: 466
  cargo_capacity_seats_down_l: 1300

seating:
  seating_capacity: 5
  seat_configuration: "2+3"

metadata:
  data_source: "Nissan official specifications"
  data_source_url: https://www.nissan-global.com/EN/ARIYA/
  last_updated: "2024-02-07"
  verified: true
```

### Step 3: Create Vehicle Variant

This is where detailed specs go. Use a template from `templates/vehicle-variant-template.yaml`.

**Example:** `data/vehicle-variants/nissan-ariya-87kwh-fwd-2024.yaml`

```yaml
id: nissan-ariya-87kwh-fwd-2024
vehicle_model_id: nissan-ariya
variant_name: "87kWh FWD"
model_year: 2024

# Battery & Range (REQUIRED)
battery_total_capacity_kwh: 90.0
battery_usable_capacity_kwh: 87.0
battery_chemistry: ncm811
battery_voltage_nominal_v: 400

range_wltp_km: 520
range_epa_km: null  # Not available
range_real_world_combined_km: 450
range_real_world_highway_km: 380
range_real_world_city_km: 570

# Powertrain (REQUIRED)
drivetrain: fwd
motors:
  front:
    type: permanent_magnet
    max_power_kw: 178
    max_power_hp: 242
    max_torque_nm: 300

# Performance (REQUIRED)
acceleration_0_100_kmh_s: 7.5
top_speed_kmh: 160

# Charging (REQUIRED)
charging_ac_max_charge_power_kw: 22.0
charging_ac_charge_time_0_100_hours: 4.5

charging_dc_max_charge_power_kw: 130.0
charging_dc_charge_time_10_80_minutes: 35
charging_dc_charge_speed_kmh: 370  # km added per hour

# Efficiency (REQUIRED)
consumption_wltp_kwh_per_100km: 16.8
consumption_real_world_combined_kwh_per_100km: 19.3

# Dimensions & Weight
curb_weight_kg: 2100
gross_vehicle_weight_kg: 2600
towing_capacity_braked_kg: 1500
towing_capacity_unbraked_kg: 750

metadata:
  data_source: "Nissan official specifications + real-world testing"
  data_source_url: https://www.nissan-global.com/EN/ARIYA/
  last_updated: "2024-02-07"
  verified: true
  confidence_level: high
  notes: "Real-world data from multiple test drives"
```

### Step 4: Add Market Availability

**Example:** `data/market-availability/nissan-ariya-87kwh-fwd-2024-de.yaml`

```yaml
id: nissan-ariya-87kwh-fwd-2024-de
variant_id: nissan-ariya-87kwh-fwd-2024
market: germany

# Pricing (REQUIRED)
pricing_base_price: 54990
pricing_currency: EUR
pricing_on_the_road_price: 56800
pricing_destination_charge: 1200
pricing_registration_fee: 610

# Availability
availability_status: available
availability_lead_time_weeks: 8
availability_production_location: "Tochigi, Japan"

# Incentives
incentives:
  - type: federal_subsidy
    name: "BAFA Umweltbonus"
    amount: 4500
    currency: EUR
    conditions: "List price under €65,000"
  
  - type: tax_exemption
    name: "Kfz-Steuer exemption"
    amount: 0
    duration_years: 10
    conditions: "First registration before 2025"

# Variants & Options
variants:
  colors:
    - name: "Glacier White"
      price: 0
      availability: standard
    
    - name: "Aurora Green"
      price: 890
      availability: standard
  
  wheels:
    - name: "19-inch alloy"
      price: 0
      diameter_inch: 19
      availability: standard
    
    - name: "20-inch alloy"
      price: 1200
      diameter_inch: 20
      availability: optional

  packages:
    - name: "Tech Package"
      price: 2500
      features:
        - "ProPILOT Assist with Navi-link"
        - "Intelligent Around View Monitor"
        - "Head-Up Display"

# Most popular configuration
typical_configuration:
  total_price: 59790
  includes:
    - "Aurora Green paint (+€890)"
    - "20-inch wheels (+€1,200)"
    - "Tech Package (+€2,500)"
    - "Winter Package (+€1,200)"

metadata:
  data_source: "Nissan Germany official price list"
  data_source_url: https://www.nissan.de/fahrzeuge/neuwagen/ariya.html
  last_updated: "2024-02-07"
  verified: true
```

## ✅ Validation

Before submitting, **always validate your YAML files**:

```bash
# Validate a single file
python scripts/validate.py --file data/vehicle-variants/nissan-ariya-87kwh-fwd-2024.yaml

# Validate all files
python scripts/validate.py --directory data/

# Build database to check relationships
python scripts/build-sqlite.py
```

### Common Validation Errors

**Missing required fields:**
```
❌ Required field 'battery_usable_capacity_kwh' is missing
```
→ Add the missing field or set to `null` if truly unavailable

**Invalid enum value:**
```
❌ 'awd' is not a valid value for 'drivetrain' (must be one of: fwd, rwd, awd)
```
→ Check `schemas/enums.json` for valid values

**Invalid reference:**
```
❌ Vehicle model 'nissan-ariya' not found
```
→ Create the manufacturer and model files first

**Type error:**
```
❌ Expected number for 'battery_usable_capacity_kwh', got string
```
→ Remove quotes from numeric values: `87.0` not `"87.0"`

## 📋 Data Quality Standards

### Required Fields

Every vehicle variant **must** include:

- **Battery**: `battery_usable_capacity_kwh`
- **Range**: `range_wltp_km` or `range_epa_km`
- **Power**: `motors.front.max_power_kw` or `motors.rear.max_power_kw`
- **Charging**: `charging_dc_max_charge_power_kw`
- **Efficiency**: `consumption_wltp_kwh_per_100km`

### Data Sources

**Always attribute your sources:**

```yaml
metadata:
  data_source: "Official manufacturer spec sheet + Car and Driver testing"
  data_source_url: https://www.caranddriver.com/reviews/...
  last_updated: "2024-02-07"
  verified: true
  confidence_level: high
```

**Confidence levels:**
- `high` - Official specs or verified real-world data
- `medium` - Third-party testing, may have small variations
- `low` - Community reports, estimates, or incomplete data

### Real-World Data

When adding real-world range/consumption:

1. **Prefer averages** from multiple tests over single data points
2. **Specify conditions**: "Mixed driving 50% highway / 50% city, 20°C"
3. **Link to source**: Blog post, video, test report
4. **Be conservative**: Round down slightly for safety

**Example:**
```yaml
range_real_world_combined_km: 450  # Average from 5 independent tests
range_real_world_highway_km: 380   # @120 km/h, 15°C
range_real_world_city_km: 570      # @30 km/h avg, 20°C

metadata:
  notes: |
    Real-world data averaged from:
    - ADAC EcoTest (455 km, 18.5 kWh/100km)
    - Auto Bild test (448 km, 19.1 kWh/100km)
    - InsideEVs 70mph test (380 km highway)
```

## 🔀 Pull Request Process

### 1. Commit Your Changes

```bash
git add data/
git commit -m "Add Nissan Ariya 87kWh FWD 2024 + German market data"
```

**Commit message format:**
```
Add [Vehicle Name] [Year] + [Markets]

- Created manufacturer: [if new]
- Created model: [model name]
- Created variant: [variant details]
- Added markets: [country codes]
```

### 2. Push to Your Fork

```bash
git push origin add-nissan-ariya-2024
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request"
3. Fill in the template:
   - Vehicle name and year
   - Data sources used
   - Any notes or caveats
   - Checklist of validation steps

### 4. PR Review

We'll review your PR and may ask for:

- Additional sources for verification
- Corrections to specs
- More detailed metadata
- Real-world data if available

**Typical turnaround:** 1-3 days

## 🐛 Reporting Issues

Found an error? [Create an issue](https://github.com/gaia-charge/evdb/issues/new) with:

- **Vehicle affected** - Manufacturer, model, variant
- **Field with error** - Which spec is wrong?
- **Correct value** - What should it be?
- **Source** - Link to official spec or test

## 📚 Resources

### Understanding YAML

- Basic syntax: https://yaml.org/
- Our templates: `templates/`
- Example files: `data/vehicle-variants/`

### Finding Specifications

**Official Sources (Best):**
- Manufacturer websites (spec sheets, press releases)
- EPA FuelEconomy.gov (USA data)
- WLTP databases (EU data)

**Third-Party Testing (Good):**
- ADAC EcoTest (Germany)
- InsideEVs 70mph range test (USA)
- Edmunds testing (USA)
- What Car? Real Range test (UK)

**Community Data (Use with caution):**
- ev-database.org
- Reddit communities (r/electricvehicles)
- Owner forums
- YouTube reviews

### Tools

- **Datasette** - Browse existing data: `datasette evdb.db --metadata metadata.json`
- **SQLite** - Query database: `sqlite3 evdb.db`
- **JSON Schema** - Understand validation: `schemas/*.schema.json`

## 💡 Tips

### Start Small

Your first contribution doesn't need to be perfect! Start with:

1. A single vehicle variant
2. Just one market
3. Official specs only (skip real-world data initially)

You can always add more detail later.

### Reuse Existing Data

If adding a new variant of an existing model:

```bash
# Copy an existing variant as template
cp data/vehicle-variants/tesla-model-3-long-range-awd-2024.yaml \
   data/vehicle-variants/tesla-model-3-rwd-2024.yaml

# Edit the new file with variant-specific changes
```

### Check Similar Vehicles

Unsure about a field? Look at similar vehicles:

```bash
# Find all Tesla Model 3 variants
ls data/vehicle-variants/tesla-model-3-*.yaml

# Find all German market data
ls data/market-availability/*-de.yaml
```

## 🎯 Priority Vehicles

We especially need data for:

### Markets
- 🇬🇧 United Kingdom
- 🇳🇴 Norway
- 🇨🇳 China
- 🇯🇵 Japan
- 🇦🇺 Australia

### Segments
- Budget EVs (under €35,000)
- Light commercial vehicles
- Performance variants
- Long-range variants (600km+)

### Manufacturers
- Chinese brands (BYD, NIO, XPeng, Li Auto)
- Legacy automakers (Ford, GM, Stellantis)
- New entrants (Rivian, Lucid, Polestar)

See [TODO.md](TODO.md) Phase 6 for current status and targets.

## 📜 License

By contributing, you agree that your contributions will be licensed under:

- **Data**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Code**: MIT License

This means your data will be:
- ✅ Free to use commercially
- ✅ Free to modify and redistribute
- ✅ Attributed to you as contributor
- ✅ Shared under the same license

## 🙏 Questions?

- **GitHub Discussions**: Ask questions, share ideas
- **Discord**: Join our community (link coming soon)
- **Email**: evdb@gaiacharge.com (coming soon)

---

**Thank you for helping build the open EV database! 🚗⚡**

Every contribution, no matter how small, makes electric vehicle data more accessible to everyone.

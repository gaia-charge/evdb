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
country: JP
founded: 1933
website: https://www.nissan-global.com/

metadata:
  sources:
    - https://www.nissan-global.com/
  created_at: "2026-02-25"
```

Required fields: `id`, `name`, `country` (ISO 3166-1 alpha-2 code).

### Step 2: Create Vehicle Model

**Example:** `data/vehicle-models/nissan-ariya.yaml`

```yaml
id: nissan-ariya
manufacturer_id: nissan
brand: Nissan
name: Ariya
body_style: suv
segment: C
platform: CMF-EV
production_start: 2022-03
generation: 1
production_status: active

dimensions:
  length_mm: 4595
  width_mm: 1850
  height_mm: 1660
  wheelbase_mm: 2775

interior:
  seating_capacity: 5
  cargo_volume_liters: 466
  cargo_volume_seats_down_liters: 1300

metadata:
  sources:
    - https://www.nissan-global.com/EN/ARIYA/
  created_at: "2026-02-25"
```

Required fields: `id`, `name`, `manufacturer_id`, `brand`, `body_style`, `segment`. `brand` is the consumer-facing brand name — it can differ from the manufacturer for multi-brand groups (e.g. manufacturer `stellantis`, brand `Fiat`).

### Step 3: Create Vehicle Variant

This is where detailed specs go. Use a template from `templates/vehicle-variant-template.yaml`.

**Example:** `data/vehicle-variants/nissan-ariya-87kwh-fwd-2024.yaml`

The variant schema enforces `additionalProperties: false` — only fields defined in
`schemas/vehicle-variant.schema.json` are accepted, all grouped in nested blocks:

```yaml
id: nissan-ariya-87kwh-fwd-2024
name: 87kWh FWD
model_id: nissan-ariya
model_year: 2024

battery:
  usable_kwh: 87.0
  total_kwh: 90.0
  chemistry: NCM
  warranty_years: 8
  warranty_km: 160000

range:
  wltp_km: 520
  epa_km: null  # not available
  real_world_km: 450
  real_world_source: "Averaged from ADAC EcoTest and Auto Bild tests"

charging:
  ac_max_kw: 22
  ac_phases: 3
  ac_connector: Type2
  dc_max_kw: 130
  dc_connector: CCS2
  time_10_to_80_min: 35

performance:
  top_speed_kmh: 160
  acceleration_0_100_sec: 7.5
  total_power_kw: 178
  total_torque_nm: 300
  drive_type: FWD

efficiency:
  wltp_kwh_per_100km: 16.8
  real_world_kwh_per_100km: 19.3

weight:
  curb_weight_kg: 2100
  gross_vehicle_weight_kg: 2600
  towing_capacity_braked_kg: 1500
  towing_capacity_unbraked_kg: 750

metadata:
  data_quality: verified
  created_at: "2026-02-25"
  sources:
    - https://www.nissan-global.com/EN/ARIYA/
    - https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/ariya/
```

Required fields: `id`, `name`, `model_id`, `model_year`. Everything else is
optional but the more complete, the better — `battery.usable_kwh`,
`range.wltp_km`, `charging.dc_max_kw`, `performance.total_power_kw`, and
`efficiency.wltp_kwh_per_100km` are the minimum for a useful entry.

### Step 4: Add Market Availability

**Example:** `data/market-availability/nissan-ariya-87kwh-fwd-2024-de.yaml`

The file name is `<variant-id>-<market>.yaml` with the market code lowercase,
and must equal the `id` field.

```yaml
id: nissan-ariya-87kwh-fwd-2024-de
variant_id: nissan-ariya-87kwh-fwd-2024
market: DE
currency: EUR
availability_status: available
available_from: "2024-01"

pricing:
  base_price: 54990
  price_including_vat: 54990
  vat_rate_percent: 19
  destination_charge: 1200

incentives:
  - name: "Kfz-Steuer exemption"
    type: tax_exemption
    amount: 0
    description: "Vehicle tax exemption for BEVs"
    eligibility: "First registration before 2026"

notes: >
  German market pricing for the 87 kWh FWD variant. Build-to-order,
  typical delivery 8 weeks.

metadata:
  data_quality: verified
  price_checked_at: "2026-02-25"
  created_at: "2026-02-25"
  sources:
    - https://www.nissan.de/fahrzeuge/neuwagen/ariya.html
```

Required fields: `id`, `variant_id`, `market` (uppercase ISO country code),
`currency`. `incentives[].type` must be one of: `rebate`, `tax_credit`,
`grant`, `subsidy`, `tax_exemption`, `discount`.

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
❌ 'model_year' is a required property
```
→ Add the missing field or set to `null` if truly unavailable

**Invalid enum value:**
```
❌ 'on_sale' is not one of ['available', 'pre-order', 'limited', 'discontinued', 'announced']
```
→ Check the `enum` lists in `schemas/*.schema.json` for valid values

**Invalid reference:**
```
❌ Vehicle model 'nissan-ariya' not found
```
→ Create the manufacturer and model files first

**Type error:**
```
❌ At 'battery -> usable_kwh': '87.0' is not of type 'number'
```
→ Remove quotes from numeric values: `87.0` not `"87.0"`

## 📋 Data Quality Standards

### Required Fields

Every vehicle variant **should** include (beyond the schema-required
`id`, `name`, `model_id`, `model_year`):

- **Battery**: `battery.usable_kwh`
- **Range**: `range.wltp_km` or `range.epa_km`
- **Power**: `performance.total_power_kw`
- **Charging**: `charging.dc_max_kw`
- **Efficiency**: `efficiency.wltp_kwh_per_100km`

### Data Sources

**Always attribute your sources** — deep links to the exact spec or price
page, not just the manufacturer homepage:

```yaml
metadata:
  data_quality: verified
  created_at: "2026-02-25"
  price_checked_at: "2026-02-25"  # market files: when the price was last checked
  sources:
    - https://www.nissan.de/fahrzeuge/neuwagen/ariya/preise.html
    - https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/ariya/
```

**Data quality levels** (`metadata.data_quality`):
- `verified` - confirmed against an official source that is cited in `sources`
- `estimated` - derived or inferred (state how in `notes`)
- `partial` - incomplete record, some fields missing
- `unverified` - taken from a single secondary source, not yet cross-checked

Records without sources cannot claim `verified`.

### Real-World Data

When adding real-world range/consumption:

1. **Prefer averages** from multiple tests over single data points
2. **Specify conditions**: "Mixed driving 50% highway / 50% city, 20°C"
3. **Link to source**: Blog post, video, test report
4. **Be conservative**: Round down slightly for safety

**Example:**
```yaml
range:
  real_world_km: 450  # average from independent tests
  real_world_source: >
    Averaged from ADAC EcoTest (455 km, 18.5 kWh/100km),
    Auto Bild test (448 km, 19.1 kWh/100km),
    InsideEVs 70mph test (380 km highway)
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

**Community Data (Use with caution, never as the only source):**
- Reddit communities (r/electricvehicles)
- Owner forums
- YouTube reviews

**Do not use ev-database.org as a source** — its licensing is incompatible
with this database.

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

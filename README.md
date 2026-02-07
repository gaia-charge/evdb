# EVDB - Open Electric Vehicle Database

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

A comprehensive, open-source database of electric vehicles with detailed specifications, built with **YAML + JSON Schema + Datasette + Streamlit**.

## 🏗️ Architecture

```
YAML Source Files → JSON Schema Validation → SQLite Database → Datasette API + Streamlit Dashboards
```

### Why This Stack?

- **YAML**: Human-readable, git-friendly source format with comments
- **JSON Schema**: Industry-standard validation ensures data quality
- **SQLite**: Single-file database, portable, fast, perfect for datasets
- **Datasette**: Instant API and web UI for SQLite databases
- **Streamlit**: Python-native dashboards for data visualization

## 📊 Data Structure

### Four Core Entities

```
manufacturers/
  └─ tesla.yaml
  └─ volkswagen.yaml

vehicle-models/
  └─ tesla-model-3.yaml (base info)
  └─ volkswagen-id4.yaml

vehicle-variants/
  ├─ tesla-model-3-rwd-2024.yaml (detailed specs)
  ├─ tesla-model-3-long-range-awd-2024.yaml
  └─ volkswagen-id4-pure-2024.yaml

market-availability/
  ├─ tesla-model-3-rwd-2024-germany.yaml (pricing)
  ├─ tesla-model-3-rwd-2024-usa.yaml
  └─ volkswagen-id4-pure-2024-poland.yaml
```

### Why This Separation?

- **Manufacturer** - Company info (name, country, website)
- **Vehicle Model** - Base model (dimensions, seating, body style)
- **Vehicle Variant** - Specific trim with full specs (battery, range, charging, performance)
- **Market Availability** - Region-specific pricing and options

This structure handles:
- ✅ Multiple trims/versions per model
- ✅ Market-specific variants
- ✅ Changes over time (model years)
- ✅ Missing/incomplete data gracefully

## 🚀 Features

- **Comprehensive Specs**: Battery, range, charging, performance, dimensions
- **Real-World Data**: Actual consumption, charging curves, not just claimed specs
- **Market Specifics**: Pricing, incentives, availability by country
- **Data Quality Tracking**: Every field marked with source and confidence level
- **Version History**: Track changes across model years
- **SQL Queryable**: Complex queries via Datasette
- **Visual Dashboards**: Interactive comparisons via Streamlit
- **API Access**: JSON API for developers
- **Open License**: CC BY-SA 4.0 - free to use, share, and build upon

## 📋 Current Status

**Progress**: 70% Complete - Ready for Deployment! 🚀  
**Vehicles**: 50 variants across 37 models from 19 manufacturers  
**Markets**: Germany (25 vehicles), USA (6), France, Poland, Italy  
**Next Milestone**: Deploy Datasette API by 2026-02-10  
**Target Public Launch**: 2026-02-20

### What's Working Now ✅

- ✅ **50 vehicle variants** with comprehensive specifications
- ✅ **Full validation pipeline** - All YAML files validated with JSON Schema
- ✅ **SQLite database** - Automated builds with relationships
- ✅ **Datasette API** - 11 canned queries + full SQL access
- ✅ **5 Datasette plugins** - Maps, charts, GraphQL, exports, search
- ✅ **CI/CD pipeline** - GitHub Actions for validation + builds
- ✅ **Comprehensive docs** - API docs, deployment guide, contributing guide

See [TODO.md](TODO.md) for detailed roadmap and [PROGRESS.md](PROGRESS.md) for recent updates.

## 🛠️ Development Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/gaia-charge/evdb.git
cd evdb

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Validate YAML Files

```bash
python scripts/validate.py --directory data/
```

### Build SQLite Database

```bash
python scripts/build-sqlite.py --input-dir data/ --output evdb.db
```

### Run Datasette

```bash
datasette evdb.db --metadata metadata.json
# Open http://localhost:8001
```

### Run Streamlit Dashboard

```bash
cd streamlit
streamlit run app.py
# Open http://localhost:8501
```

## 📖 Documentation

- [**CONTRIBUTING.md**](CONTRIBUTING.md) - **Complete guide** to adding vehicles and data ✅
- [**API_DOCS.md**](API_DOCS.md) - **Comprehensive API** documentation with examples ✅
- [**DEPLOYMENT.md**](DEPLOYMENT.md) - **Deployment guide** for Vercel/Fly.io ✅
- [**TODO.md**](TODO.md) - **Roadmap** with 10 implementation phases
- [**PROGRESS.md**](PROGRESS.md) - **Recent updates** and session logs
- [**SCHEMA_DESIGN.md**](SCHEMA_DESIGN.md) - **Technical details** of schema design

## 🤝 Contributing

**We need your help!** Contributions welcome:

- 🚗 **Vehicle specifications** - Battery, range, charging, performance
- 📊 **Real-world data** - Actual consumption and range tests
- 💰 **Market pricing** - Regional pricing and options
- 🌍 **New markets** - UK, Norway, China, Japan, Australia
- 🔧 **Code improvements** - Scripts, validation, features
- 📖 **Translations** - Help internationalize the database

### Quick Start Guide

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the complete guide including:

- 📝 How to add a vehicle (step-by-step)
- ✅ Validation and testing workflow
- 📋 Data quality standards
- 🔀 Pull request process
- 🎯 Priority vehicles we need

**TL;DR:**
1. Fork → Clone → Create branch
2. Copy template from `templates/`
3. Fill in specs (see [CONTRIBUTING.md](CONTRIBUTING.md))
4. Validate: `python scripts/validate.py --file your-file.yaml`
5. Submit pull request

All contributions must include source attribution. Data is licensed under CC BY-SA 4.0.

## 📂 Repository Structure

```
evdb/
├── data/                       # YAML source files
│   ├── manufacturers/
│   ├── vehicle-models/
│   ├── vehicle-variants/
│   ├── market-availability/
│   └── reference/
│       ├── connectors.yaml
│       └── platforms.yaml
├── schemas/                    # JSON Schema validation
│   ├── manufacturer.schema.json
│   ├── vehicle-model.schema.json
│   ├── vehicle-variant.schema.json
│   └── market-availability.schema.json
├── scripts/                    # Build and validation tools
│   ├── validate.py
│   ├── build-sqlite.py
│   └── import-yaml.py
├── templates/                  # YAML templates for contributors
├── streamlit/                  # Streamlit dashboard
│   └── app.py
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD pipelines
├── metadata.json              # Datasette configuration
└── requirements.txt           # Python dependencies
```

## 🔌 API Examples

### Get All Manufacturers

```bash
curl https://evdb.gaiacharge.com/manufacturers.json
```

### Find Vehicles by Range

```bash
curl "https://evdb.gaiacharge.com/vehicle-variants.json?range_real_world_combined_km__gte=500"
```

### SQL Query

```bash
curl "https://evdb.gaiacharge.com/evdb.json?sql=\
SELECT m.name as manufacturer, vm.name as model, vv.variant_name, \
       vv.battery_usable_capacity_kwh, vv.range_real_world_combined_km \
FROM vehicle_variants vv \
JOIN vehicle_models vm ON vv.vehicle_model_id = vm.id \
JOIN manufacturers m ON vm.manufacturer_id = m.id \
WHERE vv.model_year = 2024 \
ORDER BY vv.range_real_world_combined_km DESC \
LIMIT 10"
```

## 📊 Example Queries

### Compare Charging Speeds

```sql
SELECT 
  m.name as manufacturer,
  vm.name as model,
  vv.variant_name,
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

### Find Budget EVs

```sql
SELECT 
  m.name, vm.name, vv.variant_name,
  ma.pricing_base_price, ma.pricing_currency,
  vv.range_real_world_combined_km
FROM vehicle_variants vv
JOIN vehicle_models vm ON vv.vehicle_model_id = vm.id
JOIN manufacturers m ON vm.manufacturer_id = m.id
JOIN market_availability ma ON vv.id = ma.variant_id
WHERE ma.market = 'germany'
  AND ma.pricing_base_price < 40000
  AND vv.range_real_world_combined_km > 300
ORDER BY vv.range_real_world_combined_km DESC;
```

## 📜 License

- **Data**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Code**: MIT License

## 🔗 Links

- **Website**: https://evdb.gaiacharge.com/ *(coming soon)*
- **API**: https://evdb.gaiacharge.com/evdb.json *(coming soon)*
- **Dashboards**: https://dashboard.evdb.gaiacharge.com/ *(coming soon)*
- **GitHub**: https://github.com/gaia-charge/evdb

## 💡 Inspiration

Inspired by comprehensive EV databases like ev-database.org, but with a focus on:
- Open data (not proprietary)
- Git-based workflow (trackable changes)
- API-first design (easy integration)
- Community contributions (crowdsourced accuracy)

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/gaia-charge/evdb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gaia-charge/evdb/discussions)
- **Email**: evdb@gaiacharge.com *(coming soon)*

---

**Built with ❤️ for the EV community**

*Data is power. Open data is power for everyone.*

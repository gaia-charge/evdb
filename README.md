# EVDB - Open Electric Vehicle Database

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Validate YAML](https://github.com/gaia-charge/evdb/actions/workflows/validate.yml/badge.svg)](https://github.com/gaia-charge/evdb/actions/workflows/validate.yml)
[![Build Database](https://github.com/gaia-charge/evdb/actions/workflows/build-deploy.yml/badge.svg)](https://github.com/gaia-charge/evdb/actions/workflows/build-deploy.yml)

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

**Vehicles**: 530+ variants across 180 models from 45 manufacturers
**Markets**: Germany, Spain, Poland, France, Netherlands, Italy (plus initial US/UK data)

Live counts: [`/v1/stats.json`](https://gaia-charge.github.io/evdb/v1/stats.json)
or the notes of the [latest release](https://github.com/gaia-charge/evdb/releases/latest).

### What's Working ✅

- ✅ **Full validation pipeline** - All YAML files validated with JSON Schema in CI
- ✅ **SQLite database** - Automated builds via GitHub Actions
- ✅ **GitHub Releases** - Pre-built database downloadable from every push
- ✅ **Static JSON API** - Generated per push, served via GitHub Pages
- ✅ **Datasette support** - Full SQL access with canned queries
- ✅ **Streamlit dashboard** - 6 pages (Home, Browse, Compare, Analytics, Data Explorer, Documentation)
- ✅ **Docs** - API docs, contributing guide, FAQ

### 📥 Download the Database

The latest pre-built SQLite database is available from [GitHub Releases](https://github.com/gaia-charge/evdb/releases/latest):

```bash
# Download latest database
wget https://github.com/gaia-charge/evdb/releases/latest/download/evdb.db

# Or with curl
curl -L -o evdb.db https://github.com/gaia-charge/evdb/releases/latest/download/evdb.db
```

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
streamlit run streamlit_app.py
# Open http://localhost:8501
```

**Features:**
- 🏠 **Home** - Database statistics and quick search
- 🔍 **Browse Vehicles** - Advanced filtering with 7 filters and 8 sort modes
- ⚖️ **Compare** - Side-by-side comparison of 2-4 vehicles with visualizations
- 📊 **Analytics** - Interactive charts for range, charging, price, and market analysis
- 💾 **Data Explorer** - SQL query interface with 8 example queries
- 📚 **Documentation** - Embedded API docs, contributing guide, and FAQ

## 📖 Documentation

- [**CONTRIBUTING.md**](CONTRIBUTING.md) - **Complete guide** to adding vehicles and data
- [**API_DOCS.md**](API_DOCS.md) - **Comprehensive API** documentation with examples
- [**FAQ.md**](FAQ.md) - **Frequently asked questions**

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
│   ├── validate.py             # JSON Schema validation
│   ├── build-sqlite.py         # YAML -> SQLite build
│   ├── generate-api.py         # SQLite -> static JSON API
│   └── analyze_missing_data.py # Data completeness report
├── templates/                  # YAML templates for contributors
├── streamlit_app.py            # Streamlit dashboard (6 pages)
├── .github/workflows/          # CI/CD pipelines
├── metadata.json               # Datasette configuration
└── requirements.txt            # Python dependencies
```

## 🔌 API Examples

Static JSON API served from GitHub Pages — see [API_DOCS.md](API_DOCS.md) for all endpoints.

```bash
# All manufacturers
curl https://gaia-charge.github.io/evdb/v1/manufacturers.json

# All vehicles (summary)
curl https://gaia-charge.github.io/evdb/v1/vehicles.json

# One vehicle, full specs + market pricing
curl https://gaia-charge.github.io/evdb/v1/vehicles/tesla-model-3-long-range-awd-2024.json

# Pre-built queries
curl https://gaia-charge.github.io/evdb/v1/queries/long-range.json

# Database statistics
curl https://gaia-charge.github.io/evdb/v1/stats.json
```

## 📊 Example Queries

### Compare Charging Speeds

```sql
SELECT
  m.name as manufacturer,
  vm.name as model,
  vv.variant_name,
  vv.dc_charge_power_kw as max_dc,
  vv.dc_charge_time_10_80_min as charge_time_min
FROM vehicle_variants vv
JOIN vehicle_models vm ON vv.model_id = vm.id
JOIN manufacturers m ON vm.manufacturer_id = m.id
WHERE vv.dc_charge_power_kw >= 150
ORDER BY vv.dc_charge_time_10_80_min ASC
LIMIT 20;
```

### Find Budget EVs

```sql
SELECT
  m.name, vm.name, vv.variant_name,
  ma.price_base, ma.currency,
  vv.range_wltp_km
FROM vehicle_variants vv
JOIN vehicle_models vm ON vv.model_id = vm.id
JOIN manufacturers m ON vm.manufacturer_id = m.id
JOIN market_availability ma ON vv.id = ma.variant_id
WHERE ma.market_code = 'DE'
  AND ma.price_base < 40000
  AND vv.range_wltp_km > 400
ORDER BY vv.range_wltp_km DESC;
```

## 📜 License

- **Data**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Code**: MIT License

## 🔗 Links

- **API**: https://gaia-charge.github.io/evdb/v1/index.json
- **Database download**: https://github.com/gaia-charge/evdb/releases/latest
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

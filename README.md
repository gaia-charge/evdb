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

**Phase**: Foundation & Tooling (10% complete)  
**Next Milestone**: Complete JSON schemas by 2026-02-08  
**Target Launch**: 2026-03-15

See [TODO.md](TODO.md) for detailed implementation plan.

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

- [**TODO.md**](TODO.md) - Complete implementation plan with 10 phases
- [**SCHEMA_DESIGN.md**](SCHEMA_DESIGN.md) - Detailed schema design rationale
- [**CONTRIBUTING.md**](CONTRIBUTING.md) - How to contribute data *(coming soon)*
- [**DATA_ENTRY_GUIDE.md**](docs/DATA_ENTRY_GUIDE.md) - Field-by-field guide *(coming soon)*
- [**API_DOCUMENTATION.md**](docs/API_DOCUMENTATION.md) - API usage examples *(coming soon)*

## 🤝 Contributing

Contributions are welcome! We need:

- ✅ Vehicle specifications
- ✅ Real-world range data
- ✅ Market pricing information
- ✅ Charging curve measurements
- ✅ Photos and media
- ✅ Translations

### Quick Start

1. Fork the repository
2. Copy a template from `templates/`
3. Fill in the data (see DATA_ENTRY_GUIDE.md)
4. Validate: `python scripts/validate.py --file your-file.yaml`
5. Submit a pull request

All data must include source attribution and follow our quality standards.

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

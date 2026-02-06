# EVDB - Open Electric Vehicle Database

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

A comprehensive, open-source database of electric vehicles with detailed specifications, market availability, and multi-language support.

## 🚀 Features

- **Comprehensive Data** - Battery specs, range, performance, charging capabilities
- **Country-Level Availability** - Market-specific data with ISO 3166-1 country codes
- **Standardized Enums** - Battery chemistry, charging standards, body types
- **Multi-Image Support** - Multiple photos with metadata and licensing
- **Internationalization** - Multi-language support (EN, DE, PL, FR, ES)
- **JSON API** - RESTful API for developers
- **Open License** - CC BY-SA 4.0

## 📋 Schema

Vehicle data follows a comprehensive JSON schema with:

- Basic info (manufacturer, body type, segment)
- Battery specifications (capacity, chemistry, warranty)
- Range estimates (WLTP, EPA, real-world)
- Performance data (power, torque, acceleration)
- Charging capabilities (AC/DC ports, speed classes)
- Dimensions and weight
- Pricing by market
- Production information
- Multiple images with metadata

See [`api/v1/schema/vehicle.json`](api/v1/schema/vehicle.json) for full schema.

## 🗂️ Project Structure

```
.
├── api/
│   └── v1/
│       └── schema/
│           ├── vehicle.json      # Vehicle data schema
│           ├── enums.json        # Standardized enumerations
│           └── manufacturer.json # Manufacturer schema
├── docs/
│   ├── ENHANCEMENTS.md          # Enhancement plan
│   ├── INTERNATIONALIZATION.md  # i18n guide
│   └── IMPLEMENTATION_ROADMAP.md # Development phases
├── scripts/
│   └── validate.js              # Data validation tool
├── content/                      # Hugo content (vehicles, manufacturers)
├── layouts/                      # Hugo templates
├── static/                       # Static assets (images, etc.)
└── config.toml                  # Hugo configuration

```

## 🛠️ Development

### Prerequisites

- [Hugo](https://gohugo.io/) (extended version)
- Node.js 18+ (for validation scripts)

### Setup

```bash
# Clone repository
git clone git@github.com:gaia-charge/evdb.git
cd evdb

# Install dependencies for validation
npm install js-yaml

# Run Hugo development server
hugo server
```

### Add a Vehicle

1. Create markdown file in `content/vehicles/`
2. Follow schema in `api/v1/schema/vehicle.json`
3. Use standardized enums from `api/v1/schema/enums.json`
4. Validate before committing:
   ```bash
   ./scripts/validate.js
   ```

## 📖 Documentation

- [**TODO.md**](TODO.md) - Current implementation tasks
- [**ENHANCEMENTS.md**](docs/ENHANCEMENTS.md) - Detailed enhancement plan
- [**INTERNATIONALIZATION.md**](docs/INTERNATIONALIZATION.md) - Multi-language guide
- [**IMPLEMENTATION_ROADMAP.md**](docs/IMPLEMENTATION_ROADMAP.md) - Development phases

## 🤝 Contributing

Contributions are welcome! Please read our [Code of Conduct](CODE_OF_CONDUCT.md) first.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Add/update vehicle data following the schema
4. Validate your changes (`./scripts/validate.js`)
5. Submit a pull request

## 📊 Data Sources

We welcome data from:
- Official manufacturer specifications
- WLTP/EPA test results
- User-submitted real-world data
- Industry databases

All submissions must include source attribution.

## 📜 License

- **Data**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Code**: MIT License

## 🔗 Links

- **Website**: https://evdb.gaiacharge.com/
- **API Docs**: https://evdb.gaiacharge.com/api/
- **GitHub**: https://github.com/gaia-charge/evdb

## 📞 Contact

For questions or suggestions, please [open an issue](https://github.com/gaia-charge/evdb/issues).

---

Built with ❤️ for the EV community

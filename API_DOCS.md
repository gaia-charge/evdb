# EVDB API Documentation

**Base URL:** `https://gaia-charge.github.io/evdb/v1`

**Version:** 1.0  
**License:** CC BY-SA 4.0

---

## Overview

EVDB provides a static JSON API for querying electric vehicle data. The API is automatically generated from the database on every push and deployed to GitHub Pages. All responses are JSON.

### Key Features

- 🚗 **534+ vehicle variants** from 45+ manufacturers
- 🔋 Battery, charging, range, and performance specifications
- 💰 Market pricing and availability (8 countries)
- 📦 Dimensions, cargo, towing, and weight data
- 🔍 Pre-built query endpoints for common use cases
- 📥 Full SQLite database download available

### CORS

All endpoints support cross-origin requests (CORS). You can call them directly from browser JavaScript.

---

## Quick Start

```bash
# Get all manufacturers
curl https://gaia-charge.github.io/evdb/v1/manufacturers.json

# Get all vehicles (summary)
curl https://gaia-charge.github.io/evdb/v1/vehicles.json

# Get a specific vehicle with full specs
curl https://gaia-charge.github.io/evdb/v1/vehicles/tesla-model-3-long-range-awd-2024.json

# Get long-range EVs
curl https://gaia-charge.github.io/evdb/v1/queries/long-range.json
```

---

## Endpoints

### Index

**`GET /v1/index.json`** — API metadata, version, and list of all endpoints.

### Statistics

**`GET /v1/stats.json`** — Database statistics (counts of manufacturers, models, variants, markets).

### Manufacturers

**`GET /v1/manufacturers.json`** — All manufacturers with country, website, parent company.

**`GET /v1/manufacturers/{id}.json`** — Single manufacturer with all their vehicle models.

### Vehicles

**`GET /v1/vehicles.json`** — All vehicles (summary: brand, model, variant, year, key specs).

**`GET /v1/vehicles/{id}.json`** — Full vehicle specifications including:
- Battery (capacity, chemistry, voltage)
- Range (WLTP, real-world)
- Performance (power, torque, acceleration, top speed)
- Charging (DC power, AC power, charge times)
- Dimensions (length, width, height, wheelbase, ground clearance)
- Cargo (trunk capacity, frunk, max cargo)
- Weight (curb, gross, payload, towing capacity)
- Market availability and pricing per country

### Markets

**`GET /v1/markets.json`** — Summary of all markets with vehicle counts and price ranges.

**`GET /v1/markets/{code}/vehicles.json`** — All vehicles available in a specific market with local pricing. Market codes: `de`, `es`, `fr`, `pl`, `gb`, `it`, `nl`, `us`.

### Pre-built Queries

| Endpoint | Description |
|----------|-------------|
| `/v1/queries/long-range.json` | EVs with 500km+ WLTP range |
| `/v1/queries/budget.json` | EVs under €40,000 (DE market) |
| `/v1/queries/performance.json` | EVs with 0-100 km/h under 5 seconds |
| `/v1/queries/most-efficient.json` | Top 50 most efficient EVs (kWh/100km) |
| `/v1/queries/fastest-charging.json` | Top 50 fastest charging EVs (DC kW) |
| `/v1/queries/best-value.json` | Top 50 best value EVs (lowest €/kWh) |
| `/v1/queries/largest-cargo.json` | Top 50 vehicles by trunk capacity |
| `/v1/queries/best-towing.json` | Top 50 vehicles by towing capacity |

---

## Response Format

All endpoints return a JSON object. List endpoints include:

```json
{
  "count": 534,
  "results": [
    { ... },
    { ... }
  ]
}
```

Single-resource endpoints return the object directly:

```json
{
  "id": "tesla-model-3-long-range-awd-2024",
  "brand": "Tesla",
  "model_name": "Model 3",
  "variant_name": "Long Range AWD",
  "model_year": 2024,
  "battery_usable_kwh": 75.0,
  "range_wltp_km": 629,
  "markets": [
    { "market_code": "DE", "currency": "EUR", "price_base": 49990 }
  ]
}
```

Null/unknown values are omitted from responses for cleaner JSON.

---

## Database Download

For advanced queries, download the full SQLite database:

```bash
wget https://github.com/gaia-charge/evdb/releases/latest/download/evdb.db
sqlite3 evdb.db "SELECT * FROM vehicle_variants WHERE range_wltp_km > 500;"
```

Or use with Datasette locally:

```bash
pip install datasette
datasette evdb.db
```

---

## JavaScript Example

```javascript
// Fetch all budget EVs
const response = await fetch('https://gaia-charge.github.io/evdb/v1/queries/budget.json');
const data = await response.json();

console.log(`Found ${data.count} budget EVs:`);
data.results.forEach(ev => {
  console.log(`${ev.brand} ${ev.model} ${ev.variant_name} - €${ev.price_eur}`);
});
```

---

## Update Frequency

The API is regenerated automatically on every push to the `main` branch (typically multiple times per day as new vehicle data is added).

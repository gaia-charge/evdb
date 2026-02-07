# EVDB API Documentation

**Base URL:** `https://evdb.datasette.io` (or your deployment URL)

**Version:** 1.0  
**Last Updated:** 2026-02-07

---

## Overview

EVDB provides a comprehensive REST API for querying electric vehicle data. All endpoints return JSON by default, with optional CSV and other formats available.

### Key Features

- 📊 **50+ vehicle variants** from 19 manufacturers
- 🔋 Battery, charging, and range specifications
- 💰 Market pricing and availability (5 countries)
- 🔌 Charging connector reference data
- 🏗️ EV platform information
- 🔍 Advanced SQL querying via Datasette

### Data License

All data is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You are free to share and adapt the data with attribution.

---

## Quick Start

### Example: Get All Manufacturers

```bash
curl "https://evdb.datasette.io/evdb/manufacturers.json"
```

### Example: Find Long-Range EVs (500km+)

```bash
curl "https://evdb.datasette.io/evdb/long_range_evs.json"
```

### Example: Compare Two Vehicles

```bash
curl "https://evdb.datasette.io/evdb/vehicles_comparison.json?ids=bmw-i4-edrive40-2024,tesla-model-3-long-range-awd-2024"
```

---

## API Endpoints

### Base Tables

All tables support JSON, CSV, and other export formats by changing the extension (e.g., `.csv`, `.json`).

#### 1. Manufacturers

**Endpoint:** `/evdb/manufacturers.json`

Returns all EV manufacturers with country, parent company, and description.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/manufacturers.json"
```

**Example Response:**
```json
{
  "rows": [
    {
      "id": "tesla",
      "name": "Tesla",
      "country": "US",
      "parent_company": null,
      "founded": 2003,
      "website": "https://www.tesla.com",
      "description": "American electric vehicle and clean energy company"
    }
  ]
}
```

**Filtering by Country:**
```bash
curl "https://evdb.datasette.io/evdb/manufacturers.json?country=DE"
```

---

#### 2. Vehicle Models

**Endpoint:** `/evdb/vehicle_models.json`

Returns base vehicle models with dimensions, body style, and platform information.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_models.json?manufacturer_id=bmw"
```

**Example Response:**
```json
{
  "rows": [
    {
      "id": "bmw-i4",
      "manufacturer_id": "bmw",
      "name": "i4",
      "body_style": "sedan",
      "segment": "D",
      "platform": "CLAR",
      "production_status": "active",
      "seating_capacity_min": 5,
      "seating_capacity_max": 5
    }
  ]
}
```

**Filtering by Body Style:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_models.json?body_style=SUV"
```

---

#### 3. Vehicle Variants

**Endpoint:** `/evdb/vehicle_variants.json`

Returns detailed specifications for each trim/variant with battery, range, charging, and performance data.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?model_id=tesla-model-3"
```

**Key Fields:**
- `battery_usable_kwh` - Usable battery capacity
- `range_wltp_km` - WLTP certified range
- `range_real_world_km` - Real-world range estimate
- `charging_dc_max_kw` - Maximum DC fast charging power
- `motors_total_power_kw` - Total motor power
- `acceleration_0_100_seconds` - 0-100 km/h time

**Filtering by Range:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?range_wltp_km__gt=500"
```

**Filtering by Charging Speed:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?charging_dc_max_kw__gt=200"
```

---

#### 4. Market Availability

**Endpoint:** `/evdb/market_availability.json`

Returns pricing and availability by country/market.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/market_availability.json?market_code=DE"
```

**Example Response:**
```json
{
  "rows": [
    {
      "variant_id": "bmw-i4-edrive40-2024",
      "market_code": "DE",
      "currency": "EUR",
      "base_price": 59500,
      "availability_status": "available",
      "lead_time_weeks": 4
    }
  ]
}
```

---

#### 5. Reference Data

##### Charging Connectors

**Endpoint:** `/evdb/connectors.json`

Returns standard charging connector types (CCS, CHAdeMO, Tesla, etc.).

```bash
curl "https://evdb.datasette.io/evdb/connectors.json"
```

##### EV Platforms

**Endpoint:** `/evdb/platforms.json`

Returns EV platforms (skateboard chassis) used by manufacturers.

```bash
curl "https://evdb.datasette.io/evdb/platforms.json"
```

---

### Database Views

Pre-joined views for easier querying.

#### Complete Vehicle Data

**Endpoint:** `/evdb/view_vehicles_full.json`

All vehicle information with manufacturer and model details joined.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/view_vehicles_full.json?_size=10"
```

**Fields Include:**
- Manufacturer name and country
- Model name and body style
- Variant specifications (battery, range, charging)
- Price data (when available)
- Production status

**Example: Filter German Manufacturers**
```bash
curl "https://evdb.datasette.io/evdb/view_vehicles_full.json?manufacturer_country=DE"
```

---

#### Latest Model Year Vehicles

**Endpoint:** `/evdb/view_vehicles_latest.json`

Only the most recent model year for each variant.

```bash
curl "https://evdb.datasette.io/evdb/view_vehicles_latest.json"
```

---

## Canned Queries

Pre-built queries for common use cases. All queries return JSON by default.

### 1. Find Vehicles by Range

**Endpoint:** `/evdb/vehicles_by_range.json`

Search for vehicles with minimum WLTP range.

**Parameters:**
- `min_range` (number, default: 400) - Minimum WLTP range in km

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicles_by_range.json?min_range=600"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Mercedes-Benz",
      "model_name": "EQS",
      "variant_name": "EQS 450+",
      "battery_usable_kwh": 107.8,
      "range_wltp_km": 782,
      "range_real_world_km": 685
    }
  ]
}
```

---

### 2. Fast Charging Vehicles

**Endpoint:** `/evdb/vehicles_by_charging_speed.json`

Vehicles with minimum DC fast charging power.

**Parameters:**
- `min_power` (number, default: 150) - Minimum DC power in kW

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicles_by_charging_speed.json?min_power=250"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Hyundai",
      "model_name": "Ioniq 5",
      "variant_name": "Ioniq 5 Long Range AWD",
      "dc_charge_power_kw": 350,
      "dc_charge_time_10_80_min": 18,
      "range_wltp_km": 507
    }
  ]
}
```

---

### 3. Find Vehicles by Price (EUR)

**Endpoint:** `/evdb/vehicles_by_price.json`

Search vehicles within price range (base EUR price).

**Parameters:**
- `min_price` (number, default: 30000) - Minimum price in EUR
- `max_price` (number, default: 60000) - Maximum price in EUR

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicles_by_price.json?min_price=40000&max_price=50000"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Tesla",
      "model_name": "Model 3",
      "variant_name": "RWD",
      "price_base_eur": 40990,
      "range_wltp_km": 513,
      "battery_usable_kwh": 60
    }
  ]
}
```

---

### 4. Most Efficient Vehicles

**Endpoint:** `/evdb/vehicles_by_efficiency.json`

Vehicles sorted by real-world energy efficiency (lowest kWh/100km).

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicles_by_efficiency.json?_size=10"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Tesla",
      "model_name": "Model 3",
      "variant_name": "RWD",
      "consumption_real_world_kwh_100km": 15.0,
      "range_wltp_km": 513,
      "range_real_world_km": 450
    }
  ]
}
```

---

### 5. Compare Specific Vehicles

**Endpoint:** `/evdb/vehicles_comparison.json`

Side-by-side comparison of selected vehicles.

**Parameters:**
- `ids` (text, comma-separated) - Variant IDs to compare

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/vehicles_comparison.json?ids=bmw-i4-edrive40-2024,tesla-model-3-long-range-awd-2024,mercedes-eqs-450plus-2024"
```

**Use Case:** Build comparison tables for your application.

---

### 6. Market Overview by Country

**Endpoint:** `/evdb/market_overview.json`

All available vehicles from manufacturers based in a specific country.

**Parameters:**
- `country` (text, default: "DE") - Country code (US/DE/KR/CN/etc.)

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/market_overview.json?country=KR"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Hyundai",
      "manufacturer_country": "KR",
      "model_name": "Ioniq 5",
      "variant_name": "Ioniq 5 Long Range AWD",
      "range_wltp_km": 507,
      "battery_usable_kwh": 77.4,
      "dc_charge_power_kw": 350
    }
  ]
}
```

---

### 7. Latest Model Years

**Endpoint:** `/evdb/latest_additions.json`

Most recent model year vehicles (top 20).

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/latest_additions.json"
```

---

### 8. Long-Range EVs (500km+)

**Endpoint:** `/evdb/long_range_evs.json`

Vehicles with WLTP range over 500km.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/long_range_evs.json"
```

---

### 9. Budget EVs under €40k

**Endpoint:** `/evdb/budget_evs.json`

Affordable electric vehicles with base EUR pricing.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/budget_evs.json"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Nissan",
      "model_name": "Leaf",
      "variant_name": "e+ 62kWh",
      "price_base_eur": 38900,
      "range_wltp_km": 385,
      "battery_usable_kwh": 59
    }
  ]
}
```

---

### 10. Performance EVs (Sub-5s 0-100)

**Endpoint:** `/evdb/performance_evs.json`

Fast-accelerating electric vehicles (0-100 km/h under 5 seconds).

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/performance_evs.json"
```

**Example Response:**
```json
{
  "rows": [
    {
      "manufacturer_name": "Porsche",
      "model_name": "Taycan",
      "variant_name": "Turbo S",
      "acceleration_0_100_sec": 2.8,
      "total_power_kw": 560,
      "drive_type": "AWD",
      "range_wltp_km": 440
    }
  ]
}
```

---

### 11. All Vehicles Overview

**Endpoint:** `/evdb/all_vehicles.json`

Complete list of all vehicles in the database.

**Example Request:**
```bash
curl "https://evdb.datasette.io/evdb/all_vehicles.json"
```

---

## Advanced Querying

Datasette supports powerful SQL queries via URL parameters.

### Query Operators

- `__exact` - Exact match (default)
- `__gt` - Greater than
- `__gte` - Greater than or equal
- `__lt` - Less than
- `__lte` - Less than or equal
- `__contains` - Contains text
- `__startswith` - Starts with
- `__endswith` - Ends with
- `__in` - In list (comma-separated)

### Examples

#### Find vehicles with >100kWh battery
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?battery_usable_kwh__gt=100"
```

#### Find SUVs from German manufacturers
```bash
curl "https://evdb.datasette.io/evdb/view_vehicles_full.json?body_style=SUV&manufacturer_country=DE"
```

#### Find vehicles with "Long Range" in name
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?variant_name__contains=Long+Range"
```

---

## Pagination

Results are paginated by default. Control pagination with:

- `_size` - Results per page (default: 100, max: 1000)
- `_next` - Next page token (returned in response)

**Example:**
```bash
curl "https://evdb.datasette.io/evdb/vehicle_variants.json?_size=10"
```

**Response includes pagination:**
```json
{
  "rows": [...],
  "next": "100",
  "next_url": "...?_next=100"
}
```

---

## Response Formats

Change the URL extension to get different formats:

- `.json` - JSON (default)
- `.csv` - CSV export
- `.jsono` - JSON objects (newline-delimited)
- `.html` - Web interface

**Example CSV Export:**
```bash
curl "https://evdb.datasette.io/evdb/long_range_evs.csv" > long_range_evs.csv
```

---

## CORS

CORS is enabled by default. You can query the API from browser-based applications.

**JavaScript Example:**
```javascript
fetch('https://evdb.datasette.io/evdb/long_range_evs.json')
  .then(response => response.json())
  .then(data => console.log(data.rows));
```

---

## Python Client Example

```python
import requests

# Get all long-range EVs
response = requests.get('https://evdb.datasette.io/evdb/long_range_evs.json')
vehicles = response.json()['rows']

for vehicle in vehicles:
    print(f"{vehicle['manufacturer_name']} {vehicle['model_name']}: {vehicle['range_wltp_km']}km")
```

**Using sqlite-utils:**
```python
from sqlite_utils import Database

# Connect to the database
db = Database('evdb.db')

# Query with Python
for row in db['vehicle_variants'].rows_where('range_wltp_km > 600'):
    print(row)
```

---

## JavaScript/Node.js Example

```javascript
const axios = require('axios');

async function getLongRangeEVs() {
  const response = await axios.get('https://evdb.datasette.io/evdb/long_range_evs.json');
  const vehicles = response.data.rows;
  
  vehicles.forEach(v => {
    console.log(`${v.manufacturer_name} ${v.model_name}: ${v.range_wltp_km}km`);
  });
}

getLongRangeEVs();
```

---

## Rate Limits

Currently no rate limits are enforced. Please be respectful:

- Cache responses when possible
- Use pagination for large datasets
- Consider downloading the full database for heavy analysis

**Download Full Database:**
```bash
curl -O "https://evdb.datasette.io/evdb.db"
```

---

## GraphQL API (Experimental)

GraphQL endpoint available via the `datasette-graphql` plugin.

**Endpoint:** `/graphql`

**Example Query:**
```graphql
{
  vehicle_variants(filter: {range_wltp_km_gt: 500}) {
    nodes {
      variant_name
      range_wltp_km
      battery_usable_kwh
    }
  }
}
```

**GraphQL Playground:** `https://evdb.datasette.io/graphql`

---

## Full-Text Search

Full-text search is available on:
- Manufacturer names and descriptions
- Model names and descriptions
- Variant names

**Coming Soon:** Full-text search UI via `datasette-configure-fts` plugin.

---

## Plugins & Extensions

EVDB uses the following Datasette plugins:

- **datasette-cluster-map** - Map visualizations
- **datasette-vega** - Charts and visualizations
- **datasette-graphql** - GraphQL API
- **datasette-export-notebook** - Export to Jupyter notebooks
- **datasette-configure-fts** - Full-text search configuration

Explore interactive features at the web interface!

---

## Data Quality

All data includes quality indicators:

- `data_quality` field: `verified`, `estimated`, `preliminary`
- `data_sources` array: Original sources for each specification

**Example:**
```json
{
  "data_quality": "verified",
  "data_sources": [
    "https://www.tesla.com/model3/specs",
    "WLTP certification 2024-01"
  ]
}
```

---

## Contributing Data

Want to add vehicles or update specifications?

1. Fork the repository: https://github.com/yourusername/evdb
2. Add/edit YAML files in `data/` directory
3. Run validation: `python scripts/validate.py`
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions.

---

## Support & Community

- **Issues:** https://github.com/yourusername/evdb/issues
- **Discussions:** https://github.com/yourusername/evdb/discussions
- **Discord:** (coming soon)

---

## Changelog

### 2026-02-07 - Initial Release (v1.0)

- 50 vehicle variants from 19 manufacturers
- 5 markets covered (Germany, USA, France, Poland, Italy)
- 11 canned queries
- GraphQL API
- Full documentation

---

## License

Data: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)  
API: MIT License

---

**Questions?** Open an issue on GitHub or email: evdb@example.com

# EVDB - Frequently Asked Questions

## General

### What is EVDB?

EVDB is an open-source database of battery-electric vehicles (BEVs) with
detailed specifications and market pricing, maintained as human-readable YAML
files in git and published as a SQLite database and a static JSON API.

### What data does it contain?

Four entity types:

- **Manufacturers** - company info (country, founding, website)
- **Vehicle models** - base model data (body style, segment, dimensions)
- **Vehicle variants** - full specs per trim (battery, range, charging, performance)
- **Market availability** - pricing, incentives, and availability per country

Current counts are always in the generated API's stats endpoint and in the
release notes of the [latest release](https://github.com/gaia-charge/evdb/releases/latest).

### Which vehicles are in scope?

Battery-electric vehicles only — no PHEVs, hybrids, or range extenders.
Coverage focuses on the European market (DE, ES, PL, FR, NL, IT and growing).

### What license does EVDB use?

- **Data**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- **Code**: MIT

Free to use commercially, modify, and redistribute — with attribution and
share-alike for the data.

## Using the data

### How do I get the database?

```bash
# Pre-built SQLite database from the latest release
curl -L -o evdb.db https://github.com/gaia-charge/evdb/releases/latest/download/evdb.db
```

Or build from source:

```bash
python scripts/build-sqlite.py --clean
```

### Is there an API?

Yes — a static JSON API generated from the database, served via GitHub Pages.
See [API_DOCS.md](API_DOCS.md) for endpoints and examples.

### How do I browse the data interactively?

```bash
# Datasette web UI + SQL
datasette evdb.db --metadata metadata.json

# Streamlit dashboard
streamlit run streamlit_app.py
```

## Data quality

### Where does the data come from?

Every record carries `metadata.sources` — URLs to manufacturer spec/price
pages, official price lists, or reputable automotive press. Records without
sources cannot claim `data_quality: verified`.

### How accurate is the pricing?

Prices are list prices at the time recorded in `metadata.price_checked_at`
(or `created_at`), including VAT for European markets. Prices change —
always check the cited source before making decisions.

### I found an error. How do I report it?

[Open an issue](https://github.com/gaia-charge/evdb/issues/new) with the
affected vehicle, the wrong field, the correct value, and a source link.
Or better: submit a pull request with the fix.

## Contributing

### How do I add a vehicle?

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full walkthrough. Short
version: copy a template from `templates/`, fill it in with sourced data,
run `python scripts/validate.py --directory data/`, open a pull request.

### What makes a good contribution?

- Sourced from official manufacturer pages or reputable press (deep links)
- Validated locally before the PR
- One vehicle or one coherent batch per PR
- No data copied from ev-database.org (incompatible licensing)

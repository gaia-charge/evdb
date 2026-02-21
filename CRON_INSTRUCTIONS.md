# EVDB Cron Instructions

**Updated:** 2026-02-21
**Status:** 533 variants, 1,182 market entries

---

## 🎯 CURRENT PRIORITY: Spanish & Polish Market Expansion

**Focus:** Add missing market-availability files for ES and PL markets.

- **ES missing:** ~201 variants (have DE but not ES)
- **PL missing:** ~371 variants (have DE but not PL)

### How to find what's missing

```bash
# Variants with DE market but no ES market
comm -23 \
  <(ls data/market-availability/*-de.yaml | sed 's/-de\.yaml//' | sed 's|.*/||' | sort) \
  <(ls data/market-availability/*-es.yaml | sed 's/-es\.yaml//' | sed 's|.*/||' | sort)

# Same for PL
comm -23 \
  <(ls data/market-availability/*-de.yaml | sed 's/-de\.yaml//' | sed 's|.*/||' | sort) \
  <(ls data/market-availability/*-pl.yaml | sed 's/-pl\.yaml//' | sed 's|.*/||' | sort)
```

### Per session workflow

1. Pick 3-5 variants missing ES or PL market files
2. Check manufacturer's local website (.es / .pl) for pricing and availability
3. Create market-availability YAML files with base_price, currency, on_sale status
4. Validate, commit to daily branch `data-fill/YYYY-MM-DD`, push
5. **Alternate between ES and PL** each session

### Market-availability file format

```yaml
variant_id: "example-variant-id-2025"
country: "ES"  # or "PL"
base_price: 45990  # EUR for ES, PLN for PL
currency: "EUR"  # or "PLN"
on_sale: true
available_trims: []  # optional
incentives: []  # optional
```

Check existing files in `data/market-availability/` for exact format reference.

### Sources

- **Spain:** manufacturer.es websites, coches.net (pricing verification)
- **Poland:** manufacturer.pl websites, electromobilnosc.pl
- **Skip** variants where manufacturer doesn't sell in that market (e.g., some Chinese brands not yet in ES/PL)
- **Do NOT use ev-database.org**

### Market-specific notes

**Spain (ES):**
- Prices in EUR, IVA (21%) included
- MOVES III subsidies if still active
- Some brands (NIO, Genesis) may not sell in Spain — skip those

**Poland (PL):**
- Prices in PLN
- "Mój elektryk" subsidy program
- Check manufacturer.pl websites

---

## 📊 Session Reporting Format

```
**Market expansion:** Added X market entries (Y for ES, Z for PL)
**Variants covered:** [list variant names]
**Skipped:** [variants not sold in that market]
**Database:** X variants, Y market entries
**Validation:** ✅ All files pass
```

---

## 🚫 Reminders

- **Daily branch workflow:** Create/use `data-fill/YYYY-MM-DD` branch, not main
- **BEVs only** — No PHEVs, hybrids, or range extenders
- **European market only**
- **Validate before committing** — Always run validate + build-sqlite
- **Quality over quantity** — Accurate prices from official sources
- **Source URLs in commit messages**
- **Do NOT use ev-database.org** (Wojtek's instruction)
- **ALL data must come from sources fetched in THIS session** — no guessing prices
- **additionalProperties: false** enforced — use exact schema field names

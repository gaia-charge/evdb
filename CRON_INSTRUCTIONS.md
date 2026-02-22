# EVDB Cron Instructions

**Updated:** 2026-02-22
**Status:** 533 variants, ~1,359 market entries

---

## 🎯 CURRENT PRIORITY: NL, FR & IT Market Expansion

**Focus:** Add missing market-availability files for NL, FR, and IT markets.

### How to find what's missing

```bash
# Variants with DE market but no NL/FR/IT market
for CC in nl fr it; do
  echo "=== Missing $CC ==="
  comm -23 \
    <(ls data/market-availability/*-de.yaml | sed 's/-de\.yaml//' | sed 's|.*/||' | sort) \
    <(ls data/market-availability/*-$CC.yaml | sed 's/-$CC\.yaml//' | sed 's|.*/||' | sort) | head -20
done
```

### Per session workflow

1. Pick 3-5 variants missing NL, FR, or IT market files
2. **Prioritize transparent-pricing brands first:** Renault, Peugeot, Citroën, Volkswagen, Škoda, SEAT/Cupra, Fiat, Opel, Hyundai, Kia, MG, BYD, Dacia
3. **Deprioritize configurator-only brands:** BMW, Audi, Mercedes — their sites hide prices behind JS configurators. Use automotive press (see sources) instead of manufacturer sites for these.
4. Create market-availability YAML files with base_price, currency, on_sale status
5. Validate, commit to daily branch `data-fill/YYYY-MM-DD`, push
6. **Rotate across NL, FR, IT** each session

### Market-availability file format

```yaml
variant_id: "example-variant-id-2025"
country: "NL"  # or "FR" or "IT"
base_price: 45990
currency: "EUR"
on_sale: true
available_trims: []  # optional
incentives: []  # optional
notes: ""  # optional, market-specific info
```

Check existing files in `data/market-availability/` for exact format reference.

### Sources

**Acceptable sources (in priority order):**
1. Official manufacturer websites (.nl, .fr, .it)
2. Reputable automotive pricing/press sites:
   - **NL:** AutoWeek.nl, Autovisie.nl, Elektrischeauto.nl, AudiBlog.nl
   - **FR:** L'Argus (largus.fr), Turbo.fr, Automobile Magazine, Actua Auto
   - **IT:** Quattroruote.it, AutoScout24.it, alVolante.it, Motor1.com IT, Automobile360.it
3. Manufacturer press releases (media.manufacturer.xx)
4. Wikipedia (for availability confirmation only)

**If manufacturer site fails** (common with BMW, Audi, Mercedes JS-heavy configurators), use the automotive pricing sites above — they pull from official price lists.

### Important rules

- **Skip** variants where brand doesn't sell in that market
- **Do NOT use ev-database.org**
- **Prioritize volume brands** (Renault, VW, Hyundai, Kia, etc.) over premium brands with opaque pricing

### Market-specific notes

**Netherlands (NL):**
- Prices in EUR, BTW (21%) included
- BPM tax may apply (note in market file if relevant)
- Bijtelling rate relevant for lease market

**France (FR):**
- Prices in EUR, TVA (20%) included
- Bonus écologique if still active
- L'Argus is the definitive pricing reference

**Italy (IT):**
- Prices in EUR, IVA (22%) included
- Ecobonus incentives if still active
- Quattroruote is the definitive pricing reference

---

## 📊 Session Reporting Format

```
**Market expansion:** Added X market entries (Y for NL, Z for FR, W for IT)
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

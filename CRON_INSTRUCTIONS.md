# EVDB Cron Instructions

**Updated:** 2026-02-10  
**Status:** 🎉 **530+ variants, 180+ models, 45+ manufacturers**

---

## 🎯 CURRENT PRIORITIES (in order)

### Priority 1: Fill Missing Data on Existing Vehicles
Many existing variants are missing key specs. **Before adding new vehicles**, check and update existing ones:

**Fields to fill:**
- `dimensions`: length_mm, width_mm, height_mm, wheelbase_mm, ground_clearance_mm
- `cargo`: trunk_capacity_liters, trunk_max_liters (seats folded), frunk_capacity_liters
- `weight`: curb_weight_kg, gross_vehicle_weight_kg, payload_kg, towing_capacity_braked_kg, towing_capacity_unbraked_kg
- `charging`: Verify DC and AC charging power is complete
- `performance`: top_speed_kmh, acceleration_0_100_sec

**How to find vehicles with missing data:**
```bash
# Check which variants lack dimensions
grep -rL "dimensions:" data/vehicle-variants/ | head -20

# Check which variants lack cargo
grep -rL "cargo:" data/vehicle-variants/ | head -20

# Check which variants lack towing
grep -rL "towing_capacity" data/vehicle-variants/ | head -20
```

**Update 5-10 existing variants per session** with missing specs. Use manufacturer websites, ADAC, ev-database.org for data.

### Priority 2: Add Spain (ES), Poland (PL), and France (FR) Market Data
Most vehicles only have Germany (DE) market data. **Add market availability files** for:

1. **Spain (ES)** — Highest priority
2. **Poland (PL)** — Second priority  
3. **France (FR)** — Third priority

**For each market, create:** `data/market-availability/[variant-id]-[country].yaml`
- Include: base price in local currency (EUR for ES/FR, PLN for PL)
- Include: available trims, colors, incentives/grants
- Check: manufacturer's local website (e.g., tesla.com/es_ES, renault.pl, peugeot.fr)

**Spanish market specifics:**
- MOVES III subsidies (if still active in 2025/2026)
- IVA (21% VAT) included in prices
- Check: manufacturer.es websites

**Polish market specifics:**
- "Mój elektryk" subsidy program
- Prices in PLN
- Check: manufacturer.pl websites

**French market specifics:**
- Bonus écologique (up to €4,000-€7,000 depending on price)
- Leasing social program
- Check: manufacturer.fr websites

**Add 3-5 market entries per session.**

### Priority 3: Add New Vehicles (Lower Priority Now)
Only if priorities 1 and 2 have been addressed in the session:
- Focus on 2025/2026 model years
- Add missing variants for existing models
- Add new models not yet in the database

---

## 📋 SESSION WORKFLOW

1. **Check what's missing:**
   ```bash
   # Count variants without dimensions
   grep -rL "dimensions:" data/vehicle-variants/ | wc -l
   
   # Count variants without ES market
   ls data/market-availability/*-es.yaml 2>/dev/null | wc -l
   ```

2. **Update 5-10 existing variants** with missing specs (dimensions, cargo, towing, weight)

3. **Add 3-5 market entries** for ES/PL/FR markets

4. **Optionally add 1-2 new vehicles** if time permits

5. **Validate and commit:**
   ```bash
   python3 scripts/validate.py --directory data/
   python3 scripts/build-sqlite.py
   git add data/
   git commit -m "Update [X] variants with dimensions/cargo data, add [Y] ES/PL/FR market entries"
   git push origin main
   ```

---

## 📊 Session Reporting Format

```
**Data enrichment:** Updated X variants with dimensions/cargo/towing data
**Market expansion:** Added Y market entries (Z for ES, W for PL, V for FR)
**New vehicles:** [if any]
**Database:** X variants, Y market entries
**Validation:** ✅ All files pass
```

---

## ✅ Per-Variant Data Update Checklist

When updating an existing variant, add ALL available data:

- [ ] `dimensions.length_mm`
- [ ] `dimensions.width_mm`  
- [ ] `dimensions.height_mm`
- [ ] `dimensions.wheelbase_mm`
- [ ] `dimensions.ground_clearance_mm`
- [ ] `cargo.trunk_capacity_liters`
- [ ] `cargo.trunk_max_liters`
- [ ] `cargo.frunk_capacity_liters` (if applicable)
- [ ] `weight.curb_weight_kg`
- [ ] `weight.gross_vehicle_weight_kg`
- [ ] `weight.payload_kg`
- [ ] `weight.towing_capacity_braked_kg`
- [ ] `weight.towing_capacity_unbraked_kg`

---

## 🚫 Reminders

- **BEVs only** — No PHEVs, hybrids, or range extenders
- **European market only** — Vehicles sold in Europe
- **Validate before committing** — Always run validate.py
- **Quality over quantity** — Better accurate data than many incomplete entries
- **Model name convention:** Model `name` must NOT include brand prefix
- **Variant name convention:** Variant `name` must NOT include model name prefix

---

## 🔗 Data Sources

- **Manufacturer websites:** .de, .es, .pl, .fr variants
- **ADAC:** adac.de/rund-ums-fahrzeug/autokatalog/ (excellent for dimensions/weight)
- **ev-database.org:** Good for cross-referencing specs
- **Euro NCAP:** euroncap.com (dimensions, weight)

---

**Daily target:** 5-10 spec updates + 3-5 market entries  
**Quality over Speed** — accurate, complete data matters more than volume

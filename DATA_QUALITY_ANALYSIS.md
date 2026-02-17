# EVDB Data Quality Analysis

**Generated:** 2026-02-17 (Updated after schema normalization)  
**Analysis Tool:** `scripts/analyze_missing_data.py`

---

## 📊 Executive Summary

**Database Scale:** 534 vehicle variants  
**Overall Completeness:** ~75% (509 variants have some missing data)

### Missing Data Breakdown (After Schema Normalization)
- 🔴 **Critical fields:** 1,191 missing (~2.2 per variant) ⬇️ 71% reduction
  - Battery capacity, WLTP range, charging specs, performance
- 🟡 **Important fields:** 1,654 missing (~3.1 per variant) ⬇️ 45% reduction
  - Consumption, city/highway range, charging times
- ⚪ **Optional fields:** 1,983 missing (~3.7 per variant)
  - Battery voltage, charging curves, recuperation specs

### ✅ Schema Normalization Complete (2026-02-17)
The database has been normalized to use canonical flat field names:
- `charging.ac.max_power_kw` → `charging.ac_max_kw` (279 files)
- `charging.dc.max_power_kw` → `charging.dc_max_kw` (279 files)
- `motors.combined.*` → `performance.total_*` (50 files)
- **Total:** 776 transformations across 279 files
- **Backups:** Saved in `/home/ada/Projects/evdb/backups/20260217_214649/`

This resolved false positives where data existed but couldn't be detected due to nested vs flat naming differences.

### Market Coverage (Geographic)
| Market | Coverage | Missing |
|--------|----------|---------|
| 🇩🇪 DE | 100% (534/534) | ✅ Complete |
| 🇪🇸 ES | 61.8% (330/534) | 204 entries |
| 🇵🇱 PL | 30.0% (160/534) | 374 entries |
| 🇫🇷 FR | 28.7% (153/534) | 381 entries |
| 🇺🇸 US | 1.1% (6/534) | 528 entries |
| Others | <1% | ~533 entries each |

---

## 🎯 Prioritized Action Plan

### Phase 1: Critical Data Fill (HIGHEST PRIORITY)
**Target:** 1,191 critical missing fields (~2.2 per variant)  
**Impact:** Achieves 98%+ critical data completeness

**Critical fields to fill (canonical schema names):**
1. `battery.usable_kwh` — Battery capacity (usable)
2. `battery.total_kwh` — Battery capacity (total)
3. `range.wltp_km` — Official WLTP range
4. `charging.ac_max_kw` — AC charging power
5. `charging.dc_max_kw` — DC fast charging power
6. `performance.acceleration_0_100_sec` — 0-100 km/h time
7. `performance.top_speed_kmh` — Top speed
8. `performance.total_power_kw` — Motor power (kW)
9. `performance.total_torque_nm` — Motor torque (Nm)

**Methodology:**
- Use manufacturer websites (official spec sheets)
- Cross-reference with ADAC, ev-database.org
- Use `browser` tool to navigate manufacturer sites
- Fill 20-30 critical fields per session

**Session target:** 5 variants fully updated per session = 45 critical fields

---

### Phase 2: Important Data Enhancement
**Target:** 1,654 important missing fields (~3.1 per variant)  
**Impact:** Enables real-world comparisons and detailed analysis

**Important fields to add (canonical schema names):**
1. `range.wltp_city_km` — WLTP city range
2. `range.wltp_highway_km` — WLTP highway range
3. `range.real_world_km` — Real-world mixed range
4. `efficiency.wltp_kwh_per_100km` — WLTP consumption
5. `efficiency.real_world_kwh_per_100km` — Real-world consumption
6. `charging.time_10_to_80_min` — DC charging time
7. `charging.time_0_to_100_min` — AC charging time

**Session target:** 3-5 variants per session = 21-35 important fields

---

### Phase 3: Market Expansion (PARALLEL PRIORITY)
**Target:** 958 missing market entries (ES, PL, FR)  
**Impact:** Makes database useful beyond German market

**Priority order:**
1. 🇪🇸 **Spain (ES):** 204 missing entries (61.8% → 100%)
2. 🇵🇱 **Poland (PL):** 374 missing entries (30.0% → 100%)
3. 🇫🇷 **France (FR):** 381 missing entries (28.7% → 100%)

**Methodology:**
- Visit manufacturer's country-specific websites (.es, .pl, .fr)
- Gather: base price (local currency), available trims, local incentives
- Use format: `data/market-availability/[variant-id]-[country].yaml`

**Session target:** 5 market entries per session

---

### Phase 4: Optional Data (LOW PRIORITY)
**Target:** 2,280 optional fields  
**Impact:** Adds advanced features for power users

**Optional fields:**
- Battery voltage architecture (400V/800V)
- DC charging curve descriptions
- Heat pump availability
- Maximum recuperation power
- Advanced efficiency metrics

**Session target:** Fill when completing critical/important data for variant

---

## 📋 Workflow Recommendations

### Daily Session Structure (60-90 minutes)

**Option A: Critical Data Focus**
1. Run analysis: `python3 scripts/analyze_missing_data.py`
2. Identify top 5 variants with most missing critical data
3. For each variant:
   - Find manufacturer spec sheet (use `browser` tool)
   - Fill all 9 critical fields
   - Add important fields if time permits
4. Validate: `python3 scripts/validate.py --directory data/`
5. Commit: `git commit -m "Fill critical data for [variants]"`

**Expected output:** 5 variants, ~11 critical fields filled (avg 2.2 per variant)

---

**Option B: Market Expansion Focus**
1. Choose target market (ES/PL/FR)
2. Select 5 variants without that market entry
3. For each variant:
   - Navigate to manufacturer's country website
   - Create market availability file
   - Include pricing, trims, incentives
4. Validate and commit

**Expected output:** 5 market entries

---

**Option C: Balanced Approach (RECOMMENDED)**
1. Fill critical data for 3 variants (~7 critical fields)
2. Add 3 market entries (ES/PL/FR)
3. Validate and commit

**Expected output:** 3 variants improved, 3 market entries added, ~45-60 minutes per session

---

## 🎯 Top 20 Variants Needing Attention (Updated Post-Normalization)

Use this prioritized list to focus efforts:

1. `ford-capri-ev-extended-range-awd-2025` — 5 critical, 6 important missing
2. `ford-capri-ev-extended-range-rwd-2025` — 5 critical, 6 important missing
3. `ford-capri-ev-standard-range-rwd-2025` — 5 critical, 6 important missing
4. `ford-explorer-ev-extended-range-awd-2025` — 5 critical, 6 important missing
5. `ford-explorer-ev-extended-range-rwd-2025` — 5 critical, 6 important missing
6. `ford-explorer-ev-standard-range-rwd-2025` — 5 critical, 6 important missing
7. `kia-ev4-long-range-2025` — 4 critical, 5 important missing
8. `kia-ev4-standard-range-2025` — 4 critical, 5 important missing
9. `opel-frontera-ev-long-range-2025` — 4 critical, 5 important missing
10. `smart-hashtag3-pro-plus-2024` — 4 critical, 5 important missing

**Note:** Most variants now have 0-4 critical fields missing (avg 2.2), a dramatic improvement from the original 7.8 average after schema normalization.

*(Run `python3 scripts/analyze_missing_data.py` for full list)*

---

## 🛠️ Using the Analysis Tool

### Generate Overall Report
```bash
python3 scripts/analyze_missing_data.py
```

### Analyze Specific Variant
```bash
python3 scripts/analyze_missing_data.py data/vehicle-variants/kia-ev9-standard-range-rwd-2024.yaml
```

### Count Missing Fields by Type
```bash
# Count variants missing critical fields
python3 scripts/analyze_missing_data.py | grep "Critical:"

# Check market coverage
python3 scripts/analyze_missing_data.py | grep -A 10 "MARKET COVERAGE"
```

---

## 📈 Success Metrics

### ✅ Completed (2026-02-17)
- [x] Schema normalization complete (776 transformations, 279 files)
- [x] Reduced critical missing from 4,155 to 1,191 (71% reduction!)
- [x] Reduced important missing from 2,990 to 1,654 (45% reduction!)

### Short-term (Next 2 weeks)
- [ ] Reduce critical missing fields from 1,191 to <600 (50% reduction)
- [ ] Increase Spain (ES) coverage from 61.8% to 80%+
- [ ] Increase Poland (PL) coverage from 30% to 50%+

### Medium-term (Next month)
- [ ] Reduce critical missing fields to <250 (80% reduction)
- [ ] Achieve 90%+ coverage for ES, PL, FR markets
- [ ] Start filling important fields systematically

### Long-term (Next quarter)
- [ ] Zero critical missing fields (100% core data)
- [ ] 100% coverage for top 4 markets (DE, ES, PL, FR)
- [ ] 80%+ of important fields filled

---

## 📚 Data Sources Reference

### Primary Sources (Official)
- Manufacturer websites: .de, .es, .pl, .fr variants
- Official spec sheets (PDF downloads)
- Press releases and media kits

### Secondary Sources (Verification)
- **ADAC:** adac.de/rund-ums-fahrzeug/autokatalog/
- **ev-database.org:** Cross-reference specs
- **Euro NCAP:** euroncap.com (dimensions, weight)
- **Spritmonitor.de:** Real-world consumption data

### Access Method
Use `browser` tool with:
```
action: "navigate"
targetUrl: "https://manufacturer.de/model/specs"
```

Then:
```
action: "snapshot"
```

This provides access to real, current data without relying on web_search.

---

## 🚀 Getting Started

1. **Run the analysis:**
   ```bash
   cd ~/Projects/evdb
   python3 scripts/analyze_missing_data.py
   ```

2. **Pick your focus:**
   - Critical data fill (highest impact)
   - Market expansion (broad reach)
   - Balanced approach (recommended)

3. **Start working:**
   - Use variant ID from top 20 list
   - Gather data from manufacturer website
   - Fill YAML file
   - Validate and commit

4. **Track progress:**
   - Re-run analysis after each session
   - Watch metrics improve
   - Celebrate milestones!

---

**Next Steps:** Run `python3 scripts/analyze_missing_data.py` and choose top 3-5 variants to update in your next session.

# EVDB Cron Instructions - Vehicle Expansion

**Updated:** 2026-02-09  
**Status:** 🎉 **Streamlit app deployed and live!**

---

## 🎯 MISSION: Expand Vehicle Database

**Goal:** Systematically add ALL electric vehicles available in Europe

**Current Status:** 174 variants across 84 models from 26 manufacturers  
**Target:** 300-500+ variants covering every BEV sold in Europe

---

## ⚠️ MODEL YEAR PRIORITY

**Focus on CURRENT and UPCOMING model years:**

- **2025 models** - Current model year (HIGHEST PRIORITY)
- **2026 models** - Upcoming models (announced, available for order)
- **2024 models** - Only if still sold new in 2026 and no 2025 refresh exists

**When adding vehicles:**
1. Check manufacturer's website for latest model year
2. Prioritize 2025/2026 model years
3. Filename pattern: `[model]-[variant]-2025.yaml` or `-2026.yaml`
4. Include `model_year: 2025` or `2026` in variant YAML

**Rationale:** We're in February 2026 - database should reflect current market, not outdated 2024 models

---

## 📋 SIMPLE WORKFLOW

### For Each Cron Session:

1. **Read VEHICLE_EXPANSION_PLAN.md**
   - Follow the week-by-week manufacturer order
   - Current priority: **Renault** (0 models - start here!)

2. **Add 1-3 vehicles per session**
   - One manufacturer at a time
   - Complete model + all variants + market data

3. **Validate before committing**
   ```bash
   python scripts/validate.py
   ```
   - Must show 0 errors

4. **Test database build**
   ```bash
   python scripts/build-sqlite.py --clean
   ```
   - Verify new vehicles appear

5. **Commit and push**
   ```bash
   git add data/
   git commit -m "Add [Manufacturer] [Model] ([variants]) with [markets] pricing"
   git push origin main
   ```

---

## ✅ Per-Vehicle Checklist

For each new vehicle, create:

- [ ] **Vehicle model YAML** → `data/vehicle-models/[manufacturer]-[model].yaml`
- [ ] **Vehicle variant YAML(s)** → `data/vehicle-variants/[model]-[variant]-2025.yaml` (or `-2026.yaml`)
- [ ] **Market availability YAML** → `data/market-availability/[variant]-[country].yaml`
  - Start with Germany (DE) or France (FR)
  - Include base price, colors, options, delivery time
  - Calculate company car tax (Germany)
  - **Use 2025 or 2026 model year** - check manufacturer's website for latest

---

## 📊 Session Reporting

Report in this format:

```
Added [Manufacturer] [Model] with [X] variants:
- Variants: [list variant names]
- Markets: [DE/FR/US/etc]
- Files: [count] created
- Database: [new total] variants (up from [old total])
- Validation: ✅ All files pass
- Next: [next model to add]
```

Example:
```
Added Renault Megane E-Tech 2025 with 3 variants:
- Variants: EV40 2025, EV60 Techno 2025, EV60 Iconic 2025
- Markets: Germany (DE), France (FR)
- Files: 7 created (1 model + 3 variants + 3 market entries)
- Database: 54 variants (up from 51, +5.9%)
- Validation: ✅ All 173 files pass
- Next: Renault Scenic E-Tech 2025
```

---

## 🔄 Existing 2024 Vehicles

**DO NOT update existing 2024 vehicles** unless:
- You're adding a NEW variant that only exists in 2025/2026
- A major refresh happened (battery upgrade, significant spec changes)

**Focus on NEW additions** with 2025/2026 model years. The 2024 vehicles are still valid historical data.

---

## 🚫 What NOT to Add

- ❌ Plug-in hybrids (PHEVs)
- ❌ Mild hybrids
- ❌ Range extenders
- ❌ Concept cars
- ❌ Discontinued models
- ❌ Models not available in Europe

**ONLY:** Pure battery-electric vehicles (BEVs) sold in Europe

---

## 🎯 Current Priority

**PRIMARY FOCUS:** Add **2025 and 2026 model years** for manufacturers with good coverage

**Priority Areas:**
1. **Update existing manufacturers** with 2025/2026 models
   - BMW (add 2025 i4/i5/iX variants)
   - Mercedes-Benz (add 2025 EQE/EQS variants)
   - Volkswagen (add 2025 ID.3/ID.4/ID.5/ID.7 variants)
   - Audi (add 2025 Q4/Q6/Q8 e-tron variants)
   - Tesla (add 2025 Model 3/Y variants with new features)

2. **Add missing 2025 manufacturers**
   - Lucid (Air, Gravity)
   - Lotus (Eletre, Emeya)
   - Maserati (Grecale Folgore, GranTurismo Folgore)
   - Cadillac (Lyriq)

3. **Continue expansions from 2024** with 2025 models
   - Expand Stellantis brands with 2025 updates
   - BYD 2025 models (Seal U, Dolphin updates)

See **VEHICLE_EXPANSION_PLAN.md** for complete roadmap, but prioritize 2025/2026 model years.

---

## 💡 Quick Tips

1. **2025/2026 model years first** - Focus on current vehicles, not outdated 2024 models
2. **Check manufacturer websites** - Verify latest specs and pricing for 2025/2026 models
3. **Use existing vehicles as templates** - Copy similar YAML, modify specs
4. **German market first** - Most important (company car tax calculations)
5. **French brands = French market** - Add home market pricing
6. **Real-world range matters** - Include real-world consumption data
7. **ALWAYS validate before committing** - No exceptions!

---

## 🔗 Key Files

- **VEHICLE_EXPANSION_PLAN.md** - Complete roadmap
- **CONTRIBUTING.md** - Field-by-field guide
- **data/** directory - See existing vehicles for structure
- **scripts/validate.py** - Validation tool
- **scripts/build-sqlite.py** - Database builder

---

**Target:** 300+ variants by mid-March  
**Daily Target:** 2-3 vehicles per day  
**Quality over Speed:** Better 200 well-documented vehicles than 500 incomplete entries

---

**🚀 Remember:** Streamlit app is live and deployed! Vehicle expansion improves the database but doesn't block the launch. Work systematically and maintain quality.

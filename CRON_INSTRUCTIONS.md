# EVDB Cron Instructions - Vehicle Expansion

**Updated:** 2026-02-07  
**Status:** 🎉 **Streamlit app deployed and live!**

---

## 🎯 MISSION: Expand Vehicle Database

**Goal:** Systematically add ALL electric vehicles available in Europe

**Current Status:** 51 variants across 19 manufacturers  
**Target:** 300-500+ variants covering every BEV sold in Europe

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
- [ ] **Vehicle variant YAML(s)** → `data/vehicle-variants/[model]-[variant]-2024.yaml`
- [ ] **Market availability YAML** → `data/market-availability/[variant]-[country].yaml`
  - Start with Germany (DE) or France (FR)
  - Include base price, colors, options, delivery time
  - Calculate company car tax (Germany)

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
Added Renault Megane E-Tech with 3 variants:
- Variants: EV40, EV60 Techno, EV60 Iconic
- Markets: Germany (DE), France (FR)
- Files: 7 created (1 model + 3 variants + 3 market entries)
- Database: 54 variants (up from 51, +5.9%)
- Validation: ✅ All 173 files pass
- Next: Renault Scenic E-Tech
```

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

**Week 1:** Renault Group (HIGHEST PRIORITY - 0 models!)
- Start with **Renault Megane E-Tech** (3 variants)
- Then **Renault Scenic E-Tech** (2 variants)
- Then **Renault Zoe** (2 variants)

**Week 2:** BYD (expand from 1 model)
- **BYD Seal** (2 variants)
- **BYD Dolphin** (2-3 variants)

**Week 3-4:** Stellantis brands (Opel, Jeep, DS, Alfa, Fiat, Peugeot)

See **VEHICLE_EXPANSION_PLAN.md** for complete roadmap (all European manufacturers).

---

## 💡 Quick Tips

1. **Use existing vehicles as templates** - Copy similar YAML, modify specs
2. **German market first** - Most important (company car tax)
3. **French brands = French market** - Add home market pricing
4. **Real-world range matters** - Include real-world consumption
5. **ALWAYS validate before committing** - No exceptions!

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

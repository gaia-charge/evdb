# EVDB Cron Session Instructions

**Last Updated:** 2026-02-07 (Updated: 16:45)  
**Status:** Active development - Vehicle expansion phase

---

## 🎯 NEW PRIORITY: VEHICLE DATA EXPANSION

**User Request (Feb 7, 16:42):** Focus background work on adding vehicle data systematically.

**Target:** Add all electric models (no hybrids) from:
1. **Tesla** (2 models → complete flagship lineup)
2. **BYD** (1 model → expand to full lineup)
3. **Renault** (0 models → HIGHEST PRIORITY)
4. **Stellantis** (3 models → expand across all brands)

**Rationale:**
- Streamlit app is **95% complete and production-ready** ✅
- Vehicle expansion can happen in parallel with launch
- Systematic manufacturer-by-manufacturer approach
- Goal: 70-100+ variants (currently 51)

---

## 📋 Current Priority: Add Vehicles One Manufacturer at a Time

**Order of Operations:**
1. **Week 1:** Renault (HIGHEST - completely missing!)
2. **Week 2:** BYD (expand beyond just Atto 3)
3. **Week 3-4:** Stellantis brands (Opel, Jeep, DS, Alfa, Fiat)
4. **Week 5:** Tesla flagships (Model S, Model X)

**What cron sessions should do:**
1. **Read VEHICLE_EXPANSION_PLAN.md** - Complete expansion roadmap
2. **Read TODO.md** - Current phase status
3. **Add vehicles systematically** - Follow manufacturer order
4. **Validate before committing** - Run `python scripts/validate.py`
5. **Test database build** - Run `python scripts/build-sqlite.py --clean`
6. **Commit with clear messages** - "Add [Manufacturer] [Model] [variants]"

---

## 📋 Current Tasks: Vehicle Data Expansion

### Week 1 Priority: Renault (HIGHEST - 0 models currently!)

**Day 1-2: Renault Megane E-Tech** (Most important - EV of the Year 2023)
- [ ] Create manufacturer entry (if missing)
- [ ] Add vehicle model: Renault Megane E-Tech
- [ ] Add 3 variants:
  - [ ] EV40 (40 kWh, 300 km range)
  - [ ] EV60 (60 kWh, 470 km range)  
  - [ ] EV60 4Control AWD (60 kWh AWD)
- [ ] Add French market pricing (home market)
- [ ] Add German market pricing (our primary market)
- [ ] Validate and test database build

**Day 3-4: Renault Scenic E-Tech** (Brand new family SUV)
- [ ] Add vehicle model: Renault Scenic E-Tech
- [ ] Add 2 variants:
  - [ ] Comfort Range 60 kWh (430 km)
  - [ ] Long Range 87 kWh (625 km - longest range Renault!)
- [ ] Add French + German market pricing
- [ ] Validate and commit

**Day 5-6: Renault Zoe** (Classic EV, still selling)
- [ ] Add vehicle model: Renault Zoe
- [ ] Add 2 variants:
  - [ ] R110 (52 kWh, 395 km)
  - [ ] R135 (52 kWh, 386 km)
- [ ] Add French + German market pricing
- [ ] Validate and commit

**Goal for Week 1:** Complete Renault lineup (3-4 models, 7-8 variants)

---

### Week 2 Priority: BYD (Expand from 1 to 4-5 models)

**Day 1-2: BYD Seal** (Tesla Model 3 competitor)
- [ ] Add vehicle model: BYD Seal
- [ ] Add 2 variants:
  - [ ] Design (82.5 kWh RWD, 570 km)
  - [ ] Excellence (82.5 kWh AWD, 520 km)
- [ ] Add German market pricing
- [ ] Validate and commit

**Day 3-4: BYD Dolphin** (Compact hatchback)
- [ ] Add vehicle model: BYD Dolphin
- [ ] Add 2 variants:
  - [ ] Active (44.9 kWh, 340 km)
  - [ ] Boost (60.4 kWh, 427 km)
- [ ] Add German market pricing
- [ ] Validate and commit

**Goal for Week 2:** Expand BYD from 1 to 3 models (5 variants)

---

## ✅ What's Already Complete

Don't redo these - they're done:
- ✅ **Streamlit app (95% complete, production-ready)**
  - ✅ Home page with stats and search
  - ✅ Browse page with 7 filters
  - ✅ Compare page with charts
  - ✅ Analytics page with 15+ visualizations
  - ✅ Data Explorer with SQL interface
  - ✅ Documentation page (embedded guides)
- ✅ Database build pipeline (build-sqlite.py)
- ✅ Validation pipeline (validate.py)
- ✅ Datasette metadata.json (11 canned queries)
- ✅ API documentation (API_DOCS.md)
- ✅ Contribution guide (CONTRIBUTING.md)
- ✅ Launch plan (LAUNCH.md)
- ✅ FAQ (FAQ.md)
- ✅ GitHub Actions CI/CD

---

## 🎯 What TO Do

**Current Focus: ADD VEHICLES SYSTEMATICALLY**

**Do:**
- ✅ Add Renault electric models (HIGHEST PRIORITY - 0 models currently)
- ✅ Add BYD electric models (expand beyond Atto 3)
- ✅ Add Stellantis brand EVs (Opel, Jeep, DS, Alfa Romeo)
- ✅ Add Tesla flagship models (Model S, Model X)
- ✅ Follow manufacturer-by-manufacturer approach
- ✅ Validate before every commit
- ✅ Add German market pricing (primary market)
- ✅ Add French market pricing for French brands

**Don't:**
- ❌ Add plug-in hybrids (PHEVs) - pure electric only
- ❌ Add mild hybrids or range extenders
- ❌ Add discontinued or concept vehicles
- ❌ Skip validation step
- ❌ Work on Streamlit app (already 95% complete)

---

## 📊 Session Reporting

When announcing session completion, report:
1. **What vehicles were added** (e.g., "Added Renault Megane E-Tech (3 variants)")
2. **Files created** (e.g., "3 files: model, 3 variants, 2 market entries")
3. **Database impact** (e.g., "Database now has 54 variants (up from 51)")
4. **Validation status** (e.g., "All 170 YAML files validate successfully")
5. **Next priority** (e.g., "Next: Add Renault Scenic E-Tech")

**Report format example:**
```
Added Renault Megane E-Tech with 3 variants (EV40, EV60, EV60 4Control AWD):
- Created 1 model file, 3 variant files, 2 market files (DE, FR)
- Database: 54 variants (up from 51, +5.9%)
- All 170 YAML files validate ✅
- Next: Renault Scenic E-Tech (2 variants)
```

---

## 🔗 Key Files to Reference

1. **VEHICLE_EXPANSION_PLAN.md** - Complete expansion roadmap (READ THIS FIRST!)
2. **TODO.md** - Phase status and action plan
3. **data/** directory structure - See existing vehicles for templates
4. **evdb.db** - The database file (currently 0.25 MB, 51 variants)
5. **requirements.txt** - Python dependencies

---

## 🚀 Success Criteria

Session is successful if:
- ✅ Added at least 1 complete vehicle model (with all variants)
- ✅ Added market pricing for at least 1 market (preferably Germany or France)
- ✅ All YAML files validate successfully (0 errors)
- ✅ Database builds successfully with new data
- ✅ Changes committed and pushed with clear message
- ✅ Progress documented in commit message

Session is NOT successful if:
- ❌ Added a plug-in hybrid (PHEV) instead of pure electric
- ❌ Skipped validation step
- ❌ Committed files that don't validate
- ❌ No clear commit message
- ❌ Worked on non-priority tasks (Streamlit app is already 95% done!)

---

## 📅 Timeline

**Vehicle Expansion Timeline:**

**Week 1 (Feb 7-13):** Renault (HIGHEST PRIORITY)  
**Week 2 (Feb 14-20):** BYD expansion  
**Week 3-4 (Feb 21-Mar 6):** Stellantis brands  
**Week 5 (Mar 7-13):** Tesla flagships

**Parallel:** Streamlit app deployment can happen anytime (already 95% complete)

**Target Database Size:** 70-100+ variants by mid-March

---

## 💡 Tips for Effective Sessions

1. **Read VEHICLE_EXPANSION_PLAN.md first** - Comprehensive roadmap with all details
2. **Follow manufacturer order** - Renault → BYD → Stellantis → Tesla
3. **Use existing vehicles as templates** - Copy similar vehicle YAML, modify specs
4. **Always validate before committing** - `python scripts/validate.py`
5. **Test database build** - `python scripts/build-sqlite.py --clean`
6. **German market first** - Best coverage, most important for company car buyers
7. **Real-world range matters** - Include real-world consumption estimates
8. **Company car tax calculations** - Critical for German market (0.25% under €70k threshold)

---

## 📋 Per-Vehicle Workflow

**For each new vehicle:**

1. **Research specifications**
   - Check manufacturer website (official specs)
   - Verify WLTP range, battery capacity, charging power
   - Find real-world test data (InsideEVs, ADAC, AutoBild)

2. **Create vehicle model YAML**
   - File: `data/vehicle-models/[manufacturer]-[model].yaml`
   - Copy template or similar existing vehicle
   - Update all specifications

3. **Create vehicle variant YAML(s)**
   - Files: `data/vehicle-variants/[model]-[variant]-2024.yaml`
   - One file per trim/battery combination
   - Complete battery, range, charging, performance specs

4. **Create market availability YAML(s)**
   - Files: `data/market-availability/[variant]-[country-code].yaml`
   - Start with German market (DE) - most important
   - Include pricing, colors, options, delivery time
   - Calculate company car tax benefits

5. **Validate**
   ```bash
   python scripts/validate.py
   ```
   - Must show 0 errors before committing
   - Fix any validation errors

6. **Test database build**
   ```bash
   python scripts/build-sqlite.py --clean
   ```
   - Verify new vehicles appear in database
   - Check SQL queries work correctly

7. **Commit & push**
   ```bash
   git add data/
   git commit -m "Add [Manufacturer] [Model] ([variants]) with [markets] pricing"
   git push origin main
   ```

---

**Remember: Quality over speed. Each vehicle should have verified specifications, real-world data, and complete market pricing. Follow the manufacturer order in VEHICLE_EXPANSION_PLAN.md!**

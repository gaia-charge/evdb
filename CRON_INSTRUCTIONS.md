# EVDB Cron Session Instructions

**Last Updated:** 2026-02-07  
**Status:** Active development - Streamlit deployment phase

---

## 🚨 CRITICAL: DO NOT ADD MORE VEHICLES

**User Request (Feb 7):** Stop adding vehicles, focus on building the platform.

**Rationale:**
- We have **51 vehicle variants** (target was 40) ✅
- We have **excellent diversity** (luxury, 800V, trucks, affordable, performance)
- We have **5 markets** covered (Germany strongest with 27 vehicles)
- **Adding more vehicles doesn't help if users can't access them**

---

## 🎯 Current Priority: Phase 8 - Streamlit App

**Goal:** Build user-friendly Streamlit web app as PRIMARY interface (not Vercel/Datasette)

**What cron sessions should do:**
1. **Read STREAMLIT_PLAN.md** - Comprehensive implementation guide
2. **Read TODO.md** - Current phase status and priorities
3. **Work on streamlit_app.py** - Build the web interface
4. **Test locally** - Ensure features work
5. **Commit progress** - Incremental commits as features complete

---

## 📋 Phase 8 Tasks (Priority Order)

### Day 1 (Feb 7) - Skeleton & Home Page
- [ ] Create `streamlit_app.py` with basic structure
- [ ] Implement database connection (with caching)
- [ ] Build Home page:
  - [ ] Display database statistics
  - [ ] Show latest additions
  - [ ] Add quick search box
- [ ] Test locally: `streamlit run streamlit_app.py`
- [ ] Commit initial version

### Day 2 (Feb 8) - Browse Vehicles
- [ ] Implement sidebar filters (price, range, charging, manufacturer, etc.)
- [ ] Build dynamic SQL query from filter selections
- [ ] Display results in searchable dataframe
- [ ] Add vehicle detail expansion
- [ ] Add export functionality (CSV/JSON)
- [ ] Test all filter combinations

### Day 3 (Feb 9) - Compare & Analytics
- [ ] Implement Compare Vehicles page (multi-select, side-by-side)
- [ ] Add basic charts in Analytics:
  - [ ] Range vs battery scatter plot
  - [ ] Charging speed comparison
  - [ ] Price distribution histogram
- [ ] Deploy to Streamlit Cloud
- [ ] Test on production

---

## ✅ What's Already Complete

Don't redo these - they're done:
- ✅ Database build pipeline (build-sqlite.py)
- ✅ Validation pipeline (validate.py)
- ✅ Datasette metadata.json (11 canned queries)
- ✅ API documentation (API_DOCS.md)
- ✅ Contribution guide (CONTRIBUTING.md)
- ✅ Launch plan (LAUNCH.md)
- ✅ FAQ (FAQ.md)
- ✅ GitHub Actions CI/CD
- ✅ 51 vehicle variants with quality data

---

## ❌ What NOT to Do

**Don't:**
- ❌ Add new vehicle variants to the database
- ❌ Add new market data (unless fixing a bug)
- ❌ Expand to new markets (UK, Norway, etc.)
- ❌ Add more manufacturers
- ❌ Work on Vercel deployment (we're using Streamlit)
- ❌ Spend time on Datasette plugins (Streamlit is primary)

**Why?** Because the launch blocker is the user interface, not the data. We have sufficient data. Focus on making it accessible.

---

## 📊 Session Reporting

When announcing session completion, report:
1. **What was built** (e.g., "Home page with stats display")
2. **Files created/modified** (e.g., "streamlit_app.py created")
3. **Testing done** (e.g., "Tested locally - works on desktop & mobile")
4. **Commits pushed** (e.g., "2 commits: skeleton + home page")
5. **Next priority** (e.g., "Next: implement sidebar filters")

**Don't report:**
- ❌ "Added vehicle X to database" (we're not doing this)
- ❌ "51 variants now 52 variants" (stop adding vehicles!)

---

## 🔗 Key Files to Reference

1. **STREAMLIT_PLAN.md** - Detailed implementation guide
2. **TODO.md** - Phase status and action plan
3. **API_DOCS.md** - Query examples (useful for SQL queries in Data Explorer)
4. **evdb.db** - The database file (0.25 MB, 51 variants)
5. **requirements.txt** - Check Streamlit dependencies are there

---

## 🚀 Success Criteria

Session is successful if:
- ✅ Moved Streamlit app forward (new feature or page)
- ✅ Code tested locally
- ✅ Changes committed and pushed
- ✅ Progress documented
- ✅ No new vehicles added

Session is NOT successful if:
- ❌ Added vehicles instead of building Streamlit app
- ❌ Spent time on non-priority tasks (like Datasette plugins)
- ❌ Broke existing functionality
- ❌ No tangible progress on Streamlit app

---

## 📅 Timeline

**Target:** Deploy to Streamlit Cloud by Feb 9, public launch Feb 15-20

**Today (Feb 7):** Start Phase 8, build skeleton + home page  
**Tomorrow (Feb 8):** Browse page with filters  
**Feb 9:** Deploy to production  
**Feb 10-12:** Soft launch & polish  
**Feb 15-20:** Public launch

---

## 💡 Tips for Effective Sessions

1. **Read STREAMLIT_PLAN.md first** - Don't guess, follow the plan
2. **Work incrementally** - One feature at a time, commit often
3. **Test as you go** - Run `streamlit run streamlit_app.py` frequently
4. **Use caching** - `@st.cache_data` and `@st.cache_resource` for performance
5. **Keep it simple** - MVP first, polish later
6. **Check mobile** - Many users will browse on phones

---

**Remember: The goal is a launched product, not a perfect database. Focus on building the interface!**

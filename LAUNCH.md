# EVDB Launch Plan

**Status**: Ready for Deployment  
**Launch Date Target**: February 15-20, 2026  
**Soft Launch**: February 10-12, 2026

---

## 🎯 Pre-Launch Checklist

### Infrastructure (Phase 7)
- [x] Database builds successfully (51 variants)
- [x] Validation pipeline working (164 files, 0 errors)
- [x] CI/CD pipeline configured (GitHub Actions)
- [x] Deployment code ready (commented in workflow)
- [ ] **BLOCKER**: Get Vercel token and activate deployment
- [ ] Verify live deployment works
- [ ] Test all API endpoints on production

### Documentation (Phase 9)
- [x] README.md polished
- [x] CONTRIBUTING.md complete (12KB guide)
- [x] API_DOCS.md comprehensive (16KB, 11 queries)
- [x] DEPLOYMENT.md ready (7.8KB)
- [ ] Add live API URL to README once deployed
- [ ] Create FAQ.md based on soft launch feedback

### Quality (Ongoing)
- [x] 50+ vehicles with verified specs
- [x] 5 markets covered (Germany primary)
- [x] All YAML files validate
- [ ] Mobile responsiveness check (post-deployment)
- [ ] Test all example API queries on production

---

## 🚀 Launch Phases

### Phase 1: Deployment (Feb 8-9)
**Goal**: Get live URL working

1. Get Vercel token from https://vercel.com/account/tokens
2. Add `VERCEL_TOKEN` to GitHub repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `VERCEL_TOKEN`
   - Value: (paste token)
3. Uncomment deployment section in `.github/workflows/build-deploy.yml` (lines 47-51)
4. Push to main branch → automatic deployment
5. Note live URL (e.g., `evdb-xxx.vercel.app`)
6. Test all endpoints:
   ```bash
   curl https://evdb-xxx.vercel.app/evdb.json
   curl https://evdb-xxx.vercel.app/evdb/vehicle_variants.json
   curl "https://evdb-xxx.vercel.app/evdb/find_by_range.json?min_range=500"
   ```
7. Update README.md with live URL
8. Verify GraphQL endpoint works
9. Test on mobile devices
10. Check response times

### Phase 2: Soft Launch (Feb 10-12)
**Goal**: Get feedback from trusted circle

**Audience**: Close friends, EV enthusiasts, tech-savvy early adopters

**Channels**:
- Personal contacts (email, DMs)
- Small EV groups/Discord servers you're in
- Tech friends who would give constructive feedback

**Ask for feedback on**:
- API usability and documentation clarity
- Missing features or data points
- UI/UX of Datasette interface
- Data accuracy for vehicles they know
- Performance and response times

**Monitor**:
- Server logs for errors
- API usage patterns
- Feedback quality and themes
- Any critical bugs or issues

**Fix Priority**:
- Critical bugs immediately
- Documentation gaps quickly
- Feature requests → roadmap

### Phase 3: Public Launch (Feb 15-20)
**Goal**: Announce to wider community

**Timing**: Weekday morning (Tuesday-Thursday, 9-11 AM ET) for maximum visibility

**Launch Sequence** (space 2-4 hours apart):

1. **Reddit**: r/electricvehicles
2. **Hacker News**: news.ycombinator.com/submit
3. **Product Hunt**: producthunt.com (needs account setup in advance)
4. **Twitter/X**: Tech and EV communities
5. **Specialized Communities**: 
   - EV Discord servers
   - Tesla/Rivian/Lucid forums
   - /r/teslamotors, /r/Rivian, etc.

---

## 📝 Launch Announcement Templates

### Reddit (r/electricvehicles)

**Title**: [Project] EVDB - Open Electric Vehicle Database with API (50+ EVs, 5 markets)

**Body**:
```markdown
Hi r/electricvehicles! 👋

I've been building an **open-source electric vehicle database** with detailed specs and a public API. After months of work, I'm excited to share it with the community!

## What is EVDB?

A comprehensive, community-driven database of electric vehicles with:
- ✅ **Detailed specs**: Battery, range (WLTP/EPA), charging speeds, performance
- ✅ **Market data**: Pricing, incentives, availability by country
- ✅ **Public API**: Free REST/GraphQL API for developers
- ✅ **Quality tracking**: Every field has source and confidence level
- ✅ **Open license**: CC BY-SA 4.0 - free to use and contribute

## Current Status

- **51 vehicle variants** across 37 models from 19 manufacturers
- **5 markets**: Germany (25 vehicles), USA (6), France, Poland, Italy
- **11 pre-built queries**: Find by range, price, charging speed, efficiency, etc.
- **Full API documentation** with examples in curl/Python/JavaScript

## Why Build This?

Existing EV databases are often:
- Behind paywalls or limited free tiers
- Incomplete or outdated
- Not open source or community-driven
- Missing real-world data (just WLTP claims)

I wanted something open, comprehensive, and developer-friendly.

## Tech Stack

YAML source files → JSON Schema validation → SQLite → Datasette API

All data is in git-friendly YAML with validation, making it easy to:
- Track changes over time
- See what changed and when
- Contribute via GitHub PRs

## Try It

🔗 **Live API**: https://evdb-xxx.vercel.app/evdb
📖 **API Docs**: https://github.com/yourusername/evdb/blob/main/API_DOCS.md
🚀 **Contribute**: https://github.com/yourusername/evdb/blob/main/CONTRIBUTING.md

Example query - EVs with 500+ km range:
```
curl "https://evdb-xxx.vercel.app/evdb/find_by_range.json?min_range=500"
```

## What's Next?

- Expand to more markets (UK, Norway, Netherlands, China)
- Add more budget EVs and Chinese brands
- Community contributions for missing vehicles
- Real-world range data collection
- Charging network integration

## How to Contribute

Missing your favorite EV? Found incorrect data? All contributions welcome!

See CONTRIBUTING.md for a step-by-step guide. It's just:
1. Fork the repo
2. Add/edit YAML files
3. Validate locally
4. Submit PR

**Feedback Welcome!** This is v1.0 - please let me know what's useful, what's missing, or what could be better.

Thanks for checking it out! 🚗⚡
```

---

### Hacker News

**Title**: EVDB – Open-source electric vehicle database with public API

**URL**: https://github.com/yourusername/evdb

**Comment** (if it gets traction):
```
Author here! Happy to answer questions about the architecture or data.

Built with YAML + JSON Schema + SQLite + Datasette because:
- YAML: Human-readable, git-friendly, easy for contributors
- JSON Schema: Validation ensures data quality
- SQLite: Single file, portable, fast
- Datasette: Instant API + web UI

Currently 51 vehicles across 5 markets. All data validated and versioned in git.

Live API: https://evdb-xxx.vercel.app/evdb
API Docs: [link]

Feedback and contributions welcome!
```

---

### Product Hunt

**Tagline**: Open electric vehicle database with free API for developers

**Description**:
```
EVDB is an open-source database of electric vehicles with detailed specifications and a free public API.

✅ 51 vehicle variants with comprehensive specs (battery, range, charging, performance)
✅ Market-specific pricing and availability (5 markets: Germany, USA, France, Poland, Italy)
✅ Free REST & GraphQL API for developers
✅ Quality-tracked data (every field has source + confidence level)
✅ Community-driven with git versioning
✅ CC BY-SA 4.0 license - free to use, share, build upon

Perfect for:
- EV comparison apps
- Charging network optimization
- Fleet management tools
- Research and analysis
- EV enthusiast projects

Built with modern stack: YAML → JSON Schema → SQLite → Datasette

All data is human-readable YAML in GitHub, making it easy to contribute and track changes over time.
```

**Topics**: `electric-vehicles`, `open-source`, `database`, `api`, `sustainability`, `automotive`, `developer-tools`

---

### Twitter/X

**Thread**:
```
🚗⚡ Excited to launch EVDB - an open-source electric vehicle database with a free public API!

51 vehicles across 5 markets, all with detailed specs, pricing, and real-world data.

Built for developers, researchers, and EV enthusiasts.

🧵 Here's what makes it different: [1/6]

---

Unlike existing EV databases, EVDB is:
✅ Completely open source (CC BY-SA 4.0)
✅ Git-versioned (track every change)
✅ Community-driven (contributions welcome)
✅ Free API (no rate limits currently)
✅ Quality-tracked (every field has source + confidence) [2/6]

---

Tech stack:
📄 YAML source files (human-readable, git-friendly)
✅ JSON Schema validation (data quality)
💾 SQLite database (portable, fast)
🔌 Datasette API (instant REST + GraphQL)

All automated with GitHub Actions CI/CD [3/6]

---

Current coverage:
🚗 51 vehicle variants from 19 manufacturers
🌍 5 markets (Germany, USA, France, Poland, Italy)
⚡ 11 pre-built queries (range, price, charging, efficiency)
📚 Comprehensive API docs with examples

[4/6]

---

Example query - Find EVs with 500+ km range:

curl "https://evdb-xxx.vercel.app/evdb/find_by_range.json?min_range=500"

Full API docs, Python/JS examples, and GraphQL endpoint available.

Perfect for building EV comparison apps, route planners, or charging tools. [5/6]

---

What's next:
📈 Expand to UK, Norway, Netherlands, China
🚙 More budget EVs and Chinese brands
🤝 Community contributions
🌐 Real-world range data
🔌 Charging network integration

Contributions welcome!

🔗 https://github.com/yourusername/evdb
📖 API: https://evdb-xxx.vercel.app/evdb

[6/6]
```

---

## 📊 Success Metrics

### Week 1 (Soft Launch)
- [ ] 10-20 people test the API
- [ ] 5-10 pieces of constructive feedback
- [ ] 0 critical bugs found
- [ ] 1-2 pull requests from community
- [ ] Document common questions → FAQ

### Month 1 (Post Public Launch)
- [ ] 100+ GitHub stars
- [ ] 10+ community contributors
- [ ] 50+ vehicles added (100+ total)
- [ ] 10+ markets covered
- [ ] 1000+ API requests/day
- [ ] Active discussions/issues on GitHub

### Month 3 (Growth)
- [ ] 500+ GitHub stars
- [ ] 50+ community contributors
- [ ] 200+ vehicles (comprehensive coverage)
- [ ] 20+ markets
- [ ] 10k+ API requests/day
- [ ] First derivative project built on EVDB API
- [ ] Featured in EV community resources

---

## 🛡️ Crisis Management

### If Something Breaks
1. **Acknowledge immediately** on GitHub issues
2. **Assess severity**: Critical (API down) vs Minor (single query broken)
3. **Fix critical issues within hours**, minor within days
4. **Communicate timeline** - be transparent
5. **Post-mortem** - what went wrong, how to prevent

### If Data Quality Issues
1. **Mark affected entries** with confidence: low
2. **Add issue comment** explaining uncertainty
3. **Request community help** for verification
4. **Update when confirmed** with proper sources
5. **Thank contributors** publicly

### If Negative Feedback
1. **Listen and understand** the concern
2. **Acknowledge if valid** - no defensiveness
3. **Explain trade-offs** if it's by design
4. **Add to roadmap** if it's a good idea
5. **Thank for feedback** regardless

---

## 🎉 Post-Launch Activities

### Week 1
- [ ] Monitor GitHub issues/PRs daily
- [ ] Respond to all feedback within 24 hours
- [ ] Fix critical bugs immediately
- [ ] Update FAQ.md with common questions
- [ ] Thank early contributors publicly

### Week 2-4
- [ ] Set up GitHub Discussions for Q&A
- [ ] Create "good first issue" labels for new contributors
- [ ] Write blog post: "Building EVDB - Lessons Learned"
- [ ] Reach out to EV publications/podcasts
- [ ] Consider Streamlit dashboard if requested

### Month 2+
- [ ] Establish regular contribution guidelines
- [ ] Create roadmap based on community feedback
- [ ] Consider sponsorship/sustainability model
- [ ] Expand core contributor team
- [ ] Plan for scaling infrastructure if needed

---

## 🙏 Community Building

**Key Principles**:
- Be welcoming and encouraging to new contributors
- Document everything clearly
- Respond quickly and kindly
- Celebrate contributions publicly
- Admit mistakes openly
- Prioritize community needs over personal vision

**Communication Channels**:
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Q&A and community chat
- README: Quick links and status updates
- CHANGELOG.md: Track all releases
- Twitter/X: Updates and announcements

**Recognition**:
- CONTRIBUTORS.md: Thank everyone who helps
- GitHub Releases: Highlight key contributions
- README badges: Show community size
- Social media: Share community wins

---

## 📅 Timeline Summary

| Date | Phase | Key Activities |
|------|-------|----------------|
| Feb 7 | **Preparation** ✅ | Documentation complete, database ready |
| Feb 8 | **Deployment** | Get Vercel token, activate deployment, test |
| Feb 9 | **Testing** | Verify all endpoints, mobile check, docs update |
| Feb 10-12 | **Soft Launch** | Share with close circle, collect feedback, fix issues |
| Feb 13-14 | **Polish** | Address soft launch feedback, prepare announcements |
| Feb 15-20 | **Public Launch** | Reddit, HN, Product Hunt, Twitter, communities |
| Feb 21-28 | **Support** | Monitor, respond, fix, improve based on feedback |
| Mar+ | **Growth** | Expand coverage, build community, new features |

---

**Ready to launch! 🚀** Just need that Vercel token to start the deployment phase.

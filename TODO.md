# EVDB Implementation TODO

This document tracks implementation tasks for building EVDB from scratch.

## 🎯 Current Phase: Foundation Setup

---

## Phase 0: Foundation (Week 1)

### Project Setup
- [x] Create comprehensive schema (`api/v1/schema/vehicle.json`)
- [x] Define standardized enums (`api/v1/schema/enums.json`)
- [x] Write documentation (ENHANCEMENTS.md, INTERNATIONALIZATION.md, ROADMAP)
- [x] Create validation script (`scripts/validate.js`)
- [x] Update domain to evdb.gaiacharge.com
- [x] Clean up old code
- [x] Update README.md
- [ ] Set up GitHub repository properly
  - [ ] Change default branch to `main`
  - [ ] Delete old `master` branch
  - [ ] Update repository description
  - [ ] Add topics/tags (evdb, electric-vehicles, open-data)
- [ ] Create `.nvmrc` or specify Node.js version
- [ ] Set up package.json with validation dependencies
- [ ] Configure Hugo properly
  - [ ] Test Hugo build locally
  - [ ] Verify JSON output works

### Documentation
- [x] Write README.md
- [x] Create TODO.md (this file)
- [ ] Write CONTRIBUTING.md
  - [ ] How to add a vehicle
  - [ ] How to validate data
  - [ ] Code review process
  - [ ] Data source requirements
- [ ] Create issue templates
  - [ ] Bug report
  - [ ] New vehicle request
  - [ ] Feature request
- [ ] Add pull request template

---

## Phase 1: Hugo Setup & Templates (Week 2-3)

### Hugo Configuration
- [ ] Configure multi-language support in `config.toml`
  - [ ] Set up language definitions (en, de, pl, fr)
  - [ ] Configure content directories
  - [ ] Set up URL structure
- [ ] Create Hugo archetypes
  - [ ] Vehicle archetype with schema defaults
  - [ ] Manufacturer archetype
- [ ] Configure taxonomies properly

### Layout Templates
- [ ] Create base layouts
  - [ ] `layouts/_default/baseof.html` (if HTML needed)
  - [ ] `layouts/_default/baseof.json` for JSON output
- [ ] Create vehicle templates
  - [ ] `layouts/vehicles/single.json` - Individual vehicle JSON
  - [ ] `layouts/vehicles/list.json` - Vehicle list JSON
  - [ ] Support all schema fields in output
- [ ] Create manufacturer templates
  - [ ] `layouts/manufacturers/single.json`
  - [ ] `layouts/manufacturers/list.json`
- [ ] Create home/index template
  - [ ] `layouts/index.json` - API root
  - [ ] Include API documentation links
- [ ] Test all templates with sample data

### Validation & CI
- [ ] Enhance validation script
  - [ ] Add schema validation (JSON Schema validator)
  - [ ] Check all required fields
  - [ ] Validate enum values
  - [ ] Check image references
  - [ ] Validate country/currency codes
- [ ] Set up GitHub Actions
  - [ ] Run validation on all PRs
  - [ ] Build Hugo site on push
  - [ ] Deploy to GitHub Pages or Netlify
- [ ] Add pre-commit hooks
  - [ ] Run validation before commit
  - [ ] Check markdown formatting

---

## Phase 2: Initial Content & Data (Week 3-4)

### Content Structure
- [ ] Create content directories
  ```
  content/
    en/
      vehicles/
      manufacturers/
    de/
      vehicles/
      manufacturers/
    pl/
      vehicles/
      manufacturers/
  ```
- [ ] Create manufacturer pages
  - [ ] Top 10 EV manufacturers (Tesla, VW, BYD, etc.)
  - [ ] Include company info, history, logo

### Initial Vehicle Data
- [ ] Add 20 popular EVs with complete data:
  - [ ] Tesla Model 3
  - [ ] Tesla Model Y
  - [ ] Volkswagen ID.4
  - [ ] Volkswagen ID.3
  - [ ] Ford Mustang Mach-E
  - [ ] Hyundai Ioniq 5
  - [ ] Kia EV6
  - [ ] BYD Atto 3
  - [ ] Nissan Ariya
  - [ ] Nissan Leaf
  - [ ] BMW iX
  - [ ] BMW i4
  - [ ] Audi e-tron / Q8 e-tron
  - [ ] Mercedes EQS
  - [ ] Polestar 2
  - [ ] MG4 Electric
  - [ ] Opel Mokka-e (already done)
  - [ ] Renault Megane E-Tech
  - [ ] Škoda Enyaq
  - [ ] Volvo XC40 Recharge

### Data Quality
- [ ] Research and verify specifications
  - [ ] Use official manufacturer specs
  - [ ] Cross-reference with certification data (WLTP)
  - [ ] Add source URLs to `external_ids`
- [ ] Add market availability data
  - [ ] At least DE, PL, FR, GB, NL, NO for each vehicle
  - [ ] Include availability dates
- [ ] Collect pricing information
  - [ ] MSRP for major markets
  - [ ] Government incentives
  - [ ] Model year

---

## Phase 3: Images & Media (Week 5-6)

### Image Infrastructure
- [ ] Choose image hosting solution
  - Option A: Store in `static/images/` (simple, but large repo)
  - Option B: External CDN (Cloudinary, Imgur, S3)
  - Option C: Git LFS (large file storage)
  - **Decision needed**: _______________
- [ ] Create image directory structure
  ```
  static/images/
    vehicles/
      tesla-model-3/
        exterior-front.jpg
        exterior-side.jpg
        interior-dashboard.jpg
        technical-battery.svg
  ```
- [ ] Set up image optimization
  - [ ] Resize to standard dimensions
  - [ ] Convert to WebP for web
  - [ ] Keep originals in high resolution

### Image Collection
- [ ] Source images for initial 20 vehicles
  - [ ] Official press photos (check licensing)
  - [ ] Wikipedia Commons (CC-licensed)
  - [ ] User submissions (with permission)
- [ ] Add image metadata to vehicle files
  - [ ] At least 3 images per vehicle
  - [ ] Include: type, subtype, credit, license, alt text
- [ ] Create image contribution guidelines
  - [ ] Acceptable licenses (CC BY-SA 4.0, Press Photos)
  - [ ] Required resolution and format
  - [ ] How to attribute sources

---

## Phase 4: Internationalization (Week 7-9)

### i18n Setup
- [ ] Create translation directories
  - [ ] `i18n/en.toml` (English UI strings)
  - [ ] `i18n/de.toml` (German UI strings)
  - [ ] `i18n/pl.toml` (Polish UI strings)
  - [ ] `i18n/fr.toml` (French UI strings)
- [ ] Translate UI elements
  - [ ] Field labels (Battery, Range, Performance, etc.)
  - [ ] Navigation
  - [ ] Error messages
  - [ ] Enum value descriptions

### Content Translation
- [ ] Translate top 10 vehicles to German
  - [ ] Title and description
  - [ ] Keep technical specs universal
  - [ ] Localize pricing (show EUR/PLN/etc.)
- [ ] Translate top 10 vehicles to Polish
- [ ] Create translation workflow
  - [ ] Use DeepL API for initial drafts?
  - [ ] Manual review required
  - [ ] Track translation status in front matter

### Language Switching
- [ ] Add language switcher to templates
- [ ] Test cross-language linking
- [ ] Verify hreflang tags for SEO

---

## Phase 5: API Enhancement (Week 10-11)

### JSON API
- [ ] Enhance JSON output
  - [ ] Include all schema fields
  - [ ] Add translation links
  - [ ] Format numbers consistently
- [ ] Create API endpoints
  - [ ] `/api/v1/vehicles/` - All vehicles
  - [ ] `/api/v1/vehicles/{id}/` - Single vehicle
  - [ ] `/api/v1/manufacturers/` - All manufacturers
  - [ ] `/api/v1/manufacturers/{id}/` - Single manufacturer
- [ ] Add filtering
  - [ ] By manufacturer
  - [ ] By body type
  - [ ] By market availability
  - [ ] By battery chemistry
  - [ ] By charging capability
  - [ ] By price range

### API Documentation
- [ ] Create OpenAPI/Swagger spec
- [ ] Generate API documentation
- [ ] Add usage examples
- [ ] Document rate limits (if any)

---

## Phase 6: Deployment & Infrastructure (Week 12)

### Hosting
- [ ] Choose hosting platform
  - Option A: GitHub Pages (free, simple)
  - Option B: Netlify (free tier, more features)
  - Option C: Vercel (free tier, fast)
  - **Decision needed**: _______________
- [ ] Set up custom domain (evdb.gaiacharge.com)
  - [ ] Configure DNS
  - [ ] Enable HTTPS
- [ ] Configure build and deploy
  - [ ] Auto-deploy on push to `main`
  - [ ] Preview deployments for PRs

### CI/CD
- [ ] GitHub Actions workflows
  - [ ] `.github/workflows/validate.yml` - Data validation
  - [ ] `.github/workflows/build.yml` - Hugo build
  - [ ] `.github/workflows/deploy.yml` - Deploy to hosting
- [ ] Set up monitoring
  - [ ] Uptime monitoring
  - [ ] Broken link checker
  - [ ] Analytics (optional, privacy-friendly)

---

## Phase 7: Community & Launch (Week 13+)

### Community Building
- [ ] Create contribution guidelines
- [ ] Set up GitHub Discussions
- [ ] Create Discord/Slack (optional)
- [ ] Write blog post announcing launch
- [ ] Share on EV forums/communities

### Data Expansion
- [ ] Add 50+ more vehicles
- [ ] Expand to more countries
- [ ] Add historical models
- [ ] User-submitted data process

### Future Features
- [ ] GraphQL API
- [ ] User accounts & contributions
- [ ] Real-world range data (user-submitted)
- [ ] Charging network integration
- [ ] Mobile app
- [ ] Vehicle comparison tool
- [ ] Market analysis tools

---

## Quick Start Checklist

**Before you start coding:**

1. [ ] Decide on image hosting strategy
2. [ ] Choose deployment platform
3. [ ] Set up Node.js environment
4. [ ] Install Hugo extended
5. [ ] Test basic Hugo build

**First week priorities:**

1. [ ] Fix GitHub repository settings
2. [ ] Write CONTRIBUTING.md
3. [ ] Set up Hugo templates
4. [ ] Add 5 vehicles with complete data
5. [ ] Get build working end-to-end

---

## Notes & Decisions

### Image Hosting Decision
**Date**: _____________  
**Decision**: _____________  
**Reasoning**: _____________

### Deployment Platform Decision
**Date**: _____________  
**Decision**: _____________  
**Reasoning**: _____________

### Translation Strategy
**Date**: _____________  
**Decision**: _____________  
**Reasoning**: _____________

---

## Resources

- **Hugo Docs**: https://gohugo.io/documentation/
- **JSON Schema**: https://json-schema.org/
- **WLTP Data**: https://www.car.info/ (Germany)
- **EPA Data**: https://www.fueleconomy.gov/ (USA)
- **Vehicle Images**: https://commons.wikimedia.org/

---

## Progress Tracking

**Last Updated**: 2026-02-06  
**Current Phase**: Phase 0 - Foundation  
**Completion**: 45%

**Next Milestone**: Complete Hugo setup and add first 5 vehicles by 2026-02-13

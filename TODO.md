# EVDB Implementation TODO

**Architecture**: YAML + JSON Schema + Datasette + Streamlit  
**Last Updated**: 2026-02-06

---

## 📋 Current Phase: Foundation & Tooling

---

## Phase 0: Project Foundation (Week 1)

### Repository Structure
- [x] Create base directory structure
- [ ] Set up proper .gitignore
- [ ] Add README.md with architecture overview
- [ ] Create directory structure:
  ```
  data/
    manufacturers/
    vehicle-models/
    vehicle-variants/
    market-availability/
    reference/
      connectors.yaml
      platforms.yaml
  schemas/
    manufacturer.schema.json
    vehicle-model.schema.json
    vehicle-variant.schema.json
    market-availability.schema.json
  scripts/
    validate.py
    build-sqlite.py
    import-yaml.py
  templates/
    manufacturer-template.yaml
    vehicle-model-template.yaml
    vehicle-variant-template.yaml
    market-availability-template.yaml
  docs/
    CONTRIBUTING.md
    DATA_ENTRY_GUIDE.md
    SCHEMA_DESIGN.md (keep as reference)
  ```

### Development Environment
- [ ] Create `requirements.txt` with dependencies:
  - [ ] `pyyaml` - YAML parsing
  - [ ] `jsonschema` - Schema validation
  - [ ] `datasette` - Database exploration
  - [ ] `sqlite-utils` - SQLite manipulation
  - [ ] `streamlit` - Dashboards
  - [ ] `click` - CLI tool building
  - [ ] `pytest` - Testing
- [ ] Create `pyproject.toml` or `setup.py`
- [ ] Set up virtual environment setup instructions
- [ ] Document Python version requirement (3.10+)

### Documentation
- [ ] Write CONTRIBUTING.md
  - [ ] How to add a manufacturer
  - [ ] How to add a vehicle
  - [ ] YAML style guide
  - [ ] Validation workflow
  - [ ] PR process
- [ ] Write DATA_ENTRY_GUIDE.md
  - [ ] Field-by-field explanations
  - [ ] Where to find data (sources)
  - [ ] How to handle unknown values
  - [ ] Data quality indicators
- [ ] Create README.md
  - [ ] Project overview
  - [ ] Architecture diagram
  - [ ] Quick start guide
  - [ ] API documentation

---

## Phase 1: Schema Definition (Week 1-2)

### JSON Schemas
- [ ] Create `schemas/manufacturer.schema.json`
  - [ ] Define all fields from SCHEMA_DESIGN.md
  - [ ] Set required fields: id, name, country
  - [ ] Add enum for countries (ISO 3166-1)
  - [ ] Add validation patterns (URLs, dates)
  
- [ ] Create `schemas/vehicle-model.schema.json`
  - [ ] Base model information
  - [ ] Body style, segment enums
  - [ ] Production dates
  - [ ] Dimensions, seating, cargo
  - [ ] Reference to manufacturer_id
  
- [ ] Create `schemas/vehicle-variant.schema.json` (largest!)
  - [ ] Battery specifications
  - [ ] Range (WLTP, EPA, real-world)
  - [ ] Charging (AC/DC)
  - [ ] Bidirectional charging (V2X)
  - [ ] Performance specs
  - [ ] Weight
  - [ ] Efficiency ratings
  - [ ] Versioning info
  - [ ] Metadata & sources
  
- [ ] Create `schemas/market-availability.schema.json`
  - [ ] Pricing by market
  - [ ] Currency codes (ISO 4217)
  - [ ] Incentives
  - [ ] Market-specific options
  - [ ] Availability dates
  
- [ ] Create reference schemas
  - [ ] `schemas/connector.schema.json`
  - [ ] `schemas/platform.schema.json`

### Enumerations
- [ ] Create `schemas/enums.json` with standardized values:
  - [ ] Body styles
  - [ ] Segments (Euro car segments)
  - [ ] Battery chemistry (NMC, NCA, LFP, LTO, etc.)
  - [ ] Drive types (RWD, FWD, AWD)
  - [ ] Connector types (Type2, CCS2, CHAdeMO, etc.)
  - [ ] Production status (active, discontinued, announced)
  - [ ] Data quality levels (verified, unverified, estimated, partial)
  - [ ] Data sources (manufacturer, measured, calculated, estimated, community)
  - [ ] Countries (ISO 3166-1 alpha-2)
  - [ ] Currencies (ISO 4217)

### Schema Testing
- [ ] Create test fixtures (valid YAML examples)
- [ ] Create test fixtures (invalid YAML for validation)
- [ ] Test all required field validation
- [ ] Test all enum validation
- [ ] Test conditional requirements
- [ ] Test cross-references (foreign keys)

---

## Phase 2: YAML Templates & Reference Data (Week 2)

### Templates
- [ ] Create `templates/manufacturer-template.yaml`
  - [ ] Include all fields with comments
  - [ ] Provide examples for each field
  - [ ] Mark required vs optional
  
- [ ] Create `templates/vehicle-model-template.yaml`
  - [ ] Comprehensive field guide
  - [ ] Common patterns (SUV, sedan, etc.)
  
- [ ] Create `templates/vehicle-variant-template.yaml`
  - [ ] Most detailed template
  - [ ] Include all optional sections
  - [ ] Examples for charge curves, consumption conditions
  
- [ ] Create `templates/market-availability-template.yaml`
  - [ ] Pricing examples
  - [ ] Incentive structures
  - [ ] Market-specific options

### Reference Data
- [ ] Create `data/reference/connectors.yaml`
  - [ ] All common EV connectors
  - [ ] Type1, Type2, CCS1, CCS2, CHAdeMO, GB/T, Tesla NACS
  - [ ] Specifications (max current, voltage, power)
  - [ ] Regional availability
  
- [ ] Create `data/reference/platforms.yaml`
  - [ ] Major EV platforms
  - [ ] MEB (Volkswagen)
  - [ ] E-GMP (Hyundai/Kia)
  - [ ] Ultium (GM)
  - [ ] EVA2 (Mercedes)
  - [ ] MEA (Stellantis)
  
- [ ] Create `data/reference/body-styles.yaml`
  - [ ] Standard body style definitions
  - [ ] Euro segment mappings

---

## Phase 3: Validation Tools (Week 2-3)

### Python Validation Script
- [ ] Create `scripts/validate.py`
  - [ ] Load YAML files
  - [ ] Validate against JSON Schema
  - [ ] Check cross-references (manufacturer_id exists, etc.)
  - [ ] Check for duplicate IDs
  - [ ] Check for required data quality fields
  - [ ] Check date formats
  - [ ] Check URL accessibility (optional)
  - [ ] Output clear error messages
  - [ ] Exit with proper codes for CI
  
- [ ] Add CLI arguments
  - [ ] `--file` - Validate single file
  - [ ] `--directory` - Validate all files in directory
  - [ ] `--schema` - Specify schema file
  - [ ] `--strict` - Enable strict mode (no warnings allowed)
  - [ ] `--fix` - Auto-fix common issues
  
- [ ] Create validation test suite
  - [ ] Test valid files pass
  - [ ] Test invalid files fail with correct errors
  - [ ] Test cross-reference validation
  - [ ] Test enum validation

### Pre-commit Hooks
- [ ] Create `.pre-commit-config.yaml`
  - [ ] YAML syntax check
  - [ ] JSON Schema validation
  - [ ] File naming conventions
  - [ ] No trailing whitespace
  - [ ] Check for merge conflicts
  
- [ ] Document pre-commit setup in CONTRIBUTING.md

---

## Phase 4: Database Build Tools (Week 3-4)

### SQLite Schema Generator
- [ ] Create `scripts/generate-sql-schema.py`
  - [ ] Read JSON schemas
  - [ ] Generate SQLite CREATE TABLE statements
  - [ ] Handle nested structures (normalize to separate tables)
  - [ ] Create indexes on foreign keys
  - [ ] Create full-text search indexes
  - [ ] Output `schema.sql`

### YAML to SQLite Importer
- [ ] Create `scripts/build-sqlite.py`
  - [ ] Load all YAML files
  - [ ] Validate before import
  - [ ] Flatten nested structures
  - [ ] Insert into SQLite database
  - [ ] Handle relationships (foreign keys)
  - [ ] Create `evdb.db`
  - [ ] Generate import statistics
  
- [ ] Handle special cases
  - [ ] Array fields (charging times, range conditions)
  - [ ] Nested objects (motors, optional equipment)
  - [ ] Many-to-many relationships
  
- [ ] Create database views
  - [ ] `view_vehicles_full` - Joined view with all info
  - [ ] `view_vehicles_latest` - Only latest model year
  - [ ] `view_vehicles_available` - Only currently available
  
- [ ] CLI arguments
  - [ ] `--input-dir` - YAML directory
  - [ ] `--output` - SQLite file path
  - [ ] `--clean` - Drop existing database
  - [ ] `--validate` - Validate before import

### Testing
- [ ] Create test dataset (5 manufacturers, 10 vehicles)
- [ ] Test database build
- [ ] Test data integrity (foreign keys)
- [ ] Test full-text search
- [ ] Benchmark import performance

---

## Phase 5: Datasette Configuration (Week 4)

### Datasette Setup
- [ ] Create `metadata.json` for Datasette
  - [ ] Database description
  - [ ] Table descriptions
  - [ ] Column descriptions
  - [ ] License information (CC BY-SA 4.0)
  
- [ ] Configure Datasette features
  - [ ] Enable facets on key fields
    - [ ] Manufacturer
    - [ ] Model year
    - [ ] Body style
    - [ ] Battery chemistry
    - [ ] Drive type
    - [ ] Charging power
  - [ ] Set up full-text search
  - [ ] Configure SQL query templates
  - [ ] Set up canned queries
  
- [ ] Create useful canned queries
  - [ ] "Find vehicles by range"
  - [ ] "Compare charging speeds"
  - [ ] "Find by market availability"
  - [ ] "Latest models by manufacturer"
  - [ ] "Budget EVs under €40k"
  - [ ] "Long-range EVs (>500km)"

### Datasette Plugins
- [ ] Install useful plugins:
  - [ ] `datasette-cluster-map` - Map visualization
  - [ ] `datasette-vega` - Charts
  - [ ] `datasette-export-notebook` - Jupyter exports
  - [ ] `datasette-graphql` - GraphQL API
  - [ ] `datasette-configure-fts` - Full-text search UI
  
- [ ] Configure plugins in `metadata.json`

### API Documentation
- [ ] Document API endpoints
  - [ ] `/manufacturers.json`
  - [ ] `/vehicle-models.json`
  - [ ] `/vehicle-variants.json`
  - [ ] `/market-availability.json`
- [ ] Document query parameters
- [ ] Provide usage examples (curl, Python, JavaScript)

---

## Phase 6: Initial Data Entry (Week 4-5)

### Manufacturers
- [ ] Create 10 major EV manufacturers:
  - [ ] Tesla
  - [ ] Volkswagen Group
  - [ ] BMW Group
  - [ ] Mercedes-Benz
  - [ ] BYD
  - [ ] Hyundai Motor Group
  - [ ] General Motors
  - [ ] Ford
  - [ ] Stellantis
  - [ ] Nissan

### Vehicle Models (Base)
- [ ] Create 20 popular vehicle models
  - [ ] Tesla Model 3
  - [ ] Tesla Model Y
  - [ ] Volkswagen ID.4
  - [ ] Volkswagen ID.3
  - [ ] BMW iX
  - [ ] BMW i4
  - [ ] Mercedes EQS
  - [ ] Mercedes EQE
  - [ ] BYD Atto 3
  - [ ] Hyundai Ioniq 5
  - [ ] Hyundai Ioniq 6
  - [ ] Kia EV6
  - [ ] Ford Mustang Mach-E
  - [ ] Ford F-150 Lightning
  - [ ] Nissan Ariya
  - [ ] Audi e-tron / Q8 e-tron
  - [ ] Polestar 2
  - [ ] MG4 Electric
  - [ ] Renault Megane E-Tech
  - [ ] Volvo XC40 Recharge

### Vehicle Variants (Detailed)
- [ ] For each model, create at least 2 variants
  - [ ] Base/standard variant
  - [ ] Long-range or performance variant
  - [ ] Include full specifications (battery, range, charging, performance)
  - [ ] Add real-world range data
  - [ ] Add charging curves if available
  
- [ ] Prioritize 2024 model year data
- [ ] Mark data quality for each field
- [ ] Include source URLs

### Market Availability
- [ ] Add market data for key regions
  - [ ] Germany (DE)
  - [ ] Poland (PL)
  - [ ] France (FR)
  - [ ] United Kingdom (GB)
  - [ ] United States (US)
  - [ ] Norway (NO)
  
- [ ] Include pricing
- [ ] Include available incentives
- [ ] Mark availability status

### Data Quality
- [ ] Verify all specs against official sources
- [ ] Add source URLs to metadata
- [ ] Use consistent units (km, kWh, kW)
- [ ] Mark estimated values appropriately
- [ ] Add notes for special cases

---

## Phase 7: CI/CD Pipeline (Week 5)

### GitHub Actions
- [ ] Create `.github/workflows/validate.yml`
  - [ ] Trigger on: push, pull_request
  - [ ] Install Python dependencies
  - [ ] Run YAML validation
  - [ ] Run JSON Schema validation
  - [ ] Check for duplicate IDs
  - [ ] Report validation errors
  
- [ ] Create `.github/workflows/build.yml`
  - [ ] Trigger on: push to main
  - [ ] Build SQLite database
  - [ ] Run database tests
  - [ ] Upload as artifact
  
- [ ] Create `.github/workflows/deploy.yml`
  - [ ] Deploy Datasette to hosting
  - [ ] Options:
    - Vercel (datasette-publish-vercel)
    - Fly.io (datasette-publish-fly)
    - Cloudflare Pages
  - [ ] Automatic deployment on main branch
  
- [ ] Create `.github/workflows/pr-preview.yml`
  - [ ] Build preview database for PRs
  - [ ] Comment on PR with preview link

### Testing in CI
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Test database build
- [ ] Test Datasette startup
- [ ] Check for broken links in docs

---

## Phase 8: Streamlit Dashboard (Week 6)

### Dashboard Setup
- [ ] Create `streamlit/` directory
- [ ] Create `streamlit/app.py` (main dashboard)
- [ ] Create `streamlit/requirements.txt`

### Dashboard Features
- [ ] **Home Page**
  - [ ] Overview statistics
  - [ ] Latest additions
  - [ ] Data quality metrics
  
- [ ] **Vehicle Comparison**
  - [ ] Multi-select vehicles
  - [ ] Side-by-side comparison table
  - [ ] Radar chart (range, charging, performance)
  - [ ] Export comparison as PDF/CSV
  
- [ ] **Range Analysis**
  - [ ] Scatter plot: battery size vs. range
  - [ ] Filter by manufacturer, body style
  - [ ] Efficiency ranking
  
- [ ] **Charging Speed Comparison**
  - [ ] Chart: charging power vs. charge time
  - [ ] Show charge curves
  - [ ] km/hour charging speed
  
- [ ] **Market Overview**
  - [ ] Vehicles by market
  - [ ] Price distribution
  - [ ] Available incentives
  
- [ ] **Database Explorer**
  - [ ] Raw SQL query interface
  - [ ] Export results to CSV

### Deployment
- [ ] Deploy to Streamlit Cloud
- [ ] Connect to SQLite database
- [ ] Set up automatic updates (daily rebuild)

---

## Phase 9: Documentation & Community (Week 6-7)

### User Documentation
- [ ] Write comprehensive README.md
  - [ ] What is EVDB
  - [ ] How to use the database
  - [ ] API examples
  - [ ] Contributing guide link
  
- [ ] Create CONTRIBUTING.md
  - [ ] Code of conduct
  - [ ] How to add data
  - [ ] YAML style guide
  - [ ] PR process
  - [ ] Review checklist
  
- [ ] Create DATA_ENTRY_GUIDE.md
  - [ ] Field-by-field guide
  - [ ] Where to find data
  - [ ] Data quality standards
  - [ ] Common pitfalls
  
- [ ] Create API_DOCUMENTATION.md
  - [ ] All endpoints
  - [ ] Query parameters
  - [ ] Response formats
  - [ ] Rate limits (if any)
  - [ ] Examples in multiple languages

### Developer Documentation
- [ ] Architecture overview
- [ ] Schema documentation
- [ ] Validation rules
- [ ] Database structure
- [ ] Build process
- [ ] Deployment guide

### Issue Templates
- [ ] Bug report template
- [ ] New vehicle request template
- [ ] Feature request template
- [ ] Data correction template

### PR Template
- [ ] Checklist for contributors
- [ ] Link to relevant issue
- [ ] Data quality verification
- [ ] Source attribution

---

## Phase 10: Launch & Growth (Week 7+)

### Pre-Launch Checklist
- [ ] Verify all systems working
- [ ] Test API endpoints
- [ ] Test Datasette deployment
- [ ] Test Streamlit dashboard
- [ ] Proofread all documentation
- [ ] Verify all links work
- [ ] Check mobile responsiveness

### Launch
- [ ] Announce on relevant forums
  - [ ] r/electricvehicles
  - [ ] EV forums
  - [ ] Hacker News
  - [ ] Product Hunt
- [ ] Share on social media
- [ ] Reach out to EV bloggers
- [ ] Create launch blog post

### Community Building
- [ ] Set up GitHub Discussions
- [ ] Create Discord server (optional)
- [ ] Monitor issues and PRs
- [ ] Respond to community feedback
- [ ] Encourage contributions

### Data Expansion
- [ ] Add 50+ more vehicles
- [ ] Expand to more markets
- [ ] Add historical models (2020-2023)
- [ ] Add upcoming models (announced)
- [ ] User-submitted real-world data

### Future Enhancements
- [ ] GraphQL API
- [ ] User accounts & contributions
- [ ] Real-world range data collection
- [ ] Charging network integration
- [ ] Mobile app
- [ ] Advanced comparison tools
- [ ] Market analysis dashboards
- [ ] Price tracking over time

---

## Quick Start (Next 48 Hours)

### Immediate Actions
1. [ ] Set up project structure (directories)
2. [ ] Create requirements.txt
3. [ ] Install development environment
4. [ ] Create first JSON schema (manufacturer)
5. [ ] Create first YAML template
6. [ ] Create basic validation script
7. [ ] Test validation with example file

### First Week Goals
1. [ ] Complete all 5 JSON schemas
2. [ ] Create all YAML templates
3. [ ] Working validation script
4. [ ] Add 3 manufacturers
5. [ ] Add 5 vehicles with full data
6. [ ] Test database build

---

## Decision Log

### Tool Choices

**Decision**: Use Datasette for API/exploration
**Date**: 2026-02-06  
**Reasoning**: Simple, powerful, built-in API, great for exploration

**Decision**: Use Streamlit for dashboards
**Date**: 2026-02-06  
**Reasoning**: Python-native, quick to build, easy to deploy

**Decision**: Use SQLite as data store
**Date**: 2026-02-06  
**Reasoning**: Single file, portable, fast, perfect for Datasette

**Decision**: Use YAML for source data
**Date**: 2026-02-06  
**Reasoning**: Human-readable, git-friendly, supports comments

**Decision**: Use JSON Schema for validation
**Date**: 2026-02-06  
**Reasoning**: Industry standard, extensive tooling, clear error messages

---

## Resources

- **YAML Spec**: https://yaml.org/spec/1.2/spec.html
- **JSON Schema**: https://json-schema.org/
- **Datasette**: https://datasette.io/
- **Streamlit**: https://streamlit.io/
- **SQLite**: https://www.sqlite.org/
- **sqlite-utils**: https://sqlite-utils.datasette.io/

### Data Sources
- **WLTP Data**: https://www.car.info/ (Germany)
- **EPA Data**: https://www.fueleconomy.gov/ (USA)
- **Manufacturer Specs**: Official websites
- **Community Data**: ev-database.org, InsideEVs, etc.

---

## Progress Tracking

**Current Phase**: Phase 0 - Foundation  
**Progress**: 10%  
**Next Milestone**: Complete JSON schemas by 2026-02-08  
**Target Launch**: 2026-03-15

---

## Notes

This architecture provides:
- ✅ **Git-friendly**: YAML source files, easy diffs
- ✅ **Validation**: JSON Schema ensures data quality
- ✅ **Queryable**: Datasette provides SQL interface
- ✅ **Visualizable**: Streamlit dashboards
- ✅ **Extensible**: Easy to add new fields/vehicles
- ✅ **API**: Built-in via Datasette
- ✅ **Open**: CC BY-SA 4.0 license

**Advantages over Hugo approach:**
1. Proper relational structure (not just flat JSON)
2. Advanced querying (SQL vs. limited Hugo queries)
3. Better for data analysis (Streamlit integration)
4. Easier to validate (JSON Schema)
5. Cleaner separation (YAML source → SQLite → API)

# EVDB Implementation Roadmap

## Quick Summary

This roadmap addresses the feedback to enhance EVDB with:
1. ✅ Country-level market availability (not just continents)
2. ✅ Standardized enums with flexibility for future additions
3. ✅ Multiple photos/illustrations per vehicle
4. ✅ Multi-language support

All schema definitions, examples, and validation tools are now ready!

## What We've Created

### 📄 Schema Files

1. **`api/v1/schema/vehicle.json`** - Complete vehicle schema with:
   - Country-level market availability with status tracking
   - All technical specifications (battery, range, performance, charging)
   - Multiple images with metadata
   - Pricing by market with currency support
   - Production information
   - All fields properly typed and documented

2. **`api/v1/schema/enums.json`** - Standardized enumerations:
   - Battery chemistry (LFP, NMC, NCA, LTO, SODIUM_ION, SOLID_STATE, OTHER)
   - Drivetrain types (FWD, RWD, AWD, 4WD)
   - Body types (13 categories + OTHER)
   - Charging standards (CCS1/2, CHAdeMO, Tesla NACS, GB/T, etc.)
   - DC speed classes (NONE through HYPER_FAST)
   - Market status (available, discontinued, announced)
   - Image types (exterior, interior, technical, press, render, user)
   - Each enum includes descriptions and use cases

### 📝 Documentation

1. **`docs/ENHANCEMENTS.md`** - Complete enhancement plan with:
   - Detailed breakdown of all improvements
   - Implementation examples
   - 5-phase rollout plan
   - Backward compatibility strategy
   - Future considerations

2. **`docs/INTERNATIONALIZATION.md`** - Multi-language implementation guide:
   - Hugo i18n configuration
   - Directory structure
   - Translation workflow
   - Best practices for what to translate vs. what to keep universal
   - Maintenance strategies

3. **`docs/IMPLEMENTATION_ROADMAP.md`** (this file)

### 🔧 Tools

1. **`scripts/validate.js`** - Data validation script that checks:
   - Required and recommended fields
   - Enum compliance
   - Data consistency (e.g., DC speed class matches actual power)
   - Logical errors (usable capacity > gross capacity)
   - Country code format
   - Image references
   - Missing translations
   - Outputs clear errors and warnings

### 📋 Examples

1. **`content/vehicles/opel-mokka-e-enhanced-example.md`** - Full example showing:
   - Market availability in 6 countries (DE, PL, FR, GB, NL, NO)
   - Complete battery specs with NMC chemistry
   - Standardized charging ports (TYPE2, CCS2)
   - DC speed class (FAST for 100kW)
   - Pricing in EUR, PLN, NOK with incentives
   - 6 images with different types and metadata
   - Production information
   - Translated content sections

## Implementation Phases

### ✅ Phase 0: Planning & Schema Design (COMPLETE)
- [x] Create comprehensive schema files
- [x] Define all enumerations
- [x] Write implementation documentation
- [x] Create validation tools
- [x] Build working examples

### Phase 1: Core Infrastructure (2-3 weeks)

#### Week 1: Schema Integration
- [ ] Update Hugo templates to support new schema fields
- [ ] Create partials for each data section (battery, charging, etc.)
- [ ] Add JSON output support for all new fields
- [ ] Set up CI/CD to run validation on PRs

#### Week 2: Data Migration
- [ ] Audit existing vehicle entries
- [ ] Migrate simple fields (body → body_type enum)
- [ ] Add country-level market data for top 50 vehicles
- [ ] Backfill missing recommended fields where data is available

#### Week 3: Validation & Testing
- [ ] Run validation script on all content
- [ ] Fix all errors and critical warnings
- [ ] Create contribution guidelines with validation instructions
- [ ] Set up pre-commit hooks

**Deliverables:**
- All existing vehicles validated against new schema
- CI pipeline with automated validation
- Updated contribution guide

### Phase 2: Enhanced Content (3-4 weeks)

#### Week 4-5: Image Infrastructure
- [ ] Set up image storage/hosting solution
- [ ] Create image upload workflow
- [ ] Implement image optimization pipeline (WebP, responsive sizes)
- [ ] Add gallery layouts to vehicle pages
- [ ] Create image submission guidelines

#### Week 6-7: Data Enrichment
- [ ] Add market availability data for all vehicles
- [ ] Collect and add multiple images per vehicle (start with top 50)
- [ ] Enrich battery specifications with chemistry data
- [ ] Add pricing information for major markets
- [ ] Source technical diagrams and illustrations

**Deliverables:**
- Image management system
- Top 50 vehicles with multiple photos
- Market availability tracking for all vehicles
- Enhanced technical specifications

### Phase 3: Internationalization (4-5 weeks)

#### Week 8-9: i18n Setup
- [ ] Configure Hugo for multiple languages
- [ ] Create directory structure for en/de/pl/fr
- [ ] Set up translation files (i18n/*.toml)
- [ ] Update templates with i18n support
- [ ] Add language switcher to UI
- [ ] Configure URL structure

#### Week 10-11: Content Translation
- [ ] Translate UI elements to DE, PL, FR
- [ ] Translate top 25 vehicles to German
- [ ] Translate top 25 vehicles to Polish
- [ ] Translate manufacturer pages
- [ ] Create translation contribution workflow

#### Week 12: Quality Assurance
- [ ] Review all translations with native speakers
- [ ] Test language switching
- [ ] Verify API outputs include language info
- [ ] Document translation workflow
- [ ] Create "translation needed" tracking

**Deliverables:**
- Full i18n support (4 languages)
- Top 25 vehicles translated to DE and PL
- Translation workflow documentation
- Language switcher UI

### Phase 4: API Enhancement (2-3 weeks)

#### Week 13-14: API v2
- [ ] Design API v2 with all new fields
- [ ] Add filtering capabilities (by market, chemistry, charging, etc.)
- [ ] Implement search with multiple criteria
- [ ] Create OpenAPI/Swagger documentation
- [ ] Add GraphQL endpoint (optional)

#### Week 15: Testing & Documentation
- [ ] API integration tests
- [ ] Performance testing and optimization
- [ ] Create API usage examples
- [ ] Write API documentation
- [ ] Announce API v2

**Deliverables:**
- API v2 with enhanced filtering
- OpenAPI documentation
- Usage examples and guides

### Phase 5: Community & Growth (Ongoing)

- [ ] Launch community contribution program
- [ ] Create contribution incentives (badges, leaderboard)
- [ ] Partner with EV manufacturers for official data
- [ ] Integrate with charging network databases
- [ ] Add user-generated content (reviews, real-world range)
- [ ] Mobile app development
- [ ] Translation crowdsourcing platform

## Quick Start for Developers

### 1. Validate Existing Content

```bash
cd /Users/suda/Projects/Personal/Node/evdb
npm install js-yaml  # If not already installed
chmod +x scripts/validate.js
./scripts/validate.js
```

### 2. Create New Vehicle Entry

```bash
# Copy the enhanced example
cp content/vehicles/opel-mokka-e-enhanced-example.md content/vehicles/your-vehicle.md

# Edit with your vehicle data
# Follow the schema in api/v1/schema/vehicle.json
# Use enums from api/v1/schema/enums.json

# Validate
./scripts/validate.js
```

### 3. Set Up Internationalization

```bash
# Update config.toml with language configuration (see docs/INTERNATIONALIZATION.md)
# Create language directories
mkdir -p content/{en,de,pl,fr}/vehicles
mkdir -p content/{en,de,pl,fr}/manufacturers

# Create i18n translation files
mkdir -p i18n
# Copy templates from docs/INTERNATIONALIZATION.md
```

## Key Decisions

### ✅ What We Got Right

1. **Country-level granularity** - Markets vary significantly even within continents
2. **Extensible enums** - "OTHER" + custom field pattern allows future flexibility
3. **Structured images** - Metadata and types support professional presentation
4. **Hugo i18n** - Native support, no external dependencies
5. **Validation-first** - Automated checks prevent data quality issues
6. **Separation of concerns** - Technical specs universal, descriptions translated

### 🎯 Trade-offs & Considerations

1. **Schema complexity** - More fields = more work, but better data quality
2. **Translation overhead** - Maintaining 4+ languages requires commitment
3. **Image hosting** - Need storage solution and optimization pipeline
4. **API versioning** - Breaking changes require v2, maintain both during transition
5. **Data entry barrier** - Rich schema might deter casual contributors (provide tools/templates)

## Success Metrics

### Phase 1-2 (Infrastructure & Content)
- ✅ 100% of vehicles pass validation
- ✅ Top 50 vehicles have ≥3 images each
- ✅ All vehicles have market availability data
- ✅ Zero CI failures on data validation

### Phase 3 (Internationalization)
- ✅ 4 languages supported (en, de, pl, fr)
- ✅ 50+ vehicles translated to German
- ✅ 50+ vehicles translated to Polish
- ✅ < 5% broken language switches

### Phase 4-5 (API & Community)
- ✅ API v2 with 10+ filter options
- ✅ 100+ vehicles in database
- ✅ 5+ community contributors per month
- ✅ 1000+ API calls per day

## Resources Needed

### Development
- **Time**: ~15 weeks for Phases 1-4 (1 developer part-time)
- **Skills**: Hugo, JavaScript/Node.js, YAML, JSON Schema, i18n

### Content
- **Images**: Storage solution (S3, Cloudinary, or similar)
- **Data**: Research time or API access to manufacturer data
- **Translation**: Native speakers for DE, PL, FR (or budget for professional translation)

### Infrastructure
- **CI/CD**: GitHub Actions (free tier likely sufficient)
- **Hosting**: Static hosting (Netlify, Vercel, GitHub Pages)
- **API**: Serverless functions or simple Node.js app

## Next Steps

### Immediate (This Week)
1. ✅ Review this roadmap
2. ✅ Validate the schema and examples
3. ⏭️ Decide on Phase 1 timeline
4. ⏭️ Set up project board for task tracking

### Short-term (Next 2 Weeks)
1. ⏭️ Update Hugo templates for new schema
2. ⏭️ Integrate validation script into CI
3. ⏭️ Start migrating existing vehicles

### Medium-term (Next Month)
1. ⏭️ Complete Phase 1
2. ⏭️ Begin image infrastructure work
3. ⏭️ Start data enrichment for top vehicles

## Questions to Resolve

1. **Image hosting**: Where should we store images? (S3, Cloudinary, GitHub LFS, other?)
2. **Translation priority**: Which vehicles should be translated first?
3. **API v1 → v2**: Breaking changes or maintain v1 alongside v2?
4. **Community platform**: GitHub Discussions, Discord, or dedicated forum?
5. **Data sources**: Which APIs/websites are acceptable sources for data?

## Conclusion

All the groundwork is done! We have:
- ✅ Complete, extensible schema
- ✅ Standardized enums with room to grow
- ✅ Multi-image support with rich metadata
- ✅ Full internationalization blueprint
- ✅ Validation tooling
- ✅ Working examples

The database is ready to scale from a simple catalog to a comprehensive, multi-language EV resource. The modular design means you can implement phases gradually without blocking progress.

**Ready to build?** Start with Phase 1, Week 1. 🚀

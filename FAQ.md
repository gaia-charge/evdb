# EVDB Frequently Asked Questions

**Last Updated**: 2026-02-07 (Pre-launch template)

---

## General Questions

### What is EVDB?

EVDB (Electric Vehicle Database) is an open-source database of electric vehicles with detailed specifications, market data, and a free public API. It's built for developers, researchers, EV enthusiasts, and anyone who needs comprehensive, structured EV data.

### Why create another EV database?

Existing EV databases are often:
- **Behind paywalls** or have limited free tiers
- **Incomplete** or out of date
- **Not open source** - can't verify or contribute
- **Missing real-world data** - just manufacturer claims

EVDB is completely open, community-driven, and focused on data quality with source tracking.

### Is it really free?

Yes! EVDB is licensed under CC BY-SA 4.0:
- ✅ Free to use commercially
- ✅ Free to modify and build upon
- ✅ Free API access (no rate limits currently)
- ✅ Free to download all data

The only requirement: attribute EVDB and share derivative data under the same license.

### How is this project funded?

Currently self-funded. Future sustainability options being considered:
- Voluntary donations/sponsorships
- "Pro" tier with enhanced features (core data always free)
- Grants from EV/sustainability organizations
- Community support

---

## Data Questions

### How many vehicles are in the database?

Currently **51 vehicle variants** across **37 models** from **19 manufacturers** in **5 markets** (Germany, USA, France, Poland, Italy).

Coverage will expand through community contributions after launch.

### How accurate is the data?

Every data field includes:
- **Source** (official specs, third-party tests, community input)
- **Confidence level** (high, medium, low)
- **Last verified date**

Data from official manufacturer sources is marked as high confidence. Third-party tests and community data are appropriately marked.

### What data is included for each vehicle?

**Vehicle Variant (Trim) Level**:
- Battery capacity (usable/gross)
- Range (WLTP, EPA, real-world)
- Charging speed (AC/DC max, 10-80% time, charging curve)
- Performance (0-100 km/h, top speed, power, torque)
- Efficiency (kWh/100km, Wh/km)
- Dimensions, weight, drag coefficient
- Drive configuration (RWD, AWD, motors)
- Battery chemistry and supplier

**Market Availability**:
- Base price and on-the-road price
- Available colors, wheels, interiors
- Optional packages and pricing
- Delivery times
- Government incentives
- Insurance costs
- Popular configurations

### How often is data updated?

- **Validation**: Every PR (automated)
- **Database builds**: Every push to main branch (automated)
- **New vehicles**: Community-driven (ongoing)
- **Price updates**: As market changes (contributors monitor)

All changes are tracked in git with full history.

### What markets are covered?

Currently:
- 🇩🇪 **Germany** (25 vehicles) - Primary focus
- 🇺🇸 **USA** (6 vehicles)
- 🇫🇷 **France** (1 vehicle)
- 🇵🇱 **Poland** (1 vehicle)
- 🇮🇹 **Italy** (1 vehicle)

Expansion planned for:
- 🇬🇧 UK
- 🇳🇴 Norway
- 🇳🇱 Netherlands
- 🇨🇳 China
- 🇨🇦 Canada

### Why is [my favorite EV] missing?

We're still building coverage! Current focus:
1. **German market** (most comprehensive data available)
2. **Popular models** (high sales volume)
3. **Diverse segments** (luxury, budget, trucks, sedans)

**Help us add it!** See [CONTRIBUTING.md](CONTRIBUTING.md) for a step-by-step guide. Adding a vehicle takes ~30 minutes.

### I found incorrect data. How do I report it?

1. **GitHub Issue**: Open an issue with details and sources
2. **Pull Request**: Even better - fix it yourself! See CONTRIBUTING.md
3. **Email**: [contact info] for sensitive issues

Please include:
- Which vehicle and field
- What's wrong
- Correct value with source link

---

## Technical Questions

### What's the API rate limit?

Currently **no rate limits** during initial launch. Fair use policy applies:
- Don't abuse the service
- Cache responses when possible
- Be reasonable with request frequency

If usage grows significantly, we may introduce generous free tier limits (e.g., 10k requests/day) with options for higher limits.

### What API formats are supported?

- **REST JSON**: Primary format
- **REST CSV**: For spreadsheet exports
- **GraphQL**: Full GraphQL API endpoint
- **SQL**: Direct queries via Datasette UI

See [API_DOCS.md](API_DOCS.md) for examples in curl, Python, and JavaScript.

### Can I download the entire database?

Yes! Multiple options:

1. **SQLite file**: Download `evdb.db` from GitHub releases or API
2. **CSV export**: Export any table via Datasette
3. **JSON export**: Query entire tables as JSON
4. **YAML source**: Clone the GitHub repo
5. **Jupyter notebook**: Export queries as notebooks

### How do I use the API in my app?

See [API_DOCS.md](API_DOCS.md) for comprehensive examples:

```bash
# Find EVs with 500+ km range
curl "https://evdb-xxx.vercel.app/evdb/find_by_range.json?min_range=500"

# Get specific vehicle
curl "https://evdb-xxx.vercel.app/evdb/vehicle_variants/tesla-model-3-long-range-awd-2024.json"

# Compare vehicles
curl "https://evdb-xxx.vercel.app/evdb/compare_vehicles.json?ids=tesla-model-3-long-range-awd-2024,bmw-i4-edrive40-2024"
```

Python and JavaScript examples also provided.

### Can I self-host the database?

Absolutely! It's just a SQLite file:

```bash
# Clone repo
git clone https://github.com/yourusername/evdb.git
cd evdb

# Build database
python scripts/build-sqlite.py

# Run Datasette locally
datasette evdb.db --metadata metadata.json
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options (Vercel, Fly.io, or self-hosted).

### What's the database schema?

Four main tables with relationships:
- **manufacturers** (company info)
- **vehicle_models** (base model info)
- **vehicle_variants** (specific trims with full specs)
- **market_availability** (pricing by region)

Plus reference data:
- **connectors** (charging port types)
- **platforms** (EV platforms/architectures)

Full schema documented in [SCHEMA_DESIGN.md](SCHEMA_DESIGN.md).

---

## Contributing Questions

### How can I contribute?

Many ways to help:

1. **Add vehicles**: See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step guide
2. **Update data**: Fix incorrect or outdated info
3. **Improve documentation**: Clarify guides, add examples
4. **Report issues**: Found a bug or have a suggestion?
5. **Build projects**: Create apps using the API and share them!
6. **Spread the word**: Help others discover EVDB

### Do I need to know programming to contribute data?

No! Adding vehicle data just requires:
- Basic YAML syntax (like indented key: value pairs)
- Finding specs online (manufacturer sites, reviews)
- Copy-paste from templates

See [CONTRIBUTING.md](CONTRIBUTING.md) for guided walkthrough with examples.

### How long does it take to add a vehicle?

Typically **20-40 minutes** depending on data availability:
- 5-10 min: Find official specs
- 5-10 min: Fill in YAML files (4 files: manufacturer, model, variant, market)
- 5 min: Validate locally
- 5-10 min: Test and submit PR

Faster for additional variants of existing models (reuse manufacturer/model files).

### What if I only have partial data?

That's okay! Partial data is better than no data:
- Use `null` for unknown fields
- Mark confidence as "low" for uncertain values
- Add comments with `# Note: ...` explaining gaps
- Others can fill in missing data later

All fields are optional except core identifiers (id, name, year).

### Will my contributions be credited?

Yes! Contributors are recognized in:
- **Git commit history** (your GitHub profile linked)
- **CONTRIBUTORS.md** (listed with contributions)
- **Release notes** (mentioned in changes)
- **GitHub PR comments** (public thanks)

### Can I contribute data from paid sources?

**Only if licensed for sharing**. Do not copy data from:
- ❌ Paid databases (EV-Database.org paid tier, etc.)
- ❌ Copyrighted reviews (unless explicitly allowed)
- ❌ Proprietary manufacturer data (dealer-only info)

**Acceptable sources**:
- ✅ Official manufacturer websites (public specs)
- ✅ Press releases and media kits
- ✅ Government testing (EPA, WLTP)
- ✅ Your own testing/measurements
- ✅ Community-shared data with permission

When in doubt, ask before contributing.

---

## Project Questions

### Who maintains EVDB?

Currently maintained by [Your Name/Organization]. Seeking active co-maintainers from the community to help with:
- Data quality reviews
- PR approvals
- Issue triage
- Feature development

Interested? Open an issue or reach out!

### What's the long-term roadmap?

**Phase 1 (Now)**: Core database + API launch

**Phase 2 (Months 1-3)**: 
- Expand coverage (100+ vehicles, 10+ markets)
- Community growth
- Quality improvements

**Phase 3 (Months 4-6)**:
- Real-world range data collection
- Charging network integration
- Historical price tracking
- Streamlit comparison dashboards

**Phase 4 (Months 7-12)**:
- Mobile app (if demand exists)
- Advanced analytics
- Partnerships with EV organizations
- Sustainability features

Community feedback will shape priorities!

### Can I use EVDB data in my commercial product?

**Yes!** Under CC BY-SA 4.0 license you can:
- ✅ Use in commercial apps/services
- ✅ Modify and extend the data
- ✅ Charge for your product

**Requirements**:
- ✅ Attribute EVDB (include link + license)
- ✅ Share derivative data under same license
- ✅ Don't imply EVDB endorses your product

Example attribution:
> "Vehicle data from EVDB (evdb.org), licensed under CC BY-SA 4.0"

### How can I support the project?

- **Contribute data**: Add vehicles, update prices, fix errors
- **Spread the word**: Share with EV communities, developers, researchers
- **Build with it**: Create apps/tools using the API
- **Provide feedback**: Suggest improvements, report issues
- **Sponsor** (future): Funding model TBD based on costs/needs

The best support is active use and contribution!

---

## Troubleshooting

### API returns empty results

Check:
- URL syntax (see API_DOCS.md for examples)
- Parameter spelling (case-sensitive)
- Value ranges (e.g., `min_range=500` not `min_range=500km`)

Example:
```bash
# ❌ Wrong
curl "https://evdb-xxx.vercel.app/evdb/find_by_range?range=500"

# ✅ Correct
curl "https://evdb-xxx.vercel.app/evdb/find_by_range.json?min_range=500"
```

### YAML validation fails locally

Common issues:
- **Indentation**: YAML uses spaces (2 or 4), not tabs
- **Missing colons**: `battery_usable_kwh: 75` (colon + space)
- **Quotes**: Use for strings with special chars (`description: "5-door SUV"`)
- **Lists**: Proper dash + space formatting

Run validation:
```bash
python scripts/validate.py --directory data
```

Detailed errors show file, line, and issue.

### Pull request validation failing

Check GitHub Actions output:
1. Click "Details" next to failed check
2. Read error message
3. Fix issue locally
4. Push update to same PR branch

Common PR issues:
- YAML syntax errors
- Invalid enum values
- Missing required fields
- Foreign key violations (referencing non-existent IDs)

### Can't find vehicle in API

Possible reasons:
- Not added yet (contribute it!)
- Different naming (check vehicle_variants table)
- Market-specific (check market_availability filters)

Search all vehicles:
```bash
curl "https://evdb-xxx.vercel.app/evdb/vehicle_variants.json?_search=tesla"
```

---

## Contact & Support

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Q&A, ideas, show & tell (coming soon)
- **Email**: [contact email] (for private inquiries)
- **Twitter/X**: [@handle] (updates and announcements)

**Response Times**:
- Critical bugs: < 24 hours
- General issues: 1-3 days
- Feature requests: Added to roadmap, discussed in community

---

*This FAQ will be updated regularly based on community questions. Don't see your question? Open a GitHub issue!*

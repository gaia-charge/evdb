# EVDB Cron Instructions

**Updated:** 2026-02-26
**Scope:** instructions for the scheduled data-fill agent. Policy for how
data gets verified lives in [VERIFICATION.md](VERIFICATION.md) — read it.

---

## 🎯 CURRENT PRIORITY: NL, FR & IT Market Expansion

**Focus:** Add missing market-availability files for NL, FR, and IT markets.

### How to find what's missing

```bash
# Variants with DE market but no NL/FR/IT market
for CC in nl fr it; do
  echo "=== Missing $CC ==="
  comm -23 \
    <(ls data/market-availability/*-de.yaml | sed 's/-de\.yaml//' | sed 's|.*/||' | sort) \
    <(ls data/market-availability/*-$CC.yaml | sed "s/-$CC\.yaml//" | sed 's|.*/||' | sort) | head -20
done
```

### Per session workflow

1. Pick 3-5 variants missing NL, FR, or IT market files
2. **Prioritize transparent-pricing brands first:** Renault, Peugeot,
   Citroën, Volkswagen, Škoda, SEAT/Cupra, Fiat, Opel, Hyundai, Kia, MG,
   BYD, Dacia
3. **Deprioritize configurator-only brands:** BMW, Audi, Mercedes — their
   sites hide prices behind JS configurators. Use automotive press (see
   sources) instead of manufacturer sites for these.
4. Create market-availability YAML files (format below)
5. Validate: `python scripts/validate.py --directory data --check-duplicates`
   — this now also runs referential-integrity, duplicate, plausibility, and
   cross-market spread checks. Fix what it reports.
6. Commit to the daily branch `data-fill/YYYY-MM-DD`, push, **open a pull
   request** — never commit to `main`. The verification workflow reviews
   the PR (see VERIFICATION.md); only confirmed records merge.

### Market-availability file format

File name is `<variant-id>-<market>.yaml` (market lowercase) and must equal
the `id` field. This is the actual schema — the required fields are `id`,
`variant_id`, `market`, `currency`:

```yaml
id: renault-5-e-tech-52-techno-2025-nl
variant_id: renault-5-e-tech-52-techno-2025
market: NL              # uppercase ISO code: NL / FR / IT
currency: EUR
availability_status: available   # available | pre-order | limited | discontinued | announced
available_from: "2025-03"

pricing:
  base_price: 31990
  price_including_vat: 31990
  vat_rate_percent: 21  # NL 21, FR 20, IT 22

incentives: []          # only real incentives; type must be one of:
                        # rebate | tax_credit | grant | subsidy | tax_exemption | discount

notes: >
  Local trim name and anything market-specific.

metadata:
  data_quality: unverified   # NEVER claim verified - the verifier assigns that
  price_checked_at: "2026-02-26"
  created_at: "2026-02-26"
  created_by: Ada
  sources:
    - https://www.renault.nl/elektrische-autos/r5/prijzen.html
```

**Metadata rules (schema-enforced):**
- allowed keys: `created_at`, `updated_at`, `data_quality`,
  `price_checked_at`, `last_verified_at`, `sources`, `notes`,
  `data_source`, `created_by`, `verified_by` — anything else fails
  validation
- `sources` must be deep links to the exact price/spec page, not homepages
- `data_quality: verified` without sources fails validation; and per
  VERIFICATION.md you must not set `verified` at all — use `unverified`
  or `estimated`

### Sources

**Acceptable sources (in priority order):**
1. Official manufacturer websites (.nl, .fr, .it)
2. Reputable automotive pricing/press sites:
   - **NL:** AutoWeek.nl, Autovisie.nl, Elektrischeauto.nl
   - **FR:** L'Argus (largus.fr), Turbo.fr, Automobile Magazine
   - **IT:** Quattroruote.it, AutoScout24.it, alVolante.it, Motor1.com IT
3. Manufacturer press releases (media.manufacturer.xx)
4. Wikipedia (for availability confirmation only)

**If a manufacturer site fails** (common with BMW, Audi, Mercedes JS-heavy
configurators), use the automotive pricing sites above — they pull from
official price lists.

**Never use ev-database.org** — its licensing is incompatible with this
database. (Historical records citing it are being re-sourced; do not add
new citations.)

### Trim mapping across markets

When a DE variant's trim name doesn't exist in NL/FR/IT, **map by specs**
(battery capacity, motor power, drivetrain), not by name:

1. Battery capacity must match within ~1 kWh
2. Motor power and drivetrain (RWD/AWD) must match
3. Note the local trim name in `notes`
4. If specs genuinely differ, do NOT map — skip it

The verifier re-checks trim mappings on specs; a wrong mapping blocks the
whole PR.

### Market-specific notes

**Netherlands (NL):** prices in EUR incl. 21% BTW; note BPM if relevant;
bijtelling matters for lease.

**France (FR):** prices in EUR incl. 20% TVA; bonus écologique only if
currently active and the model qualifies (China-built models generally do
not); L'Argus is the pricing reference.

**Italy (IT):** prices in EUR incl. 22% IVA; Ecobonus only if active;
Quattroruote is the pricing reference.

---

## 📊 Session Reporting Format

```
**Market expansion:** Added X market entries (Y NL, Z FR, W IT)
**Variants covered:** [list]
**Skipped:** [variants not sold in that market, and why]
**PR:** [link]
**Validation:** ✅ validate.py green including cross-checks
```

---

## 🚫 Hard rules

- **PR-only workflow** — never push to `main`; branch `data-fill/YYYY-MM-DD`
- **BEVs only** — no PHEVs, hybrids, range extenders
- **European market only**
- **All data from sources fetched in THIS session** — no guessing, no
  recalling prices from memory
- **Never set `data_quality: verified` on your own records**
- **No ev-database.org**
- **Validate before committing** — `validate.py` + `build-sqlite.py` must
  both pass
- Quality over quantity: a wrong price is worse than a missing file

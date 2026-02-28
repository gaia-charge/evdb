# Local source evidence store

Downloaded manufacturer datasheets, spec pages, and press kits used to fill
data gaps. **Everything here except this README and manifests is gitignored**
— these documents are manufacturer-copyrighted and must not be committed or
redistributed; only facts extracted from them go into `data/` (with the
source URL cited in `metadata.sources`).

## Layout

```
sources/
  <brand>/
    manifest.yaml          # what was fetched, from where, when
    <model-id>/
      spec-page.html       # saved official spec/tech-data page
      press-kit.pdf        # official press kit or technical datasheet
      price-list.pdf       # official price list (often carries tech data)
```

## manifest.yaml format

```yaml
brand: renault
fetched_at: "2026-08-13"
documents:
  - file: renault-5/spec-page.html
    url: https://www.renault.fr/vehicules-electriques/r5/specifications.html
    type: spec_page          # spec_page | press_kit | datasheet | price_list
    covers_models: [renault-5-e-tech]
    covers_variants: [renault-5-e-tech-52-techno-2025]
    fields_present: [charging.time_10_to_80_min, features.heat_pump]
    notes: ""
skipped:
  - model: renault-twizy
    reason: discontinued, no official page remains
```

## Rules

- **Official sources only**: manufacturer websites, their press portals
  (media.stellantis.com, press.bmwgroup.com, ...), official importer sites.
  No aggregators, no ev-database.org.
- Record every download in the manifest immediately — an unrecorded file
  is unusable evidence.
- Extraction into `data/` happens as a separate reviewed step (see
  VERIFICATION.md); this store is input material, not the database.

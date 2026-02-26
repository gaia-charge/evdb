# Data Verification Policy

Every change to `data/` goes through two independent gates before it reaches
`main`: a deterministic gate (schema + cross-file checks) and an adversarial
verification gate (an independent agent that tries to refute the change
against its cited sources).

## Why

The database is largely written by automated agents. The observed failure
mode is not malformed YAML — validation catches that — it is **plausible but
wrong data**: a price copied from the wrong trim, colors from a different
model, a record self-labelled `verified` by the same agent that wrote it.
The only defense is separating the author from the verifier.

## Roles

### Author (human or agent)

- Works on a branch (`data-fill/YYYY-MM-DD` for the cron agent), never on
  `main`. Opens a pull request.
- Every new or changed record carries `metadata.sources` with **deep links**
  to the exact spec/price page (not a homepage), and
  `metadata.price_checked_at` (market files) or `metadata.updated_at`.
- The author may set `data_quality: estimated | partial | unverified` —
  **never `verified`**. `verified` is the verifier's to give.

### Verifier (independent agent)

- Runs with fresh context on the PR diff. It does not see the author's
  session, reasoning, or notes — only the changed files and their cited
  sources.
- For each new or changed record it must independently:
  1. Fetch every URL in `metadata.sources`.
  2. Confirm the record's claims against what the source actually says —
     price, trim name, model year, battery, VAT inclusion.
  3. Actively try to refute: is this price for the *right trim*? Right
     *model year*? Does the market file's trim mapping (see
     CRON_INSTRUCTIONS.md) actually match on specs? Is the currency and
     VAT treatment correct for the market?
  4. Cross-check one independent source when the primary is press rather
     than the manufacturer.
- Verdict per record: `confirmed` | `refuted` | `source-unreachable`,
  with a one-line reason quoting the source.
- On `confirmed`, the verifier (not the author) may set
  `data_quality: verified` and `verified_by`.

## Merge rules

1. `validate.yml` must pass (schema + referential integrity + plausibility
   + cross-market spread).
2. The verification workflow must report every record `confirmed`.
3. Any `refuted` or `source-unreachable` record blocks the PR until fixed
   or removed. Disagreement between author and verifier goes to a human.

## Deterministic checks (already in CI)

`scripts/validate.py --directory data --check-duplicates` enforces:

- JSON Schema per file, `verified` ⇒ non-empty `sources`
- market → variant → model → manufacturer referential integrity
- filename = id, `(variant_id, market)` uniqueness, semantic duplicate
  variant detection
- plausibility bands (battery vs range, price bands, currency↔market)
- cross-market price spread > 1.5x raises a warning that the verifier
  must resolve

## Re-verification (freshness)

Prices rot. A weekly job samples the records with the oldest
`last_verified_at` / `price_checked_at`, re-fetches their sources, and:

- refreshes `last_verified_at` when the source still agrees,
- updates the price (as a normal PR through this same policy) when it
  changed,
- downgrades `data_quality` to `unverified` when the source is gone.

Records older than ~180 days without re-verification should be treated as
stale regardless of their label.

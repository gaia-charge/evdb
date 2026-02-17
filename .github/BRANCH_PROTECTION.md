# Branch Protection Setup

To enforce schema validation and prevent invalid data from being merged, configure these branch protection rules for the `main` branch:

## Recommended Settings

### 1. Require Status Checks
✅ **Require status checks to pass before merging**
- Check: `validate` (from Validate YAML Data workflow)
- Check: `build` (from Build Database workflow)

✅ **Require branches to be up to date before merging**

### 2. Require Pull Request Reviews
✅ **Require a pull request before merging**
✅ **Require approvals: 1**
✅ **Dismiss stale pull request approvals when new commits are pushed**

### 3. Additional Settings
✅ **Require conversation resolution before merging**
✅ **Do not allow bypassing the above settings**

## How to Configure

1. Go to: `https://github.com/gaia-charge/evdb/settings/branches`
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable the settings listed above
5. Click "Create" or "Save changes"

## What This Protects Against

- ❌ **Schema violations**: Invalid YAML files that don't match the JSON Schema
- ❌ **Duplicate IDs**: Multiple entities with the same identifier
- ❌ **Build failures**: Changes that break the SQLite database build
- ❌ **Unreviewed changes**: Direct pushes to main without peer review

## Local Validation

Before pushing, always validate locally:

```bash
# Validate all YAML files
python scripts/validate.py --directory data --check-duplicates

# Build the database to ensure no breaking changes
python scripts/build-sqlite.py
```

## CI Workflow

The validation workflow runs on:
- Every push to `main` or `develop`
- Every pull request targeting `main` or `develop`
- Only when relevant files change:
  - `data/**/*.yaml`
  - `schemas/**/*.json`
  - `scripts/validate.py`
  - Validation workflow itself

## Exit Codes

- `0`: All validations passed ✅
- `1`: Validation errors found ❌

The CI will fail and block merging if any validation errors are detected.

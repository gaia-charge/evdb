# EVDB Deployment Guide

This guide explains how to deploy the EVDB Datasette instance to production.

## Prerequisites

- GitHub repository with workflows enabled
- Datasette installed (`pip install datasette`)
- Database built (`python scripts/build-sqlite.py`)

## Deployment Options

We support three deployment options. Choose based on your needs:

### Option A: Vercel (Recommended)

**Pros:**
- Free tier available
- Global CDN
- Automatic HTTPS
- Easy GitHub integration
- Zero config deployment

**Cons:**
- Read-only (no write operations)
- Cold start on first request
- Limited to 100GB bandwidth/month (free tier)

**Setup:**

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Install datasette-publish-vercel:
```bash
pip install datasette-publish-vercel
```

3. Authenticate with Vercel:
```bash
vercel login
```

4. Deploy:
```bash
datasette publish vercel evdb.db \
  --metadata metadata.json \
  --project evdb \
  --install datasette-cluster-map \
  --install datasette-vega \
  --install datasette-graphql \
  --install datasette-export-notebook \
  --install datasette-configure-fts
```

5. Get deployment URL (will be something like `evdb-xxx.vercel.app`)

**GitHub Actions Setup:**

1. Get Vercel token: https://vercel.com/account/tokens
2. Add token to GitHub secrets as `VERCEL_TOKEN`
3. Uncomment Vercel deployment section in `.github/workflows/build-deploy.yml`
4. Push to main branch

### Option B: Fly.io

**Pros:**
- Free tier: 3 shared-cpu-1x 256MB VMs
- Persistent storage
- Custom domains
- Global deployment

**Cons:**
- Requires credit card for free tier
- More complex setup
- Cold start on inactivity

**Setup:**

1. Install flyctl:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Install datasette-publish-fly:
```bash
pip install datasette-publish-fly
```

3. Authenticate:
```bash
flyctl auth login
```

4. Deploy:
```bash
datasette publish fly evdb.db \
  --metadata metadata.json \
  --app evdb \
  --install datasette-cluster-map \
  --install datasette-vega \
  --install datasette-graphql \
  --install datasette-export-notebook \
  --install datasette-configure-fts
```

**GitHub Actions Setup:**

1. Get Fly.io token: `flyctl auth token`
2. Add token to GitHub secrets as `FLY_TOKEN`
3. Uncomment Fly.io deployment section in `.github/workflows/build-deploy.yml`
4. Push to main branch

### Option C: GitHub Pages (Static Export)

**Pros:**
- Completely free
- No server required
- Fast and reliable
- Easy setup

**Cons:**
- Read-only (no dynamic queries)
- Large dataset may hit size limits
- No plugin support
- Static HTML only

**Setup:**

1. Build static site:
```bash
datasette publish static evdb.db \
  --output _site \
  --metadata metadata.json
```

2. Deploy to GitHub Pages:
```bash
# Enable GitHub Pages in repository settings
# Set source to "gh-pages" branch
```

**Not Recommended**: Limited functionality, no API access.

## Recommended: Vercel Deployment

For most use cases, Vercel is the best choice:

1. **Easy setup**: One command deployment
2. **Free tier**: Generous limits for most projects
3. **Global CDN**: Fast access worldwide
4. **Automatic SSL**: HTTPS by default
5. **GitHub integration**: Auto-deploy on push

### Step-by-Step Vercel Setup

1. **Install tools**:
```bash
pip install datasette datasette-publish-vercel
npm install -g vercel
```

2. **Test locally**:
```bash
datasette evdb.db --metadata metadata.json --port 8765
# Visit http://localhost:8765
```

3. **Deploy to Vercel**:
```bash
datasette publish vercel evdb.db \
  --metadata metadata.json \
  --project evdb \
  --install datasette-cluster-map \
  --install datasette-vega \
  --install datasette-graphql \
  --install datasette-export-notebook \
  --install datasette-configure-fts
```

4. **Get URL**:
- You'll get a URL like `evdb-xxx.vercel.app`
- Test all queries and plugins
- Check API responses

5. **Set up custom domain** (optional):
```bash
vercel domains add evdb.yourdomain.com
```

6. **Enable GitHub Actions**:
- Go to https://vercel.com/account/tokens
- Create new token
- Add to GitHub secrets as `VERCEL_TOKEN`
- Uncomment Vercel section in `.github/workflows/build-deploy.yml`
- Push to main branch

### Environment Variables (Optional)

If you need environment variables for plugins:

```bash
datasette publish vercel evdb.db \
  --metadata metadata.json \
  --project evdb \
  --env SECRET_KEY=your-secret-key \
  --install datasette-cluster-map
```

## Testing Deployment

After deployment, test these endpoints:

1. **Homepage**: `https://your-url.vercel.app/`
2. **Database**: `https://your-url.vercel.app/evdb`
3. **Manufacturers**: `https://your-url.vercel.app/evdb/manufacturers.json`
4. **Vehicle Variants**: `https://your-url.vercel.app/evdb/vehicle_variants.json`
5. **Canned Query**: `https://your-url.vercel.app/evdb/range-finder?min_range=500`
6. **GraphQL**: `https://your-url.vercel.app/graphql` (if installed)

### Test Checklist

- [ ] Homepage loads
- [ ] All tables visible
- [ ] Canned queries work
- [ ] JSON export works
- [ ] CSV export works
- [ ] Plugins loaded (check footer)
- [ ] Mobile responsive
- [ ] HTTPS working
- [ ] Custom domain (if configured)

## Monitoring & Maintenance

### Vercel

- Dashboard: https://vercel.com/dashboard
- Monitor bandwidth, requests, errors
- Check deployment logs
- Free tier: 100GB bandwidth/month

### Fly.io

- Dashboard: https://fly.io/dashboard
- Monitor CPU, memory, requests
- Check logs: `flyctl logs`
- Free tier: 3 VMs with 256MB RAM

### Database Updates

Automatic via GitHub Actions:

1. Commit YAML changes to `main` branch
2. GitHub Actions validates data
3. Builds new SQLite database
4. Deploys to Vercel/Fly.io
5. New data live within 2-5 minutes

Manual update:

```bash
# Rebuild database
python scripts/build-sqlite.py

# Test locally
datasette evdb.db --metadata metadata.json

# Re-deploy
datasette publish vercel evdb.db --metadata metadata.json --project evdb
```

## Troubleshooting

### Deployment fails

1. Check GitHub Actions logs
2. Verify secrets are set (VERCEL_TOKEN or FLY_TOKEN)
3. Test build locally: `python scripts/build-sqlite.py`
4. Test datasette locally: `datasette evdb.db`

### Plugins not loading

1. Check metadata.json plugin configuration
2. Verify plugins installed in deployment:
   - Add `--install plugin-name` to publish command
   - Check plugin compatibility with datasette version

### Large database size

1. Compress images/media
2. Remove unnecessary fields
3. Consider pagination limits
4. Use Fly.io for persistent storage

### CORS errors

Add to metadata.json:
```json
{
  "allow_cors": true
}
```

### Rate limiting

Add to metadata.json:
```json
{
  "plugins": {
    "datasette-ratelimit": {
      "rate": "1000/hour"
    }
  }
}
```

## Cost Estimation

### Vercel (Recommended)

- **Free tier**: 100GB bandwidth, unlimited requests
- **Pro tier** ($20/month): 1TB bandwidth, priority support
- **Estimate**: Free tier sufficient for 100k+ API requests/month

### Fly.io

- **Free tier**: 3 shared-cpu-1x 256MB VMs, 3GB storage
- **Estimate**: Free tier sufficient for small-medium traffic
- **Paid**: $1.94/month per 256MB RAM, $0.15/GB storage

### GitHub Pages

- **Free**: Unlimited static hosting
- **Limitation**: 1GB repository size limit

## Next Steps

After deployment:

1. Update README.md with live URL
2. Add API examples with real endpoints
3. Share on r/electricvehicles, Hacker News
4. Monitor usage and errors
5. Set up analytics (optional)
6. Consider custom domain
7. Document API rate limits

## Support

- **Issues**: https://github.com/yourusername/evdb/issues
- **Datasette Docs**: https://docs.datasette.io/
- **Vercel Support**: https://vercel.com/support
- **Fly.io Support**: https://community.fly.io/

---

**Last Updated**: 2026-02-07

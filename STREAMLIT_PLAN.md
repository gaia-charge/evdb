# Streamlit App Implementation Plan

**Decision Date:** 2026-02-07  
**Rationale:** User requested Streamlit deployment instead of Vercel/Datasette as primary interface

---

## 🎯 Goal

Build a user-friendly Streamlit web app that allows non-technical users to explore, compare, and analyze electric vehicle data from the EVDB database.

---

## 📦 Architecture

```
streamlit_app.py (main entry point)
├── 🏠 Home Page
│   ├── Database statistics (manufacturers, models, variants, markets)
│   ├── Latest additions
│   ├── Quick search box
│   └── Navigation links
│
├── 🔍 Browse Vehicles
│   ├── Interactive filters sidebar
│   │   ├── Price range slider (€20k-€250k)
│   │   ├── WLTP range slider (200-800 km)
│   │   ├── DC charging power slider (50-350 kW)
│   │   ├── Manufacturer multi-select
│   │   ├── Body style multi-select
│   │   ├── Drive type (RWD/FWD/AWD)
│   │   ├── Battery chemistry (NMC/NCA/LFP)
│   │   └── Market (Germany/USA/France/etc.)
│   ├── Searchable dataframe
│   ├── Vehicle detail expansion
│   └── Export filtered results (CSV/JSON)
│
├── ⚖️ Compare Vehicles
│   ├── Multi-select (2-4 vehicles)
│   ├── Side-by-side comparison table
│   ├── Radar chart (range, charging, performance, price)
│   ├── Bar charts (battery size, power, range)
│   └── Export comparison (PDF/PNG)
│
├── 📊 Analytics Dashboard
│   ├── Range Analysis
│   │   ├── Battery capacity vs. WLTP range scatter
│   │   ├── Efficiency ranking (kWh/100km)
│   │   ├── EPA vs WLTP correlation
│   │   └── Real-world vs rated range
│   ├── Charging Speeds
│   │   ├── DC max power comparison (bar chart)
│   │   ├── 10-80% charge time ranking
│   │   ├── 800V vs 400V platform comparison
│   │   └── AC vs DC charging availability
│   ├── Price Distribution
│   │   ├── Price histogram by segment
│   │   ├── Price vs range scatter
│   │   ├── Price vs power scatter
│   │   └── Best value analysis (€/km range)
│   └── Market Overview
│       ├── Vehicles by market (heatmap)
│       ├── Manufacturer market share
│       ├── Body style distribution
│       ├── Battery chemistry breakdown
│       └── Drive type distribution
│
├── 💾 Data Explorer
│   ├── SQL query interface (for power users)
│   ├── Pre-built query templates
│   ├── Query result display
│   └── Export results
│
└── 📚 Documentation
    ├── Embedded API_DOCS.md
    ├── Embedded CONTRIBUTING.md
    ├── FAQ
    └── About the project
```

---

## 🛠 Technical Stack

```python
# Core
import streamlit as st
import sqlite3
import pandas as pd

# Visualizations
import plotly.express as px
import plotly.graph_objects as go
import altair as alt  # Alternative charting library

# Data processing
import numpy as np
from datetime import datetime

# Optional
from PIL import Image  # For vehicle images if we add them later
import base64  # For download links
```

---

## 📋 Implementation Phases

### Phase 1: Skeleton & Home Page (Day 1 - Today)
- [ ] Create `streamlit_app.py` with basic structure
- [ ] Connect to `evdb.db` SQLite database
- [ ] Implement Home page:
  - [ ] Query database for statistics
  - [ ] Display count of manufacturers, models, variants
  - [ ] Show market coverage
  - [ ] Add quick search box
- [ ] Test locally: `streamlit run streamlit_app.py`
- [ ] Commit to repo

### Phase 2: Browse Vehicles (Day 1-2)
- [ ] Implement sidebar filters:
  - [ ] Price range slider
  - [ ] WLTP range slider
  - [ ] DC charging power slider
  - [ ] Manufacturer multi-select
  - [ ] Body style multi-select
  - [ ] Drive type filter
  - [ ] Battery chemistry filter
  - [ ] Market filter
- [ ] Build SQL query from filter selections
- [ ] Display results in `st.dataframe()` with pagination
- [ ] Add vehicle detail expansion (click to see full specs)
- [ ] Add export button (CSV/JSON)
- [ ] Test all filters

### Phase 3: Compare Vehicles (Day 2)
- [ ] Add vehicle multi-select widget (max 4 vehicles)
- [ ] Query selected vehicles from database
- [ ] Display side-by-side comparison table
- [ ] Create radar chart with Plotly:
  - [ ] Range (normalized)
  - [ ] Charging speed (normalized)
  - [ ] Power (normalized)
  - [ ] Price (inverted & normalized - lower is better)
  - [ ] Efficiency (inverted & normalized)
- [ ] Add bar charts for key metrics
- [ ] Add export functionality

### Phase 4: Analytics Dashboard (Day 2-3)
- [ ] **Range Analysis Tab:**
  - [ ] Battery vs range scatter (Plotly)
  - [ ] Efficiency ranking table
  - [ ] EPA vs WLTP comparison
  - [ ] Real-world vs rated range
  
- [ ] **Charging Speeds Tab:**
  - [ ] DC max power bar chart
  - [ ] Charge time ranking
  - [ ] 800V vs 400V comparison
  
- [ ] **Price Distribution Tab:**
  - [ ] Price histogram by body style
  - [ ] Price vs range scatter
  - [ ] Value analysis (€/km)
  
- [ ] **Market Overview Tab:**
  - [ ] Market heatmap
  - [ ] Manufacturer pie chart
  - [ ] Body style breakdown
  - [ ] Battery chemistry pie

### Phase 5: Data Explorer (Day 3)
- [ ] Add SQL query text area
- [ ] Provide query templates dropdown:
  - [ ] "Find vehicles by range >500km"
  - [ ] "Budget EVs under €40k"
  - [ ] "Fast charging >200kW"
  - [ ] "Latest models by manufacturer"
  - [ ] "800V platform vehicles"
- [ ] Execute query and display results
- [ ] Add error handling for bad SQL
- [ ] Add export results button

### Phase 6: Documentation Pages (Day 3)
- [ ] Embed API_DOCS.md content
- [ ] Embed CONTRIBUTING.md content
- [ ] Create FAQ page
- [ ] Add "About" page with project info

### Phase 7: Polish & Deploy (Day 4)
- [ ] Configure Streamlit theme (`.streamlit/config.toml`)
- [ ] Add favicon and logo
- [ ] Test mobile responsiveness
- [ ] Optimize performance (caching)
- [ ] Deploy to Streamlit Cloud
- [ ] Test on production
- [ ] Update README with live URL

---

## 🎨 Streamlit Configuration

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#4CAF50"  # Green for EVs
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

---

## 💾 Database Connection

```python
import streamlit as st
import sqlite3
import pandas as pd

@st.cache_resource
def get_connection():
    """Create cached database connection"""
    return sqlite3.connect('evdb.db', check_same_thread=False)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_vehicles(_conn):
    """Load all vehicles from database (cached)"""
    query = "SELECT * FROM view_vehicles_full"
    return pd.read_sql_query(query, _conn)

# Usage
conn = get_connection()
df = load_vehicles(conn)
```

---

## 📊 Example Visualizations

### 1. Range vs Battery Capacity Scatter

```python
import plotly.express as px

fig = px.scatter(
    df,
    x='battery_usable_kwh',
    y='range_wltp_km',
    color='manufacturer_name',
    size='motors_total_power_kw',
    hover_name='variant_name',
    hover_data=['price_base_eur', 'charging_dc_max_kw'],
    title='Battery Capacity vs. WLTP Range',
    labels={
        'battery_usable_kwh': 'Battery Capacity (kWh)',
        'range_wltp_km': 'WLTP Range (km)',
        'motors_total_power_kw': 'Power (kW)'
    }
)
st.plotly_chart(fig, use_container_width=True)
```

### 2. Charging Speed Comparison

```python
# Top 10 fastest charging EVs
top_charging = df.nlargest(10, 'charging_dc_max_kw')

fig = px.bar(
    top_charging,
    x='variant_name',
    y='charging_dc_max_kw',
    color='voltage_system',
    title='Top 10 Fastest Charging EVs',
    labels={'charging_dc_max_kw': 'DC Max Power (kW)'}
)
st.plotly_chart(fig, use_container_width=True)
```

### 3. Radar Chart Comparison

```python
import plotly.graph_objects as go

# Normalize metrics (0-1 scale)
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

categories = ['Range', 'Charging', 'Power', 'Efficiency', 'Value']

fig = go.Figure()

for vehicle in selected_vehicles:
    vehicle_data = df[df['id'] == vehicle].iloc[0]
    
    values = [
        normalize(df['range_wltp_km'])[vehicle_data.name],
        normalize(df['charging_dc_max_kw'])[vehicle_data.name],
        normalize(df['motors_total_power_kw'])[vehicle_data.name],
        1 - normalize(df['consumption_wltp_kwh_100km'])[vehicle_data.name],  # Lower is better
        1 - normalize(df['price_base_eur'])[vehicle_data.name]  # Lower is better
    ]
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=vehicle_data['variant_name']
    ))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    title="Vehicle Comparison Radar"
)

st.plotly_chart(fig, use_container_width=True)
```

---

## 🚀 Deployment Steps

### 1. Prepare Repository
```bash
# Ensure these files exist:
- streamlit_app.py
- evdb.db (or build script)
- requirements.txt (with streamlit dependencies)
- .streamlit/config.toml
```

### 2. Streamlit Cloud Setup
1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `gaia-charge/evdb`
5. Branch: `main`
6. Main file path: `streamlit_app.py`
7. Click "Deploy"

### 3. Post-Deployment
- Test all features on live site
- Update README.md with live URL
- Share with friends for feedback

---

## 📝 Requirements.txt Updates

```txt
# Existing
pyyaml>=6.0
jsonschema>=4.17.0
click>=8.1.0
rich>=13.0.0
pytest>=7.2.0
sqlite-utils>=3.34
datasette>=0.64.0
datasette-cluster-map>=0.17.0
datasette-vega>=0.6.2
datasette-export-notebook>=1.0
datasette-graphql>=2.2
datasette-configure-fts>=1.1

# NEW: Streamlit dependencies
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
altair>=5.1.0
numpy>=1.24.0
```

---

## 🎯 Success Criteria

### Must Have (MVP)
- [ ] Home page with database stats
- [ ] Vehicle browser with working filters
- [ ] Basic comparison (side-by-side table)
- [ ] At least 3 charts in Analytics
- [ ] Deploys successfully to Streamlit Cloud
- [ ] Mobile responsive

### Nice to Have (Post-Launch)
- [ ] Advanced radar chart comparison
- [ ] SQL query explorer
- [ ] Export to PDF
- [ ] Vehicle images
- [ ] Dark mode toggle
- [ ] Real-time data quality indicators

---

## ⚠️ Important Notes

1. **Stop adding vehicles via cron** - Focus on building the app
2. **Database must be included** - Either commit `evdb.db` or auto-build on startup
3. **Performance matters** - Use `@st.cache_data` aggressively
4. **Mobile first** - Test on phone, many EV shoppers browse on mobile
5. **Keep it simple** - Don't over-engineer, iterate based on feedback

---

## 📅 Timeline

**Day 1 (Feb 7):** Phases 1-2 (Home + Browse)  
**Day 2 (Feb 8):** Phases 3-4 (Compare + Analytics)  
**Day 3 (Feb 9):** Phases 5-7 (Explorer + Docs + Deploy)  
**Day 4 (Feb 10):** Testing + Polish  
**Day 5-7 (Feb 11-13):** Soft launch + feedback  
**Feb 15-20:** Public launch

---

## 🔗 Resources

- Streamlit Docs: https://docs.streamlit.io/
- Plotly Python: https://plotly.com/python/
- Streamlit Gallery: https://streamlit.io/gallery
- Streamlit Cloud: https://streamlit.io/cloud
- EVDB Repo: https://github.com/gaia-charge/evdb

"""
EVDB - Electric Vehicle Database Explorer
A user-friendly Streamlit interface for exploring EV data
"""

import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
import plotly.express as px
import requests
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="EVDB - Electric Vehicle Database",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Plausible analytics helper
def track_pageview(page_name):
    """Send a pageview to Plausible with the current tab as the URL path."""
    page_path = "/" + page_name.split(" ", 1)[-1].lower().replace(" ", "-")
    components.html(f"""
<script>
// Get the parent (Streamlit) origin for proper URL tracking
var baseUrl = 'https://evdb.streamlit.app';
try {{ baseUrl = window.parent.location.origin || baseUrl; }} catch(e) {{}}
var trackUrl = baseUrl + '{page_path}';

// Load and init Plausible
var s = document.createElement('script');
s.async = true;
s.src = 'https://plausible.io/js/pa-rPKfOBHbOTq8L3IHShOcM.js';
s.onload = function() {{
    if (window.plausible) {{
        window.plausible('pageview', {{u: trackUrl}});
    }}
}};
document.head.appendChild(s);
</script>
""", height=0)

# GitHub release configuration
GITHUB_REPO = "gaia-charge/evdb"
RELEASE_DB_URL = f"https://github.com/{GITHUB_REPO}/releases/latest/download/evdb.db"
RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DB_DIR = Path(tempfile.gettempdir()) / "evdb"
DB_PATH = DB_DIR / "evdb.db"


def _get_latest_release_tag():
    """Check the latest release tag from GitHub API"""
    try:
        resp = requests.get(RELEASE_API_URL, timeout=10,
                            headers={"Accept": "application/vnd.github.v3+json"})
        if resp.ok:
            return resp.json().get("tag_name")
    except Exception:
        pass
    return None


def _download_database():
    """Download the database from the latest GitHub release."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(RELEASE_DB_URL, timeout=60, stream=True,
                        allow_redirects=True)
    resp.raise_for_status()
    tmp = DB_PATH.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
    tmp.rename(DB_PATH)


@st.cache_resource(ttl=300)
def get_connection(_release_tag):
    """Create database connection, keyed by release tag for auto-refresh.
    When the tag changes, Streamlit creates a new connection to the new DB."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    tag_file = DB_DIR / ".release_tag"
    current_tag = tag_file.read_text().strip() if tag_file.exists() else None

    need_download = not DB_PATH.exists() or (_release_tag and _release_tag != current_tag)

    if need_download:
        try:
            _download_database()
            if _release_tag:
                tag_file.write_text(_release_tag)
        except Exception as e:
            if not DB_PATH.exists():
                st.error(f"⚠️ Failed to download database: {e}")
                st.stop()

    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def format_vehicle_name(brand, model, variant, year=None):
    """Format vehicle display name, avoiding duplicate brand/model prefixes.
    
    Examples:
        brand='Audi', model='Q6 e-tron', variant='RWD'       → 'Audi Q6 e-tron RWD'
        brand='MG',   model='MG4 Electric', variant='XPower'  → 'MG4 Electric XPower' (skip brand, model already has it)
        brand='BMW',  model='i4', variant='eDrive40'          → 'BMW i4 eDrive40'
    """
    # Skip brand prefix if model name already starts with brand
    if model.upper().startswith(brand.upper()):
        name = model
    else:
        name = f"{brand} {model}"
    
    if variant and variant != 'Base':
        name = f"{name} {variant}"
    
    if year:
        name = f"{name} ({year})"
    
    return name


def format_vehicle_column(df):
    """Apply format_vehicle_name to a DataFrame with manufacturer/model/variant_name/model_year columns."""
    return df.apply(
        lambda r: format_vehicle_name(
            r['manufacturer'], r['model'], r['variant_name'],
            str(int(r['model_year'])) if pd.notna(r.get('model_year')) else None
        ), axis=1
    )

@st.cache_data(ttl=3600)
def get_database_stats(_conn):
    """Get database statistics (cached for 1 hour)"""
    stats = {}
    
    # Get counts
    stats['manufacturers'] = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM manufacturers", _conn
    ).iloc[0]['count']
    
    stats['models'] = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM vehicle_models", _conn
    ).iloc[0]['count']
    
    stats['variants'] = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM vehicle_variants", _conn
    ).iloc[0]['count']
    
    stats['markets'] = pd.read_sql_query(
        "SELECT COUNT(DISTINCT market_code) as count FROM market_availability", _conn
    ).iloc[0]['count']
    
    # Get market breakdown
    stats['market_breakdown'] = pd.read_sql_query("""
        SELECT market_code, COUNT(*) as vehicles
        FROM market_availability
        GROUP BY market_code
        ORDER BY vehicles DESC
    """, _conn)
    
    # Get latest additions (last 5)
    stats['latest_additions'] = pd.read_sql_query("""
        SELECT 
            m.brand as manufacturer,
            m.name as model,
            v.variant_name,
            v.model_year,
            v.range_wltp_km,
            ma.price_base as price_eur
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
        ORDER BY v.created_at DESC
        LIMIT 5
    """, _conn)
    
    return stats

@st.cache_data(ttl=3600)
def load_markdown_file(filename):
    """Load markdown file content (cached for 1 hour)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"⚠️ File `{filename}` not found."
    except Exception as e:
        return f"⚠️ Error loading file: {str(e)}"

def format_vehicle_specs(row):
    """Format vehicle specifications into a structured dictionary"""
    specs = {
        'Manufacturer': row.get('manufacturer', 'N/A'),
        'Model': f"{row.get('model', '')} {row.get('variant_name', '')}".strip(),
        'Year': int(row['model_year']) if pd.notna(row.get('model_year')) else 'N/A',
        'Body Style': row.get('body_style') if pd.notna(row.get('body_style')) else 'N/A',
        'Drive Type': row.get('drive_type') if pd.notna(row.get('drive_type')) else 'N/A',
        '🔋 BATTERY & RANGE': '',
        'Battery Capacity': f"{row['battery_usable_kwh']:.1f} kWh" if pd.notna(row.get('battery_usable_kwh')) else 'N/A',
        'Battery Chemistry': row.get('battery_chemistry') if pd.notna(row.get('battery_chemistry')) else 'N/A',
        'Battery Architecture': row.get('battery_architecture') if pd.notna(row.get('battery_architecture')) else 'N/A',
        'WLTP Range': f"{int(row['range_wltp_km'])} km" if pd.notna(row.get('range_wltp_km')) else 'N/A',
        'Real-World Range': f"{int(row['range_real_world_km'])} km" if pd.notna(row.get('range_real_world_km')) else 'N/A',
        'Consumption': f"{row['consumption_real_world_kwh_100km']:.1f} kWh/100km" if pd.notna(row.get('consumption_real_world_kwh_100km')) else 'N/A',
        '⚡ PERFORMANCE': '',
        'Total Power': f"{int(row['total_power_kw'])} kW ({int(row['total_power_kw'] * 1.341)} hp)" if pd.notna(row.get('total_power_kw')) else 'N/A',
        'Total Torque': f"{int(row['total_torque_nm'])} Nm" if pd.notna(row.get('total_torque_nm')) else 'N/A',
        '0-100 km/h': f"{row['acceleration_0_100_sec']:.1f} sec" if pd.notna(row.get('acceleration_0_100_sec')) else 'N/A',
        'Top Speed': f"{int(row['top_speed_kph'])} km/h" if pd.notna(row.get('top_speed_kph')) else 'N/A',
        '🔌 CHARGING': '',
        'DC Fast Charge': f"{int(row['dc_charge_power_kw'])} kW" if pd.notna(row.get('dc_charge_power_kw')) else 'N/A',
        'DC 10-80%': f"{int(row['dc_charge_time_10_80_min'])} min" if pd.notna(row.get('dc_charge_time_10_80_min')) else 'N/A',
        'AC Charge': f"{row['ac_charge_power_kw']:.1f} kW" if pd.notna(row.get('ac_charge_power_kw')) else 'N/A',
    }
    
    # Add dimensions section if any dimension data is available
    has_dimensions = any([
        pd.notna(row.get('length_mm')),
        pd.notna(row.get('width_mm')),
        pd.notna(row.get('height_mm')),
        pd.notna(row.get('wheelbase_mm'))
    ])
    
    if has_dimensions:
        specs['📏 DIMENSIONS'] = ''
        if pd.notna(row.get('length_mm')):
            specs['Length'] = f"{int(row['length_mm'])} mm"
        if pd.notna(row.get('width_mm')):
            specs['Width'] = f"{int(row['width_mm'])} mm"
        if pd.notna(row.get('width_with_mirrors_mm')):
            specs['Width (with mirrors)'] = f"{int(row['width_with_mirrors_mm'])} mm"
        if pd.notna(row.get('height_mm')):
            specs['Height'] = f"{int(row['height_mm'])} mm"
        if pd.notna(row.get('wheelbase_mm')):
            specs['Wheelbase'] = f"{int(row['wheelbase_mm'])} mm"
        if pd.notna(row.get('ground_clearance_mm')):
            specs['Ground Clearance'] = f"{int(row['ground_clearance_mm'])} mm"
        if pd.notna(row.get('turning_circle_m')):
            specs['Turning Circle'] = f"{row['turning_circle_m']:.1f} m"
    
    # Add weight section if any weight data is available
    has_weight = any([
        pd.notna(row.get('weight_curb_kg')),
        pd.notna(row.get('weight_gross_kg')),
        pd.notna(row.get('payload_kg'))
    ])
    
    if has_weight:
        specs['⚖️ WEIGHT'] = ''
        specs['Curb Weight'] = f"{int(row['weight_curb_kg'])} kg" if pd.notna(row.get('weight_curb_kg')) else 'N/A'
        specs['Gross Weight'] = f"{int(row['weight_gross_kg'])} kg" if pd.notna(row.get('weight_gross_kg')) else 'N/A'
        specs['Payload'] = f"{int(row['payload_kg'])} kg" if pd.notna(row.get('payload_kg')) else 'N/A'
    
    # Add cargo section if any cargo data is available
    has_cargo = any([
        pd.notna(row.get('trunk_capacity_liters')),
        pd.notna(row.get('frunk_capacity_liters')),
        pd.notna(row.get('roof_load_kg'))
    ])
    
    if has_cargo:
        specs['📦 CARGO CAPACITY'] = ''
        specs['Trunk'] = f"{int(row['trunk_capacity_liters'])} L" if pd.notna(row.get('trunk_capacity_liters')) else 'N/A'
        if pd.notna(row.get('trunk_max_liters')):
            specs['Trunk (Max)'] = f"{int(row['trunk_max_liters'])} L"
        if pd.notna(row.get('frunk_capacity_liters')):
            specs['Frunk'] = f"{int(row['frunk_capacity_liters'])} L"
        if pd.notna(row.get('roof_load_kg')):
            specs['Roof Load'] = f"{int(row['roof_load_kg'])} kg"
    
    # Add towing section if towing data is available
    has_towing = any([
        pd.notna(row.get('towing_capacity_braked_kg')),
        pd.notna(row.get('towing_capacity_unbraked_kg'))
    ])
    
    if has_towing:
        specs['🚙 TOWING CAPACITY'] = ''
        specs['Braked Trailer'] = f"{int(row['towing_capacity_braked_kg'])} kg" if pd.notna(row.get('towing_capacity_braked_kg')) else 'N/A'
        if pd.notna(row.get('towing_capacity_unbraked_kg')):
            specs['Unbraked Trailer'] = f"{int(row['towing_capacity_unbraked_kg'])} kg"
    
    # Add pricing at the end
    specs['💰 PRICING (GERMANY)'] = ''
    specs['Base Price'] = f"€{int(row['price_eur']):,}" if pd.notna(row.get('price_eur')) else 'TBD'
    specs['On-the-Road Price'] = f"€{int(row['price_otr_eur']):,}" if pd.notna(row.get('price_otr_eur')) else 'TBD'
    
    return specs

def show_vehicle_details(vehicle_data):
    """Display detailed vehicle specifications in a formatted table"""
    specs = format_vehicle_specs(vehicle_data)
    
    # Create single-column DataFrame for display
    specs_df = pd.DataFrame({
        'Specification': list(specs.keys()),
        'Value': list(specs.values())
    })
    
    # Display as dataframe
    st.dataframe(
        specs_df,
        hide_index=True,
        use_container_width=True,
        height=800
    )

@st.cache_data(ttl=3600)
def search_vehicles(_conn, query):
    """Search vehicles by name (cached)"""
    search_query = f"%{query}%"
    return pd.read_sql_query("""
        SELECT 
            v.id,
            m.brand as manufacturer,
            m.name as model,
            v.variant_name,
            v.model_year,
            v.battery_usable_kwh,
            v.range_wltp_km,
            v.total_power_kw,
            v.acceleration_0_100_sec,
            ma.price_base as price_eur,
            ma.market_code
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id
        WHERE 
            m.brand LIKE ? OR
            m.name LIKE ? OR
            v.variant_name LIKE ?
        ORDER BY m.brand, m.name, v.variant_name
        LIMIT 20
    """, _conn, params=(search_query, search_query, search_query))

# Initialize connection (check for latest release on every page load)
_current_release = _get_latest_release_tag()
conn = get_connection(_current_release)

# Sidebar navigation
st.sidebar.title("⚡ EVDB")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "🔍 Browse Vehicles", "⚖️ Compare", "📊 Analytics", "💾 Data Explorer", "📚 Documentation"]
)

# Track page navigation
track_pageview(page)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("""
**EVDB** is a community-driven open database of electric vehicle specifications.

- 🎯 Comprehensive specs
- 💰 Market pricing
- 🔋 Battery & charging data
- 🌍 Multi-market coverage
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>

**License:** CC BY-SA 4.0  
**GitHub:** [gaia-charge/evdb](https://github.com/gaia-charge/evdb)

</small>
""", unsafe_allow_html=True)

# Main content based on selected page
if page == "🏠 Home":
    st.title("⚡ Electric Vehicle Database")
    st.markdown("""
    Welcome to **EVDB** - a comprehensive, open-source database of electric vehicle specifications,
    pricing, and market availability across multiple countries.
    """)
    
    # Load statistics
    stats = get_database_stats(conn)
    
    # Key metrics
    st.markdown("### 📊 Database Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Manufacturers",
            value=stats['manufacturers'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Vehicle Models",
            value=stats['models'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Variants",
            value=stats['variants'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Markets",
            value=stats['markets'],
            delta=None
        )
    
    # Market breakdown
    st.markdown("### 🌍 Market Coverage")
    
    market_names = {
        'DE': '🇩🇪 Germany',
        'ES': '🇪🇸 Spain',
        'FR': '🇫🇷 France',
        'GB': '🇬🇧 United Kingdom',
        'IT': '🇮🇹 Italy',
        'NL': '🇳🇱 Netherlands',
        'PL': '🇵🇱 Poland',
        'US': '🇺🇸 United States',
    }
    
    market_df = stats['market_breakdown'].copy()
    market_df['Market'] = market_df['market_code'].map(market_names).fillna(market_df['market_code'])
    market_df = market_df[['Market', 'vehicles']]
    market_df.columns = ['Market', 'Vehicles']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            market_df,
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.markdown(f"""
        **Total vehicles with pricing:**  
        {market_df['Vehicles'].sum()} entries across {stats['markets']} markets
        
        **Primary market:** Germany  
        **Newest additions:** USA, France, Poland, Italy
        """)
    
    # Latest additions
    st.markdown("### 🆕 Latest Additions")
    
    latest = stats['latest_additions'].copy()
    latest['Vehicle'] = format_vehicle_column(latest)
    latest['Year'] = latest['model_year'].astype(int)
    
    st.dataframe(
        latest[['Vehicle', 'Year', 'range_wltp_km', 'price_eur']],
        column_config={
            'Vehicle': st.column_config.TextColumn('Vehicle', width='large'),
            'Year': st.column_config.NumberColumn('Year', format="%d"),
            'range_wltp_km': st.column_config.NumberColumn('Range', format="%d km"),
            'price_eur': st.column_config.NumberColumn('Price', format="€%d"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Quick search
    st.markdown("### 🔍 Quick Search")
    
    search_query = st.text_input(
        "Search for a vehicle by manufacturer, model, or variant:",
        placeholder="e.g., Tesla Model 3, BMW iX, Ioniq 5..."
    )
    
    if search_query:
        results = search_vehicles(conn, search_query)
        
        if len(results) > 0:
            st.success(f"Found {len(results)} result(s)")
            
            # Format results
            display_results = results.copy()
            display_results['Vehicle'] = format_vehicle_column(display_results)
            display_results['Market'] = display_results['market_code'].fillna('N/A')
            
            st.dataframe(
                display_results[['Vehicle', 'battery_usable_kwh', 'range_wltp_km', 'total_power_kw', 'acceleration_0_100_sec', 'price_eur', 'Market']],
                column_config={
                    'Vehicle': st.column_config.TextColumn('Vehicle', width='large'),
                    'battery_usable_kwh': st.column_config.NumberColumn('Battery', format="%.1f kWh"),
                    'range_wltp_km': st.column_config.NumberColumn('Range', format="%d km"),
                    'total_power_kw': st.column_config.NumberColumn('Power', format="%d kW"),
                    'acceleration_0_100_sec': st.column_config.NumberColumn('0-100', format="%.1fs"),
                    'price_eur': st.column_config.NumberColumn('Price', format="€%d"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No vehicles found. Try a different search term.")
    
    # Call to action
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🔍 Browse Database
        Explore all vehicles with advanced filters by price, range, charging speed, and more.
        """)
    
    with col2:
        st.markdown("""
        #### ⚖️ Compare Vehicles
        Select multiple vehicles and compare their specifications side-by-side with interactive charts.
        """)
    
    with col3:
        st.markdown("""
        #### 📊 Analytics
        Discover insights with interactive visualizations of range, charging speeds, pricing, and market trends.
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🤝 Contributing
    
    EVDB is community-driven and open-source. We welcome contributions!
    
    - **Add vehicle data:** Help expand our database with missing vehicles
    - **Improve accuracy:** Report errors or suggest corrections
    - **Build features:** Contribute code to improve the platform
    
    Check out our [Contributing Guide](https://github.com/gaia-charge/evdb/blob/main/CONTRIBUTING.md) to get started.
    """)

elif page == "🔍 Browse Vehicles":
    st.title("🔍 Browse Vehicles")
    st.markdown("Explore all vehicles with advanced filtering options")
    
    # Load available markets
    @st.cache_data(ttl=3600)
    def load_available_markets(_conn):
        """Load list of markets with vehicle counts"""
        return pd.read_sql_query("""
            SELECT market_code, COUNT(DISTINCT variant_id) as count
            FROM market_availability
            WHERE market_code != 'US'
            GROUP BY market_code
            ORDER BY count DESC
        """, _conn)
    
    markets_df = load_available_markets(conn)
    market_options = {"🇪🇺 All Europe": "ALL"}
    market_flags = {'DE': '🇩🇪', 'ES': '🇪🇸', 'FR': '🇫🇷', 'PL': '🇵🇱', 'IT': '🇮🇹', 'NL': '🇳🇱', 'AT': '🇦🇹', 'BE': '🇧🇪', 'PT': '🇵🇹', 'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'CH': '🇨🇭', 'GB': '🇬🇧'}
    market_names = {'DE': 'Germany', 'ES': 'Spain', 'FR': 'France', 'PL': 'Poland', 'IT': 'Italy', 'NL': 'Netherlands', 'AT': 'Austria', 'BE': 'Belgium', 'PT': 'Portugal', 'SE': 'Sweden', 'NO': 'Norway', 'DK': 'Denmark', 'CH': 'Switzerland', 'GB': 'United Kingdom'}
    for _, row in markets_df.iterrows():
        code = row['market_code']
        flag = market_flags.get(code, '🏳️')
        name = market_names.get(code, code)
        market_options[f"{flag} {name} ({int(row['count'])})"] = code
    
    # Load all data
    @st.cache_data(ttl=3600)
    def load_browse_data(_conn, market_code):
        """Load all vehicle data with filters"""
        if market_code == "ALL":
            # Show all vehicles, use cheapest European price
            return pd.read_sql_query("""
                SELECT 
                    v.id,
                    m.brand as manufacturer,
                    m.name as model,
                    v.variant_name,
                    v.model_year,
                    m.body_style,
                    v.battery_usable_kwh,
                    v.battery_chemistry,
                    v.range_wltp_km,
                    v.range_real_world_km,
                    v.total_power_kw,
                    v.acceleration_0_100_sec,
                    v.dc_charge_power_kw,
                    v.dc_charge_time_10_80_min,
                    v.drive_type,
                    v.length_mm,
                    v.width_mm,
                    v.width_with_mirrors_mm,
                    v.height_mm,
                    v.wheelbase_mm,
                    v.ground_clearance_mm,
                    v.turning_circle_m,
                    v.trunk_capacity_liters,
                    v.trunk_max_liters,
                    v.frunk_capacity_liters,
                    v.roof_load_kg,
                    v.towing_capacity_braked_kg,
                    v.towing_capacity_unbraked_kg,
                    v.payload_kg,
                    v.weight_curb_kg,
                    v.weight_gross_kg,
                    COALESCE(ma_eur.min_price, ma_pln.price_eur_equiv) as price_eur,
                    COALESCE(ma_eur.market_code, ma_pln.market_code) as market_code
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                LEFT JOIN (
                    SELECT variant_id, MIN(price_base) as min_price, 
                           MIN(market_code) as market_code
                    FROM market_availability 
                    WHERE market_code IN ('DE','ES','FR','IT','NL','AT','BE','PT','SE','NO','DK','CH','GB')
                      AND currency = 'EUR'
                    GROUP BY variant_id
                ) ma_eur ON v.id = ma_eur.variant_id
                LEFT JOIN (
                    SELECT variant_id, price_base * 0.23 as price_eur_equiv,
                           market_code
                    FROM market_availability 
                    WHERE market_code = 'PL' AND currency = 'PLN'
                ) ma_pln ON v.id = ma_pln.variant_id AND ma_eur.variant_id IS NULL
                ORDER BY m.brand, m.name, v.variant_name
            """, _conn)
        else:
            return pd.read_sql_query(f"""
                SELECT 
                    v.id,
                    m.brand as manufacturer,
                    m.name as model,
                    v.variant_name,
                    v.model_year,
                    m.body_style,
                    v.battery_usable_kwh,
                    v.battery_chemistry,
                    v.range_wltp_km,
                    v.range_real_world_km,
                    v.total_power_kw,
                    v.acceleration_0_100_sec,
                    v.dc_charge_power_kw,
                    v.dc_charge_time_10_80_min,
                    v.drive_type,
                    v.length_mm,
                    v.width_mm,
                    v.width_with_mirrors_mm,
                    v.height_mm,
                    v.wheelbase_mm,
                    v.ground_clearance_mm,
                    v.turning_circle_m,
                    v.trunk_capacity_liters,
                    v.trunk_max_liters,
                    v.frunk_capacity_liters,
                    v.roof_load_kg,
                    v.towing_capacity_braked_kg,
                    v.towing_capacity_unbraked_kg,
                    v.payload_kg,
                    v.weight_curb_kg,
                    v.weight_gross_kg,
                    ma.price_base as price_eur,
                    ma.market_code
                FROM vehicle_variants v
                JOIN vehicle_models m ON v.model_id = m.id
                LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = '{market_code}'
                ORDER BY m.brand, m.name, v.variant_name
            """, _conn)
    
    # Sidebar filters
    st.sidebar.markdown("### 🌍 Market")
    selected_market_label = st.sidebar.selectbox(
        "Show prices for:",
        options=list(market_options.keys()),
        index=0
    )
    selected_market = market_options[selected_market_label]
    
    df = load_browse_data(conn, selected_market)
    
    st.sidebar.markdown("### 🎚️ Filters")
    
    # Manufacturer filter
    all_manufacturers = sorted(df['manufacturer'].unique().tolist())
    selected_manufacturers = st.sidebar.multiselect(
        "Manufacturer:",
        options=all_manufacturers,
        default=[]
    )
    
    # Body style filter
    all_body_styles = sorted([bs for bs in df['body_style'].unique() if pd.notna(bs)])
    selected_body_styles = st.sidebar.multiselect(
        "Body Style:",
        options=all_body_styles,
        default=[]
    )
    
    # Drive type filter
    all_drive_types = sorted([dt for dt in df['drive_type'].unique() if pd.notna(dt)])
    selected_drive_types = st.sidebar.multiselect(
        "Drive Type:",
        options=all_drive_types,
        default=[]
    )
    
    # Price range filter
    price_currency = "PLN" if selected_market == 'PL' else "EUR"
    st.sidebar.markdown(f"#### Price ({price_currency})")
    price_min_val = int(df['price_eur'].min()) if df['price_eur'].notna().any() else 20000
    price_max_val = int(df['price_eur'].max()) if df['price_eur'].notna().any() else 150000
    price_step = 10000 if selected_market == 'PL' else 5000
    price_fmt = "%d PLN" if selected_market == 'PL' else "€%d"
    
    price_range = st.sidebar.slider(
        "Price Range:",
        min_value=price_min_val,
        max_value=price_max_val,
        value=(price_min_val, price_max_val),
        step=price_step,
        format=price_fmt
    )
    
    # WLTP range filter
    st.sidebar.markdown("#### Range (WLTP)")
    range_min_val = int(df['range_wltp_km'].min()) if df['range_wltp_km'].notna().any() else 200
    range_max_val = int(df['range_wltp_km'].max()) if df['range_wltp_km'].notna().any() else 800
    
    range_filter = st.sidebar.slider(
        "WLTP Range (km):",
        min_value=range_min_val,
        max_value=range_max_val,
        value=(range_min_val, range_max_val),
        step=50
    )
    
    # DC charging power filter
    st.sidebar.markdown("#### Charging Speed")
    charge_min_val = int(df['dc_charge_power_kw'].min()) if df['dc_charge_power_kw'].notna().any() else 50
    charge_max_val = int(df['dc_charge_power_kw'].max()) if df['dc_charge_power_kw'].notna().any() else 350
    
    charge_power = st.sidebar.slider(
        "DC Charge Power (kW):",
        min_value=charge_min_val,
        max_value=charge_max_val,
        value=(charge_min_val, charge_max_val),
        step=10
    )
    
    # Battery chemistry filter
    all_chemistries = sorted([c for c in df['battery_chemistry'].unique() if pd.notna(c)])
    selected_chemistries = st.sidebar.multiselect(
        "Battery Chemistry:",
        options=all_chemistries,
        default=[]
    )
    
    # Dimensions filters
    st.sidebar.markdown("#### Dimensions")
    
    if df['length_mm'].notna().any():
        len_min = int(df['length_mm'].min())
        len_max = int(df['length_mm'].max())
        dim_length_range = st.sidebar.slider(
            "Length (mm):",
            min_value=len_min,
            max_value=len_max,
            value=(len_min, len_max),
            step=100
        )
    else:
        dim_length_range = None
    
    if df['width_mm'].notna().any():
        w_min = int(df['width_mm'].min())
        w_max = int(df['width_mm'].max())
        dim_width_range = st.sidebar.slider(
            "Width (mm):",
            min_value=w_min,
            max_value=w_max,
            value=(w_min, w_max),
            step=50
        )
    else:
        dim_width_range = None
    
    if df['height_mm'].notna().any():
        h_min = int(df['height_mm'].min())
        h_max = int(df['height_mm'].max())
        dim_height_range = st.sidebar.slider(
            "Height (mm):",
            min_value=h_min,
            max_value=h_max,
            value=(h_min, h_max),
            step=50
        )
    else:
        dim_height_range = None
    
    # Cargo capacity filter
    st.sidebar.markdown("#### Cargo Capacity")
    if df['trunk_capacity_liters'].notna().any():
        trunk_min_val = int(df['trunk_capacity_liters'].min())
        trunk_max_val = int(df['trunk_capacity_liters'].max())
        trunk_range = st.sidebar.slider(
            "Trunk Capacity (liters):",
            min_value=trunk_min_val,
            max_value=trunk_max_val,
            value=(trunk_min_val, trunk_max_val),
            step=50
        )
    else:
        trunk_range = None
    
    # Towing capacity filter
    st.sidebar.markdown("#### Towing Capacity")
    if df['towing_capacity_braked_kg'].notna().any():
        has_towing_filter = st.sidebar.checkbox("Has Towing Capability", value=False)
        
        if has_towing_filter:
            towing_min_val = int(df['towing_capacity_braked_kg'].min()) if df['towing_capacity_braked_kg'].notna().any() else 0
            towing_max_val = int(df['towing_capacity_braked_kg'].max()) if df['towing_capacity_braked_kg'].notna().any() else 2500
            
            towing_capacity_min = st.sidebar.number_input(
                "Min Towing Capacity (kg):",
                min_value=0,
                max_value=towing_max_val,
                value=0,
                step=250
            )
        else:
            towing_capacity_min = 0
    else:
        has_towing_filter = False
        towing_capacity_min = 0
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters"):
        st.rerun()
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_manufacturers:
        filtered_df = filtered_df[filtered_df['manufacturer'].isin(selected_manufacturers)]
    
    if selected_body_styles:
        filtered_df = filtered_df[filtered_df['body_style'].isin(selected_body_styles)]
    
    if selected_drive_types:
        filtered_df = filtered_df[filtered_df['drive_type'].isin(selected_drive_types)]
    
    if selected_chemistries:
        filtered_df = filtered_df[filtered_df['battery_chemistry'].isin(selected_chemistries)]
    
    # Price filter (handle NaN)
    filtered_df = filtered_df[
        (filtered_df['price_eur'].isna()) | 
        ((filtered_df['price_eur'] >= price_range[0]) & (filtered_df['price_eur'] <= price_range[1]))
    ]
    
    # Range filter
    filtered_df = filtered_df[
        (filtered_df['range_wltp_km'] >= range_filter[0]) & 
        (filtered_df['range_wltp_km'] <= range_filter[1])
    ]
    
    # Charge power filter (handle NaN)
    filtered_df = filtered_df[
        (filtered_df['dc_charge_power_kw'].isna()) | 
        ((filtered_df['dc_charge_power_kw'] >= charge_power[0]) & (filtered_df['dc_charge_power_kw'] <= charge_power[1]))
    ]
    
    # Dimensions filters
    if dim_length_range is not None:
        len_min, len_max = dim_length_range
        if len_min > int(df['length_mm'].min()) or len_max < int(df['length_mm'].max()):
            filtered_df = filtered_df[
                (filtered_df['length_mm'].isna()) |
                ((filtered_df['length_mm'] >= len_min) & (filtered_df['length_mm'] <= len_max))
            ]
    if dim_width_range is not None:
        w_min, w_max = dim_width_range
        if w_min > int(df['width_mm'].min()) or w_max < int(df['width_mm'].max()):
            filtered_df = filtered_df[
                (filtered_df['width_mm'].isna()) |
                ((filtered_df['width_mm'] >= w_min) & (filtered_df['width_mm'] <= w_max))
            ]
    if dim_height_range is not None:
        h_min, h_max = dim_height_range
        if h_min > int(df['height_mm'].min()) or h_max < int(df['height_mm'].max()):
            filtered_df = filtered_df[
                (filtered_df['height_mm'].isna()) |
                ((filtered_df['height_mm'] >= h_min) & (filtered_df['height_mm'] <= h_max))
            ]
    
    # Cargo capacity filter
    if trunk_range is not None:
        t_min, t_max = trunk_range
        if t_min > int(df['trunk_capacity_liters'].min()) or t_max < int(df['trunk_capacity_liters'].max()):
            filtered_df = filtered_df[
                (filtered_df['trunk_capacity_liters'].isna()) |
                ((filtered_df['trunk_capacity_liters'] >= t_min) & (filtered_df['trunk_capacity_liters'] <= t_max))
            ]
    
    # Towing capacity filter
    if has_towing_filter:
        if towing_capacity_min > 0:
            filtered_df = filtered_df[
                (filtered_df['towing_capacity_braked_kg'].notna()) & 
                (filtered_df['towing_capacity_braked_kg'] >= towing_capacity_min)
            ]
        else:
            filtered_df = filtered_df[filtered_df['towing_capacity_braked_kg'].notna()]
    
    # Display results count
    st.markdown(f"### Found {len(filtered_df)} vehicle(s)")
    
    if len(filtered_df) == 0:
        st.warning("No vehicles match the selected filters. Try adjusting your criteria.")
    else:
        # Sort options
        col1, col2 = st.columns([3, 1])
        
        with col1:
            sort_by = st.selectbox(
                "Sort by:",
                options=[
                    "Manufacturer (A-Z)",
                    "Price (Low-High)",
                    "Price (High-Low)",
                    "Range (High-Low)",
                    "Range (Low-High)",
                    "Charging Speed (High-Low)",
                    "Power (High-Low)"
                ],
                index=0
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            export_format = st.selectbox("Export:", ["CSV", "JSON"])
        
        # Apply sorting
        if sort_by == "Manufacturer (A-Z)":
            filtered_df = filtered_df.sort_values(['manufacturer', 'model', 'variant_name'])
        elif sort_by == "Price (Low-High)":
            filtered_df = filtered_df.sort_values('price_eur', na_position='last')
        elif sort_by == "Price (High-Low)":
            filtered_df = filtered_df.sort_values('price_eur', ascending=False, na_position='last')
        elif sort_by == "Range (High-Low)":
            filtered_df = filtered_df.sort_values('range_wltp_km', ascending=False)
        elif sort_by == "Range (Low-High)":
            filtered_df = filtered_df.sort_values('range_wltp_km')
        elif sort_by == "Charging Speed (High-Low)":
            filtered_df = filtered_df.sort_values('dc_charge_power_kw', ascending=False, na_position='last')
        elif sort_by == "Power (High-Low)":
            filtered_df = filtered_df.sort_values('total_power_kw', ascending=False)
        
        # Format display data — keep numeric columns for proper sorting
        display_df = filtered_df.copy()
        display_df['Vehicle'] = format_vehicle_column(display_df)
        
        # Price column label and format based on market
        price_label = 'Price (PLN)' if selected_market == 'PL' else 'Price (EUR)'
        price_format = "%d PLN" if selected_market == 'PL' else "€%d"
        
        # Display table with selection — use column_config for formatting
        event = st.dataframe(
            display_df[[
                'Vehicle', 'body_style', 'battery_usable_kwh', 'range_wltp_km', 
                'range_real_world_km', 'total_power_kw', 'acceleration_0_100_sec', 
                'dc_charge_power_kw', 'drive_type', 'price_eur'
            ]].rename(columns={
                'body_style': 'Body',
                'drive_type': 'Drive'
            }),
            column_config={
                'Vehicle': st.column_config.TextColumn('Vehicle', width='large'),
                'battery_usable_kwh': st.column_config.NumberColumn('Battery', format="%.1f kWh"),
                'range_wltp_km': st.column_config.NumberColumn('WLTP Range', format="%d km"),
                'range_real_world_km': st.column_config.NumberColumn('Real Range', format="%d km"),
                'total_power_kw': st.column_config.NumberColumn('Power', format="%d kW"),
                'acceleration_0_100_sec': st.column_config.NumberColumn('0-100', format="%.1fs"),
                'dc_charge_power_kw': st.column_config.NumberColumn('DC Charge', format="%d kW"),
                'price_eur': st.column_config.NumberColumn(price_label, format=price_format),
            },
            hide_index=True,
            use_container_width=True,
            height=400,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Show detailed specs if a vehicle is selected
        if event and event.selection and len(event.selection.get('rows', [])) > 0:
            selected_idx = event.selection['rows'][0]
            selected_vehicle = filtered_df.iloc[selected_idx]
            
            st.markdown("---")
            st.markdown(f"### 📋 Detailed Specifications: {format_vehicle_name(selected_vehicle['manufacturer'], selected_vehicle['model'], selected_vehicle['variant_name'])}")
            
            # Need to fetch complete vehicle data including pricing fields
            @st.cache_data(ttl=3600)
            def get_vehicle_details(_conn, vehicle_id):
                return pd.read_sql_query("""
                    SELECT 
                        v.id,
                        m.brand as manufacturer,
                        m.name as model,
                        v.variant_name,
                        v.model_year,
                        m.body_style,
                        v.battery_usable_kwh,
                        v.battery_chemistry,
                        CASE WHEN v.battery_voltage >= 700 THEN '800V' 
                             WHEN v.battery_voltage IS NOT NULL THEN '400V' END as battery_architecture,
                        v.range_wltp_km,
                        v.range_real_world_km,
                        v.consumption_real_world_kwh_100km,
                        v.total_power_kw,
                        v.total_torque_nm,
                        v.acceleration_0_100_sec,
                        v.top_speed_kph,
                        v.drive_type,
                        v.dc_charge_power_kw,
                        v.dc_charge_time_10_80_min,
                        v.ac_charge_power_kw,
                        v.weight_curb_kg,
                        v.weight_gross_kg,
                        v.payload_kg,
                        v.length_mm,
                        v.width_mm,
                        v.width_with_mirrors_mm,
                        v.height_mm,
                        v.wheelbase_mm,
                        v.ground_clearance_mm,
                        v.turning_circle_m,
                        v.trunk_capacity_liters,
                        v.trunk_max_liters,
                        v.frunk_capacity_liters,
                        v.roof_load_kg,
                        v.towing_capacity_braked_kg,
                        v.towing_capacity_unbraked_kg,
                        ma.price_base as price_eur,
                        ma.price_including_vat as price_otr_eur
                    FROM vehicle_variants v
                    JOIN vehicle_models m ON v.model_id = m.id
                    LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
                    WHERE v.id = ?
                """, _conn, params=(vehicle_id,))
            
            vehicle_details_df = get_vehicle_details(conn, selected_vehicle['id'])
            if not vehicle_details_df.empty:
                show_vehicle_details(vehicle_details_df.iloc[0])
        
        # Export functionality
        if export_format == "CSV":
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"evdb_browse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:  # JSON
            json_data = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"evdb_browse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Quick stats
        st.markdown("---")
        st.markdown("### 📊 Quick Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_price = filtered_df['price_eur'].mean()
            st.metric(
                "Average Price",
                f"€{int(avg_price):,}" if pd.notna(avg_price) else "N/A"
            )
        
        with col2:
            avg_range = filtered_df['range_wltp_km'].mean()
            st.metric(
                "Average Range",
                f"{int(avg_range)} km" if pd.notna(avg_range) else "N/A"
            )
        
        with col3:
            avg_power = filtered_df['total_power_kw'].mean()
            st.metric(
                "Average Power",
                f"{int(avg_power)} kW" if pd.notna(avg_power) else "N/A"
            )
        
        with col4:
            avg_charge = filtered_df['dc_charge_power_kw'].mean()
            st.metric(
                "Average DC Charge",
                f"{int(avg_charge)} kW" if pd.notna(avg_charge) else "N/A"
            )

elif page == "⚖️ Compare":
    st.title("⚖️ Compare Vehicles")
    st.markdown("Select 2-4 vehicles to compare side-by-side")
    
    # Load all vehicles
    @st.cache_data(ttl=3600)
    def load_all_vehicles(_conn):
        """Load all vehicles for comparison"""
        df = pd.read_sql_query("""
            SELECT 
                v.id,
                m.brand as manufacturer,
                m.name as model,
                v.variant_name,
                v.model_year,
                m.body_style,
                v.battery_usable_kwh,
                v.battery_chemistry,
                CASE WHEN v.battery_voltage >= 700 THEN '800V' WHEN v.battery_voltage IS NOT NULL THEN '400V' END as battery_architecture,
                v.range_wltp_km,
                v.range_real_world_km,
                v.consumption_real_world_kwh_100km,
                v.total_power_kw,
                v.total_torque_nm,
                v.acceleration_0_100_sec,
                v.top_speed_kph,
                v.drive_type,
                v.dc_charge_power_kw,
                v.dc_charge_time_10_80_min,
                v.ac_charge_power_kw,
                v.weight_curb_kg,
                v.weight_gross_kg,
                v.payload_kg,
                v.length_mm,
                v.width_mm,
                v.width_with_mirrors_mm,
                v.height_mm,
                v.wheelbase_mm,
                v.ground_clearance_mm,
                v.turning_circle_m,
                v.trunk_capacity_liters,
                v.trunk_max_liters,
                v.frunk_capacity_liters,
                v.roof_load_kg,
                v.towing_capacity_braked_kg,
                v.towing_capacity_unbraked_kg,
                ma.price_base as price_eur,
                ma.price_including_vat as price_otr_eur
            FROM vehicle_variants v
            JOIN vehicle_models m ON v.model_id = m.id
            LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
            ORDER BY m.brand, m.name, v.variant_name
        """, _conn)
        df['full_name'] = format_vehicle_column(df)
        return df
    
    vehicles_df = load_all_vehicles(conn)
    
    # Vehicle selection
    st.markdown("### Select Vehicles to Compare")
    
    # Create options list (vehicle names)
    vehicle_options = vehicles_df['full_name'].tolist()
    
    # Multi-select with max 4 vehicles
    selected_vehicles = st.multiselect(
        "Choose 2-4 vehicles:",
        options=vehicle_options,
        default=[],
        max_selections=4,
        help="Select between 2 and 4 vehicles to compare"
    )
    
    if len(selected_vehicles) < 2:
        st.info("👆 Please select at least 2 vehicles to start comparing")
        
        # Show some popular comparisons as suggestions
        st.markdown("### 💡 Popular Comparisons")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Performance EVs:**
            - Tesla Model 3 Performance (2024)
            - BMW i4 M50 (2024)
            - Porsche Taycan Turbo S (2024)
            
            **Long Range Leaders:**
            - Mercedes-Benz EQS 450+ (2024)
            - BMW iX xDrive50 (2024)
            - Tesla Model 3 Long Range AWD (2024)
            """)
        
        with col2:
            st.markdown("""
            **Korean 800V Platforms:**
            - Hyundai Ioniq 5 Long Range AWD (2024)
            - Hyundai Ioniq 6 Long Range AWD (2024)
            - Kia EV6 GT (2024)
            
            **Budget-Friendly:**
            - Tesla Model 3 RWD (2024)
            - VW ID.3 Pro (2024)
            - Hyundai Ioniq 6 Standard Range RWD (2024)
            """)
    
    else:
        # Get data for selected vehicles
        selected_df = vehicles_df[vehicles_df['full_name'].isin(selected_vehicles)].copy()
        
        st.success(f"✅ Comparing {len(selected_vehicles)} vehicles")
        
        # Create comparison table
        st.markdown("### 📊 Specification Comparison")
        
        # Transpose for side-by-side view
        comparison_data = {}
        
        for _, row in selected_df.iterrows():
            vehicle_name = row['full_name']
            comparison_data[vehicle_name] = format_vehicle_specs(row)
        
        # Create DataFrame for display
        comparison_table = pd.DataFrame(comparison_data)
        
        # Display table with styling
        st.dataframe(
            comparison_table,
            use_container_width=True,
            height=800
        )
        
        # Visualizations
        st.markdown("---")
        st.markdown("### 📈 Visual Comparison")
        
        # Prepare data for charts (only numeric values)
        chart_data = selected_df[['full_name', 'battery_usable_kwh', 'range_wltp_km', 
                                   'total_power_kw', 'dc_charge_power_kw', 
                                   'acceleration_0_100_sec', 'price_eur']].copy()
        
        # Rename for better chart labels
        chart_data.columns = ['Vehicle', 'Battery (kWh)', 'Range (km)', 
                              'Power (kW)', 'DC Charge (kW)', '0-100 (sec)', 'Price (EUR)']
        
        # Shorten vehicle names for charts
        chart_data['Vehicle Short'] = chart_data['Vehicle'].apply(
            lambda x: ' '.join(x.split()[:-1])  # Remove year
        )
        
        # Create tabs for different chart types
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📊 Bar Charts", "🎯 Radar Chart", "💰 Value Analysis"])
        
        with chart_tab1:
            st.markdown("#### Key Specifications")
            
            # Create 2x3 grid of bar charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Battery capacity
                import plotly.express as px
                
                fig_battery = px.bar(
                    chart_data,
                    x='Vehicle Short',
                    y='Battery (kWh)',
                    title='Battery Capacity (kWh)',
                    color='Vehicle Short',
                    text='Battery (kWh)'
                )
                fig_battery.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_battery.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_battery, use_container_width=True)
                
                # Power
                fig_power = px.bar(
                    chart_data,
                    x='Vehicle Short',
                    y='Power (kW)',
                    title='Total Power (kW)',
                    color='Vehicle Short',
                    text='Power (kW)'
                )
                fig_power.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                fig_power.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_power, use_container_width=True)
                
                # DC Charging
                fig_charge = px.bar(
                    chart_data,
                    x='Vehicle Short',
                    y='DC Charge (kW)',
                    title='DC Fast Charging (kW)',
                    color='Vehicle Short',
                    text='DC Charge (kW)'
                )
                fig_charge.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                fig_charge.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_charge, use_container_width=True)
            
            with col2:
                # Range
                fig_range = px.bar(
                    chart_data,
                    x='Vehicle Short',
                    y='Range (km)',
                    title='WLTP Range (km)',
                    color='Vehicle Short',
                    text='Range (km)'
                )
                fig_range.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                fig_range.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_range, use_container_width=True)
                
                # 0-100 (inverted - lower is better)
                fig_accel = px.bar(
                    chart_data,
                    x='Vehicle Short',
                    y='0-100 (sec)',
                    title='0-100 km/h (seconds)',
                    color='Vehicle Short',
                    text='0-100 (sec)'
                )
                fig_accel.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_accel.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_accel, use_container_width=True)
                
                # Price
                fig_price = px.bar(
                    chart_data.dropna(subset=['Price (EUR)']),
                    x='Vehicle Short',
                    y='Price (EUR)',
                    title='Base Price (EUR)',
                    color='Vehicle Short',
                    text='Price (EUR)'
                )
                fig_price.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
                fig_price.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_price, use_container_width=True)
        
        with chart_tab2:
            st.markdown("#### Multi-Dimensional Comparison")
            
            # Prepare radar chart data (normalize to 0-100 scale)
            radar_data = selected_df[['full_name', 'battery_usable_kwh', 'range_wltp_km', 
                                      'total_power_kw', 'dc_charge_power_kw']].copy()
            
            # Normalize each metric to 0-100 scale
            for col in ['battery_usable_kwh', 'range_wltp_km', 'total_power_kw', 'dc_charge_power_kw']:
                if radar_data[col].notna().any():
                    max_val = radar_data[col].max()
                    if max_val > 0:
                        radar_data[f'{col}_normalized'] = (radar_data[col] / max_val) * 100
            
            # Create radar chart using plotly
            import plotly.graph_objects as go
            
            categories = ['Battery\nCapacity', 'WLTP\nRange', 'Power', 'DC Fast\nCharging']
            
            fig_radar = go.Figure()
            
            for _, row in radar_data.iterrows():
                vehicle_short = ' '.join(row['full_name'].split()[:-1])
                
                values = [
                    row.get('battery_usable_kwh_normalized', 0),
                    row.get('range_wltp_km_normalized', 0),
                    row.get('total_power_kw_normalized', 0),
                    row.get('dc_charge_power_kw_normalized', 0)
                ]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=vehicle_short
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                title="Normalized Performance Comparison (0-100 scale)",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            st.info("""
            **Note:** Each metric is normalized to a 0-100 scale where 100 represents the 
            best value among the selected vehicles. This allows for easy visual comparison 
            across different units (kWh, km, kW).
            """)
        
        with chart_tab3:
            st.markdown("#### Value for Money Analysis")
            
            # Filter vehicles with pricing
            priced_vehicles = selected_df[selected_df['price_eur'].notna()].copy()
            
            if len(priced_vehicles) == 0:
                st.warning("No pricing data available for selected vehicles")
            else:
                # Calculate value metrics
                priced_vehicles['EUR per kWh'] = priced_vehicles['price_eur'] / priced_vehicles['battery_usable_kwh']
                priced_vehicles['EUR per km Range'] = priced_vehicles['price_eur'] / priced_vehicles['range_wltp_km']
                priced_vehicles['EUR per kW Power'] = priced_vehicles['price_eur'] / priced_vehicles['total_power_kw']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price per kWh
                    fig_value_kwh = px.bar(
                        priced_vehicles,
                        x='full_name',
                        y='EUR per kWh',
                        title='Price per kWh Battery (lower is better)',
                        color='full_name',
                        text='EUR per kWh'
                    )
                    fig_value_kwh.update_traces(texttemplate='€%{text:.0f}', textposition='outside')
                    fig_value_kwh.update_layout(showlegend=False, xaxis_title='', height=300)
                    fig_value_kwh.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_value_kwh, use_container_width=True)
                    
                    # Price per kW
                    fig_value_kw = px.bar(
                        priced_vehicles,
                        x='full_name',
                        y='EUR per kW Power',
                        title='Price per kW Power (lower is better)',
                        color='full_name',
                        text='EUR per kW Power'
                    )
                    fig_value_kw.update_traces(texttemplate='€%{text:.0f}', textposition='outside')
                    fig_value_kw.update_layout(showlegend=False, xaxis_title='', height=300)
                    fig_value_kw.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_value_kw, use_container_width=True)
                
                with col2:
                    # Price per km range
                    fig_value_range = px.bar(
                        priced_vehicles,
                        x='full_name',
                        y='EUR per km Range',
                        title='Price per km Range (lower is better)',
                        color='full_name',
                        text='EUR per km Range'
                    )
                    fig_value_range.update_traces(texttemplate='€%{text:.0f}', textposition='outside')
                    fig_value_range.update_layout(showlegend=False, xaxis_title='', height=300)
                    fig_value_range.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_value_range, use_container_width=True)
                    
                    # Summary table
                    st.markdown("#### Value Summary")
                    value_summary = priced_vehicles[['full_name', 'EUR per kWh', 'EUR per km Range', 'EUR per kW Power']].copy()
                    value_summary.columns = ['Vehicle', '€/kWh', '€/km', '€/kW']
                    value_summary = value_summary.round(0)
                    
                    st.dataframe(
                        value_summary,
                        hide_index=True,
                        use_container_width=True
                    )
        
        # Export functionality
        st.markdown("---")
        st.markdown("### 💾 Export Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as CSV
            csv_export = comparison_table.T.to_csv()
            st.download_button(
                label="⬇️ Download Comparison (CSV)",
                data=csv_export,
                file_name=f"evdb_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export as JSON
            json_export = selected_df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download Data (JSON)",
                data=json_export,
                file_name=f"evdb_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

elif page == "📊 Analytics":
    st.title("📊 Analytics Dashboard")
    st.markdown("Explore market trends, performance patterns, and value analysis across all vehicles")
    
    # Load all vehicles with market data
    @st.cache_data(ttl=3600)
    def get_analytics_data(_conn):
        """Get comprehensive vehicle data for analytics"""
        query = """
        SELECT 
            v.id,
            m.brand as manufacturer,
            m.name as model,
            v.variant_name,
            v.model_year,
            m.body_style,
            m.segment,
            v.battery_usable_kwh,
            v.battery_chemistry,
            CASE WHEN v.battery_voltage >= 700 THEN '800V' WHEN v.battery_voltage IS NOT NULL THEN '400V' END as battery_architecture,
            v.range_wltp_km,
            v.range_real_world_km,
            v.consumption_real_world_kwh_100km,
            v.dc_charge_power_kw,
            v.dc_charge_time_10_80_min,
            v.total_power_kw,
            v.drive_type,
            v.length_mm,
            v.trunk_capacity_liters,
            v.trunk_max_liters,
            v.towing_capacity_braked_kg,
            v.weight_curb_kg,
            v.payload_kg,
            ma.price_base as price_eur
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
        ORDER BY m.brand, m.name, v.variant_name
        """
        return pd.read_sql_query(query, _conn)
    
    conn = get_connection(_current_release)
    df = get_analytics_data(conn)
    
    # Create full vehicle name including year to avoid duplicate aggregation
    df['vehicle_name'] = df.apply(
        lambda r: format_vehicle_name(r['manufacturer'], r['model'], r['variant_name'], int(r['model_year']) if pd.notna(r['model_year']) else None), axis=1
    )
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📏 Range Analysis",
        "⚡ Charging Speeds",
        "💰 Price Distribution",
        "📦 Dimensions & Practicality",
        "🌍 Market Overview"
    ])
    
    # Tab 1: Range Analysis
    with tab1:
        st.markdown("### Battery Capacity vs. Range")
        st.markdown("Explore the relationship between battery size and real-world range")
        
        # Battery vs Range scatter plot
        fig_range = px.scatter(
            df.dropna(subset=['battery_usable_kwh', 'range_wltp_km', 'total_power_kw', 'body_style']),
            x='battery_usable_kwh',
            y='range_wltp_km',
            color='body_style',
            size='total_power_kw',
            hover_data=['vehicle_name', 'range_real_world_km', 'consumption_real_world_kwh_100km'],
            title='Battery Capacity vs. WLTP Range',
            labels={
                'battery_usable_kwh': 'Battery Capacity (kWh)',
                'range_wltp_km': 'WLTP Range (km)',
                'body_style': 'Body Style',
                'total_power_kw': 'Power (kW)'
            }
        )
        fig_range.update_layout(height=500)
        st.plotly_chart(fig_range, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Most Efficient Vehicles")
        st.markdown("Vehicles ranked by real-world consumption (lower is better)")
        
        # Efficiency ranking
        efficiency_df = df.dropna(subset=['consumption_real_world_kwh_100km']).sort_values(
            'consumption_real_world_kwh_100km'
        ).head(15)
        
        fig_efficiency = px.bar(
            efficiency_df,
            x='consumption_real_world_kwh_100km',
            y='vehicle_name',
            orientation='h',
            color='consumption_real_world_kwh_100km',
            color_continuous_scale='RdYlGn_r',
            title='Top 15 Most Efficient EVs (kWh/100km)',
            labels={
                'consumption_real_world_kwh_100km': 'Consumption (kWh/100km)',
                'vehicle_name': 'Vehicle'
            }
        )
        fig_efficiency.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Range statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_range = df['range_wltp_km'].mean()
            st.metric("Average WLTP Range", f"{avg_range:.0f} km")
        with col2:
            max_range = df['range_wltp_km'].max()
            max_range_vehicle = df.loc[df['range_wltp_km'].idxmax(), 'vehicle_name']
            st.metric("Best Range", f"{max_range:.0f} km", delta=max_range_vehicle)
        with col3:
            avg_efficiency = df['consumption_real_world_kwh_100km'].mean()
            st.metric("Average Consumption", f"{avg_efficiency:.1f} kWh/100km")
    
    # Tab 2: Charging Speeds
    with tab2:
        st.markdown("### DC Fast Charging Power Comparison")
        st.markdown("Compare charging capabilities across all vehicles")
        
        # DC charge power histogram
        fig_dc_hist = px.histogram(
            df.dropna(subset=['dc_charge_power_kw']),
            x='dc_charge_power_kw',
            nbins=20,
            title='DC Fast Charging Power Distribution',
            labels={'dc_charge_power_kw': 'DC Charge Power (kW)', 'count': 'Number of Vehicles'},
            color_discrete_sequence=['#4CAF50']
        )
        fig_dc_hist.update_layout(height=400)
        st.plotly_chart(fig_dc_hist, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 800V vs 400V Platform Comparison")
        
        # Filter vehicles with architecture data
        arch_df = df.dropna(subset=['battery_architecture', 'dc_charge_power_kw'])
        
        if not arch_df.empty:
            fig_arch = px.box(
                arch_df,
                x='battery_architecture',
                y='dc_charge_power_kw',
                color='battery_architecture',
                title='DC Charging Power by Platform Architecture',
                labels={
                    'battery_architecture': 'Platform Architecture',
                    'dc_charge_power_kw': 'DC Charge Power (kW)'
                }
            )
            fig_arch.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_arch, use_container_width=True)
            
            # Statistics by architecture
            arch_stats = arch_df.groupby('battery_architecture').agg({
                'dc_charge_power_kw': ['mean', 'max', 'count']
            }).round(1)
            
            st.markdown("#### Platform Statistics")
            for arch in arch_stats.index:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{arch} - Average", f"{arch_stats.loc[arch, ('dc_charge_power_kw', 'mean')]:.0f} kW")
                with col2:
                    st.metric(f"{arch} - Maximum", f"{arch_stats.loc[arch, ('dc_charge_power_kw', 'max')]:.0f} kW")
                with col3:
                    st.metric(f"{arch} - Vehicles", f"{int(arch_stats.loc[arch, ('dc_charge_power_kw', 'count')])}")
        else:
            st.info("Platform architecture data not available for comparison")
        
        st.markdown("---")
        st.markdown("### Fastest Charging Vehicles")
        
        # Top charging speeds
        top_charging = df.dropna(subset=['dc_charge_power_kw', 'battery_architecture']).nlargest(15, 'dc_charge_power_kw')
        
        fig_top_charging = px.bar(
            top_charging,
            x='dc_charge_power_kw',
            y='vehicle_name',
            orientation='h',
            color='battery_architecture',
            title='Top 15 Fastest Charging EVs',
            labels={
                'dc_charge_power_kw': 'DC Charge Power (kW)',
                'vehicle_name': 'Vehicle',
                'battery_architecture': 'Architecture'
            }
        )
        fig_top_charging.update_layout(height=600)
        st.plotly_chart(fig_top_charging, use_container_width=True)
    
    # Tab 3: Price Distribution
    with tab3:
        st.markdown("### Price Distribution (German Market)")
        
        price_df = df.dropna(subset=['price_eur'])
        
        if not price_df.empty:
            # Price histogram
            fig_price_hist = px.histogram(
                price_df,
                x='price_eur',
                nbins=20,
                title='EV Price Distribution',
                labels={'price_eur': 'Base Price (EUR)', 'count': 'Number of Vehicles'},
                color_discrete_sequence=['#2196F3']
            )
            fig_price_hist.update_layout(height=400)
            st.plotly_chart(fig_price_hist, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Price by Body Style")
            
            # Box plot by body style
            fig_price_body = px.box(
                price_df.dropna(subset=['body_style']),
                x='body_style',
                y='price_eur',
                color='body_style',
                title='Price Distribution by Body Style',
                labels={
                    'body_style': 'Body Style',
                    'price_eur': 'Base Price (EUR)'
                }
            )
            fig_price_body.update_layout(height=400, showlegend=False)
            fig_price_body.update_xaxes(tickangle=45)
            st.plotly_chart(fig_price_body, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Value Analysis: Price per kWh")
            st.markdown("Which vehicles offer the best battery value for money?")
            
            # Calculate price per kWh
            value_df = price_df.dropna(subset=['battery_usable_kwh']).copy()
            value_df['price_per_kwh'] = value_df['price_eur'] / value_df['battery_usable_kwh']
            
            # Best value vehicles
            best_value = value_df.nsmallest(15, 'price_per_kwh')
            
            fig_value = px.bar(
                best_value,
                x='price_per_kwh',
                y='vehicle_name',
                orientation='h',
                color='price_per_kwh',
                color_continuous_scale='RdYlGn_r',
                title='Top 15 Best Value EVs (€/kWh - Lower is Better)',
                labels={
                    'price_per_kwh': 'Price per kWh (EUR)',
                    'vehicle_name': 'Vehicle'
                }
            )
            fig_value.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_value, use_container_width=True)
            
            # Price statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_price = price_df['price_eur'].mean()
                st.metric("Average Price", f"€{avg_price:,.0f}")
            with col2:
                median_price = price_df['price_eur'].median()
                st.metric("Median Price", f"€{median_price:,.0f}")
            with col3:
                avg_value = value_df['price_per_kwh'].mean()
                st.metric("Average €/kWh", f"€{avg_value:.0f}")
        else:
            st.info("Pricing data not available. Add market availability data to enable price analysis.")
    
    # Tab 4: Dimensions & Practicality
    with tab4:
        st.markdown("### Cargo Capacity Distribution")
        
        cargo_df = df.dropna(subset=['trunk_capacity_liters'])
        
        if not cargo_df.empty:
            # Cargo capacity histogram
            fig_cargo_hist = px.histogram(
                cargo_df,
                x='trunk_capacity_liters',
                nbins=20,
                title='Trunk Capacity Distribution',
                labels={'trunk_capacity_liters': 'Trunk Capacity (Liters)', 'count': 'Number of Vehicles'},
                color_discrete_sequence=['#FF9800']
            )
            fig_cargo_hist.update_layout(height=400)
            st.plotly_chart(fig_cargo_hist, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Length vs. Cargo Capacity")
            st.markdown("How does vehicle length correlate with cargo space?")
            
            # Length vs cargo scatter
            length_cargo_df = df.dropna(subset=['length_mm', 'trunk_capacity_liters', 'body_style'])
            
            if not length_cargo_df.empty:
                fig_length_cargo = px.scatter(
                    length_cargo_df,
                    x='length_mm',
                    y='trunk_capacity_liters',
                    color='body_style',
                    hover_data=['vehicle_name'],
                    title='Vehicle Length vs. Trunk Capacity',
                    labels={
                        'length_mm': 'Length (mm)',
                        'trunk_capacity_liters': 'Trunk Capacity (Liters)',
                        'body_style': 'Body Style'
                    }
                )
                fig_length_cargo.update_layout(height=500)
                st.plotly_chart(fig_length_cargo, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### Most Spacious Vehicles")
            
            # Top cargo capacity
            top_cargo = cargo_df.nlargest(15, 'trunk_capacity_liters')
            
            fig_top_cargo = px.bar(
                top_cargo,
                x='trunk_capacity_liters',
                y='vehicle_name',
                orientation='h',
                color='trunk_capacity_liters',
                color_continuous_scale='YlOrRd',
                title='Top 15 Vehicles by Trunk Capacity',
                labels={
                    'trunk_capacity_liters': 'Trunk Capacity (Liters)',
                    'vehicle_name': 'Vehicle'
                }
            )
            fig_top_cargo.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_top_cargo, use_container_width=True)
            
            # Cargo statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_cargo = cargo_df['trunk_capacity_liters'].mean()
                st.metric("Average Trunk", f"{avg_cargo:.0f} L")
            with col2:
                max_cargo = cargo_df['trunk_capacity_liters'].max()
                max_cargo_vehicle = cargo_df.loc[cargo_df['trunk_capacity_liters'].idxmax(), 'vehicle_name']
                st.metric("Largest Trunk", f"{max_cargo:.0f} L", delta=max_cargo_vehicle)
            with col3:
                avg_max = df['trunk_max_liters'].mean()
                st.metric("Avg Max Capacity", f"{avg_max:.0f} L" if pd.notna(avg_max) else "N/A")
        else:
            st.info("Cargo capacity data not yet available for most vehicles.")
        
        st.markdown("---")
        st.markdown("### Towing Capacity by Brand/Segment")
        
        towing_df = df.dropna(subset=['towing_capacity_braked_kg'])
        
        if not towing_df.empty:
            # Towing by brand
            towing_by_brand = towing_df.groupby('manufacturer')['towing_capacity_braked_kg'].agg(['mean', 'max', 'count']).reset_index()
            towing_by_brand = towing_by_brand[towing_by_brand['count'] >= 2].sort_values('mean', ascending=False).head(15)
            
            fig_towing_brand = px.bar(
                towing_by_brand,
                x='mean',
                y='manufacturer',
                orientation='h',
                title='Average Towing Capacity by Brand (brands with 2+ vehicles)',
                labels={
                    'mean': 'Average Towing Capacity (kg)',
                    'manufacturer': 'Brand'
                },
                color='mean',
                color_continuous_scale='Blues'
            )
            fig_towing_brand.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_towing_brand, use_container_width=True)
            
            # Towing by segment
            towing_by_segment = towing_df.dropna(subset=['segment']).groupby('segment')['towing_capacity_braked_kg'].agg(['mean', 'count']).reset_index()
            towing_by_segment = towing_by_segment[towing_by_segment['count'] >= 2].sort_values('mean', ascending=False)
            
            if not towing_by_segment.empty:
                fig_towing_segment = px.bar(
                    towing_by_segment,
                    x='segment',
                    y='mean',
                    title='Average Towing Capacity by Segment',
                    labels={
                        'segment': 'Segment',
                        'mean': 'Average Towing Capacity (kg)'
                    },
                    color='mean',
                    color_continuous_scale='Greens'
                )
                fig_towing_segment.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_towing_segment, use_container_width=True)
            
            # Top towing vehicles
            st.markdown("### Best Towing Capacity")
            top_towing = towing_df.nlargest(10, 'towing_capacity_braked_kg')
            
            fig_top_towing = px.bar(
                top_towing,
                x='towing_capacity_braked_kg',
                y='vehicle_name',
                orientation='h',
                color='towing_capacity_braked_kg',
                color_continuous_scale='RdYlGn',
                title='Top 10 Vehicles by Towing Capacity',
                labels={
                    'towing_capacity_braked_kg': 'Towing Capacity (kg)',
                    'vehicle_name': 'Vehicle'
                }
            )
            fig_top_towing.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_top_towing, use_container_width=True)
            
            # Towing statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_towing = towing_df['towing_capacity_braked_kg'].mean()
                st.metric("Average Towing", f"{avg_towing:.0f} kg")
            with col2:
                max_towing = towing_df['towing_capacity_braked_kg'].max()
                st.metric("Max Towing", f"{max_towing:.0f} kg")
            with col3:
                pct_with_towing = (len(towing_df) / len(df)) * 100
                st.metric("Vehicles with Towing", f"{pct_with_towing:.1f}%")
        else:
            st.info("Towing capacity data not yet available for most vehicles.")
        
        st.markdown("---")
        st.markdown("### Weight Distribution")
        
        weight_df = df.dropna(subset=['weight_curb_kg'])
        
        if not weight_df.empty:
            # Weight histogram
            fig_weight = px.histogram(
                weight_df,
                x='weight_curb_kg',
                nbins=20,
                title='Curb Weight Distribution',
                labels={'weight_curb_kg': 'Curb Weight (kg)', 'count': 'Number of Vehicles'},
                color_discrete_sequence=['#9C27B0']
            )
            fig_weight.update_layout(height=400)
            st.plotly_chart(fig_weight, use_container_width=True)
            
            # Weight statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_weight = weight_df['weight_curb_kg'].mean()
                st.metric("Average Weight", f"{avg_weight:.0f} kg")
            with col2:
                lightest = weight_df['weight_curb_kg'].min()
                st.metric("Lightest", f"{lightest:.0f} kg")
            with col3:
                heaviest = weight_df['weight_curb_kg'].max()
                st.metric("Heaviest", f"{heaviest:.0f} kg")
        else:
            st.info("Weight data not yet available for most vehicles.")
    
    # Tab 5: Market Overview
    with tab5:
        st.markdown("### Market Coverage")
        
        # Manufacturer distribution
        mfr_counts = df.groupby('manufacturer').size().reset_index(name='vehicle_count')
        mfr_counts = mfr_counts.sort_values('vehicle_count', ascending=False)
        
        fig_mfr = px.bar(
            mfr_counts,
            x='vehicle_count',
            y='manufacturer',
            orientation='h',
            title='Vehicles by Manufacturer',
            labels={
                'vehicle_count': 'Number of Variants',
                'manufacturer': 'Manufacturer'
            },
            color='vehicle_count',
            color_continuous_scale='Viridis'
        )
        fig_mfr.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_mfr, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Body Style Distribution")
        
        # Body style pie chart
        body_counts = df.groupby('body_style').size().reset_index(name='count')
        
        fig_body = px.pie(
            body_counts,
            values='count',
            names='body_style',
            title='Vehicle Distribution by Body Style',
            hole=0.4
        )
        fig_body.update_layout(height=500)
        st.plotly_chart(fig_body, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Drive Type Distribution")
        
        # Drive type distribution
        drive_counts = df.groupby('drive_type').size().reset_index(name='count')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_drive = px.pie(
                drive_counts,
                values='count',
                names='drive_type',
                title='Drive Type Distribution',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_drive.update_layout(height=400)
            st.plotly_chart(fig_drive, use_container_width=True)
        
        with col2:
            # Battery chemistry distribution
            chem_counts = df.groupby('battery_chemistry').size().reset_index(name='count')
            
            fig_chem = px.pie(
                chem_counts,
                values='count',
                names='battery_chemistry',
                title='Battery Chemistry Distribution',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_chem.update_layout(height=400)
            st.plotly_chart(fig_chem, use_container_width=True)
        
        # Overall statistics
        st.markdown("---")
        st.markdown("### Database Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vehicles", len(df))
        with col2:
            st.metric("Manufacturers", df['manufacturer'].nunique())
        with col3:
            st.metric("Models", df['model'].nunique())
        with col4:
            with_pricing = df['price_eur'].notna().sum()
            st.metric("With Pricing", with_pricing)

elif page == "💾 Data Explorer":
    st.title("💾 Data Explorer")
    st.markdown("### Run custom SQL queries on the EVDB database")
    
    # Warning about SQL injection
    st.info("ℹ️ **Read-only access:** This interface only allows SELECT queries. Database is not modifiable through this interface.")
    
    # Pre-built query templates
    st.markdown("#### 📋 Example Queries")
    
    example_queries = {
        "All Vehicles Overview": """SELECT 
    m.name AS manufacturer,
    mo.name AS model,
    v.variant_name,
    v.model_year,
    v.battery_usable_kwh,
    v.range_wltp_km,
    v.total_power_kw,
    v.dc_charge_power_kw,
    ma.price_base AS price_eur
FROM vehicle_variants v
JOIN vehicle_models mo ON v.model_id = mo.id
LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
ORDER BY mo.brand, mo.name, v.variant_name;""",
        
        "Top 10 Longest Range EVs": """SELECT 
    mo.brand AS manufacturer,
    mo.name AS model,
    v.variant_name,
    v.range_wltp_km,
    v.range_real_world_km,
    v.battery_usable_kwh
FROM vehicle_variants v
JOIN vehicle_models mo ON v.model_id = mo.id
ORDER BY v.range_wltp_km DESC
LIMIT 10;""",
        
        "Fastest Charging Vehicles": """SELECT 
    mo.brand AS manufacturer,
    mo.name AS model,
    v.variant_name,
    v.dc_charge_power_kw,
    v.dc_charge_time_10_80_min,
    v.battery_usable_kwh
FROM vehicle_variants v
JOIN vehicle_models mo ON v.model_id = mo.id
WHERE v.dc_charge_power_kw IS NOT NULL
ORDER BY v.dc_charge_power_kw DESC
LIMIT 10;""",
        
        "Most Efficient Vehicles": """SELECT 
    mo.brand AS manufacturer,
    mo.name AS model,
    v.variant_name,
    v.consumption_real_world_kwh_100km,
    v.range_real_world_km,
    v.battery_usable_kwh
FROM vehicle_variants v
JOIN vehicle_models mo ON v.model_id = mo.id
WHERE v.consumption_real_world_kwh_100km IS NOT NULL
ORDER BY v.consumption_real_world_kwh_100km ASC
LIMIT 10;""",
        
        "Vehicles by Manufacturer Count": """SELECT 
    m.name AS manufacturer,
    m.country,
    COUNT(DISTINCT mo.id) AS models,
    COUNT(v.id) AS variants
FROM manufacturers m
LEFT JOIN vehicle_models mo ON m.id = mo.manufacturer_id
LEFT JOIN vehicle_variants v ON mo.id = v.model_id
GROUP BY m.id, m.name, m.country
ORDER BY variants DESC;""",
        
        "Price Distribution by Body Style": """SELECT 
    mo.body_style,
    COUNT(v.id) AS vehicles,
    ROUND(AVG(ma.price_base), 0) AS avg_price_eur,
    MIN(ma.price_base) AS min_price_eur,
    MAX(ma.price_base) AS max_price_eur
FROM vehicle_variants v
JOIN vehicle_models mo ON v.model_id = mo.id
LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
WHERE ma.price_base IS NOT NULL
GROUP BY mo.body_style
ORDER BY avg_price_eur DESC;""",
        
        "800V vs 400V Platform Comparison": """SELECT
    CASE
        WHEN v.battery_voltage >= 700 THEN '800V Platform'
        WHEN v.battery_voltage IS NOT NULL THEN '400V Platform'
        ELSE 'Other/Unknown'
    END AS architecture,
    COUNT(v.id) AS vehicles,
    ROUND(AVG(v.dc_charge_power_kw), 1) AS avg_dc_power_kw,
    MAX(v.dc_charge_power_kw) AS max_dc_power_kw,
    ROUND(AVG(v.dc_charge_time_10_80_min), 1) AS avg_charge_time_min
FROM vehicle_variants v
WHERE v.battery_voltage IS NOT NULL
GROUP BY architecture
ORDER BY avg_dc_power_kw DESC;""",
        
        "Database Schema Info": """SELECT 
    name AS table_name,
    type
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;"""
    }
    
    # Query selector
    selected_example = st.selectbox(
        "Choose an example query:",
        ["Custom Query"] + list(example_queries.keys())
    )
    
    # Query editor
    st.markdown("#### ✏️ SQL Query Editor")
    
    if selected_example == "Custom Query":
        default_query = "-- Write your SELECT query here\nSELECT * FROM manufacturers LIMIT 10;"
    else:
        default_query = example_queries[selected_example]
    
    query = st.text_area(
        "Enter your SQL query:",
        value=default_query,
        height=250,
        help="Only SELECT queries are allowed. Use JOIN to combine tables."
    )
    
    # Execute query button
    col1, col2 = st.columns([1, 4])
    with col1:
        execute_button = st.button("▶️ Run Query", type="primary", use_container_width=True)
    with col2:
        st.markdown("**Tip:** Press Ctrl+Enter in the query box to run")
    
    # Execute query
    if execute_button or (query and query.strip()):
        # Validate query (basic security check)
        query_upper = query.strip().upper()
        
        # Check if it's a SELECT query
        if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
            st.error("❌ Only SELECT queries are allowed. No INSERT, UPDATE, DELETE, DROP, etc.")
        elif any(dangerous in query_upper for dangerous in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']):
            st.error("❌ Potentially dangerous keywords detected. Only read-only queries are allowed.")
        else:
            try:
                # Execute query
                conn = get_connection(_current_release)
                start_time = datetime.now()
                df = pd.read_sql_query(query, conn)
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Display results
                st.success(f"✅ Query executed successfully in {execution_time:.3f} seconds")
                
                # Result statistics
                st.markdown(f"**Results:** {len(df)} rows × {len(df.columns)} columns")
                
                # Display results table
                st.markdown("#### 📊 Query Results")
                
                # Pagination for large results
                if len(df) > 100:
                    st.warning(f"⚠️ Large result set ({len(df)} rows). Showing first 100 rows. Use LIMIT in your query for better performance.")
                    st.dataframe(df.head(100), use_container_width=True, height=400)
                else:
                    st.dataframe(df, use_container_width=True, height=400)
                
                # Export options
                st.markdown("#### 💾 Export Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # CSV export
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"evdb_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # JSON export
                    json_data = df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📋 Download JSON",
                        data=json_data,
                        file_name=f"evdb_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col3:
                    # Excel export (requires openpyxl)
                    st.markdown("**Excel export:** Coming soon")
                
                # Show column info
                with st.expander("📋 Column Information"):
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.astype(str),
                        'Non-Null Count': df.count(),
                        'Null Count': df.isnull().sum()
                    })
                    st.dataframe(col_info, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Query error: {str(e)}")
                st.markdown("**Common issues:**")
                st.markdown("- Check table/column names (use the schema query to see available tables)")
                st.markdown("- Ensure proper JOIN syntax")
                st.markdown("- Verify column references")
    
    # Database schema reference
    st.markdown("---")
    st.markdown("#### 📖 Database Schema Reference")
    
    with st.expander("📊 Available Tables & Columns"):
        conn = get_connection(_current_release)
        
        # Get all tables
        tables = pd.read_sql_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """, conn)
        
        for table_name in tables['name']:
            st.markdown(f"**`{table_name}`**")
            
            # Get columns for this table
            columns = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
            
            # Display columns
            for _, col in columns.iterrows():
                null_str = "" if col['notnull'] == 1 else " (nullable)"
                pk_str = " 🔑" if col['pk'] == 1 else ""
                st.markdown(f"- `{col['name']}` - {col['type']}{null_str}{pk_str}")
            
            st.markdown("")  # Empty line between tables

elif page == "📚 Documentation":
    st.title("📚 Documentation")
    
    doc_section = st.selectbox(
        "Select documentation:",
        ["About EVDB", "API Documentation", "Contributing Guide", "FAQ"]
    )
    
    if doc_section == "About EVDB":
        st.markdown("""
        ## About EVDB
        
        **EVDB** (Electric Vehicle Database) is a community-driven, open-source database 
        providing comprehensive specifications, pricing, and market availability data for 
        electric vehicles worldwide.
        
        ### Mission
        
        Our mission is to make electric vehicle data freely accessible, accurate, and 
        comprehensive to support consumers, researchers, developers, and policymakers 
        in the transition to sustainable transportation.
        
        ### Key Features
        
        - **Comprehensive Specs:** Battery capacity, range, charging speeds, performance
        - **Market Pricing:** Real-world pricing across multiple markets
        - **Open Data:** CC BY-SA 4.0 license - free to use and share
        - **API Access:** Full RESTful and GraphQL API
        - **Community-Driven:** Anyone can contribute vehicle data
        
        ### Data Sources
        
        All data is sourced from:
        - Official manufacturer specifications
        - Government certification databases (EPA, WLTP)
        - Verified community contributions
        
        ### Technology Stack
        
        - **Data Format:** YAML source files with JSON Schema validation
        - **Database:** SQLite with full relational structure
        - **API:** Datasette (REST + GraphQL)
        - **Frontend:** Streamlit (this app)
        - **CI/CD:** GitHub Actions
        - **Hosting:** Streamlit Cloud (frontend), Vercel (API)
        
        ### License
        
        EVDB is licensed under **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike).
        
        This means you can:
        - ✅ Use the data commercially
        - ✅ Modify and redistribute
        - ✅ Build applications using the data
        
        As long as you:
        - 📝 Provide attribution
        - 🔄 Share modifications under the same license
        
        ### Contact & Links
        
        - **GitHub:** [github.com/gaia-charge/evdb](https://github.com/gaia-charge/evdb)
        - **API Docs:** [See API Documentation section]
        - **Issues:** [Report bugs or request features](https://github.com/gaia-charge/evdb/issues)
        - **Discussions:** [Join the conversation](https://github.com/gaia-charge/evdb/discussions)
        """)
    
    elif doc_section == "API Documentation":
        st.markdown("## API Documentation")
        st.markdown("""
        Complete reference for accessing EVDB data via REST and GraphQL APIs.
        Also available on [GitHub](https://github.com/gaia-charge/evdb/blob/main/API_DOCS.md).
        """)
        
        # Load and display API_DOCS.md
        api_docs = load_markdown_file("API_DOCS.md")
        st.markdown(api_docs)
    
    elif doc_section == "Contributing Guide":
        st.markdown("## Contributing to EVDB")
        st.markdown("""
        Learn how to add vehicles, improve data quality, and contribute to the project.
        Also available on [GitHub](https://github.com/gaia-charge/evdb/blob/main/CONTRIBUTING.md).
        """)
        
        # Load and display CONTRIBUTING.md
        contributing = load_markdown_file("CONTRIBUTING.md")
        st.markdown(contributing)
    
    elif doc_section == "FAQ":
        st.markdown("## Frequently Asked Questions")
        st.markdown("""
        Common questions about EVDB, data sources, and how to use the database.
        Also available on [GitHub](https://github.com/gaia-charge/evdb/blob/main/FAQ.md).
        """)
        
        # Load and display FAQ.md
        faq = load_markdown_file("FAQ.md")
        st.markdown(faq)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>
        EVDB is open-source and community-driven. Licensed under CC BY-SA 4.0.<br>
        <a href="https://github.com/gaia-charge/evdb" target="_blank">GitHub</a> • 
        <a href="https://github.com/gaia-charge/evdb/blob/main/CONTRIBUTING.md" target="_blank">Contribute</a> • 
        <a href="https://github.com/gaia-charge/evdb/issues" target="_blank">Report Issue</a>
    </p>
</div>
""", unsafe_allow_html=True)

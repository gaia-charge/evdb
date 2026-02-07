"""
EVDB - Electric Vehicle Database Explorer
A user-friendly Streamlit interface for exploring EV data
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="EVDB - Electric Vehicle Database",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection (cached)
@st.cache_resource
def get_connection():
    """Create cached database connection"""
    return sqlite3.connect('evdb.db', check_same_thread=False)

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
            mfr.name as manufacturer,
            m.name as model,
            v.variant_name,
            v.model_year,
            v.range_wltp_km,
            ma.price_base as price_eur
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
        ORDER BY v.id DESC
        LIMIT 5
    """, _conn)
    
    return stats

@st.cache_data(ttl=3600)
def search_vehicles(_conn, query):
    """Search vehicles by name (cached)"""
    search_query = f"%{query}%"
    return pd.read_sql_query("""
        SELECT 
            v.id,
            mfr.name as manufacturer,
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
        JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id
        WHERE 
            mfr.name LIKE ? OR
            m.name LIKE ? OR
            v.variant_name LIKE ?
        ORDER BY mfr.name, m.name, v.variant_name
        LIMIT 20
    """, _conn, params=(search_query, search_query, search_query))

# Initialize connection
conn = get_connection()

# Sidebar navigation
st.sidebar.title("⚡ EVDB")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "🔍 Browse Vehicles", "⚖️ Compare", "📊 Analytics", "💾 Data Explorer", "📚 Documentation"]
)

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
**GitHub:** [openclaw/evdb](https://github.com/openclaw/evdb)

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
        'US': '🇺🇸 United States',
        'FR': '🇫🇷 France',
        'PL': '🇵🇱 Poland',
        'IT': '🇮🇹 Italy'
    }
    
    market_df = stats['market_breakdown'].copy()
    market_df['Market'] = market_df['market_code'].map(market_names)
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
    latest['Vehicle'] = latest['manufacturer'] + ' ' + latest['model'] + ' ' + latest['variant_name']
    latest['Year'] = latest['model_year'].astype(int)
    latest['Range'] = latest['range_wltp_km'].apply(lambda x: f"{int(x)} km" if pd.notna(x) else "N/A")
    latest['Price'] = latest['price_eur'].apply(
        lambda x: f"€{int(x):,}" if pd.notna(x) else "TBD"
    )
    
    display_latest = latest[['Vehicle', 'Year', 'Range', 'Price']]
    
    st.dataframe(
        display_latest,
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
            display_results['Vehicle'] = (
                display_results['manufacturer'] + ' ' + 
                display_results['model'] + ' ' + 
                display_results['variant_name'] + ' (' + 
                display_results['model_year'].astype(str) + ')'
            )
            display_results['Battery'] = display_results['battery_usable_kwh'].apply(
                lambda x: f"{x:.1f} kWh" if pd.notna(x) else "N/A"
            )
            display_results['Range'] = display_results['range_wltp_km'].apply(
                lambda x: f"{int(x)} km" if pd.notna(x) else "N/A"
            )
            display_results['Power'] = display_results['total_power_kw'].apply(
                lambda x: f"{int(x)} kW" if pd.notna(x) else "N/A"
            )
            display_results['0-100'] = display_results['acceleration_0_100_sec'].apply(
                lambda x: f"{x:.1f}s" if pd.notna(x) else "N/A"
            )
            display_results['Price'] = display_results['price_eur'].apply(
                lambda x: f"€{int(x):,}" if pd.notna(x) else "TBD"
            )
            display_results['Market'] = display_results['market_code'].fillna('N/A')
            
            st.dataframe(
                display_results[['Vehicle', 'Battery', 'Range', 'Power', '0-100', 'Price', 'Market']],
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
    
    Check out our [Contributing Guide](https://github.com/openclaw/evdb/blob/main/CONTRIBUTING.md) to get started.
    """)

elif page == "🔍 Browse Vehicles":
    st.title("🔍 Browse Vehicles")
    st.info("🚧 Coming soon: Advanced filtering and browsing interface")
    st.markdown("""
    This page will include:
    - Interactive filters (price, range, charging speed, manufacturer, body style)
    - Sortable and searchable data table
    - Vehicle detail expansion
    - Export functionality (CSV/JSON)
    """)

elif page == "⚖️ Compare":
    st.title("⚖️ Compare Vehicles")
    st.info("🚧 Coming soon: Side-by-side vehicle comparison")
    st.markdown("""
    This page will include:
    - Multi-select vehicle picker (2-4 vehicles)
    - Side-by-side comparison table
    - Radar chart visualization
    - Bar charts for key metrics
    - Export comparison as PDF/PNG
    """)

elif page == "📊 Analytics":
    st.title("📊 Analytics Dashboard")
    st.info("🚧 Coming soon: Interactive data visualizations")
    st.markdown("""
    This page will include:
    - **Range Analysis:** Battery vs range, efficiency rankings
    - **Charging Speeds:** DC power comparison, 800V vs 400V
    - **Price Distribution:** Price histograms, value analysis
    - **Market Overview:** Market heatmap, manufacturer share
    """)

elif page == "💾 Data Explorer":
    st.title("💾 Data Explorer")
    st.info("🚧 Coming soon: SQL query interface for power users")
    st.markdown("""
    This page will include:
    - SQL query text editor
    - Pre-built query templates
    - Query result display
    - Export results (CSV/JSON)
    """)

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
        
        - **GitHub:** [github.com/openclaw/evdb](https://github.com/openclaw/evdb)
        - **API Docs:** [See API Documentation section]
        - **Issues:** [Report bugs or request features](https://github.com/openclaw/evdb/issues)
        - **Discussions:** [Join the conversation](https://github.com/openclaw/evdb/discussions)
        """)
    
    elif doc_section == "API Documentation":
        st.info("🚧 API documentation will be embedded here from API_DOCS.md")
        st.markdown("""
        Full API documentation is available in the repository:
        [API_DOCS.md](https://github.com/openclaw/evdb/blob/main/API_DOCS.md)
        """)
    
    elif doc_section == "Contributing Guide":
        st.info("🚧 Contributing guide will be embedded here from CONTRIBUTING.md")
        st.markdown("""
        Full contributing guide is available in the repository:
        [CONTRIBUTING.md](https://github.com/openclaw/evdb/blob/main/CONTRIBUTING.md)
        """)
    
    elif doc_section == "FAQ":
        st.info("🚧 FAQ will be embedded here from FAQ.md")
        st.markdown("""
        Full FAQ is available in the repository:
        [FAQ.md](https://github.com/openclaw/evdb/blob/main/FAQ.md)
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>
        EVDB is open-source and community-driven. Licensed under CC BY-SA 4.0.<br>
        <a href="https://github.com/openclaw/evdb" target="_blank">GitHub</a> • 
        <a href="https://github.com/openclaw/evdb/blob/main/CONTRIBUTING.md" target="_blank">Contribute</a> • 
        <a href="https://github.com/openclaw/evdb/issues" target="_blank">Report Issue</a>
    </p>
</div>
""", unsafe_allow_html=True)

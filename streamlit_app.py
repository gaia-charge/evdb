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
    st.markdown("Explore all vehicles with advanced filtering options")
    
    # Load all data
    @st.cache_data(ttl=3600)
    def load_browse_data(_conn):
        """Load all vehicle data with filters"""
        return pd.read_sql_query("""
            SELECT 
                v.id,
                mfr.name as manufacturer,
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
                ma.price_base as price_eur,
                ma.market_code
            FROM vehicle_variants v
            JOIN vehicle_models m ON v.model_id = m.id
            JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
            LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
            ORDER BY mfr.name, m.name, v.variant_name
        """, _conn)
    
    df = load_browse_data(conn)
    
    # Sidebar filters
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
    st.sidebar.markdown("#### Price (EUR)")
    price_min_val = int(df['price_eur'].min()) if df['price_eur'].notna().any() else 20000
    price_max_val = int(df['price_eur'].max()) if df['price_eur'].notna().any() else 150000
    
    price_range = st.sidebar.slider(
        "Price Range:",
        min_value=price_min_val,
        max_value=price_max_val,
        value=(price_min_val, price_max_val),
        step=5000,
        format="€%d"
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
        
        # Format display data
        display_df = filtered_df.copy()
        display_df['Vehicle'] = (
            display_df['manufacturer'] + ' ' + 
            display_df['model'] + ' ' + 
            display_df['variant_name'] + ' (' + 
            display_df['model_year'].astype(str) + ')'
        )
        display_df['Battery'] = display_df['battery_usable_kwh'].apply(
            lambda x: f"{x:.1f} kWh" if pd.notna(x) else "N/A"
        )
        display_df['WLTP Range'] = display_df['range_wltp_km'].apply(
            lambda x: f"{int(x)} km" if pd.notna(x) else "N/A"
        )
        display_df['Real Range'] = display_df['range_real_world_km'].apply(
            lambda x: f"{int(x)} km" if pd.notna(x) else "N/A"
        )
        display_df['Power'] = display_df['total_power_kw'].apply(
            lambda x: f"{int(x)} kW" if pd.notna(x) else "N/A"
        )
        display_df['0-100'] = display_df['acceleration_0_100_sec'].apply(
            lambda x: f"{x:.1f}s" if pd.notna(x) else "N/A"
        )
        display_df['DC Charge'] = display_df['dc_charge_power_kw'].apply(
            lambda x: f"{int(x)} kW" if pd.notna(x) else "N/A"
        )
        display_df['Price'] = display_df['price_eur'].apply(
            lambda x: f"€{int(x):,}" if pd.notna(x) else "TBD"
        )
        
        # Display table
        st.dataframe(
            display_df[[
                'Vehicle', 'body_style', 'Battery', 'WLTP Range', 
                'Real Range', 'Power', '0-100', 'DC Charge', 'drive_type', 'Price'
            ]].rename(columns={
                'body_style': 'Body',
                'drive_type': 'Drive'
            }),
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
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
        return pd.read_sql_query("""
            SELECT 
                v.id,
                mfr.name || ' ' || m.name || ' ' || v.variant_name || ' (' || v.model_year || ')' as full_name,
                mfr.name as manufacturer,
                m.name as model,
                v.variant_name,
                v.model_year,
                m.body_style,
                v.battery_usable_kwh,
                v.battery_chemistry,
                v.battery_architecture,
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
                v.ac_charge_time_0_100_min,
                ma.price_base as price_eur,
                ma.price_on_the_road as price_otr_eur
            FROM vehicle_variants v
            JOIN vehicle_models m ON v.model_id = m.id
            JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
            LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
            ORDER BY mfr.name, m.name, v.variant_name
        """, _conn)
    
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
            comparison_data[vehicle_name] = {
                'Manufacturer': row['manufacturer'],
                'Model': f"{row['model']} {row['variant_name']}",
                'Year': int(row['model_year']),
                'Body Style': row['body_style'] if pd.notna(row['body_style']) else 'N/A',
                'Drive Type': row['drive_type'] if pd.notna(row['drive_type']) else 'N/A',
                '': '**Battery & Range**',
                'Battery Capacity': f"{row['battery_usable_kwh']:.1f} kWh" if pd.notna(row['battery_usable_kwh']) else 'N/A',
                'Battery Chemistry': row['battery_chemistry'] if pd.notna(row['battery_chemistry']) else 'N/A',
                'Battery Architecture': row['battery_architecture'] if pd.notna(row['battery_architecture']) else 'N/A',
                'WLTP Range': f"{int(row['range_wltp_km'])} km" if pd.notna(row['range_wltp_km']) else 'N/A',
                'Real-World Range': f"{int(row['range_real_world_km'])} km" if pd.notna(row['range_real_world_km']) else 'N/A',
                'Consumption': f"{row['consumption_real_world_kwh_100km']:.1f} kWh/100km" if pd.notna(row['consumption_real_world_kwh_100km']) else 'N/A',
                ' ': '**Performance**',
                'Total Power': f"{int(row['total_power_kw'])} kW ({int(row['total_power_kw'] * 1.341)} hp)" if pd.notna(row['total_power_kw']) else 'N/A',
                'Total Torque': f"{int(row['total_torque_nm'])} Nm" if pd.notna(row['total_torque_nm']) else 'N/A',
                '0-100 km/h': f"{row['acceleration_0_100_sec']:.1f} sec" if pd.notna(row['acceleration_0_100_sec']) else 'N/A',
                'Top Speed': f"{int(row['top_speed_kph'])} km/h" if pd.notna(row['top_speed_kph']) else 'N/A',
                '  ': '**Charging**',
                'DC Fast Charge': f"{int(row['dc_charge_power_kw'])} kW" if pd.notna(row['dc_charge_power_kw']) else 'N/A',
                'DC 10-80%': f"{int(row['dc_charge_time_10_80_min'])} min" if pd.notna(row['dc_charge_time_10_80_min']) else 'N/A',
                'AC Charge': f"{row['ac_charge_power_kw']:.1f} kW" if pd.notna(row['ac_charge_power_kw']) else 'N/A',
                'AC 0-100%': f"{int(row['ac_charge_time_0_100_min'])} min" if pd.notna(row['ac_charge_time_0_100_min']) else 'N/A',
                '   ': '**Pricing (Germany)**',
                'Base Price': f"€{int(row['price_eur']):,}" if pd.notna(row['price_eur']) else 'TBD',
                'On-the-Road Price': f"€{int(row['price_otr_eur']):,}" if pd.notna(row['price_otr_eur']) else 'TBD',
            }
        
        # Create DataFrame for display
        comparison_table = pd.DataFrame(comparison_data)
        
        # Display table
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
            mfr.name as manufacturer,
            m.name as model,
            v.variant_name,
            v.model_year,
            m.body_style,
            v.battery_usable_kwh,
            v.battery_chemistry,
            v.battery_architecture,
            v.range_wltp_km,
            v.range_real_world_km,
            v.consumption_real_world_kwh_100km,
            v.dc_charge_power_kw,
            v.dc_charge_time_10_80_min,
            v.total_power_kw,
            v.drive_type,
            ma.price_base as price_eur
        FROM vehicle_variants v
        JOIN vehicle_models m ON v.model_id = m.id
        JOIN manufacturers mfr ON m.manufacturer_id = mfr.id
        LEFT JOIN market_availability ma ON v.id = ma.variant_id AND ma.market_code = 'DE'
        ORDER BY mfr.name, m.name, v.variant_name
        """
        return pd.read_sql_query(query, _conn)
    
    conn = get_connection()
    df = get_analytics_data(conn)
    
    # Create full vehicle name
    df['vehicle_name'] = df['manufacturer'] + ' ' + df['model'] + ' ' + df['variant_name']
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📏 Range Analysis",
        "⚡ Charging Speeds",
        "💰 Price Distribution",
        "🌍 Market Overview"
    ])
    
    # Tab 1: Range Analysis
    with tab1:
        st.markdown("### Battery Capacity vs. Range")
        st.markdown("Explore the relationship between battery size and real-world range")
        
        # Battery vs Range scatter plot
        fig_range = px.scatter(
            df.dropna(subset=['battery_usable_kwh', 'range_wltp_km']),
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
        top_charging = df.dropna(subset=['dc_charge_power_kw']).nlargest(15, 'dc_charge_power_kw')
        
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
                price_df,
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
            fig_price_body.update_xaxis(tickangle=45)
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
    
    # Tab 4: Market Overview
    with tab4:
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

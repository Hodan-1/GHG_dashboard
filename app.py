import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load both long and wide format data
@st.cache_data
def load_data():
    # Load long format for visualisations
    df_long = pd.read_csv("data/long_form_hierarchical.csv")
    
    # Create wide format for table view
    df_wide = df_long.pivot_table(
        index=['Year', 'Main_Category', 'Sub_Category', 'Detail_Category'],
        columns='Gas',
        values='Emissions_kt'
    ).reset_index()
    
    return df_long, df_wide

def filter_by_hierarchy(df, level):
    if level == "Main Sectors Only":
        return df[df['Detail_Category'].isna()]
    elif level == "Include Subsectors":
        return df[df['Detail_Category'].isna() | df['Sub_Category'].isna()]
    else:
        return df

# Load both formats
df_long, df_wide = load_data()

# Title
st.title(" Greenhouse Gas Emissions Dashboard")
st.markdown("###  Analysis of Emissions by Sector and Gas Type")

# Sidebar filters
st.sidebar.header("Filters")

# Year range selector
years = sorted(df_long['Year'].unique())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years))
)

# Main category selector - excluding "Total national emissions"
main_categories = sorted(df_long[df_long['Main_Category'] != "Total national emissions"]['Main_Category'].unique())
selected_main_cats = st.sidebar.multiselect(
    "Select Main Categories",
    options=main_categories,
    default=main_categories
)

# Gas type selector
gases = sorted(df_long['Gas'].unique())
selected_gases = st.sidebar.multiselect(
    "Select Gas Types",
    options=gases,
    default=gases
)

# Add hierarchy level selector
hierarchy_level = st.sidebar.radio(
    "Select Detail Level",
    ["Main Sectors Only", "Include Subsectors", "All Details"]
)

# Filter long format data
filtered_df_long = df_long[
    (df_long['Year'].between(year_range[0], year_range[1])) &
    (df_long['Main_Category'].isin(selected_main_cats)) &
    (df_long['Gas'].isin(selected_gases)) &
    (df_long['Main_Category'] != "Total national emissions")
]

# Filter wide format data
filtered_df_wide = df_wide[
    (df_wide['Year'].between(year_range[0], year_range[1])) &
    (df_wide['Main_Category'].isin(selected_main_cats)) &
    (df_wide['Main_Category'] != "Total national emissions")
]

# Apply hierarchy filter
filtered_df_long = filter_by_hierarchy(filtered_df_long, hierarchy_level)
filtered_df_wide = filter_by_hierarchy(filtered_df_wide, hierarchy_level)

# Create three columns for metrics
col1, col2, col3 = st.columns(3)

# Calculate averages
total_emissions = filtered_df_long['Emissions_kt'].sum()
avg_annual = filtered_df_long.groupby('Year')['Emissions_kt'].sum().mean()
num_sectors = filtered_df_long['Main_Category'].nunique()

# Display averages
col1.metric("Total Emissions (kt)", f"{total_emissions:,.0f}")
col2.metric("Average Annual Emissions (kt)", f"{avg_annual:,.0f}")
col3.metric("Number of Sectors", num_sectors)

# Create tabs for different visualisations
tab1, tab2 = st.tabs(["Emissions Over Time", "Sector Analysis"])

with tab1:
    # Time series plot
    emissions_by_year = filtered_df_long.groupby(['Year', 'Gas'])['Emissions_kt'].sum().reset_index()
    fig1 = px.line(
        emissions_by_year,
        x='Year',
        y='Emissions_kt',
        color='Gas',
        title='Emissions Trends by Gas Type',
        labels={'Emissions_kt': 'Emissions (kt)', 'Year': 'Year'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Stacked area chart by main category
    emissions_by_sector = filtered_df_long.groupby(['Year', 'Main_Category'])['Emissions_kt'].sum().reset_index()
    fig2 = px.area(
        emissions_by_sector,
        x='Year',
        y='Emissions_kt',
        color='Main_Category',
        title='Emissions by Sector Over Time',
        labels={'Emissions_kt': 'Emissions (kt)', 'Year': 'Year'}
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of total emissions by sector
        sector_total = filtered_df_long.groupby('Main_Category')['Emissions_kt'].sum().reset_index()
        fig3 = px.pie(
            sector_total,
            values='Emissions_kt',
            names='Main_Category',
            title='Distribution of Emissions by Sector'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Bar chart of emissions by gas type for each sector
        fig4 = px.bar(
            filtered_df_long.groupby(['Main_Category', 'Gas'])['Emissions_kt'].sum().reset_index(),
            x='Main_Category',
            y='Emissions_kt',
            color='Gas',
            title='Emissions by Sector and Gas Type',
            labels={'Emissions_kt': 'Emissions (kt)'}
        )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

  

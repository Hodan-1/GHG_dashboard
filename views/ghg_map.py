"""
GHG Map page for the GHG Emissions Dashboard.
Interactive world map showing CO2 emissions over time.
"""

import streamlit as st
import plotly.express as px
from helper.utils import create_complete_map_figure, get_co2_column


def render_ghg_map_page(sidebar_data):
    """Enhanced GHG Map page with better storytelling"""
    
    # Enhanced header with context
    st.markdown("""
    ### Welcome to the Climate Reporting Journey

    This interactive map visualises carbon dioxide (CO₂) emissions over time for UNFCCC Annex I countries.  
    Explore how these nations have shaped global emissions since 1990, data submitted under the earliest international climate agreements, when the world first united under the UNFCCC to address climate change.
    """)

    
    # Add context about what users will discover
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ###  **What You'll Discover**
        - **Emission hotspots** and their evolution
        - **Success stories** of countries reducing emissions
        - **Impact of global events** (economic crises, pandemics)
        - **Policy effectiveness** across different nations
        """)
    
    with col2:
        st.markdown("""
        ###  **The Data Story**
        - **33+ years** of official climate reporting
        - **Annex I countries**: Developed nations with binding targets
        - **Standardized reporting** through UNFCCC protocols
        - **Real policy impacts** reflected in the numbers
        """)
    
    with col3:
        st.markdown("""
        - **Press Play** to watch emissions evolve over time
        - **Hover over countries** for detailed insights
        - **Spot the trends** - which countries are leading?
        - **Connect the dots** between events and emissions
        """)
    
    st.markdown("---")
    
    # Use pre-loaded data
    all_emissions_df = st.session_state.preloaded_data['all_emissions']
    geojson = st.session_state.preloaded_data['geojson']
    year_range = sidebar_data['year_range']

    if all_emissions_df is not None and geojson is not None:
        # Add some quick stats before the map
        co2_column = get_co2_column(all_emissions_df)
        
        # Calculate interesting statistics
        total_emissions_latest = all_emissions_df[all_emissions_df['Year'] == year_range[1]][co2_column].sum()
        total_emissions_earliest = all_emissions_df[all_emissions_df['Year'] == year_range[0]][co2_column].sum()
        change_percent = ((total_emissions_latest - total_emissions_earliest) / total_emissions_earliest) * 100
        
        # Top emitters
        latest_year_data = all_emissions_df[all_emissions_df['Year'] == year_range[1]]
        top_emitters = latest_year_data.nlargest(3, co2_column)['Country'].tolist()
        
        # Quick insights box
        st.info(f"""
        **Quick Insights for {year_range[0]}-{year_range[1]}**:
        
        - **Total Change**: Annex I emissions have {'increased' if change_percent > 0 else 'decreased'} by **{abs(change_percent):.1f}%**
        - **Top 3 Emitters**: {', '.join(top_emitters)}
        - **Latest Total**: {total_emissions_latest:,.0f} kt CO₂ in {year_range[1]}
        - **Countries Tracked**: {len(latest_year_data)} Annex I nations
        """)
        
        # Use cached complete figure
        fig = create_complete_map_figure(all_emissions_df, year_range, geojson)
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption(" Use the play button to see emissions evolve over time, or drag the slider to jump to specific years!")

        # Enhanced expandable section with more engaging content
        with st.expander("Understanding the Climate Data "):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ####  **How is this data collected?**
                
                Since **1992**, countries have been required to report their greenhouse gas emissions annually. 
                This dashboard shows data from **Annex I countries** - the developed nations that took on 
                binding emission reduction targets under the Kyoto Protocol.
                
                **What makes this data special?**
                -  **Standardised methodology** across all countries
                -  **Independent verification** by international experts  
                -  **Policy-relevant** - directly used for climate negotiations
                -  **Comprehensive coverage** of all major emission sources
                """)
            
            with col2:
                st.markdown("""
                ####  **Why Annex I Countries Matter**
                
                These countries represent:
                - **~60% of historical emissions** since 1850
                - **Major economies** with significant climate policies
                - **Technology leaders** in clean energy innovation
                - **First movers** in carbon pricing and regulation
                
                **Key Milestones in This Data:**
                - **1997**: Kyoto Protocol signed
                - **2008-2012**: First Kyoto commitment period
                - **2015**: Paris Agreement adopted
                - **2020**: COVID-19 impact visible
                """)
        
        # Add a "What's Next" section
        st.markdown("### Want to find out more?")
        
        next_col1, next_col2, next_col3 = st.columns(3)
        
        with next_col1:
            st.markdown("""
            **📈 Emissions Trends**
            
            Dive deep into individual country stories. See how policies, 
            economic changes, and global events shaped emission trajectories.
            """)
        
        with next_col2:
            st.markdown("""
            **🏭 Sector Analysis**
            
            Discover which sectors drive emissions in each country. 
            Compare energy, transport, industry, and agriculture impacts.
            """)
        
        with next_col3:
            st.markdown("""
            **🌡️ Climate Impact**
            
            Connect emissions to real-world consequences. Explore the 
            relationship between emissions and extreme weather events.
            """)

    else:
        st.error("Required data not available")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import folium
from streamlit_folium import st_folium
import statsmodels.api as sm  
import json



# Set page configuration
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "GHG Map"

@st.cache_data    
def load_country_data(country_code):
    """Load data for a specific country with hierarchy levels"""
    country_path = f"data/processed_data/{country_code}"
    data_dict = {
        'Total': None,
        'Sectors': None,
        'Subsectors': None,
        'Sub-subsectors': None
    }
    
    for level in data_dict.keys():
        level_path = os.path.join(country_path, level.lower())
        if os.path.exists(level_path):
            files = glob.glob(os.path.join(level_path, "*.csv"))
            if files:
                data_dict[level] = pd.concat([pd.read_csv(f) for f in files])
    
    return data_dict

@st.cache_data
def load_weather_data():
    """Load extreme weather events data"""
    try:
        weather_data = pd.read_csv('data/EM-DATA/summary_extreme_weather_all_countries.csv')
        return weather_data
    except:
        return None

@st.cache_data
def load_temperature_data():
    """Load global temperature anomaly data"""
    try:
        temp_data = pd.read_csv('data/EM-DATA/global_temp_anomalies.csv')
        return temp_data
    except:
        return None  
     
@st.cache_data
def load_global_emission():
    """
    Load global emissions data
    """
    try:
        global_emissions = pd.read_csv("data/EM-DATA/global_emissions.csv")
        return global_emissions
    except:
        return None
    
@st.cache_data
def load_geojson():
    """Load the GeoJSON data for world countries"""
    try:
        with open('countries.geo.json') as f:
            geojson = json.load(f)
        return geojson
    except:
        return None
   
data_root = "data/processed_data"
country_folders = sorted([
    name for name in os.listdir(data_root)
    if os.path.isdir(os.path.join(data_root, name))
])

# Display uppercase in the sidebar
country_labels = [name for name in country_folders]

def conditional_sidebar():
    """
    Conditionally render sidebar based on current tab
    """

    # Sidebar country selector with unique key for each tab
    if st.session_state.current_tab == 'Emissions Trends':
        selected_label = st.sidebar.selectbox(
            "Select Country",
            options=country_labels,
            key="country_selectbox_map"
        )

    elif st.session_state.current_tab == 'Emissions Trends':
        selected_label = st.sidebar.selectbox(
            "Select Country",
            options=country_labels,
            key="country_selectbox_trends"
        )
    elif st.session_state.current_tab == 'Sector Distribution':
        selected_label = st.sidebar.selectbox(
            "Select Country",
            options=country_labels,
            key="country_selectbox_sector"
        )
    elif st.session_state.current_tab == 'Climate Change Impact':
        selected_label = st.sidebar.selectbox(
            "Select Country",
            options=country_labels,
            key="country_selectbox_impact"
        )
    elif st.session_state.current_tab == 'Data View':
        selected_label = st.sidebar.selectbox(
            "Select Country",
            options=country_labels,
            key="country_selectbox_view"
        )
    
    # Map label back to folder name
    selected_country_folder = selected_label

    # Load data for selected country
    data_dict = load_country_data(selected_country_folder)

    # Total emissions data (for Tab 1)
    total_emissions_df = data_dict['Total']

    if st.session_state.current_tab == 'GHG Map':
        if total_emissions_df is not None:
            # Year range selector
            years = sorted(total_emissions_df['Year'].unique())
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="year_range_map"
            )
        return selected_country_folder, year_range, data_dict, total_emissions_df, None, None, None

    elif st.session_state.current_tab == 'Emissions Trends':
        if total_emissions_df is not None:
            # Year range selector
            years = sorted(total_emissions_df['Year'].unique())
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="year_range_trends"
            )
        return selected_country_folder, year_range, data_dict, total_emissions_df, None, None, None

    elif st.session_state.current_tab == 'Sector Distribution':
        hierarchy_options = ['Sectors', 'Subsectors', 'Sub-subsectors (Energy)']
        selected_hierarchy = st.sidebar.radio(
            "Select Detail Level for Sector Analysis",
            options=hierarchy_options,
            key="hierarchy_radio"
        )

        # Get the correct dataset for sector analysis
        sector_df = data_dict.get(selected_hierarchy)

        if total_emissions_df is not None:
            # Year range selector
            years = sorted(total_emissions_df['Year'].unique())
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="year_range_sector"
            )

        if sector_df is not None:
            # Sector selector for Tab 2
            available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
            selected_sectors = st.sidebar.multiselect(
                "Select Sectors for Sector Analysis",
                options=available_sectors,
                default=available_sectors,
                key="sector_multiselect"
            )

        return selected_country_folder, year_range, data_dict, total_emissions_df, sector_df, selected_hierarchy, selected_sectors
    
    elif st.session_state.current_tab == 'Climate Change Impact':
        if total_emissions_df is not None:
            # Year range selector
            years = sorted(total_emissions_df['Year'].unique())
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="year_range_impact"
            )
        return selected_country_folder, year_range, data_dict, total_emissions_df, None, None, None

    elif st.session_state.current_tab == 'Data View':
        if total_emissions_df is not None:
            # Year range selector
            years = sorted(total_emissions_df['Year'].unique())
            year_range = st.sidebar.slider(
                "Select Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="year_range_view"
            )
        return selected_country_folder, year_range, data_dict, None, None, None, None





# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["GHG Map", "Emissions Trends", "Sector Distribution", " Climate Change Impact", "Data View"])
with tab1:
    st.session_state.current_tab = "GHG Map"
    year_range, data_dict, total_emissions_df = conditional_sidebar()

    st.header("Introduction to CO₂ Emissions by Country")
    
    st.write(
        "This interactive map displays carbon dioxide (CO₂) emissions over time "
        "for UNFCCC Annex I countries. Emissions are measured in kilotonnes (kt) "
        "and sourced from the Common Reporting Tables 2025, which reflect " 
        "standardised national greenhouse gas inventories submitted under international climate agreements." 
        " Hover over a country to explore emissions at a specific point in time."
    )
    # Get chosen gases
    co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]

    # Load GeoJSON data
    geojson = load_geojson()
    
    if geojson is not None and total_emissions_df is not None:
        # Create frames for animation
        frames = []
        
        # Get all years in the range
        years = range(year_range[0], year_range[1] + 1)
        
        # Get list of all available country folders
        all_country_folders = [name for name in os.listdir("data/processed_data") 
                            if os.path.isdir(os.path.join("data/processed_data", name))]
        
        # Create frames for each year
        for year in years:
            emissions_df = pd.DataFrame()
            for country_folder in all_country_folders:
                country_path = f"data/processed_data/{country_folder}/total"
                if os.path.exists(country_path):
                    files = glob.glob(os.path.join(country_path, "*.csv"))
                    if files:
                        df = pd.concat([pd.read_csv(f) for f in files])
                        year_data = df[df['Year'] == year]
                        if not year_data.empty:
                            emissions = {
                                'Country': country_folder,
                                co2_column: year_data[co2_column].sum()
                            }
                            emissions_df = pd.concat([emissions_df, pd.DataFrame([emissions])], 
                                                ignore_index=True)
            
            frame = go.Frame(
                data=[go.Choropleth(
                    locations=emissions_df['Country'],
                    z=emissions_df[co2_column],
                    geojson=geojson,
                    featureidkey="properties.name",
                    colorscale="YlOrRd",
                    zmin=0,
                    zmax=emissions_df[co2_column].max(),
                    colorbar=dict(
                        title="CO2 Emissions (kt)",
                        thickness=15,
                        len=0.5
                    ),
                    hovertemplate="<b>%{location}</b><br>" +
                                "CO2 Emissions: %{z:,.2f} kt<br>" +
                                "<i>Click for more information</i><extra></extra>"
                )],
                name=str(year)
            )
            frames.append(frame)

        # Create the base choropleth map (initial frame)
        fig = go.Figure()
        fig.add_trace(go.Choropleth(
            locations=frames[0].data[0].locations,
            z=frames[0].data[0].z,
            geojson=geojson,
            featureidkey="properties.name",
            colorscale="YlOrRd",
            zmin=0,
            zmax=max([frame.data[0].z.max() for frame in frames]),
            colorbar=dict(
                title="CO2 Emissions (kt)",
                thickness=15,
                len=0.5
            ),
            hovertemplate="<b>%{location}</b><br>" +
                        "CO2 Emissions: %{z:,.2f} kt<br>" +
                        "<i>Click for more information</i><extra></extra>"
        ))

        # Update layout
        fig.update_layout(
            title=f"Global CO2 Emissions by Country ({year_range[0]}-{year_range[1]})",
            margin={"r":0,"t":40,"l":0,"b":0},
            geo=dict(
                showframe=False,
                showcountries=True,
                showcoastlines=True,
                countrycolor="Black",
                showocean=True,
                oceancolor="LightBlue",
                projection_type="natural earth"
            ),
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                    'fromcurrent': True}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True},
                                        'mode': 'immediate',
                                        'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 20},
                    'prefix': 'Year:',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {
                        'args': [[f'{year}'],
                                {'frame': {'duration': 300, 'redraw': True},
                                'mode': 'immediate',
                                'transition': {'duration': 300}}],
                        'label': f'{year}',
                        'method': 'animate'
                    } for year in years
                ]
            }]
        )

        # Add frames to the figure
        fig.frames = frames

        st.plotly_chart(fig, use_container_width=True)
        st.caption("Carbon dioxide emissions over time (1990–2023) for Annex I countries as reported to the UNFCCC. Measured in kilotonnes of CO₂ equivalents.")

        # Introduction for GHG emissions
        with st.expander("Learn more about Greenhouse Gas reporting"):
            st.markdown("""
            Greenhouse gases (GHGs) trap heat in Earth's atmosphere and drive climate change.

            - **Carbon dioxide (CO₂)** is the most prominent GHG, emitted primarily from burning fossil fuels.
            - However, **CO₂ is not the only greenhouse gas**. Others include **methane (CH₄)**, **nitrous oxide (N₂O)**, and **fluorinated gases**, which also significantly contribute to global warming, some with much higher warming potential than CO₂.
            - This map focuses specifically on **CO₂ emissions** reported by **Annex I countries** under the **UNFCCC** framework.

            #### About the Data
            Since 1992, countries have reported annual emissions following UNFCCC guidelines. 
            The **Kyoto Protocol** and **Paris Agreement** have further shaped these reporting systems, introducing tools like the **Common Reporting Tables (CRTs)** for standardized submissions.

            *Click a country to explore its emissions, or visit the 'Emissions Trends' tab to compare changes over time.*
            """)

    else:
        st.error("Required data not available")

with tab2:
    st.session_state.current_tab = "Emissions Trends"
    selected_country_folder, year_range, data_dict, total_emissions_df = conditional_sidebar()

    st.header("National Emissions Trends")

    st.write("Greenhouse gases (GHGs) differ in how they're produced and how strongly they warm the planet."
    "In this section, you can explore how **total emissions have changed over time** for different gases, based on national inventories submitted via the **UNFCCC Common Reporting Tables (CRTs)**.")

    st.subheader("CO₂ Emissions Over Time")
    st.markdown("""
    Carbon dioxide (**CO₂**) is the most significant greenhouse gas globally, primarily  from **burning fossil fuels**, **industrial processes**, and **deforestation**.
    This line chart shows the trend in net CO₂ emissions (including removals where land-use changes absorb CO₂) across the selected time range.
    """)

    # Filter total emissions data by year
    filtered_total_df = total_emissions_df[
        total_emissions_df['Year'].between(year_range[0], year_range[1])
    ]

    # Get chosen gases
    co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]


    # First plot - CO2 Emissions
    st.subheader("CO2 Emissions Over Time")
    d1, d2 = st.tabs(["Graph", "Table"])

    with d1:
        fig_co2 = px.line(
            filtered_total_df,
            x='Year',
            y=co2_column,
            title='Net CO2 Emissions/Removals',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_co2, use_container_width=True, key='CO2 emission graph')

    with d2:
        st.subheader("CO2 Emissions Data Table")
        # Display data specific to CO2 emissions
        co2_data = filtered_total_df[['Year', co2_column]]
        st.dataframe(co2_data)
        
        # Download button for CO2 data
        csv_co2 = co2_data.to_csv(index=False)
        st.download_button(
            label="Download CO2 Data as CSV",
            data=csv_co2,
            file_name=f'co2_emissions_{selected_country_folder}.csv',
            mime='text/csv',
            key='download_co2'
        )

    # Gas selection for other gases
    selected_gases_tab1 = st.multiselect(
        "Select Gases for Emissions Trends",
        options=[co2_column] + other_gas_columns,
        default=[co2_column]
    )

    # Second plot - Other Greenhouse Gases
    st.subheader("Other Greenhouse Gases Over Time")
    d3, d4 = st.tabs(["Graph", "Table"])

    with d3:
        fig_other = px.line(
            filtered_total_df,
            x='Year',
            y=selected_gases_tab1,
            title='Other Greenhouse Gas Emissions',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_other, use_container_width=True, key='Other gases graph')

    with d4:
        st.subheader("Other Greenhouse Gases Data Table")
        # Display data for selected gases
        other_gases_data = filtered_total_df[['Year'] + selected_gases_tab1]
        st.dataframe(other_gases_data)
        
        # Download button for other gases data
        csv_other = other_gases_data.to_csv(index=False)
        st.download_button(
            label="Download Selected Gases Data as CSV",
            data=csv_other,
            file_name=f'other_gases_{selected_country_folder}.csv',
            mime='text/csv',
            key='download_other'
        )
    st.markdown("**You selected the following gases.**  "
    "Expand the sections below to learn more about their sources and environmental impact."
    "For a more detailed breakdown by emission sectors (e.g. transport, energy, agriculture), see the [**Sector Distribution**](#Sector Distribution) tab.")


    st.markdown("#### Gas Information")

    if "CO2 (kt)" in selected_gases_tab1:
        with st.expander("Carbon Dioxide (CO₂)"):
            st.markdown("""
            CO₂ is the most abundant human-emitted greenhouse gas. 
            It mainly comes from **fossil fuel combustion**, **deforestation**, and **Industrial Processes**.
            While less potent per molecule than other gases, it stays in the atmosphere for **hundreds of years**.

            **Info**: CO₂ accounts for over **75% of global GHG emissions**.
            """)

    if "CH4 (kt)" in selected_gases_tab1:
        with st.expander(" Methane (CH₄)"):
            st.markdown("""
            Methane is a ** short-lived climate pollutant**  over **25 times stronger than CO₂** over 100 years.
            It's mainly released by **livestock**, **landfills**, and **fossil fuel extraction**.    
            Methane breaks down faster than CO₂ but has a **much greater global warming potential** in the short term.
            """)

    if "N2O (kt)" in selected_gases_tab1:
        with st.expander("Nitrous Oxide (N₂O)"):
            st.markdown("""
            N₂O has a **global warming potential ~300 times that of CO₂**.
            It is mostly emitted from **agricultural activities**, especially **fertiliser use**, as well as **wastewater** and **industry**.
            
            It also contributes to the **depletion of the ozone layer**.
            """)

    if "HFCs (kt)" in selected_gases_tab1:
        with st.expander(" Hydrofluorocarbons (HFCs)"):
            st.markdown("""
            HFCs are synthetic gases used in **air conditioning**, **refrigeration**, and **aerosol propellants**.
            Their warming potential ranges from **hundreds to thousands of times** stronger than CO₂.
            
            Many are being phased out under international agreements like the **Kigali Amendment**.
            """)

    if "PFCs (kt)" in selected_gases_tab1:
        with st.expander(" Perfluorocarbons (PFCs)"):
            st.markdown("""
            PFCs are emitted during **aluminium production** and **semiconductor manufacturing**.
            They are extremely long-lived, lasting **up to 50,000 years**.

            Though emissions are low, their **climate impact is significant** per molecule.
            """)

    if "SF6 (kt)" in selected_gases_tab1:
        with st.expander(" Sulphur Hexafluoride (SF₆)"):
            st.markdown("""
            SF₆ is mainly used as an **insulating gas** in electrical systems.
            It is the **most potent greenhouse gas**, with a GWP more than **23,000 times greater than CO₂** over 100 years.

            Despite small quantities, its **impact is large** due to its strength and long atmospheric lifetime.
            """)

with tab3:
    st.session_state.current_tab = "Sector Distribution"
    selected_country_folder, year_range, data_dict, total_emissions_df, sector_df, selected_hierarchy, selected_sectors = conditional_sidebar()

    chart_explanations = {
    'United States': (
        "The United States has a diverse economy where **energy and transportation** are major contributors "
        "to greenhouse gas emissions. You'll likely see large $CO_2$ emissions from power generation and "
        "road transport, reflecting the country's reliance on fossil fuels. "
        "**Agriculture** is also a significant sector, and this is where you would see a notable distribution of **methane** emissions from livestock. "
        "Like Australia, the 'Land Use' sector can sometimes show negative emissions because forests and "
        "soil act as a **carbon sink**, absorbing more carbon than they release."
    ),
    'UK': (
        "The UK has made significant progress in decarbonizing its **energy sector**, largely by phasing out coal (last coal plant closed in 2024). "
        "The charts will show a decreasing share of emissions from this sector over time. "
        "**Industrial processes** and transportation remain key areas, with policies like carbon pricing "
        "influencing their emissions distribution. The 'Land Use' sector here also functions as a **carbon sink** due to "
        "reforestation and sustainable land management."
    ),
    'Australia': (
        "Australia's economy is heavily reliant on resource extraction and exports, especially coal. The "
        "charts for Australia will show a high concentration of emissions in the **energy sector** due to "
        "its coal-fired power plants. Like the US, Australia also has a large agricultural sector, "
        "contributing significantly to **methane** emissions from livestock. "
        "Notably, the 'Land Use, Land-Use Change, and Forestry' sector often has negative emissions, "
        "meaning it acts as a **carbon sink** by absorbing more carbon than it releases, thanks to "
        "reduced land clearing and reforestation efforts."
    ),
    'Ukraine': (
        "Ukraine's emissions profile is shaped by its heavy industry and energy sectors. The data reflects "
        "the country's industrial past, with a focus on decarbonization efforts as it aligns with EU standards. "
        "The charts may show emissions from **heavy manufacturing and industrial processes**, with future "
        "trends likely to show a shift towards greener energy sources."
    ),
    'Austria': (
        "Austria is a leader in renewable energy, particularly with its vast **hydropower resources**. The charts will "
        "reflect this, showing a much lower share of emissions from the energy sector compared to countries "
        "that rely on fossil fuels. The emissions distribution will likely be more concentrated in "
        "transport and industrial sectors. The extensive forests also make the 'Land Use' sector a significant **carbon sink**."
    )
}

    # This dictionary provides specific explanations for each type of gas.
    gas_explanations = {
        'CO2 (kt)': (
            "**Carbon Dioxide ($CO_2$)** is the primary greenhouse gas, mostly from the burning of fossil fuels "
            "in the **energy sector** (power plants, transportation) and **industrial processes**."
        ),
        'CH4 (kt)': (
            "**Methane ($CH_4$)** is a potent greenhouse gas, and its distribution is often concentrated "
            "in the **agriculture sector** (from livestock and land use), and the **waste sector** (from landfills)."
        ),
        'N2O (kt)': (
            "**Nitrous Oxide ($N_2O$)** primarily comes from the **agriculture sector**, particularly from soil "
            "management and fertilizer use. It can also be a byproduct of some industrial processes."
        ),
        'HFCs (kt)': (
            "**Hydrofluorocarbons (HFCs)** are a type of F-gas. They are not naturally occurring and are primarily "
            "used in industrial applications like refrigeration and air conditioning. In some cases, a specific "
            "industry's emissions might be 100% HFCs."
        ),
        'PFCs (kt)': (
            "**Perfluorocarbons (PFCs)** are potent F-gases. They are primarily a byproduct of industrial "
            "processes, such as aluminum smelting and semiconductor manufacturing."
        ),
        'SF6 (kt)': (
            "**Sulfur Hexafluoride ($SF_6$)** is an extremely potent F-gas with a long atmospheric lifetime. It "
            "is most commonly used as an electrical insulator in high-voltage equipment, which falls under "
            "the **industrial processes** sector."
        ),
    }

    policy_data = {
    'United States of America': {
        'Sectors': {
            'Energy': {
                'description': 'The U.S. is heavily investing in clean energy to decarbonize its grid, primarily through the Inflation Reduction Act (IRA).',
                'policies': [
                    'IRA Tax Credits: Generous tax credits for renewable energy projects (e.g., wind, solar) and technologies like carbon capture and storage (CCS).',
                    'State-level RPS: Many states have their own Renewable Portfolio Standards, mandating a percentage of electricity from renewable sources.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policy focuses on providing financial incentives for industrial decarbonization.',
                'policies': [
                    'IRA Funding: The IRA provides billions in funding for industrial technologies and tax credits for clean hydrogen and CCS deployment.',
                    'AIM Act: The American Innovation and Manufacturing Act phases down the use of hydrofluorocarbons (HFCs), which are potent greenhouse gases.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies are aimed at supporting sustainable land management practices and reducing agricultural emissions.',
                'policies': [
                    'IRA Conservation Programs: The IRA allocates significant funding to boost conservation programs and incentivize climate-smart agriculture.',
                    'Biofuels Initiatives: Supports the production and use of biofuels to reduce emissions from the transportation sector.',
                ]
            },
            'Waste': {
                'description': 'Focuses on reducing methane emissions from landfills through collection and use.',
                'policies': [
                    'Landfill Methane Rule: Federal regulations require large landfills to capture methane emissions.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The IRA is the key driver, providing tax credits for renewable energy projects and carbon capture.',
                'policies': [
                    'IRA Clean Electricity Tax Credits: Provides credits for wind, solar, and other zero-emission technologies.',
                    'Carbon Capture Tax Credits (45Q): Offers significant tax credits for companies that capture and store CO2.',
                ]
            },
            'Road Transport': {
                'description': 'Federal and state policies promote the transition to electric vehicles.',
                'policies': [
                    'EV Tax Credits: Consumers can get up to $7,500 for purchasing new electric vehicles under the IRA.',
                    'CAFE Standards: Federal regulations that mandate increasing fuel efficiency for all vehicles.',
                ]
            },
        }
    },
    'United Kingdom': {
        'Sectors': {
            'Energy': {
                'description': 'The UK has rapidly decarbonized its energy sector by phasing out coal and  investing in offshore wind.',
                'policies': [
                    'Offshore Wind Target: Aims for 50 GW of offshore wind capacity by 2030.',
                    'Contracts for Difference (CfD): A scheme that provides long-term price certainty for renewable energy investors.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are focused on industrial decarbonization and transitioning to low-carbon fuels and technologies.',
                'policies': [
                    'Carbon Pricing: The UK Emissions Trading Scheme (ETS) places a cap and price on carbon, encouraging industries to reduce emissions.',
                    'Industrial Decarbonisation Strategy: A plan to transition to low-carbon fuels (like hydrogen) and technologies in key industrial clusters.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies support a move to sustainable farming practices and better land management.',
                'policies': [
                    'Environmental Land Management Schemes (ELMs): Incentivizes farmers to adopt environmentally friendly practices.',
                    'Tree Planting Targets: Aims to increase tree cover to absorb more carbon.',
                ]
            },
            'Waste': {
                'description': 'Policy focuses on increasing recycling rates and diverting waste from landfills to reduce methane.',
                'policies': [
                    'Waste and Resources Strategy: Sets targets for higher recycling rates and a move towards a circular economy.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The UK has successfully phased out coal and is now focused on ramping up renewables.',
                'policies': [
                    'Final Coal Plant Closure: The last coal-fired power plant closed in 2024.',
                    'CfD Auctions: Government-led auctions to secure investment in new renewable energy projects at a set price.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are designed to accelerate the transition to electric vehicles.',
                'policies': [
                    '2035 ICE Ban: A policy to ban the sale of new petrol and diesel cars and vans from 2035.',
                    'Zero Emission Vehicle Mandate: Requires car manufacturers to sell a rising percentage of zero-emission vehicles annually.',
                ]
            },
        }
    },
    'Australia': {
        'Sectors': {
            'Energy': {
                'description': 'The electricity sector is Australia\'s largest source of emissions due to its reliance on coal. Policies are aimed at a rapid transition to renewables.',
                'policies': [
                    'Safeguard Mechanism: Sets emissions limits for Australia’s largest industrial polluters, requiring them to reduce emissions or buy offsets.',
                    'Capacity Investment Scheme (CIS): Provides revenue certainty for new clean energy projects.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are focused on managing emissions from industry and chemical processes.',
                'policies': [
                    'Safeguard Mechanism: Covers industrial facilities, encouraging them to invest in emissions reduction technologies.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policy provides incentives for farmers to adopt sustainable practices and sequester carbon.',
                'policies': [
                    'Carbon Farming Initiative: Supports farmers in undertaking projects to reduce emissions or store carbon in the landscape.',
                    'National Methane Program: Initiatives aimed at reducing methane from livestock through improved feed and management.',
                ]
            },
            'Waste': {
                'description': 'Policies focus on landfill gas capture and improved waste management.',
                'policies': [
                    'Landfill Gas Capture: Regulations and incentives to capture methane from landfills for energy generation.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The Capacity Investment Scheme is a key tool for accelerating the transition away from coal.',
                'policies': [
                    'Capacity Investment Scheme (CIS): Provides a government-backed revenue floor for new clean energy projects.',
                    'State Renewable Energy Zones: State-level initiatives to build out infrastructure for large-scale solar and wind projects.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are focused on encouraging the uptake of electric vehicles.',
                'policies': [
                    'EV Subsidies and Tax Breaks: Provides financial incentives for purchasing EVs.',
                ]
            },
        }
    },
    'Ukraine': {
        'Sectors': {
            'Energy': {
                'description': 'Climate policy is heavily influenced by EU accession and the need for green post-war reconstruction.',
                'policies': [
                    'EU Alignment: Adopting EU climate and energy policies as part of its path to joining the European Union.',
                    'Green Reconstruction: Plans to rebuild a decentralized, modern energy grid with a higher share of renewables to improve energy security.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Focuses on improving energy efficiency in industry and reducing emissions from processes.',
                'policies': [
                    'Energy Efficiency Fund: A state-run program that provides financial support for businesses to implement energy-saving measures.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies focus on sustainable farming and improving waste management in the agricultural sector.',
                'policies': [
                    'Land Management Initiatives: Promotes sustainable land use to combat degradation and support biodiversity.',
                    'Biomass for Energy: Incentives for using agricultural waste for energy generation.',
                ]
            },
            'Waste': {
                'description': 'Policies aim to modernize waste management to reduce methane emissions.',
                'policies': [
                    'National Waste Management Strategy: Aims to improve waste collection and processing, including better landfill gas management.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'Policies promote a shift to renewable energy and a more resilient, decentralized grid.',
                'policies': [
                    'Green Tariff: A feed-in tariff system that encourages investment in renewable energy projects.',
                    'Grid Modernization: Post-war reconstruction efforts prioritize a modern, decentralized grid.',
                ]
            },
            'Road Transport': {
                'description': 'Policies are aimed at promoting the use of electric vehicles and alternative fuels.',
                'policies': [
                    'EV Subsidies: Provides incentives for the purchase of electric vehicles.',
                ]
            },
        }
    },
    'Austria': {
        'Sectors': {
            'Energy': {
                'description': 'Austria is a leader in renewable electricity, with a goal of achieving 100% renewable electricity by 2030.',
                'policies': [
                    'Renewable Energy Expansion Act: Sets a target of adding 27 TWh of renewable electricity by 2030.',
                    'EU ETS: As an EU member, heavy industry and power sectors are covered by the EU Emissions Trading System.',
                ]
            },
            'Industrial Processes & Product Use': {
                'description': 'Policies are tied to EU-wide regulations and domestic support for green technologies.',
                'policies': [
                    'EU ETS: Regulates emissions for large industrial facilities.',
                    'Green Industrial Strategy: Initiatives to promote clean technologies and processes, such as green hydrogen.',
                ]
            },
            'Agriculture, Forestry & Other Land Use': {
                'description': 'Policies focus on sustainable agriculture and the preservation of natural landscapes.',
                'policies': [
                    'Adaptation Strategy: The Austrian Strategy for Adaptation to Climate Change includes specific measures for the agricultural sector.',
                    'Biofuels Mandate: Policies that require a certain percentage of transport fuels to be sourced from biofuels.',
                ]
            },
            'Waste': {
                'description': 'Austria has achieved significant emissions reductions in this sector through improved management and recycling.',
                'policies': [
                    'Waste Management Strategy: Continuous improvement in waste collection and recycling to divert waste from landfills.',
                ]
            },
        },
        'Subsectors': {
            'Electricity & Heat Generation': {
                'description': 'The country leverages its vast hydropower and biomass resources to achieve high levels of renewable energy.',
                'policies': [
                    'Hydropower Investment: Ongoing investment in hydropower, a major source of renewable energy.',
                    'Renewable Energy Act: Provides financial support and a legal framework for renewable energy development.',
                ]
            },
            'Road Transport': {
                'description': 'Policies aim to shift people away from private cars and towards public transport and EVs.',
                'policies': [
                    'Climate Ticket: An affordable, nationwide public transport pass.',
                    'EV Subsidies: Provides financial incentives for the purchase of electric vehicles and charging infrastructure.',
                ]
            },
        }
    }
}
    st.header("Sector Distribution")
    st.write("Here, you can explore a detailed breakdown of greenhouse gas emissions by sector over time. Below the charts, you'll find an overview of the specific climate policies implemented in the selected country to address these emissions.")

    if sector_df is not None:
        # Sector selector for Tab 2
        available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
        selected_sectors = st.multiselect(
            "Select Sectors for Sector Analysis",
            options=available_sectors,
            default=available_sectors
        )

        # Gas selector for Bar Chart (Checkboxes)
        available_gases_tab2_bar = [co2_column] + other_gas_columns
        selected_gases_tab2_bar = st.multiselect(
            "Select Gases for Bar Chart",
            options=available_gases_tab2_bar,
            default=[co2_column]  # Default to CO2
        )

        

        # Filter sector data
        filtered_sector_df = sector_df[
            (sector_df['Year'].between(year_range[0], year_range[1])) &
            (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
        ]

        # Bar chart of emissions by gas type for each sector
        st.subheader("Emissions by Sector and Gas Type")
        latest_year = filtered_sector_df['Year'].max()
        latest_data = filtered_sector_df[filtered_sector_df['Year'] == latest_year]

        # Melt the data for the selected gases
        latest_data_melted = latest_data.melt(
            id_vars=['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'],
            value_vars=selected_gases_tab2_bar,
            var_name='Gas',
            value_name='Emissions_kt'
        )

        fig_bar = px.bar(
            latest_data_melted,
            x='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
            y='Emissions_kt',
            color='Gas',
            title=f'Emissions by Sector and Gas Type ({latest_year})',
            labels={'Emissions_kt': 'Emissions (kt)',
                    'GREENHOUSE GAS SOURCE AND SINK CATEGORIES': 'Sector'}
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True, key='Sector bar chart')

        if selected_label in chart_explanations:
            st.write(chart_explanations[selected_label])

        # Gas selector for Pie Chart (Dropdown)
        available_gases_tab2_pie = [co2_column] + other_gas_columns
        selected_gas_tab2_pie = st.selectbox(
            "Select Gas for Pie Chart",
            options=available_gases_tab2_pie,
            index=0  # Default to the first gas (CO2)
        )
        # Pie chart of emissions distribution by sector
        st.subheader("Distribution of Emissions by Sector")
        fig_pie = px.pie(
            latest_data,
            values=selected_gas_tab2_pie,
            names='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
            title=f'Distribution of {selected_gas_tab2_pie} by Sector ({latest_year})'
        )
        st.plotly_chart(fig_pie, use_container_width=True, key='Sector pie chart')

        # Display the explanation for the selected gas
        if selected_gas_tab2_pie in gas_explanations:
            st.write(gas_explanations[selected_gas_tab2_pie])

        st.markdown("---")
        
        # Stacked area chart showing emissions by sector over time
        t1, t2 = st.tabs(['Area Chart', 'Line Chart'])
        st.subheader("Emissions by Sector Over Time")
        with t1:
            fig_area = px.area(
            filtered_sector_df,
            x='Year',
            y=selected_gas_tab2_pie,
            color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
            title=f'{selected_gas_tab2_pie} Emissions by Sector Over Time',
            labels={'value': 'Emissions (kt)'}
        )
            st.plotly_chart(fig_area, use_container_width=True, key='area  chart')

        with t2:
            fig_line = px.line(
            filtered_sector_df,
            x='Year',
            y=selected_gas_tab2_pie,
            color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
            title=f'{selected_gas_tab2_pie} Emissions by Sector Over Time',
            labels={'value': 'Emissions (kt)'}
        )
            st.plotly_chart(fig_line, use_container_width=True, key='line_chart')

    if selected_hierarchy == 'Sectors':
        st.markdown("### Sector-Level Policies")
        if selected_label in policy_data and 'Sectors' in policy_data[selected_label]:
            for sector, details in policy_data[selected_label]['Sectors'].items():
                with st.expander(f"**{sector}**"):
                    st.write(details['description'])
                    st.markdown("##### Key Policies:")
                    for policy in details['policies']:
                        st.markdown(f"- {policy}")
        else:
            st.write(f"No sector-level policy data available for {selected_label}.")

    elif selected_hierarchy == 'Subsectors':
        st.markdown("### Subsector-Level Policies")
        if selected_label in policy_data and 'Subsectors' in policy_data[selected_label]:
            for subsector, details in policy_data[selected_label]['Subsectors'].items():
                with st.expander(f"**{subsector}**"):
                    st.write(details['description'])
                    st.markdown("##### Key Policies:")
                    for policy in details['policies']:
                        st.markdown(f"- {policy}")
        else:
            st.write(f"No subsector-level policy data available for {selected_label}.")
    
    elif selected_hierarchy == 'Sub-subsectors':
        st.warning(
            "The policy data for 'Sub-subsectors' is not yet available. "
            "Please select 'Sectors' or 'Subsectors'."
        )    

    st.markdown("---")
    st.header("Global Climate Commitments & Policies by Sector")

    sector_goals = {
        "Energy Supply": """
            - Coal phase-out by 2030 (EU pledge)
            - Net-zero energy sector by 2050 (EU pledge)
            - 100% clean electricity target in many NDCs
            """,
        "Transport": """
            - Phase-out of internal combustion engine cars (2035 in EU)
            - 100% EV sales by 2035 in some countries
            - CORSIA (aviation carbon offsetting)) agreement for aviation (2021). Although weekly enforced.
            """,
        "Industry": """
            - EU ETS (carbon market), with stricter caps post-2020
            - Clean industrial strategy (e.g. hydrogen, CCUS)
            """,
        "Agriculture": """
            - Global Methane Pledge (30% reduction) by 2030
            - Climate-smart farming & soil carbon programs
            - Sustainable livestock and fertilizer practices
            """,
        "Residential & Commercial": """
            - All new buildings to be net-zero carbon by 2030 (many NDCs)
            - Renovation wave across EU
            """,
        "Waste": """
            - Landfill bans, methane capture regulations
            - Circular economy frameworks in most Annex I countries
            """
    }

    # Filter to sectors currently selected, or all if none selected
    goals_sectors = selected_sectors if selected_sectors else list(sector_goals.keys())

    selected_sector_goal = st.selectbox(
        "Select a sector to view global climate commitments:",
        options=goals_sectors
    )

    if selected_sector_goal in sector_goals:
        st.markdown(f"### Global Climate Commitments for {selected_sector_goal}")
        st.markdown(sector_goals[selected_sector_goal])

with tab4:  
    st.session_state.current_tab = "Climate Change Impact"
    selected_country_folder, year_range, data_dict, total_emissions_df = conditional_sidebar()

    st.header("Climate Change Impact Analysis")
    
    # Load all required data
    weather_data = load_weather_data()
    temp_data = load_temperature_data()
    emissions_data = load_global_emission()
    
    if all(data is not None for data in [weather_data, temp_data, total_emissions_df]):
        # 1. Global Temperature Changes
        st.subheader("Global Temperature Changes")
        st.markdown("""
        Global temperature changes are one of the primary indicators of climate change. 
        The temperature anomaly shows how much warmer or cooler a period is compared to the baseline period (1951-1980).
        """)
        
        filtered_temp_data = temp_data[temp_data['Year'].between(year_range[0], year_range[1])]
        
        # Temperature metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            temp_change = filtered_temp_data['Temperature_Anomaly'].iloc[-1] - filtered_temp_data['Temperature_Anomaly'].iloc[0]
            st.metric("Total Temperature Change", f"{temp_change:.2f}°C", delta=f"{temp_change:.2f}°C")
        with col2:
            avg_temp = filtered_temp_data['Temperature_Anomaly'].mean()
            st.metric("Average Temperature Anomaly", f"{avg_temp:.2f}°C")
        with col3:
            latest_temp = filtered_temp_data['Temperature_Anomaly'].iloc[-1]
            st.metric("Latest Temperature Anomaly", f"{latest_temp:.2f}°C")

        # Temperature trend visualization
        fig_temp = px.line(
            filtered_temp_data,
            x='Year',
            y='Temperature_Anomaly',
            title='Global Temperature Anomalies Over Time',
            labels={'Temperature_Anomaly': 'Temperature Anomaly (°C)'}
        )
        fig_temp.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Baseline")
        st.plotly_chart(fig_temp, use_container_width=True)

        st.markdown("---")

        # 2. Relationship with Global CO2 Emissions
        st.subheader("Global Temperature and CO2 Emissions")
        st.markdown("""
        Carbon dioxide (CO₂) is the primary greenhouse gas contributing to global warming. 
        Here we can see the relationship between global temperature changes and CO₂ emissions.
        """)
        
        # Create combined global dataset
        global_combined = pd.merge(
            filtered_temp_data,
            emissions_data[['Year', 'CO2']],
            on='Year',
            how='inner'
        )
        
        # Combined temperature and emissions visualization
        fig_global = go.Figure()
        
        fig_global.add_trace(go.Scatter(
            x=global_combined['Year'],
            y=global_combined['Temperature_Anomaly'],
            name='Temperature Anomaly',
            yaxis='y1'
        ))
        
        fig_global.add_trace(go.Scatter(
            x=global_combined['Year'],
            y=global_combined['CO2'],
            name='Global CO2 Emissions',
            yaxis='y2'
        ))
        
        fig_global.update_layout(
            title='Global Temperature Anomalies and CO2 Emissions',
            yaxis=dict(title='Temperature Anomaly (°C)'),
            yaxis2=dict(title='CO2 Emissions (kt)', overlaying='y', side='right')
        )
        
        st.plotly_chart(fig_global, use_container_width=True)

        # Correlation scatter plot
        fig_scatter = px.scatter(
            global_combined,
            x='CO2',
            y='Temperature_Anomaly',
            title='Temperature Anomaly vs CO2 Emissions',
            labels={'CO2': 'CO2 Emissions (kt)', 'Temperature_Anomaly': 'Temperature Anomaly (°C)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")

        # 3. National Level Impacts
        st.subheader(f"Local Impact: Extreme Weather Events in {selected_label}")
        st.markdown("""
        As global temperatures rise, countries experience increased frequency and intensity of extreme weather events. 
        Here we examine the relationship between national emissions and extreme weather events.
        """)
        
        # Filter for selected country
        country_weather = weather_data[weather_data['Country'] == selected_label]
        country_emissions = total_emissions_df  # Your UNFCCC data for the selected country
        
        # National overview metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_events = len(country_weather)
            st.metric("Total Extreme Events", total_events)
        with col2:
            total_deaths = country_weather['Total Deaths'].sum()
            st.metric("Total Deaths", f"{total_deaths:,}")
        with col3:
            total_affected = country_weather['Total Affected'].sum()
            st.metric("Total People Affected", f"{total_affected:,}")

        # Event analysis toggle
        chart_type = st.radio(
            "Select Analysis View",
            ["Annual Frequency", "Event Types Distribution"]
        )

        if chart_type == "Annual Frequency":
            yearly_events = country_weather.groupby('Year').size().reset_index(name='Number of Events')
            fig_events = px.bar(
                yearly_events,
                x='Year',
                y='Number of Events',
                title=f'Annual Extreme Weather Events in {selected_label}'
            )
            st.plotly_chart(fig_events, use_container_width=True)
        else:
            event_dist = country_weather.groupby(['Year', 'Disaster Type']).size().reset_index(name='count')
            fig_dist = px.bar(
                event_dist,
                x='Year',
                y='count',
                color='Disaster Type',
                title=f'Types of Extreme Weather Events in {selected_label}',
                barmode='stack'
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        # Combine national data
        national_combined = pd.merge(
            country_weather.groupby('Year').agg({
                'Total Deaths': 'sum',
                'Total Affected': 'sum',
                'Disaster Type': 'count'
            }).reset_index(),
            country_emissions[['Year', co2_column]],
            on='Year',
            how='inner'
        )
        
        # National visualization
        fig_national = px.scatter(
            national_combined,
            x=co2_column,
            y='Disaster Type',
            size='Total Affected',
            hover_data=['Year', 'Total Deaths'],
            title=f'Relationship between CO2 Emissions and Extreme Weather Events in {selected_label}'
        )
        st.plotly_chart(fig_national, use_container_width=True)

        # Key insights
        st.subheader("Key Findings")
        global_correlation = global_combined['Temperature_Anomaly'].corr(global_combined['CO2'])
        national_correlation = national_combined[co2_column].corr(national_combined['Disaster Type'])
        
        st.info(f"""
        Analysis Summary:
        * Global temperature-emissions correlation: {global_correlation:.2f}
        * {selected_label}'s emissions-extreme events correlation: {national_correlation:.2f}
        * Most common disaster type in {selected_label}: {country_weather['Disaster Type'].mode().iloc[0]}
        * Global temperature increase: {temp_change:.2f}°C
        * Total affected people in {selected_label}: {total_affected:,}
        """)

    else:
        st.error("Required data not available")


with tab5:
    st.session_state.current_tab = "Data View"
    selected_country_folder, year_range, data_dict = conditional_sidebar()

    st.header(" Data Explorer & Download")

    st.markdown("Browse and download datasets including GHG emissions, gas species, temperature anomalies, and extreme weather events.")

    dataset_options = {
        "Total Emissions": os.path.join(data_root, selected_country_folder, "total", f"{selected_country_folder}_total_combined.csv"),
        "Sector Emissions": os.path.join(data_root, selected_country_folder, "sectors", f"{selected_country_folder}_sectors_combined.csv"),
        "Subsector Emissions": os.path.join(data_root, selected_country_folder, "subsectors", f"{selected_country_folder}_subsectors_combined.csv"),
        "Sub-subsector Emissions": os.path.join(data_root, selected_country_folder, "sub_subsectors", f"{selected_country_folder}_sub_subsectors_combined.csv"),
        "Extreme Weather": "data/EM-DATA/summary_extreme_weather_all_countries.csv",
        "Temperature Anomalies": "data/EM-DATA/global_temp_anomalies.csv"
    }

    # Add gas versions of each hierarchy level
    gas_species_folder = os.path.join(data_root, selected_country_folder)
    for gas_folder in os.listdir(gas_species_folder):
        gas_path = os.path.join(gas_species_folder, gas_folder)
        if not os.path.isdir(gas_path):
            continue

        gas = gas_folder.upper()
        for level in ["total", "sectors", "subsectors", "sub_subsectors"]:
            combined_file = os.path.join(gas_path, level, f"{selected_country_folder}_{level}_{gas.lower()}_combined.csv")
            if os.path.exists(combined_file):
                key = f"{gas} - {level.capitalize()} Emissions"
                dataset_options[key] = combined_file

    selected_dataset_name = st.selectbox("Select a dataset to explore", list(dataset_options.keys()))
    dataset_path = dataset_options[selected_dataset_name]

    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)

        if 'Year' in df.columns:
            years = sorted(df['Year'].dropna().unique())
            year_filter = st.slider("Filter by Year", min_value=int(min(years)), max_value=int(max(years)),
                                    value=(int(min(years)), int(max(years))))
            df = df[df['Year'].between(year_filter[0], year_filter[1])]

        st.write(f"Preview of **{selected_dataset_name}**")
        st.dataframe(df.head(100))

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f" Download {selected_dataset_name} as CSV",
            data=csv,
            file_name=f"{selected_dataset_name.replace(' ', '_').lower()}.csv",
            mime='text/csv'
        )
    else:
        st.warning("Dataset not found.")

    st.markdown("---")
    st.subheader(" Dataset Descriptions")


# Metrics summary (move to top later)
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

latest_year = filtered_total_df['Year'].max()
total_co2 = filtered_total_df[co2_column].sum()
avg_annual_co2 = filtered_total_df.groupby('Year')[co2_column].sum().mean()
latest_co2 = filtered_total_df[filtered_total_df['Year'] == latest_year][co2_column].sum()

col1.metric("Total CO2 Emissions", f"{total_co2:,.0f} kt")
col2.metric("Average Annual CO2", f"{avg_annual_co2:,.0f} kt")
col3.metric("Latest Year CO2", f"{latest_co2:,.0f} kt")


# Footer
st.markdown("---")
st.markdown("Data source: National Greenhouse Gas Inventory Submissions")

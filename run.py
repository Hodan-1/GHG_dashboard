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

def load_global_emission():
    """Load global emissions data"""
    try:
        global_emissions = pd.read_csv("data/EM-DATA/global_emissions.csv")
        return global_emissions
    except:
        return None

def load_geojson():
    """Load the GeoJSON data for world countries"""
    try:
        with open('countries.geo.json') as f:
            geojson = json.load(f)
        return geojson
    except:
        return None
    
@st.cache_data
def load_all_total_emissions():
    all_country_folders = [
        name for name in os.listdir("data/processed_data")
        if os.path.isdir(os.path.join("data/processed_data", name))
    ]
    
    all_data = []
    for country_folder in all_country_folders:
        country_path = f"data/processed_data/{country_folder}/total"
        if os.path.exists(country_path):
            files = glob.glob(os.path.join(country_path, "*.csv"))
            for f in files:
                df = pd.read_csv(f)
                df = df[df['Year'] >= 1990]  
                df["Country"] = country_folder  # Keep track of country
                all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return None    

data_root = "data/processed_data"
country_folders = sorted([
    name for name in os.listdir(data_root)
    if os.path.isdir(os.path.join(data_root, name))
])

# Display uppercase in the sidebar
country_labels = [name for name in country_folders]

# Dynamic Sidebar Functions
def get_ghg_map_sidebar():
    """Sidebar for GHG Map page - only year range"""
    sidebar_data = {
        'year_range': None,
    }
    
    # Load all emissions data to get year range
    all_emissions_df = load_all_total_emissions()
    if all_emissions_df is not None:
        years = sorted(all_emissions_df['Year'].unique())
        sidebar_data['year_range'] = st.sidebar.slider(
            "Select Year Range",
            min_value=min(years),
            max_value=max(years),
            value=(min(years), max(years)),
            key="ghg_map_year_range"
        )
    
    return sidebar_data

def get_emissions_trends_sidebar(country_labels):
    """Sidebar for Emissions Trends page - country + year range"""
    sidebar_data = {
        'selected_country_folder': None,
        'year_range': None,
        'data_dict': None,
        'total_emissions_df': None,
        'co2_df': None,
        'other_gases_df': None
    }

    # Country selector
    selected_label = st.sidebar.selectbox(
        "Select Country",
        options=country_labels,
        key="emissions_trends_country_selector"
    )
    
    sidebar_data['selected_country_folder'] = selected_label

    # Load all datasets for selected country
    sidebar_data['data_dict'] = load_country_data(selected_label)
    total_df = sidebar_data['data_dict']['Total']
    sidebar_data['total_emissions_df'] = total_df

    # Filter CO₂-only and other gases
    co2_column = [col for col in total_df.columns if "CO2" in col][0]
    sidebar_data['co2_df'] = total_df[['Year', 'Country', co2_column]]
    other_gas_columns = [col for col in total_df.columns if col != co2_column and col not in ['Year', 'Country']]
    sidebar_data['other_gases_df'] = total_df[['Year', 'Country'] + other_gas_columns]

    # Year slider
    years = sorted(total_df['Year'].unique())
    sidebar_data['year_range'] = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        key="emissions_trends_year_range"
    )

    return sidebar_data

def get_sector_distribution_sidebar(country_labels):
    """Sidebar for Sector Distribution page - country + year range + hierarchy"""
    sidebar_data = {
        'selected_country_folder': None,
        'year_range': None,
        'data_dict': None,
        'total_emissions_df': None,
        'selected_hierarchy': None
    }

    # Country selector
    selected_label = st.sidebar.selectbox(
        "Select Country",
        options=country_labels,
        key="sector_distribution_country_selector"
    )
    
    sidebar_data['selected_country_folder'] = selected_label

    # Load all datasets for selected country
    sidebar_data['data_dict'] = load_country_data(selected_label)
    total_df = sidebar_data['data_dict']['Total']
    sidebar_data['total_emissions_df'] = total_df

    # Year slider
    years = sorted(total_df['Year'].unique())
    sidebar_data['year_range'] = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        key="sector_distribution_year_range"
    )

    # Hierarchy level selector
    hierarchy_options = ['Sectors', 'Subsectors', 'Sub-subsectors']  
    sidebar_data['selected_hierarchy'] = st.sidebar.radio(
        "Select Detail Level",
        options=hierarchy_options,
        key="sector_hierarchy"
    )

    return sidebar_data

def get_climate_impact_sidebar(country_labels):
    """Sidebar for Climate Impact page - country + year range"""
    sidebar_data = {
        'selected_country_folder': None,
        'year_range': None,
        'data_dict': None,
        'total_emissions_df': None,
    }

    # Country selector
    selected_label = st.sidebar.selectbox(
        "Select Country",
        options=country_labels,
        key="climate_impact_country_selector"
    )
    
    sidebar_data['selected_country_folder'] = selected_label

    # Load all datasets for selected country
    sidebar_data['data_dict'] = load_country_data(selected_label)
    total_df = sidebar_data['data_dict']['Total']
    sidebar_data['total_emissions_df'] = total_df

    # Year slider
    years = sorted(total_df['Year'].unique())
    sidebar_data['year_range'] = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        key="climate_impact_year_range"
    )

    return sidebar_data

def get_data_view_sidebar(country_labels):
    """Sidebar for Data View page - country + year range"""
    sidebar_data = {
        'selected_country_folder': None,
        'year_range': None,
        'data_dict': None,
        'total_emissions_df': None,
    }

    # Country selector
    selected_label = st.sidebar.selectbox(
        "Select Country",
        options=country_labels,
        key="data_view_country_selector"
    )
    
    sidebar_data['selected_country_folder'] = selected_label

    # Load all datasets for selected country
    sidebar_data['data_dict'] = load_country_data(selected_label)
    total_df = sidebar_data['data_dict']['Total']
    sidebar_data['total_emissions_df'] = total_df

    # Year slider
    years = sorted(total_df['Year'].unique())
    sidebar_data['year_range'] = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        key="data_view_year_range"
    )

    return sidebar_data

# Page Functions
def render_ghg_map_page(sidebar_data):
    """Render the GHG Map page"""
    st.header("Introduction to CO₂ Emissions by Country")
    st.write("This interactive map displays carbon dioxide (CO₂) emissions over time...")

    # Load data for ALL countries (not using sidebar selection)
    all_emissions_df = load_all_total_emissions()
    
    # Get year range from sidebar
    year_range = sidebar_data['year_range']
    
    if all_emissions_df is not None:
        # Get chosen gases from the combined dataset
        co2_column = [col for col in all_emissions_df.columns if 'CO2' in col][0]

        # Load GeoJSON data
        geojson = load_geojson()
        
        if geojson is not None:
            # Create frames for animation
            frames = []
            
            # Get all years in the selected range
            years = range(year_range[0], year_range[1] + 1)
            
            # Create frames for each year
            for year in years:
                # Filter the pre-loaded all_country data for this year
                year_data = all_emissions_df[all_emissions_df['Year'] == year]
                
                if not year_data.empty:
                    # Aggregate by country
                    emissions_df = year_data.groupby('Country')[co2_column].sum().reset_index()
                    
                    frame = go.Frame(
                        data=[go.Choropleth(
                            locations=emissions_df['Country'],
                            z=emissions_df[co2_column],
                            geojson=geojson,
                            featureidkey="properties.name",
                            colorscale="YlOrRd",
                            zmin=0,
                            zmax=emissions_df[co2_column].max(),
                            colorbar=dict(title="CO2 Emissions (kt)"),
                            hovertemplate="<b>%{location}</b><br>CO2: %{z:,.0f} kt<extra></extra>"
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

                *Click a country to explore its emissions, or visit the 'Emissions Trends' page to compare changes over time.*
                """)

        else:
            st.error("GeoJSON data not available")
    else:
        st.error("Required data not available")

def render_emissions_trends_page(sidebar_data):
    """Render the Emissions Trends page"""
    # Access the returned values
    total_emissions_df = sidebar_data['total_emissions_df']
    data_dict = sidebar_data['data_dict']
    selected_country_folder = sidebar_data['selected_country_folder']
    year_range = sidebar_data['year_range']
    co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]
    
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
    "For a more detailed breakdown by emission sectors (e.g. transport, energy, agriculture), see the **Sector Distribution** page.")

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

def render_sector_distribution_page(sidebar_data):
    """Render the Sector Distribution page"""
    # Access returned values
    total_emissions_df = sidebar_data['total_emissions_df']
    data_dict = sidebar_data['data_dict']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    selected_hierarchy = sidebar_data['selected_hierarchy']
    
    if total_emissions_df is not None:
        # Get CO2 column
        co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
        other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]
    
        # Get sector data
        sector_df = data_dict.get(selected_hierarchy)
        
        if sector_df is not None:
            # Sector selection
            available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
            selected_sectors = st.multiselect(
                "Select Sectors",
                options=available_sectors,
                default=available_sectors,
                key="sector_selection"
            )
            
            # Filter sector data
            filtered_sector_df = sector_df[
                (sector_df['Year'].between(year_range[0], year_range[1])) &
                (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
            ]
            
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
            }
        }
    }

    st.header("Sector Distribution")
    st.write("Here, you can explore a detailed breakdown of greenhouse gas emissions by sector over time. Below the charts, you'll find an overview of the specific climate policies implemented in the selected country to address these emissions.")

    # Gas selector for Bar Chart (Checkboxes)
    available_gases_tab2_bar = [co2_column] + other_gas_columns
    selected_gases_tab2_bar = st.multiselect(
        "Select Gases for Bar Chart",
        options=available_gases_tab2_bar,
        default=[co2_column]  # Default to CO2
    )

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

    if selected_country_folder in chart_explanations:
        st.write(chart_explanations[selected_country_folder])

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

def render_climate_impact_page(sidebar_data):
    """Render the Climate Impact page"""
    # Access returned values
    total_emissions_df = sidebar_data['total_emissions_df']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    
    # Load additional datasets
    weather_data = load_weather_data()
    temp_data = load_temperature_data()
    emissions_data = load_global_emission()
    
    if all(data is not None for data in [weather_data, temp_data, total_emissions_df]):
        co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
        
        # Temperature Analysis 
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
        st.subheader(f"Local Impact: Extreme Weather Events in {selected_country_folder}")
        st.markdown("""
        As global temperatures rise, countries experience increased frequency and intensity of extreme weather events. 
        Here we examine the relationship between national emissions and extreme weather events.
        """)
        
        # Filter for selected country
        country_weather = weather_data[weather_data['Country'] == selected_country_folder]
        country_emissions = total_emissions_df  
        
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
                title=f'Annual Extreme Weather Events in {selected_country_folder}'
            )
            st.plotly_chart(fig_events, use_container_width=True)
        else:
            event_dist = country_weather.groupby(['Year', 'Disaster Type']).size().reset_index(name='count')
            fig_dist = px.bar(
                event_dist,
                x='Year',
                y='count',
                color='Disaster Type',
                title=f'Types of Extreme Weather Events in {selected_country_folder}',
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
            title=f'Relationship between CO2 Emissions and Extreme Weather Events in {selected_country_folder}'
        )
        st.plotly_chart(fig_national, use_container_width=True)

        # Key insights
        st.subheader("Key Findings")
        global_correlation = global_combined['Temperature_Anomaly'].corr(global_combined['CO2'])
        national_correlation = national_combined[co2_column].corr(national_combined['Disaster Type'])
        
        st.info(f"""
        Analysis Summary:
        * Global temperature-emissions correlation: {global_correlation:.2f}
        * {selected_country_folder}'s emissions-extreme events correlation: {national_correlation:.2f}
        * Most common disaster type in {selected_country_folder}: {country_weather['Disaster Type'].mode().iloc[0]}
        * Global temperature increase: {temp_change:.2f}°C
        * Total affected people in {selected_country_folder}: {total_affected:,}
        """)

    else:
        st.error("Required data not available")


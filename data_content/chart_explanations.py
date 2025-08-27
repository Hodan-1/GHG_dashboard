"""
Chart explanations for different countries in the GHG Emissions Dashboard.
Contains country-specific context for understanding emissions patterns.
"""

# Chart explanations by country
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

"""
Pages for the GHG Emissions Dashboard.
Contains all page rendering functions.
"""

from .ghg_map import render_ghg_map_page
from .emissions_trends import render_emissions_trends_page
from .sector_distribution import render_sector_distribution_page
from .climate_impact import render_climate_impact_page
from .data_view import render_data_view_page

__all__ = [
    'render_ghg_map_page',
    'render_emissions_trends_page', 
    'render_sector_distribution_page',
    'render_climate_impact_page',
    'render_data_view_page'
]
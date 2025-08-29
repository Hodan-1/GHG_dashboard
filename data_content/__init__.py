"""
Static content and data for the GHG Emissions Dashboard.

Contains dictionaries of policy data, sector goals, gas information, and chart explanations.
"""

from .policy_data import policy_data
from .sector_goals import global_climate_policies
from .gas_information import gas_explanations
from .chart_explanations import chart_explanations

__all__ = [
    'policy_data',
    'global_climate_policies', 
    'gas_explanations',
    'chart_explanations'
]

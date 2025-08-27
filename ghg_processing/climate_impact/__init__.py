"""
Climate Impact Data Processing Module

Tools for processing climate impact datasets including extreme weather events,
global emissions data, and temperature anomalies.
"""

from .extreme_weather import process_extreme_weather_data
from .global_emissions import process_global_emissions  
from .temperature import process_temperature_anomalies

__all__ = [
    'process_extreme_weather_data',
    'process_global_emissions',
    'process_temperature_anomalies'
]

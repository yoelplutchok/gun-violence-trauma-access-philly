"""
Trauma Desert: Mapping Gun Violence Burden Against Trauma System Capacity in Philadelphia

This package provides utilities for analyzing the spatial relationship between
gun violence incidents and access to Level I trauma centers in Philadelphia.
"""

__version__ = "0.1.0"
__author__ = "Trauma Desert Research Team"

from .paths import PATHS
from .io_utils import (
    load_config,
    load_geojson,
    save_geojson,
    load_csv,
    save_csv,
    update_manifest,
)
from .logging_utils import get_logger, log_step

__all__ = [
    "PATHS",
    "load_config",
    "load_geojson",
    "save_geojson",
    "load_csv",
    "save_csv",
    "update_manifest",
    "get_logger",
    "log_step",
]


#!/usr/bin/env python3
"""
Create master analysis dataset combining all tract-level metrics.

Joins tract boundaries, shooting density, transport times, and demographics
into a single GeoJSON file ready for analysis and visualization.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, load_geojson, save_geojson
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def create_master_dataset() -> Path:
    """
    Create master analysis dataset combining all metrics.
    
    Returns:
        Path to the output GeoJSON file.
    """
    with StepLogger("Loading tract shooting density", logger):
        density_file = PATHS.processed / "tract_shooting_density.geojson"
        tracts = load_geojson(density_file)
        logger.info(f"  Loaded {len(tracts)} tracts with shooting density")
    
    with StepLogger("Loading transport times", logger):
        transport_file = PATHS.processed / "tract_transport_times.csv"
        transport = load_csv(transport_file)
        logger.info(f"  Loaded transport times for {len(transport)} tracts")
        
        # Ensure GEOID types match
        transport['GEOID'] = transport['GEOID'].astype(str)
        tracts['GEOID'] = tracts['GEOID'].astype(str)
    
    with StepLogger("Joining transport times to tracts", logger):
        # Merge transport data
        master = tracts.merge(
            transport[['GEOID', 'time_to_nearest', 'nearest_trauma_center', 
                       'time_category', 'time_percentile', 'within_golden_hour']],
            on='GEOID',
            how='left'
        )
        logger.info(f"  Joined transport times")
    
    with StepLogger("Creating classification terciles", logger):
        # Calculate terciles for shooting density
        master['density_tercile'] = pd.qcut(
            master['annual_shootings_per_sq_mi'].rank(method='first'),
            q=3,
            labels=['Low', 'Medium', 'High']
        )
        
        # Calculate terciles for transport time using rank to handle ties
        master['time_tercile'] = pd.qcut(
            master['time_to_nearest'].rank(method='first'),
            q=3,
            labels=['Low', 'Medium', 'High']
        )
        
        logger.info("  Created density and time terciles")
        
        # Distribution check
        logger.info("  Density tercile distribution:")
        for label, count in master['density_tercile'].value_counts().sort_index().items():
            logger.info(f"    {label}: {count} tracts")
        
        logger.info("  Time tercile distribution:")
        for label, count in master['time_tercile'].value_counts().sort_index().items():
            logger.info(f"    {label}: {count} tracts")
        
        # Convert categorical to string for GeoJSON compatibility
        master['density_tercile'] = master['density_tercile'].astype(str)
        master['time_tercile'] = master['time_tercile'].astype(str)
    
    with StepLogger("Validating master dataset", logger):
        # Check for missing values in key fields
        key_fields = [
            'GEOID', 'total_shootings', 'annual_shootings_per_sq_mi',
            'time_to_nearest', 'total_population', 'pct_black', 'pct_poverty'
        ]
        
        for field in key_fields:
            missing = master[field].isna().sum()
            if missing > 0:
                logger.warning(f"  Missing values in {field}: {missing}")
            else:
                logger.info(f"  {field}: complete")
        
        # Summary statistics
        logger.info("\nMaster dataset summary:")
        logger.info(f"  Total tracts: {len(master)}")
        logger.info(f"  Total shootings: {master['total_shootings'].sum():,}")
        logger.info(f"  Total population: {master['total_population'].sum():,}")
        logger.info(f"  Avg density: {master['annual_shootings_per_sq_mi'].mean():.1f} per sq mi/yr")
        logger.info(f"  Avg time to trauma: {master['time_to_nearest'].mean():.1f} min")
        logger.info(f"  Avg % Black: {master['pct_black'].mean():.1f}%")
        logger.info(f"  Avg % Poverty: {master['pct_poverty'].mean():.1f}%")
    
    with StepLogger("Saving master dataset", logger):
        # Define output columns in logical order
        output_cols = [
            # Identifiers
            'GEOID', 'TRACTCE', 'NAME', 'geometry',
            
            # Geography
            'area_sq_mi',
            
            # Demographics
            'total_population', 'pct_black', 'pct_poverty', 'median_household_income',
            
            # Shooting metrics
            'total_shootings', 'fatal_shootings', 'recent_shootings',
            'shootings_per_year', 'fatality_rate',
            'shootings_per_sq_mi', 'annual_shootings_per_sq_mi',
            'shootings_per_10k_pop', 'annual_shootings_per_10k',
            'density_percentile', 'density_tercile',
            
            # Transport metrics
            'time_to_nearest', 'nearest_trauma_center', 'time_category',
            'time_percentile', 'time_tercile', 'within_golden_hour',
        ]
        
        # Keep only columns that exist
        output_cols = [c for c in output_cols if c in master.columns]
        master = master[output_cols]
        
        output_file = PATHS.processed / "tracts_analysis_ready.geojson"
        master.to_file(output_file, driver="GeoJSON")
        logger.info(f"  Saved to: {output_file}")
        logger.info(f"  Columns: {len(master.columns)}")
    
    return output_file


if __name__ == "__main__":
    output_path = create_master_dataset()
    print(f"\n✅ Master dataset created: {output_path}")


#!/usr/bin/env python3
"""
Assign shooting incidents to census tracts using spatial join.

Performs point-in-polygon matching to associate each shooting
with its containing census tract.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, save_csv, load_geojson
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def assign_shootings_to_tracts() -> Path:
    """
    Perform spatial join of shootings to census tracts.
    
    Returns:
        Path to the output file with tract assignments.
    """
    with StepLogger("Loading shooting data", logger):
        shootings_file = PATHS.processed / "shootings_clean.csv"
        df = load_csv(shootings_file)
        logger.info(f"  Loaded {len(df):,} shooting records")
    
    with StepLogger("Loading census tract boundaries", logger):
        tracts_file = PATHS.geo / "philadelphia_tracts.geojson"
        tracts = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(tracts)} census tracts")
        
        # Ensure CRS is set
        if tracts.crs is None:
            tracts = tracts.set_crs("EPSG:4326")
    
    with StepLogger("Creating point geometries from shooting coordinates", logger):
        # Create GeoDataFrame from shootings
        geometry = [Point(lng, lat) for lng, lat in zip(df['lng'], df['lat'])]
        shootings_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        logger.info(f"  Created {len(shootings_gdf):,} point geometries")
    
    with StepLogger("Performing spatial join (point-in-polygon)", logger):
        # Spatial join - each shooting gets the attributes of its containing tract
        joined = gpd.sjoin(
            shootings_gdf,
            tracts[['GEOID', 'TRACTCE', 'NAME', 'geometry']],
            how='left',
            predicate='within'
        )
        
        # Check for unmatched shootings
        unmatched = joined['GEOID'].isna().sum()
        if unmatched > 0:
            logger.warning(f"  Shootings not matched to any tract: {unmatched}")
        else:
            logger.info("  All shootings matched to tracts!")
        
        # Check tract distribution
        tract_counts = joined['GEOID'].value_counts()
        logger.info(f"  Tracts with shootings: {len(tract_counts)}")
        logger.info(f"  Max shootings in a tract: {tract_counts.max()}")
        logger.info(f"  Median shootings per tract: {tract_counts.median():.0f}")
    
    with StepLogger("Saving joined data", logger):
        # Drop geometry column for CSV output
        output_df = joined.drop(columns=['geometry', 'index_right'], errors='ignore')
        
        # Rename tract columns for clarity
        output_df = output_df.rename(columns={
            'GEOID': 'tract_geoid',
            'TRACTCE': 'tract_code',
            'NAME': 'tract_name'
        })
        
        output_file = PATHS.processed / "shootings_with_tracts.csv"
        save_csv(output_df, output_file)
        logger.info(f"  Saved to: {output_file}")
        logger.info(f"  Total records: {len(output_df):,}")
    
    return output_file


if __name__ == "__main__":
    output_path = assign_shootings_to_tracts()
    print(f"\n✅ Spatial join complete: {output_path}")


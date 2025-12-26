#!/usr/bin/env python3
"""
Create bivariate classification for trauma desert analysis.

Combines shooting density and transport time into a 3×3 matrix
to identify areas with both high violence burden AND poor trauma access.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, save_geojson, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Bivariate classification matrix
# Class 9 = High Density + High Time = TRAUMA DESERT
BIVARIATE_MATRIX = {
    ('Low', 'Low'): 1,
    ('Low', 'Medium'): 2,
    ('Low', 'High'): 3,
    ('Medium', 'Low'): 4,
    ('Medium', 'Medium'): 5,
    ('Medium', 'High'): 6,
    ('High', 'Low'): 7,
    ('High', 'Medium'): 8,
    ('High', 'High'): 9,
}

# Labels for each class
CLASS_LABELS = {
    1: "Low burden, Good access",
    2: "Low burden, Moderate access",
    3: "Low burden, Poor access",
    4: "Moderate burden, Good access",
    5: "Moderate burden, Moderate access",
    6: "Moderate burden, Poor access",
    7: "High burden, Good access",
    8: "High burden, Moderate access",
    9: "TRAUMA DESERT",
}

# Priority categories
PRIORITY_CATEGORIES = {
    9: "Trauma Desert",
    8: "High Burden",
    7: "High Burden",
    6: "Access Gap",
    3: "Access Gap",
    5: "Moderate",
    4: "Moderate",
    2: "Low Priority",
    1: "Low Priority",
}


def create_bivariate_classification() -> Path:
    """
    Create bivariate classification combining density and transport time.
    
    Returns:
        Path to the classified output file.
    """
    with StepLogger("Loading master analysis dataset", logger):
        master_file = PATHS.processed / "tracts_analysis_ready.geojson"
        gdf = load_geojson(master_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
    
    with StepLogger("Creating bivariate classification", logger):
        # Check for unknown tercile combinations before classification
        unknown_mask = gdf.apply(
            lambda row: (row['density_tercile'], row['time_tercile']) not in BIVARIATE_MATRIX, 
            axis=1
        )
        if unknown_mask.any():
            logger.warning(f"  {unknown_mask.sum()} tracts have unknown tercile combinations")
            for idx, row in gdf[unknown_mask].iterrows():
                logger.warning(f"    GEOID {row['GEOID']}: density={row['density_tercile']}, time={row['time_tercile']}")
        
        # Assign bivariate class based on density and time terciles
        gdf['bivariate_class'] = gdf.apply(
            lambda row: BIVARIATE_MATRIX.get(
                (row['density_tercile'], row['time_tercile']), 
                5  # Default to middle if unknown
            ),
            axis=1
        )
        
        # Add class labels
        gdf['bivariate_label'] = gdf['bivariate_class'].map(CLASS_LABELS)
        
        # Add priority category
        gdf['priority_category'] = gdf['bivariate_class'].map(PRIORITY_CATEGORIES)
        
        logger.info("  Bivariate classification assigned")
    
    with StepLogger("Analyzing classification distribution", logger):
        logger.info("  Class distribution:")
        for cls in sorted(gdf['bivariate_class'].unique()):
            count = (gdf['bivariate_class'] == cls).sum()
            label = CLASS_LABELS.get(cls, "Unknown")
            pct = count / len(gdf) * 100
            logger.info(f"    Class {cls} ({label}): {count} tracts ({pct:.1f}%)")
        
        logger.info("\n  Priority category distribution:")
        for cat, count in gdf['priority_category'].value_counts().sort_index().items():
            pct = count / len(gdf) * 100
            logger.info(f"    {cat}: {count} tracts ({pct:.1f}%)")
    
    with StepLogger("Analyzing trauma desert characteristics", logger):
        trauma_deserts = gdf[gdf['bivariate_class'] == 9].copy()
        logger.info(f"\n  TRAUMA DESERTS IDENTIFIED: {len(trauma_deserts)}")
        
        if len(trauma_deserts) > 0:
            # Demographics
            avg_pct_black = trauma_deserts['pct_black'].mean()
            avg_pct_poverty = trauma_deserts['pct_poverty'].mean()
            total_pop = trauma_deserts['total_population'].sum()
            total_shootings = trauma_deserts['total_shootings'].sum()
            
            logger.info(f"  Population in trauma deserts: {total_pop:,}")
            logger.info(f"  Shootings in trauma deserts: {total_shootings:,}")
            logger.info(f"  Avg % Black: {avg_pct_black:.1f}%")
            logger.info(f"  Avg % Poverty: {avg_pct_poverty:.1f}%")
            
            # Compare to city average
            city_pct_black = gdf['pct_black'].mean()
            city_pct_poverty = gdf['pct_poverty'].mean()
            
            logger.info(f"\n  City average % Black: {city_pct_black:.1f}%")
            logger.info(f"  City average % Poverty: {city_pct_poverty:.1f}%")
            logger.info(f"  Disparity ratio (Black): {avg_pct_black / city_pct_black:.2f}x")
            logger.info(f"  Disparity ratio (Poverty): {avg_pct_poverty / city_pct_poverty:.2f}x")
    
    with StepLogger("Saving classified dataset", logger):
        output_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf.to_file(output_file, driver="GeoJSON")
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = create_bivariate_classification()
    print(f"\n✅ Bivariate classification complete: {output_path}")


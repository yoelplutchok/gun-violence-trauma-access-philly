#!/usr/bin/env python3
"""
Spot check individual tracts for data accuracy.

Examines 3 trauma desert tracts and 3 low-priority tracts
to manually verify classification accuracy.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv, save_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def spot_check_tract(gdf: gpd.GeoDataFrame, geoid: str) -> dict:
    """
    Perform detailed spot check on a single tract.
    
    Args:
        gdf: GeoDataFrame with all tract data
        geoid: GEOID of tract to check
        
    Returns:
        Dict with spot check results
    """
    tract = gdf[gdf['GEOID'] == geoid].iloc[0]
    
    return {
        'GEOID': geoid,
        'NAME': tract.get('NAME', 'N/A'),
        'bivariate_class': int(tract['bivariate_class']),
        'bivariate_label': tract['bivariate_label'],
        'priority_category': tract['priority_category'],
        'total_shootings': int(tract['total_shootings']),
        'annual_density': round(tract['annual_shootings_per_sq_mi'], 1),
        'density_tercile': tract['density_tercile'],
        'time_to_nearest': int(tract['time_to_nearest']),
        'time_tercile': tract['time_tercile'],
        'nearest_hospital': tract['nearest_trauma_center'],
        'total_population': int(tract['total_population']),
        'pct_black': round(tract['pct_black'], 1),
        'pct_poverty': round(tract['pct_poverty'], 1),
        'fatality_rate': round(tract['fatality_rate'], 1),
    }


def run_spot_checks() -> Path:
    """Run spot checks on sample tracts."""
    logger.info("=" * 60)
    logger.info("RUNNING SPOT CHECKS")
    logger.info("=" * 60)
    
    with StepLogger("Loading classified data", logger):
        gdf = load_geojson(PATHS.processed / "tracts_bivariate_classified.geojson")
        logger.info(f"  Loaded {len(gdf)} tracts")
    
    # Select tracts for spot checking
    trauma_deserts = gdf[gdf['bivariate_class'] == 9].sort_values(
        'total_shootings', ascending=False
    )
    low_priority = gdf[gdf['bivariate_class'] == 1].sort_values(
        'total_population', ascending=False
    )
    
    with StepLogger("Spot checking trauma desert tracts", logger):
        logger.info("\n  TRAUMA DESERT TRACTS (Class 9):")
        logger.info("  " + "=" * 60)
        
        td_checks = []
        for i, (_, tract) in enumerate(trauma_deserts.head(3).iterrows()):
            check = spot_check_tract(gdf, tract['GEOID'])
            td_checks.append(check)
            
            logger.info(f"\n  [{i+1}] Tract {check['NAME']} (GEOID: {check['GEOID']})")
            logger.info(f"      Classification: {check['bivariate_label']}")
            logger.info(f"      Shootings: {check['total_shootings']} ({check['annual_density']}/sq mi/yr)")
            logger.info(f"      Density tercile: {check['density_tercile']}")
            logger.info(f"      Time to trauma: {check['time_to_nearest']} min → {check['nearest_hospital']}")
            logger.info(f"      Time tercile: {check['time_tercile']}")
            logger.info(f"      Population: {check['total_population']:,}")
            logger.info(f"      Demographics: {check['pct_black']:.1f}% Black, {check['pct_poverty']:.1f}% Poverty")
            logger.info(f"      Fatality rate: {check['fatality_rate']:.1f}%")
            
            # Verify classification logic
            if check['density_tercile'] == 'High' and check['time_tercile'] == 'High':
                logger.info(f"      ✅ CLASSIFICATION VERIFIED (High density + High time = Class 9)")
            else:
                logger.warning(f"      ⚠️ CLASSIFICATION MISMATCH - review required")
    
    with StepLogger("Spot checking low-priority tracts", logger):
        logger.info("\n  LOW PRIORITY TRACTS (Class 1):")
        logger.info("  " + "=" * 60)
        
        lp_checks = []
        for i, (_, tract) in enumerate(low_priority.head(3).iterrows()):
            check = spot_check_tract(gdf, tract['GEOID'])
            lp_checks.append(check)
            
            logger.info(f"\n  [{i+1}] Tract {check['NAME']} (GEOID: {check['GEOID']})")
            logger.info(f"      Classification: {check['bivariate_label']}")
            logger.info(f"      Shootings: {check['total_shootings']} ({check['annual_density']}/sq mi/yr)")
            logger.info(f"      Density tercile: {check['density_tercile']}")
            logger.info(f"      Time to trauma: {check['time_to_nearest']} min → {check['nearest_hospital']}")
            logger.info(f"      Time tercile: {check['time_tercile']}")
            logger.info(f"      Population: {check['total_population']:,}")
            logger.info(f"      Demographics: {check['pct_black']:.1f}% Black, {check['pct_poverty']:.1f}% Poverty")
            
            # Verify classification logic
            if check['density_tercile'] == 'Low' and check['time_tercile'] == 'Low':
                logger.info(f"      ✅ CLASSIFICATION VERIFIED (Low density + Low time = Class 1)")
            else:
                logger.warning(f"      ⚠️ CLASSIFICATION MISMATCH - review required")
    
    with StepLogger("Saving spot check results", logger):
        all_checks = td_checks + lp_checks
        check_df = pd.DataFrame(all_checks)
        output_file = PATHS.tables / "spot_check_results.csv"
        save_csv(check_df, output_file)
        logger.info(f"  Saved to: {output_file}")
    
    logger.info("\n" + "=" * 60)
    logger.info("SPOT CHECK COMPLETE")
    logger.info("=" * 60)
    
    return output_file


if __name__ == "__main__":
    output_path = run_spot_checks()
    print(f"\n✅ Spot checks complete: {output_path}")


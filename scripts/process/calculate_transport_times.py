#!/usr/bin/env python3
"""
Calculate transport time from each census tract to nearest Level I trauma center.

Uses isochrone polygons to determine which time interval each tract
centroid falls within for each trauma center, then finds the minimum.
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

# Time categories for classification
TIME_CATEGORIES = [5, 10, 15, 20, 30]


def calculate_transport_times() -> Path:
    """
    Calculate transport time from each tract to nearest trauma center.
    
    Returns:
        Path to the output CSV file.
    """
    with StepLogger("Loading tract boundaries", logger):
        tracts_file = PATHS.geo / "philadelphia_tracts.geojson"
        tracts = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(tracts)} census tracts")
        
        # Calculate centroids for each tract
        tracts['centroid'] = tracts.geometry.centroid
        logger.info("  Calculated tract centroids")
    
    with StepLogger("Loading trauma center isochrones", logger):
        isochrones_file = PATHS.isochrones / "trauma_center_isochrones.geojson"
        isochrones = load_geojson(isochrones_file)
        logger.info(f"  Loaded {len(isochrones)} isochrone polygons")
        
        # Get unique hospitals
        hospitals = isochrones['hospital_name'].unique()
        logger.info(f"  Trauma centers: {len(hospitals)}")
        for h in hospitals:
            logger.info(f"    - {h}")
    
    with StepLogger("Determining transport time for each tract", logger):
        results = []
        
        for idx, tract in tracts.iterrows():
            tract_geoid = tract['GEOID']
            centroid = tract['centroid']
            
            # Find minimum time to any trauma center
            min_time = None
            nearest_hospital = None
            
            for hospital in hospitals:
                # Get isochrones for this hospital, sorted by time (ascending)
                hospital_isochrones = isochrones[
                    isochrones['hospital_name'] == hospital
                ].sort_values('time_minutes')
                
                # Check each time interval from smallest to largest
                for _, iso in hospital_isochrones.iterrows():
                    if iso.geometry.contains(centroid):
                        time_minutes = iso['time_minutes']
                        if min_time is None or time_minutes < min_time:
                            min_time = time_minutes
                            nearest_hospital = hospital
                        break  # Found the smallest interval for this hospital
            
            # If centroid is outside all isochrones, assign 30+ category
            if min_time is None:
                min_time = 31  # Represents "30+ minutes"
                nearest_hospital = "Beyond coverage"
            
            results.append({
                'GEOID': tract_geoid,
                'time_to_nearest': min_time,
                'nearest_trauma_center': nearest_hospital,
            })
        
        transport_df = pd.DataFrame(results)
        logger.info(f"  Calculated transport times for {len(transport_df)} tracts")
    
    with StepLogger("Analyzing transport time distribution", logger):
        # Distribution by time category
        def categorize_time(t):
            if t <= 5:
                return "0-5 min"
            elif t <= 10:
                return "5-10 min"
            elif t <= 15:
                return "10-15 min"
            elif t <= 20:
                return "15-20 min"
            elif t <= 30:
                return "20-30 min"
            else:
                return "30+ min"
        
        transport_df['time_category'] = transport_df['time_to_nearest'].apply(categorize_time)
        
        logger.info("  Distribution by time category:")
        for cat in ["0-5 min", "5-10 min", "10-15 min", "15-20 min", "20-30 min", "30+ min"]:
            count = (transport_df['time_category'] == cat).sum()
            pct = count / len(transport_df) * 100
            logger.info(f"    {cat}: {count} tracts ({pct:.1f}%)")
        
        # Distribution by nearest hospital
        logger.info("  Distribution by nearest trauma center:")
        for hospital, count in transport_df['nearest_trauma_center'].value_counts().items():
            pct = count / len(transport_df) * 100
            logger.info(f"    {hospital}: {count} tracts ({pct:.1f}%)")
        
        # Calculate percentile rank for transport time
        transport_df['time_percentile'] = transport_df['time_to_nearest'].rank(pct=True).round(3)
        
        # Create binary flag for "golden hour" access (within 20 min)
        transport_df['within_golden_hour'] = transport_df['time_to_nearest'] <= 20
        within_golden = transport_df['within_golden_hour'].sum()
        logger.info(f"  Tracts within 20 min of Level I: {within_golden} ({within_golden/len(transport_df)*100:.1f}%)")
    
    with StepLogger("Saving transport time data", logger):
        output_file = PATHS.processed / "tract_transport_times.csv"
        save_csv(transport_df, output_file)
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = calculate_transport_times()
    print(f"\n✅ Transport times calculated: {output_path}")


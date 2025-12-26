#!/usr/bin/env python3
"""
Identify and rank trauma desert neighborhoods.

Creates a detailed list of trauma desert tracts with rankings
and aggregated statistics for policy recommendations.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, save_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def identify_trauma_deserts() -> tuple:
    """
    Identify, rank, and analyze trauma desert tracts.
    
    Returns:
        Tuple of paths to (ranked_tracts.csv, summary_stats.csv)
    """
    with StepLogger("Loading classified tract data", logger):
        classified_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(classified_file)
        logger.info(f"  Loaded {len(gdf)} classified tracts")
    
    with StepLogger("Filtering to trauma desert tracts", logger):
        trauma_deserts = gdf[gdf['bivariate_class'] == 9].copy()
        logger.info(f"  Trauma desert tracts: {len(trauma_deserts)}")
        
        if len(trauma_deserts) == 0:
            logger.warning("  No trauma deserts identified!")
            return None, None
    
    with StepLogger("Creating composite ranking score", logger):
        # Normalize density and time to 0-1 scale (with division by zero protection)
        density_range = trauma_deserts['annual_shootings_per_sq_mi'].max() - trauma_deserts['annual_shootings_per_sq_mi'].min()
        trauma_deserts['density_norm'] = (
            (trauma_deserts['annual_shootings_per_sq_mi'] - trauma_deserts['annual_shootings_per_sq_mi'].min()) /
            (density_range if density_range > 0 else 1)
        )
        
        time_range = trauma_deserts['time_to_nearest'].max() - trauma_deserts['time_to_nearest'].min()
        trauma_deserts['time_norm'] = (
            (trauma_deserts['time_to_nearest'] - trauma_deserts['time_to_nearest'].min()) /
            (time_range if time_range > 0 else 1)
        )
        
        # Composite score: 50% density + 50% time
        trauma_deserts['trauma_desert_score'] = (
            0.5 * trauma_deserts['density_norm'] + 
            0.5 * trauma_deserts['time_norm']
        ).round(3)
        
        # Rank by composite score (higher = worse)
        trauma_deserts['priority_rank'] = trauma_deserts['trauma_desert_score'].rank(
            ascending=False, method='min'
        ).astype(int)
        
        logger.info("  Composite score calculated and ranked")
    
    with StepLogger("Creating ranked trauma desert list", logger):
        # Sort by priority rank
        trauma_deserts = trauma_deserts.sort_values('priority_rank')
        
        # Select output columns
        output_cols = [
            'priority_rank', 'GEOID', 'NAME',
            'total_shootings', 'annual_shootings_per_sq_mi', 'fatality_rate',
            'time_to_nearest', 'nearest_trauma_center',
            'total_population', 'pct_black', 'pct_poverty',
            'trauma_desert_score'
        ]
        
        ranked_df = trauma_deserts[output_cols].copy()
        
        # Display top trauma deserts
        logger.info("\n  TOP 10 TRAUMA DESERT TRACTS:")
        logger.info("  " + "-" * 80)
        for idx, row in ranked_df.head(10).iterrows():
            logger.info(
                f"  #{int(row['priority_rank']):2d} | Tract {row['NAME']} | "
                f"{row['total_shootings']:3.0f} shootings | "
                f"{row['time_to_nearest']:.0f} min to trauma | "
                f"{row['pct_black']:.0f}% Black | "
                f"{row['pct_poverty']:.0f}% Poverty"
            )
    
    with StepLogger("Creating summary statistics", logger):
        # Trauma desert aggregate stats
        td_stats = {
            'metric': [],
            'trauma_desert_tracts': [],
            'city_overall': [],
            'disparity_ratio': []
        }
        
        all_tracts = gdf
        
        metrics = [
            ('Total Tracts', len(trauma_deserts), len(all_tracts)),
            ('Total Population', trauma_deserts['total_population'].sum(), all_tracts['total_population'].sum()),
            ('Total Shootings', trauma_deserts['total_shootings'].sum(), all_tracts['total_shootings'].sum()),
            ('Avg Shootings per Sq Mi/Yr', trauma_deserts['annual_shootings_per_sq_mi'].mean(), all_tracts['annual_shootings_per_sq_mi'].mean()),
            ('Avg Time to Level I (min)', trauma_deserts['time_to_nearest'].mean(), all_tracts['time_to_nearest'].mean()),
            ('Avg % Black', trauma_deserts['pct_black'].mean(), all_tracts['pct_black'].mean()),
            ('Avg % Poverty', trauma_deserts['pct_poverty'].mean(), all_tracts['pct_poverty'].mean()),
            ('Avg Fatality Rate (%)', trauma_deserts['fatality_rate'].mean(), all_tracts['fatality_rate'].mean()),
        ]
        
        for metric_name, td_val, city_val in metrics:
            td_stats['metric'].append(metric_name)
            td_stats['trauma_desert_tracts'].append(round(td_val, 1) if isinstance(td_val, float) else td_val)
            td_stats['city_overall'].append(round(city_val, 1) if isinstance(city_val, float) else city_val)
            if city_val > 0:
                td_stats['disparity_ratio'].append(round(td_val / city_val, 2))
            else:
                td_stats['disparity_ratio'].append(None)
        
        summary_df = pd.DataFrame(td_stats)
        
        logger.info("\n  SUMMARY STATISTICS:")
        for _, row in summary_df.iterrows():
            logger.info(f"    {row['metric']}: {row['trauma_desert_tracts']} (city: {row['city_overall']}, ratio: {row['disparity_ratio']})")
    
    with StepLogger("Identifying nearest trauma centers for intervention", logger):
        # Which trauma centers serve the trauma desert areas?
        tc_serving = trauma_deserts['nearest_trauma_center'].value_counts()
        logger.info("\n  Trauma centers nearest to trauma desert tracts:")
        for tc, count in tc_serving.items():
            logger.info(f"    {tc}: {count} tracts")
    
    with StepLogger("Saving outputs", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        
        # Save ranked list
        ranked_file = PATHS.tables / "trauma_desert_tracts.csv"
        save_csv(ranked_df, ranked_file)
        logger.info(f"  Saved ranked list: {ranked_file}")
        
        # Save summary stats
        summary_file = PATHS.tables / "trauma_desert_summary_statistics.csv"
        save_csv(summary_df, summary_file)
        logger.info(f"  Saved summary stats: {summary_file}")
    
    return ranked_file, summary_file


if __name__ == "__main__":
    ranked_path, summary_path = identify_trauma_deserts()
    print(f"\n✅ Trauma deserts identified:")
    print(f"   Ranked list: {ranked_path}")
    print(f"   Summary: {summary_path}")


#!/usr/bin/env python3
"""
Calculate tract-level shooting density metrics.

Aggregates shooting data to census tract level and calculates
density per square mile and per capita rates.
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


def calculate_tract_density() -> Path:
    """
    Calculate shooting density by census tract.
    
    Returns:
        Path to the output GeoJSON file.
    """
    with StepLogger("Loading shooting data with tracts", logger):
        shootings_file = PATHS.processed / "shootings_with_tracts.csv"
        df = load_csv(shootings_file, parse_dates=['date'])
        logger.info(f"  Loaded {len(df):,} shooting records")
        
        # Filter to records with valid tract assignment
        df = df[df['tract_geoid'].notna()].copy()
        logger.info(f"  Records with tract assignment: {len(df):,}")
    
    with StepLogger("Loading tract boundaries and demographics", logger):
        tracts_file = PATHS.geo / "philadelphia_tracts.geojson"
        tracts = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(tracts)} tract boundaries")
        
        demographics_file = PATHS.processed / "tract_demographics.csv"
        demographics = load_csv(demographics_file)
        logger.info(f"  Loaded demographics for {len(demographics)} tracts")
    
    with StepLogger("Calculating aggregate statistics by tract", logger):
        # Calculate time range for annual rates
        min_year = df['year'].min()
        max_year = df['year'].max()
        years_span = max_year - min_year + 1
        logger.info(f"  Data spans {years_span} years ({min_year}-{max_year})")
        
        # Aggregate by tract
        tract_stats = df.groupby('tract_geoid').agg(
            total_shootings=('objectid', 'count'),
            fatal_shootings=('is_fatal', 'sum'),
            recent_shootings=('year', lambda x: (x == max_year).sum()),
            avg_victim_age=('age', 'mean'),
            pct_male=('is_male', 'mean'),
            pct_outside=('is_outside', 'mean'),
        ).reset_index()
        
        # Calculate annual average
        tract_stats['shootings_per_year'] = tract_stats['total_shootings'] / years_span
        
        # Calculate fatality rate
        tract_stats['fatality_rate'] = (
            tract_stats['fatal_shootings'] / tract_stats['total_shootings'] * 100
        ).round(1)
        
        logger.info(f"  Calculated stats for {len(tract_stats)} tracts")
    
    with StepLogger("Joining to tract geometries and demographics", logger):
        # Ensure GEOID types match (both as string)
        # tract_geoid is float64, need to convert to int then string to avoid ".0" suffix
        tract_stats['tract_geoid'] = tract_stats['tract_geoid'].astype(int).astype(str)
        tracts['GEOID'] = tracts['GEOID'].astype(str)
        
        # Join tract stats to tract boundaries
        tracts_with_stats = tracts.merge(
            tract_stats,
            left_on='GEOID',
            right_on='tract_geoid',
            how='left'
        )
        
        # Fill NaN for tracts with no shootings
        tracts_with_stats['total_shootings'] = tracts_with_stats['total_shootings'].fillna(0).astype(int)
        tracts_with_stats['fatal_shootings'] = tracts_with_stats['fatal_shootings'].fillna(0).astype(int)
        tracts_with_stats['shootings_per_year'] = tracts_with_stats['shootings_per_year'].fillna(0)
        tracts_with_stats['recent_shootings'] = tracts_with_stats['recent_shootings'].fillna(0).astype(int)
        
        # Join demographics (ensure GEOID types match)
        demographics['GEOID'] = demographics['GEOID'].astype(str)
        tracts_with_stats = tracts_with_stats.merge(
            demographics[['GEOID', 'total_population', 'pct_black', 'pct_poverty', 'median_household_income']],
            on='GEOID',
            how='left'
        )
        
        logger.info(f"  Merged demographics for {len(tracts_with_stats)} tracts")
    
    with StepLogger("Calculating density metrics", logger):
        # Shooting density per square mile
        tracts_with_stats['shootings_per_sq_mi'] = (
            tracts_with_stats['total_shootings'] / tracts_with_stats['area_sq_mi']
        ).round(1)
        
        # Annual density per square mile
        tracts_with_stats['annual_shootings_per_sq_mi'] = (
            tracts_with_stats['shootings_per_year'] / tracts_with_stats['area_sq_mi']
        ).round(1)
        
        # Per capita rate (per 10,000 residents)
        tracts_with_stats['shootings_per_10k_pop'] = (
            tracts_with_stats['total_shootings'] / tracts_with_stats['total_population'] * 10000
        ).round(1)
        
        # Annual per capita rate
        tracts_with_stats['annual_shootings_per_10k'] = (
            tracts_with_stats['shootings_per_year'] / tracts_with_stats['total_population'] * 10000
        ).round(2)
        
        # Handle inf values from division by zero (unpopulated tracts)
        for col in ['shootings_per_10k_pop', 'annual_shootings_per_10k']:
            tracts_with_stats[col] = tracts_with_stats[col].replace([float('inf'), float('-inf')], 0)
        
        # Calculate percentile ranks for classification
        tracts_with_stats['density_percentile'] = tracts_with_stats['annual_shootings_per_sq_mi'].rank(pct=True).round(3)
        
        logger.info("  Summary statistics:")
        logger.info(f"    Total shootings: {tracts_with_stats['total_shootings'].sum():,}")
        logger.info(f"    Tracts with 0 shootings: {(tracts_with_stats['total_shootings'] == 0).sum()}")
        logger.info(f"    Max shootings in one tract: {tracts_with_stats['total_shootings'].max()}")
        logger.info(f"    Max density: {tracts_with_stats['annual_shootings_per_sq_mi'].max():.1f} per sq mi per year")
    
    with StepLogger("Identifying high-burden tracts", logger):
        # Top 10 tracts by shooting count
        top_10 = tracts_with_stats.nlargest(10, 'total_shootings')[['GEOID', 'NAME', 'total_shootings', 'annual_shootings_per_sq_mi', 'pct_black']]
        logger.info("  Top 10 tracts by shooting count:")
        for _, row in top_10.iterrows():
            logger.info(f"    {row['NAME']}: {row['total_shootings']} shootings, {row['annual_shootings_per_sq_mi']:.0f}/sq mi/yr, {row['pct_black']:.0f}% Black")
    
    with StepLogger("Saving tract density data", logger):
        # Select output columns
        output_cols = [
            'GEOID', 'TRACTCE', 'NAME', 'geometry', 'area_sq_mi',
            'total_population', 'pct_black', 'pct_poverty', 'median_household_income',
            'total_shootings', 'fatal_shootings', 'recent_shootings',
            'shootings_per_year', 'fatality_rate',
            'shootings_per_sq_mi', 'annual_shootings_per_sq_mi',
            'shootings_per_10k_pop', 'annual_shootings_per_10k',
            'density_percentile',
        ]
        
        output_gdf = tracts_with_stats[output_cols].copy()
        
        output_file = PATHS.processed / "tract_shooting_density.geojson"
        output_gdf.to_file(output_file, driver="GeoJSON")
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = calculate_tract_density()
    print(f"\n✅ Tract density calculated: {output_path}")


#!/usr/bin/env python3
"""
Analyze demographic disparities in trauma access.

Tests whether trauma access correlates with neighborhood race and income,
and quantifies disparities across bivariate classification categories.
"""

import sys
from pathlib import Path

import pandas as pd
import geopandas as gpd
import numpy as np
from scipy import stats

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, save_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def analyze_demographic_disparity() -> Path:
    """
    Analyze relationship between demographics and trauma access.
    
    Returns:
        Path to the disparity analysis output file.
    """
    with StepLogger("Loading classified tract data", logger):
        classified_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(classified_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
        
        # Filter to tracts with valid demographic data
        gdf = gdf[gdf['pct_black'].notna() & gdf['pct_poverty'].notna()].copy()
        logger.info(f"  Tracts with valid demographics: {len(gdf)}")
    
    with StepLogger("Analyzing demographics by bivariate class", logger):
        class_stats = gdf.groupby('bivariate_class').agg({
            'pct_black': 'mean',
            'pct_poverty': 'mean',
            'total_population': 'sum',
            'total_shootings': 'sum',
            'annual_shootings_per_sq_mi': 'mean',
            'time_to_nearest': 'mean',
            'GEOID': 'count'
        }).round(1)
        
        class_stats = class_stats.rename(columns={'GEOID': 'tract_count'})
        class_stats = class_stats.reset_index()
        
        logger.info("\n  Demographics by bivariate class:")
        logger.info("  Class | Tracts | Avg %Black | Avg %Poverty | Shootings | Avg Time")
        logger.info("  " + "-" * 70)
        for _, row in class_stats.iterrows():
            logger.info(
                f"    {int(row['bivariate_class']):1d}   |  {int(row['tract_count']):3d}   |   "
                f"{row['pct_black']:5.1f}%   |    {row['pct_poverty']:5.1f}%    |   "
                f"{int(row['total_shootings']):5d}   |  {row['time_to_nearest']:.1f} min"
            )
    
    with StepLogger("Calculating correlation coefficients", logger):
        # Correlation: % Black vs Transport Time
        corr_black_time, p_black_time = stats.pearsonr(
            gdf['pct_black'].fillna(0), 
            gdf['time_to_nearest']
        )
        logger.info(f"\n  Correlation: % Black vs Transport Time")
        logger.info(f"    r = {corr_black_time:.3f}, p = {p_black_time:.4f}")
        logger.info(f"    Interpretation: {'Significant' if p_black_time < 0.05 else 'Not significant'}")
        
        # Correlation: % Black vs Shooting Density
        corr_black_density, p_black_density = stats.pearsonr(
            gdf['pct_black'].fillna(0), 
            gdf['annual_shootings_per_sq_mi']
        )
        logger.info(f"\n  Correlation: % Black vs Shooting Density")
        logger.info(f"    r = {corr_black_density:.3f}, p = {p_black_density:.6f}")
        logger.info(f"    Interpretation: {'Significant' if p_black_density < 0.05 else 'Not significant'}")
        
        # Correlation: % Poverty vs Transport Time
        corr_pov_time, p_pov_time = stats.pearsonr(
            gdf['pct_poverty'].fillna(0), 
            gdf['time_to_nearest']
        )
        logger.info(f"\n  Correlation: % Poverty vs Transport Time")
        logger.info(f"    r = {corr_pov_time:.3f}, p = {p_pov_time:.4f}")
        logger.info(f"    Interpretation: {'Significant' if p_pov_time < 0.05 else 'Not significant'}")
    
    with StepLogger("Comparing trauma deserts vs non-trauma deserts", logger):
        trauma_deserts = gdf[gdf['bivariate_class'] == 9]
        non_trauma_deserts = gdf[gdf['bivariate_class'] != 9]
        
        # T-tests for demographic differences
        t_black, p_black = stats.ttest_ind(
            trauma_deserts['pct_black'].dropna(),
            non_trauma_deserts['pct_black'].dropna()
        )
        
        t_poverty, p_poverty = stats.ttest_ind(
            trauma_deserts['pct_poverty'].dropna(),
            non_trauma_deserts['pct_poverty'].dropna()
        )
        
        logger.info("\n  Statistical comparison: Trauma Deserts vs Other Tracts")
        logger.info("  " + "-" * 60)
        
        logger.info(f"\n  % Black:")
        logger.info(f"    Trauma Deserts: {trauma_deserts['pct_black'].mean():.1f}%")
        logger.info(f"    Other Tracts: {non_trauma_deserts['pct_black'].mean():.1f}%")
        logger.info(f"    t-statistic: {t_black:.2f}, p-value: {p_black:.4f}")
        logger.info(f"    Difference: {'SIGNIFICANT' if p_black < 0.05 else 'Not significant'}")
        
        logger.info(f"\n  % Poverty:")
        logger.info(f"    Trauma Deserts: {trauma_deserts['pct_poverty'].mean():.1f}%")
        logger.info(f"    Other Tracts: {non_trauma_deserts['pct_poverty'].mean():.1f}%")
        logger.info(f"    t-statistic: {t_poverty:.2f}, p-value: {p_poverty:.4f}")
        logger.info(f"    Difference: {'SIGNIFICANT' if p_poverty < 0.05 else 'Not significant'}")
    
    with StepLogger("Analyzing shooting burden by race", logger):
        # Calculate population-weighted averages
        total_pop = gdf['total_population'].sum()
        total_black_pop = (gdf['total_population'] * gdf['pct_black'] / 100).sum()
        
        # Shootings in predominantly Black tracts (>50% Black)
        black_tracts = gdf[gdf['pct_black'] > 50]
        other_tracts = gdf[gdf['pct_black'] <= 50]
        
        shootings_black_tracts = black_tracts['total_shootings'].sum()
        shootings_other_tracts = other_tracts['total_shootings'].sum()
        pop_black_tracts = black_tracts['total_population'].sum()
        pop_other_tracts = other_tracts['total_population'].sum()
        
        rate_black_tracts = shootings_black_tracts / pop_black_tracts * 10000 if pop_black_tracts > 0 else 0
        rate_other_tracts = shootings_other_tracts / pop_other_tracts * 10000 if pop_other_tracts > 0 else 0
        
        logger.info("\n  Shooting burden by neighborhood racial composition:")
        logger.info(f"    Tracts >50% Black: {len(black_tracts)} tracts, {pop_black_tracts:,} residents")
        logger.info(f"      Shootings: {shootings_black_tracts:,} ({shootings_black_tracts/gdf['total_shootings'].sum()*100:.1f}%)")
        logger.info(f"      Rate: {rate_black_tracts:.1f} per 10,000 residents")
        
        logger.info(f"\n    Tracts ≤50% Black: {len(other_tracts)} tracts, {pop_other_tracts:,} residents")
        logger.info(f"      Shootings: {shootings_other_tracts:,} ({shootings_other_tracts/gdf['total_shootings'].sum()*100:.1f}%)")
        logger.info(f"      Rate: {rate_other_tracts:.1f} per 10,000 residents")
        
        logger.info(f"\n    Rate ratio: {rate_black_tracts/rate_other_tracts:.1f}x higher in predominantly Black tracts")
    
    with StepLogger("Saving disparity analysis results", logger):
        # Create comprehensive results DataFrame
        results = {
            'analysis': [],
            'metric': [],
            'value': [],
            'comparison': [],
            'p_value': [],
            'interpretation': []
        }
        
        # Correlations
        results['analysis'].extend(['Correlation', 'Correlation', 'Correlation'])
        results['metric'].extend(['% Black vs Transport Time', '% Black vs Shooting Density', '% Poverty vs Transport Time'])
        results['value'].extend([corr_black_time, corr_black_density, corr_pov_time])
        results['comparison'].extend(['r coefficient', 'r coefficient', 'r coefficient'])
        results['p_value'].extend([p_black_time, p_black_density, p_pov_time])
        results['interpretation'].extend([
            'Significant' if p_black_time < 0.05 else 'Not significant',
            'Significant' if p_black_density < 0.05 else 'Not significant',
            'Significant' if p_pov_time < 0.05 else 'Not significant',
        ])
        
        # T-tests
        results['analysis'].extend(['T-test', 'T-test'])
        results['metric'].extend(['% Black in TD vs Other', '% Poverty in TD vs Other'])
        results['value'].extend([t_black, t_poverty])
        results['comparison'].extend(['t-statistic', 't-statistic'])
        results['p_value'].extend([p_black, p_poverty])
        results['interpretation'].extend([
            'Significant' if p_black < 0.05 else 'Not significant',
            'Significant' if p_poverty < 0.05 else 'Not significant',
        ])
        
        results_df = pd.DataFrame(results)
        
        output_file = PATHS.tables / "demographic_disparity_analysis.csv"
        save_csv(results_df, output_file)
        logger.info(f"  Saved to: {output_file}")
        
        # Also save class-level statistics
        class_file = PATHS.tables / "demographics_by_bivariate_class.csv"
        save_csv(class_stats, class_file)
        logger.info(f"  Saved class stats to: {class_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = analyze_demographic_disparity()
    print(f"\n✅ Demographic disparity analysis complete: {output_path}")


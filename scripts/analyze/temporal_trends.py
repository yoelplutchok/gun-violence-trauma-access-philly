#!/usr/bin/env python3
"""
Temporal Trend Analysis.

Analyzes how shooting patterns have changed over time,
identifies emerging hotspots, and examines year-over-year trends.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, save_csv, normalize_geoid
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def analyze_temporal_trends() -> Path:
    """
    Analyze temporal trends in shooting data.
    
    Returns:
        Path to the trends output file.
    """
    with StepLogger("Loading shooting data", logger):
        shootings_file = PATHS.processed / "shootings_with_tracts.csv"
        df = load_csv(shootings_file, parse_dates=['date'])
        df = df[df['tract_geoid'].notna()].copy()
        df['tract_geoid'] = normalize_geoid(df['tract_geoid'])
        logger.info(f"  Loaded {len(df)} shooting records")
    
    with StepLogger("Analyzing annual trends", logger):
        # Annual counts
        annual = df.groupby('year').agg({
            'objectid': 'count',
            'is_fatal': 'sum'
        }).reset_index()
        annual.columns = ['year', 'total_shootings', 'fatal_shootings']
        annual['fatality_rate'] = (annual['fatal_shootings'] / annual['total_shootings'] * 100).round(1)
        
        logger.info("\n  ANNUAL SHOOTING TRENDS:")
        logger.info("  Year  | Total | Fatal | Rate")
        logger.info("  " + "-" * 35)
        for _, row in annual.iterrows():
            logger.info(f"  {int(row['year'])}  | {int(row['total_shootings']):5d} | {int(row['fatal_shootings']):4d}  | {row['fatality_rate']:.1f}%")
        
        # Trend calculation
        if len(annual) > 1:
            min_year = annual['year'].min()
            max_year = annual['year'].max()
            start_val = annual[annual['year'] == min_year]['total_shootings'].values[0]
            end_val = annual[annual['year'] == max_year]['total_shootings'].values[0]
            change_pct = (end_val - start_val) / start_val * 100
            
            logger.info(f"\n  Overall trend ({int(min_year)}-{int(max_year)}): {change_pct:+.1f}%")
            
            # Peak year
            peak_year = annual.loc[annual['total_shootings'].idxmax(), 'year']
            peak_count = annual['total_shootings'].max()
            logger.info(f"  Peak year: {int(peak_year)} ({int(peak_count)} shootings)")
    
    with StepLogger("Analyzing tract-level trends", logger):
        # Calculate shootings by tract and year
        tract_year = df.groupby(['tract_geoid', 'year']).size().unstack(fill_value=0)
        
        # Get first and last year columns
        years = sorted(tract_year.columns)
        first_year = years[0]
        last_year = years[-1]
        
        # Recent period (last 3 years)
        recent_years = years[-3:] if len(years) >= 3 else years
        
        # Calculate trends
        tract_stats = pd.DataFrame({
            'tract_geoid': tract_year.index,
            'first_year_shootings': tract_year[first_year].values,
            'last_year_shootings': tract_year[last_year].values,
            'total_shootings': tract_year.sum(axis=1).values,
            'avg_annual': tract_year.mean(axis=1).values,
            'recent_avg': tract_year[recent_years].mean(axis=1).values,
        })
        
        # Calculate trend (change from first to last year)
        tract_stats['change'] = tract_stats['last_year_shootings'] - tract_stats['first_year_shootings']
        tract_stats['pct_change'] = np.where(
            tract_stats['first_year_shootings'] > 0,
            (tract_stats['change'] / tract_stats['first_year_shootings'] * 100).round(1),
            np.where(tract_stats['last_year_shootings'] > 0, 100, 0)
        )
        
        # Identify emerging hotspots (low in first year, high recently)
        tract_stats['is_emerging'] = (
            (tract_stats['first_year_shootings'] <= 5) & 
            (tract_stats['recent_avg'] >= 10)
        )
        
        # Identify improving areas (high in first year, lower recently)
        tract_stats['is_improving'] = (
            (tract_stats['first_year_shootings'] >= 10) & 
            (tract_stats['recent_avg'] < tract_stats['avg_annual'] * 0.7)
        )
        
        logger.info(f"\n  TRACT-LEVEL TRENDS ({int(first_year)} to {int(last_year)}):")
        logger.info(f"  Tracts with increasing shootings: {(tract_stats['change'] > 0).sum()}")
        logger.info(f"  Tracts with decreasing shootings: {(tract_stats['change'] < 0).sum()}")
        logger.info(f"  Tracts with no change: {(tract_stats['change'] == 0).sum()}")
        logger.info(f"  Emerging hotspots: {tract_stats['is_emerging'].sum()}")
        logger.info(f"  Improving areas: {tract_stats['is_improving'].sum()}")
    
    with StepLogger("Identifying top emerging hotspots", logger):
        emerging = tract_stats[tract_stats['is_emerging']].copy()
        emerging = emerging.sort_values('recent_avg', ascending=False)
        
        if len(emerging) > 0:
            logger.info(f"\n  TOP EMERGING HOTSPOTS:")
            logger.info("  " + "-" * 60)
            for i, row in emerging.head(10).iterrows():
                logger.info(
                    f"  Tract {row['tract_geoid']}: "
                    f"{int(row['first_year_shootings'])} ({int(first_year)}) → "
                    f"{row['recent_avg']:.1f} avg/yr (recent)"
                )
    
    with StepLogger("Analyzing race trends over time", logger):
        race_year = df.groupby(['year', 'race']).size().unstack(fill_value=0)
        
        # Calculate percentage by year
        race_pct = race_year.div(race_year.sum(axis=1), axis=0) * 100
        
        logger.info("\n  RACE COMPOSITION OVER TIME:")
        logger.info("  Year  | Black% | White% | Other%")
        logger.info("  " + "-" * 40)
        for year in sorted(race_pct.index)[-5:]:  # Last 5 years
            black_pct = race_pct.loc[year, 'Black'] if 'Black' in race_pct.columns else 0
            white_pct = race_pct.loc[year, 'White'] if 'White' in race_pct.columns else 0
            other_pct = 100 - black_pct - white_pct
            logger.info(f"  {int(year)}  |  {black_pct:.1f}%  |  {white_pct:.1f}%  |  {other_pct:.1f}%")
    
    with StepLogger("Analyzing fatality trends", logger):
        # Monthly trend for recent years
        df['month'] = df['date'].dt.month
        recent_df = df[df['year'] >= df['year'].max() - 2]
        
        monthly = recent_df.groupby('month').agg({
            'objectid': 'count',
            'is_fatal': 'sum'
        })
        monthly.columns = ['shootings', 'fatal']
        monthly['fatality_rate'] = (monthly['fatal'] / monthly['shootings'] * 100).round(1)
        
        # Find peak months
        peak_month = monthly['shootings'].idxmax()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        logger.info(f"\n  SEASONAL PATTERNS (last 3 years):")
        logger.info(f"  Peak month: {month_names[peak_month-1]} ({int(monthly.loc[peak_month, 'shootings'])} shootings)")
        
        # Summer vs winter
        summer = monthly.loc[[6, 7, 8], 'shootings'].mean()
        winter = monthly.loc[[12, 1, 2], 'shootings'].mean()
        logger.info(f"  Summer avg (Jun-Aug): {summer:.0f}/month")
        logger.info(f"  Winter avg (Dec-Feb): {winter:.0f}/month")
        logger.info(f"  Summer/Winter ratio: {summer/winter:.2f}x")
    
    with StepLogger("Saving temporal analysis results", logger):
        # Save annual trends
        annual_file = PATHS.tables / "temporal_trends_annual.csv"
        save_csv(annual, annual_file)
        logger.info(f"  Saved annual trends: {annual_file}")
        
        # Save tract trends
        tract_file = PATHS.tables / "temporal_trends_by_tract.csv"
        save_csv(tract_stats, tract_file)
        logger.info(f"  Saved tract trends: {tract_file}")
    
    return annual_file


if __name__ == "__main__":
    output_path = analyze_temporal_trends()
    print(f"\n✅ Temporal trend analysis complete: {output_path}")


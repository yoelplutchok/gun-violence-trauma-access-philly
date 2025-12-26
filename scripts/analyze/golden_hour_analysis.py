#!/usr/bin/env python3
"""
Golden Hour Analysis.

Analyzes what percentage of shootings occur within various
time intervals of Level I trauma care, with breakdowns by
victim demographics.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, save_csv, normalize_geoid
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def analyze_golden_hour() -> tuple:
    """
    Analyze golden hour coverage for shooting victims.
    
    Returns:
        Tuple of paths to output files.
    """
    with StepLogger("Loading shooting data with tracts", logger):
        shootings_file = PATHS.processed / "shootings_with_tracts.csv"
        shootings = load_csv(shootings_file, parse_dates=['date'])
        logger.info(f"  Loaded {len(shootings)} shooting records")
    
    with StepLogger("Loading tract transport times", logger):
        transport_file = PATHS.processed / "tract_transport_times.csv"
        transport = load_csv(transport_file)
        
        # Ensure GEOID types match using standardized utility function
        transport['GEOID'] = normalize_geoid(transport['GEOID'])
        # Filter out shootings without tract assignment first
        shootings = shootings[shootings['tract_geoid'].notna()].copy()
        shootings['tract_geoid'] = normalize_geoid(shootings['tract_geoid'])
        
        logger.info(f"  Loaded transport times for {len(transport)} tracts")
    
    with StepLogger("Joining transport times to shootings", logger):
        shootings = shootings.merge(
            transport[['GEOID', 'time_to_nearest', 'time_category', 'within_golden_hour']],
            left_on='tract_geoid',
            right_on='GEOID',
            how='left'
        )
        
        # Check for unmatched
        unmatched = shootings['time_to_nearest'].isna().sum()
        if unmatched > 0:
            logger.warning(f"  Shootings without transport time: {unmatched}")
        
        # Filter to matched only
        shootings = shootings[shootings['time_to_nearest'].notna()].copy()
        logger.info(f"  Shootings with transport time: {len(shootings)}")
    
    with StepLogger("Calculating golden hour distribution", logger):
        total = len(shootings)
        
        # Overall distribution
        time_dist = {
            '0-5 min': (shootings['time_to_nearest'] <= 5).sum(),
            '5-10 min': ((shootings['time_to_nearest'] > 5) & (shootings['time_to_nearest'] <= 10)).sum(),
            '10-15 min': ((shootings['time_to_nearest'] > 10) & (shootings['time_to_nearest'] <= 15)).sum(),
            '15-20 min': ((shootings['time_to_nearest'] > 15) & (shootings['time_to_nearest'] <= 20)).sum(),
            '20-30 min': ((shootings['time_to_nearest'] > 20) & (shootings['time_to_nearest'] <= 30)).sum(),
            '30+ min': (shootings['time_to_nearest'] > 30).sum(),
        }
        
        logger.info("\n  GOLDEN HOUR COVERAGE - ALL SHOOTINGS:")
        logger.info("  " + "-" * 50)
        cumulative = 0
        for interval, count in time_dist.items():
            pct = count / total * 100
            cumulative += count
            cum_pct = cumulative / total * 100
            logger.info(f"    {interval}: {count:,} ({pct:.1f}%) | Cumulative: {cum_pct:.1f}%")
        
        within_20 = (shootings['time_to_nearest'] <= 20).sum()
        beyond_20 = (shootings['time_to_nearest'] > 20).sum()
        logger.info(f"\n  Within 20 min of Level I: {within_20:,} ({within_20/total*100:.1f}%)")
        logger.info(f"  Beyond 20 min of Level I: {beyond_20:,} ({beyond_20/total*100:.1f}%)")
    
    with StepLogger("Analyzing golden hour by fatality", logger):
        fatal_shootings = shootings[shootings['is_fatal'] == True]
        nonfatal_shootings = shootings[shootings['is_fatal'] == False]
        
        logger.info(f"\n  FATAL vs NON-FATAL SHOOTINGS:")
        logger.info("  " + "-" * 50)
        
        for category, df in [("Fatal", fatal_shootings), ("Non-Fatal", nonfatal_shootings)]:
            within = (df['time_to_nearest'] <= 20).sum()
            total_cat = len(df)
            avg_time = df['time_to_nearest'].mean()
            logger.info(f"  {category} ({total_cat:,} victims):")
            logger.info(f"    Within 20 min: {within:,} ({within/total_cat*100:.1f}%)")
            logger.info(f"    Average time to trauma: {avg_time:.1f} min")
    
    with StepLogger("Analyzing golden hour by victim race", logger):
        logger.info(f"\n  GOLDEN HOUR COVERAGE BY RACE:")
        logger.info("  " + "-" * 60)
        
        race_results = []
        for race in ['Black', 'White', 'Hispanic', 'Asian']:
            race_df = shootings[shootings['race'] == race]
            if len(race_df) == 0:
                continue
            
            total_race = len(race_df)
            within_10 = (race_df['time_to_nearest'] <= 10).sum()
            within_20 = (race_df['time_to_nearest'] <= 20).sum()
            beyond_20 = (race_df['time_to_nearest'] > 20).sum()
            avg_time = race_df['time_to_nearest'].mean()
            
            race_results.append({
                'race': race,
                'total_shootings': total_race,
                'within_10_min': within_10,
                'pct_within_10': within_10 / total_race * 100,
                'within_20_min': within_20,
                'pct_within_20': within_20 / total_race * 100,
                'beyond_20_min': beyond_20,
                'pct_beyond_20': beyond_20 / total_race * 100,
                'avg_time_min': avg_time,
            })
            
            logger.info(f"  {race} ({total_race:,} victims):")
            logger.info(f"    Within 10 min: {within_10:,} ({within_10/total_race*100:.1f}%)")
            logger.info(f"    Within 20 min: {within_20:,} ({within_20/total_race*100:.1f}%)")
            logger.info(f"    Beyond 20 min: {beyond_20:,} ({beyond_20/total_race*100:.1f}%)")
            logger.info(f"    Average time: {avg_time:.1f} min")
            logger.info("")
        
        race_df = pd.DataFrame(race_results)
    
    with StepLogger("Analyzing shootings beyond golden hour", logger):
        beyond_golden = shootings[shootings['time_to_nearest'] > 20]
        
        if len(beyond_golden) > 0:
            logger.info(f"\n  SHOOTINGS BEYOND 20 MIN ({len(beyond_golden):,} total):")
            logger.info("  " + "-" * 50)
            
            # Race breakdown
            logger.info("  By race:")
            for race, count in beyond_golden['race'].value_counts().items():
                pct = count / len(beyond_golden) * 100
                logger.info(f"    {race}: {count} ({pct:.1f}%)")
            
            # Fatal vs non-fatal
            fatal_beyond = beyond_golden['is_fatal'].sum()
            logger.info(f"\n  Fatal shootings beyond 20 min: {fatal_beyond} ({fatal_beyond/len(beyond_golden)*100:.1f}%)")
            
            # Average time
            logger.info(f"  Average time to trauma: {beyond_golden['time_to_nearest'].mean():.1f} min")
    
    with StepLogger("Saving golden hour analysis results", logger):
        # Overall distribution
        dist_df = pd.DataFrame([
            {'time_interval': k, 'shooting_count': v, 'percentage': v/total*100}
            for k, v in time_dist.items()
        ])
        
        dist_file = PATHS.tables / "golden_hour_distribution.csv"
        save_csv(dist_df, dist_file)
        logger.info(f"  Saved distribution: {dist_file}")
        
        # By race
        race_file = PATHS.tables / "golden_hour_by_race.csv"
        save_csv(race_df, race_file)
        logger.info(f"  Saved by race: {race_file}")
    
    return dist_file, race_file


if __name__ == "__main__":
    dist_path, race_path = analyze_golden_hour()
    print(f"\n✅ Golden hour analysis complete:")
    print(f"   Distribution: {dist_path}")
    print(f"   By race: {race_path}")


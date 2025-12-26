#!/usr/bin/env python3
"""
Data validation and quality assurance checks.

Verifies data integrity across the pipeline and generates
a validation report.
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import geopandas as gpd
import numpy as np

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, load_geojson, save_csv, normalize_geoid
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


class ValidationResult:
    """Container for validation results."""
    def __init__(self, name: str):
        self.name = name
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def add_check(self, check_name: str, status: str, message: str):
        self.checks.append({
            'check': check_name,
            'status': status,
            'message': message
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        else:
            self.warnings += 1
    
    def summary(self) -> str:
        return f"{self.name}: {self.passed} passed, {self.failed} failed, {self.warnings} warnings"


def validate_shooting_data() -> ValidationResult:
    """Validate shooting data quality."""
    result = ValidationResult("Shooting Data")
    
    # Load data
    raw_file = list(PATHS.raw.glob("shootings_*.csv"))[0]
    raw_df = load_csv(raw_file)
    clean_df = load_csv(PATHS.processed / "shootings_clean.csv", parse_dates=['date'])
    
    # Check 1: Records retained
    retention = len(clean_df) / len(raw_df) * 100
    if retention >= 99:
        result.add_check("Record retention", "PASS", f"{retention:.1f}% retained")
    elif retention >= 95:
        result.add_check("Record retention", "WARN", f"{retention:.1f}% retained (some loss)")
    else:
        result.add_check("Record retention", "FAIL", f"Only {retention:.1f}% retained")
    
    # Check 2: No null coordinates
    null_coords = clean_df[['lat', 'lng']].isnull().any(axis=1).sum()
    if null_coords == 0:
        result.add_check("Null coordinates", "PASS", "No null coordinates")
    else:
        result.add_check("Null coordinates", "FAIL", f"{null_coords} records with null coords")
    
    # Check 3: Coordinates in Philadelphia bounds
    in_bounds = (
        (clean_df['lat'] >= 39.86) & (clean_df['lat'] <= 40.14) &
        (clean_df['lng'] >= -75.28) & (clean_df['lng'] <= -74.95)
    ).all()
    if in_bounds:
        result.add_check("Coordinate bounds", "PASS", "All points within Philadelphia")
    else:
        out_of_bounds = len(clean_df[~(
            (clean_df['lat'] >= 39.86) & (clean_df['lat'] <= 40.14) &
            (clean_df['lng'] >= -75.28) & (clean_df['lng'] <= -74.95)
        )])
        result.add_check("Coordinate bounds", "WARN", f"{out_of_bounds} points outside bounds")
    
    # Check 4: Date range valid
    min_date = clean_df['date'].min()
    max_date = clean_df['date'].max()
    if min_date.year >= 2015 and max_date.year <= 2025:
        result.add_check("Date range", "PASS", f"{min_date.date()} to {max_date.date()}")
    else:
        result.add_check("Date range", "WARN", f"Unexpected range: {min_date} to {max_date}")
    
    # Check 5: Fatality rate reasonable
    fatal_rate = clean_df['is_fatal'].mean() * 100
    if 15 <= fatal_rate <= 30:
        result.add_check("Fatality rate", "PASS", f"{fatal_rate:.1f}% (within expected range)")
    else:
        result.add_check("Fatality rate", "WARN", f"{fatal_rate:.1f}% (outside typical 15-30% range)")
    
    return result


def validate_tract_data() -> ValidationResult:
    """Validate census tract data."""
    result = ValidationResult("Census Tract Data")
    
    # Load data
    tracts = load_geojson(PATHS.geo / "philadelphia_tracts.geojson")
    demographics = load_csv(PATHS.processed / "tract_demographics.csv")
    
    # Normalize GEOID types
    tracts['GEOID'] = normalize_geoid(tracts['GEOID'])
    demographics['GEOID'] = normalize_geoid(demographics['GEOID'])
    
    # Check 1: Expected tract count
    if len(tracts) == 408:
        result.add_check("Tract count", "PASS", "408 tracts (expected)")
    elif 400 <= len(tracts) <= 420:
        result.add_check("Tract count", "WARN", f"{len(tracts)} tracts (expected ~408)")
    else:
        result.add_check("Tract count", "FAIL", f"{len(tracts)} tracts (expected ~408)")
    
    # Check 2: Demographics join
    tracts_with_demo = tracts.merge(demographics, on='GEOID', how='left')
    missing_demo = tracts_with_demo['total_population'].isna().sum()
    if missing_demo == 0:
        result.add_check("Demographics join", "PASS", "All tracts have demographics")
    else:
        result.add_check("Demographics join", "WARN", f"{missing_demo} tracts missing demographics")
    
    # Check 3: Population total reasonable
    total_pop = demographics['total_population'].sum()
    if 1_500_000 <= total_pop <= 1_700_000:
        result.add_check("Population total", "PASS", f"{total_pop:,} (reasonable for Phila)")
    else:
        result.add_check("Population total", "WARN", f"{total_pop:,} (check accuracy)")
    
    # Check 4: Percentages sum correctly
    pct_cols = demographics[['pct_black', 'pct_white', 'pct_asian']].sum(axis=1)
    over_100 = (pct_cols > 105).sum()  # Allow 5% for rounding
    if over_100 == 0:
        result.add_check("Race percentages", "PASS", "Percentages valid")
    else:
        result.add_check("Race percentages", "WARN", f"{over_100} tracts with >105% race totals")
    
    # Check 5: No negative income values
    neg_income = (demographics['median_household_income'] < 0).sum()
    if neg_income == 0:
        result.add_check("Income values", "PASS", "No negative income values")
    else:
        result.add_check("Income values", "WARN", f"{neg_income} tracts with negative income (Census suppression)")
    
    return result


def validate_spatial_joins() -> ValidationResult:
    """Validate spatial join integrity."""
    result = ValidationResult("Spatial Joins")
    
    # Load data
    shootings = load_csv(PATHS.processed / "shootings_with_tracts.csv")
    density = load_geojson(PATHS.processed / "tract_shooting_density.geojson")
    
    # Check 1: Shootings assigned to tracts
    assigned = shootings['tract_geoid'].notna().sum()
    total = len(shootings)
    pct_assigned = assigned / total * 100
    if pct_assigned >= 99:
        result.add_check("Shooting assignment", "PASS", f"{pct_assigned:.1f}% assigned to tracts")
    else:
        result.add_check("Shooting assignment", "WARN", f"Only {pct_assigned:.1f}% assigned")
    
    # Check 2: Total shootings preserved
    shootings_sum = density['total_shootings'].sum()
    if abs(shootings_sum - assigned) <= 10:
        result.add_check("Shooting count preservation", "PASS", f"Counts match ({shootings_sum:,.0f})")
    else:
        result.add_check("Shooting count preservation", "WARN", 
                        f"Mismatch: {shootings_sum:.0f} in density vs {assigned} assigned")
    
    # Check 3: All tracts have density values
    null_density = density['annual_shootings_per_sq_mi'].isna().sum()
    if null_density == 0:
        result.add_check("Density completeness", "PASS", "All tracts have density values")
    else:
        result.add_check("Density completeness", "FAIL", f"{null_density} tracts missing density")
    
    return result


def validate_bivariate_classification() -> ValidationResult:
    """Validate bivariate classification."""
    result = ValidationResult("Bivariate Classification")
    
    # Load data
    gdf = load_geojson(PATHS.processed / "tracts_bivariate_classified.geojson")
    
    # Check 1: All tracts classified
    unclassified = gdf['bivariate_class'].isna().sum()
    if unclassified == 0:
        result.add_check("Classification completeness", "PASS", "All tracts classified")
    else:
        result.add_check("Classification completeness", "FAIL", f"{unclassified} unclassified")
    
    # Check 2: Class distribution covers 1-9
    classes = set(gdf['bivariate_class'].unique())
    expected = set(range(1, 10))
    if classes == expected:
        result.add_check("Class coverage", "PASS", "All 9 classes present")
    else:
        missing = expected - classes
        result.add_check("Class coverage", "WARN", f"Missing classes: {missing}")
    
    # Check 3: Trauma deserts (class 9) reasonable count
    td_count = (gdf['bivariate_class'] == 9).sum()
    if 10 <= td_count <= 50:
        result.add_check("Trauma desert count", "PASS", f"{td_count} trauma deserts (reasonable)")
    else:
        result.add_check("Trauma desert count", "WARN", f"{td_count} trauma deserts (check methodology)")
    
    # Check 4: Tercile distribution roughly equal
    for tercile_col in ['density_tercile', 'time_tercile']:
        counts = gdf[tercile_col].value_counts()
        min_pct = counts.min() / len(gdf) * 100
        max_pct = counts.max() / len(gdf) * 100
        if max_pct - min_pct <= 15:
            result.add_check(f"{tercile_col} balance", "PASS", f"Balanced ({min_pct:.0f}%-{max_pct:.0f}%)")
        else:
            result.add_check(f"{tercile_col} balance", "WARN", f"Imbalanced ({min_pct:.0f}%-{max_pct:.0f}%)")
    
    return result


def validate_transport_times() -> ValidationResult:
    """Validate transport time calculations."""
    result = ValidationResult("Transport Times")
    
    # Load data
    transport = load_csv(PATHS.processed / "tract_transport_times.csv")
    
    # Check 1: All tracts have transport times
    null_times = transport['time_to_nearest'].isna().sum()
    if null_times == 0:
        result.add_check("Time completeness", "PASS", "All tracts have transport times")
    else:
        result.add_check("Time completeness", "WARN", f"{null_times} tracts missing times")
    
    # Check 2: Time range reasonable
    min_time = transport['time_to_nearest'].min()
    max_time = transport['time_to_nearest'].max()
    if min_time >= 0 and max_time <= 45:
        result.add_check("Time range", "PASS", f"{min_time}-{max_time} min (reasonable)")
    else:
        result.add_check("Time range", "WARN", f"{min_time}-{max_time} min (check outliers)")
    
    # Check 3: Average time reasonable
    avg_time = transport['time_to_nearest'].mean()
    if 8 <= avg_time <= 20:
        result.add_check("Average time", "PASS", f"{avg_time:.1f} min (reasonable for urban area)")
    else:
        result.add_check("Average time", "WARN", f"{avg_time:.1f} min (unusual)")
    
    # Check 4: All tracts assigned to a trauma center
    missing_tc = transport['nearest_trauma_center'].isna().sum()
    if missing_tc == 0:
        result.add_check("Trauma center assignment", "PASS", "All tracts assigned")
    else:
        result.add_check("Trauma center assignment", "FAIL", f"{missing_tc} unassigned")
    
    return result


def run_all_validations() -> Path:
    """Run all validation checks and generate report."""
    logger.info("=" * 60)
    logger.info("RUNNING DATA VALIDATION")
    logger.info("=" * 60)
    
    results = []
    
    with StepLogger("Validating shooting data", logger):
        results.append(validate_shooting_data())
    
    with StepLogger("Validating census tract data", logger):
        results.append(validate_tract_data())
    
    with StepLogger("Validating spatial joins", logger):
        results.append(validate_spatial_joins())
    
    with StepLogger("Validating bivariate classification", logger):
        results.append(validate_bivariate_classification())
    
    with StepLogger("Validating transport times", logger):
        results.append(validate_transport_times())
    
    # Generate report
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    all_checks = []
    
    for r in results:
        logger.info(f"\n{r.summary()}")
        total_passed += r.passed
        total_failed += r.failed
        total_warnings += r.warnings
        
        for check in r.checks:
            status_icon = "✅" if check['status'] == 'PASS' else ("❌" if check['status'] == 'FAIL' else "⚠️")
            logger.info(f"  {status_icon} {check['check']}: {check['message']}")
            all_checks.append({
                'category': r.name,
                'check': check['check'],
                'status': check['status'],
                'message': check['message']
            })
    
    logger.info("\n" + "=" * 60)
    logger.info(f"TOTAL: {total_passed} passed, {total_failed} failed, {total_warnings} warnings")
    
    if total_failed == 0:
        logger.info("✅ ALL CRITICAL CHECKS PASSED")
    else:
        logger.warning(f"❌ {total_failed} CRITICAL CHECKS FAILED - REVIEW REQUIRED")
    
    logger.info("=" * 60)
    
    # Save report
    report_df = pd.DataFrame(all_checks)
    report_file = PATHS.tables / "validation_report.csv"
    save_csv(report_df, report_file)
    logger.info(f"\nReport saved to: {report_file}")
    
    return report_file


if __name__ == "__main__":
    report_path = run_all_validations()
    print(f"\n✅ Validation complete: {report_path}")


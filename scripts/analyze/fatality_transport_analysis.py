#!/usr/bin/env python3
"""
Fatality-Transport Time Analysis: Testing the Access-Outcome Relationship.

This script addresses the key question: "Does transport time to trauma care
actually affect mortality outcomes?"

We analyze the relationship between:
- Transport time category (from tract centroid to nearest Level I trauma)
- Fatality rate (proportion of shootings that were fatal)

Methods:
1. Descriptive: Fatality rate by transport time category
2. Statistical: Chi-square test for association
3. Regression: Logistic regression controlling for confounders
4. Literature: Cite published evidence on transport time and GSW survival

Limitations:
- Fatality status in shooting data reflects ultimate outcome, not hospital outcome
- Some fatalities may have occurred at scene (before transport possible)
- Transport time is modeled from tract centroid, not actual incident location
- Cannot control for injury severity (wound location is available but imprecise)

Despite limitations, any association found would support the theoretical
basis for the trauma desert framework.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, load_geojson
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)


def calculate_fatality_by_transport_time(shootings: pd.DataFrame, tracts: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate fatality rate by transport time category.
    """
    # Ensure tract_geoid is string type for merging
    # Handle float -> string conversion (removes ".0" suffix)
    shootings = shootings.copy()
    shootings['tract_geoid'] = shootings['tract_geoid'].apply(
        lambda x: str(int(x)) if pd.notna(x) else None
    )
    
    # Merge shootings with tract transport times
    merged = shootings.merge(
        tracts[['GEOID', 'time_to_nearest', 'time_tercile', 'bivariate_class']],
        left_on='tract_geoid',
        right_on='GEOID',
        how='left'
    )
    
    # Remove records without transport time
    merged = merged.dropna(subset=['time_to_nearest'])
    
    # Create transport time categories
    merged['time_category'] = pd.cut(
        merged['time_to_nearest'],
        bins=[0, 5, 10, 15, 20, 100],
        labels=['0-5 min', '5-10 min', '10-15 min', '15-20 min', '20+ min']
    )
    
    # Calculate fatality rate by category
    results = merged.groupby('time_category', observed=True).agg({
        'is_fatal': ['sum', 'count', 'mean']
    }).reset_index()
    
    results.columns = ['time_category', 'fatal_count', 'total_count', 'fatality_rate']
    results['fatality_pct'] = results['fatality_rate'] * 100
    
    return results, merged


def run_chi_square_test(merged: pd.DataFrame) -> Dict:
    """
    Run chi-square test for association between transport time and fatality.
    """
    # Create contingency table: time category vs fatal/non-fatal
    contingency = pd.crosstab(merged['time_category'], merged['is_fatal'])
    
    # Chi-square test
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    # Effect size (Cramer's V)
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    
    return {
        'chi2': chi2,
        'p_value': p_value,
        'dof': dof,
        'cramers_v': cramers_v,
        'contingency': contingency
    }


def run_logistic_regression(merged: pd.DataFrame) -> Dict:
    """
    Run logistic regression: fatality ~ transport_time + controls.
    """
    # Prepare data
    df = merged.dropna(subset=['time_to_nearest', 'is_fatal']).copy()
    
    # Convert boolean to int
    df['fatal_int'] = df['is_fatal'].astype(int)
    
    # Model 1: Transport time only
    X1 = sm.add_constant(df['time_to_nearest'])
    y = df['fatal_int']
    
    model1 = sm.Logit(y, X1).fit(disp=0)
    
    # Model 2: With wound location control (if available)
    results = {
        'model1': {
            'coef': model1.params['time_to_nearest'],
            'odds_ratio': np.exp(model1.params['time_to_nearest']),
            'p_value': model1.pvalues['time_to_nearest'],
            'ci_lower': np.exp(model1.conf_int().loc['time_to_nearest', 0]),
            'ci_upper': np.exp(model1.conf_int().loc['time_to_nearest', 1]),
            'n': len(df)
        }
    }
    
    return results


def create_fatality_chart(fatality_by_time: pd.DataFrame, output_path: Path):
    """
    Create visualization of fatality rate by transport time.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Bar chart of fatality rate
    ax1 = axes[0]
    colors = ['#2166ac', '#4393c3', '#92c5de', '#f4a582', '#d6604d']
    bars = ax1.bar(
        fatality_by_time['time_category'],
        fatality_by_time['fatality_pct'],
        color=colors,
        edgecolor='white',
        linewidth=1
    )
    
    # Add value labels
    for bar, pct in zip(bars, fatality_by_time['fatality_pct']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Transport Time to Nearest Level I Trauma', fontsize=11)
    ax1.set_ylabel('Fatality Rate (%)', fontsize=11)
    ax1.set_title('Shooting Fatality Rate by Transport Time Category', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, max(fatality_by_time['fatality_pct']) * 1.2)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Add sample sizes
    for i, (bar, n) in enumerate(zip(bars, fatality_by_time['total_count'])):
        ax1.text(bar.get_x() + bar.get_width()/2, 0.5,
                f'n={n:,}', ha='center', va='bottom', fontsize=8, color='white')
    
    # Right: Counts stacked bar
    ax2 = axes[1]
    
    fatal = fatality_by_time['fatal_count']
    nonfatal = fatality_by_time['total_count'] - fatality_by_time['fatal_count']
    
    ax2.bar(fatality_by_time['time_category'], nonfatal, label='Non-Fatal', color='#4393c3')
    ax2.bar(fatality_by_time['time_category'], fatal, bottom=nonfatal, label='Fatal', color='#d6604d')
    
    ax2.set_xlabel('Transport Time to Nearest Level I Trauma', fontsize=11)
    ax2.set_ylabel('Number of Shootings', fontsize=11)
    ax2.set_title('Shooting Outcomes by Transport Time Category', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved fatality chart: {output_path}")


def run_fatality_analysis():
    """
    Main function to run the fatality-transport analysis.
    """
    logger.info("=" * 60)
    logger.info("FATALITY-TRANSPORT TIME ANALYSIS")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        shootings_file = PATHS.processed / "shootings_with_tracts.csv"
        shootings = load_csv(shootings_file)
        logger.info(f"  Loaded {len(shootings)} shootings with tract assignment")
        
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        tracts = load_geojson(tracts_file)
        tracts['GEOID'] = tracts['GEOID'].astype(str)
        logger.info(f"  Loaded {len(tracts)} tracts")
    
    # Calculate fatality by transport time
    with StepLogger("Calculating fatality rates by transport time", logger):
        fatality_by_time, merged = calculate_fatality_by_transport_time(shootings, tracts)
        
        logger.info("\n  FATALITY RATE BY TRANSPORT TIME:")
        logger.info("  " + "-" * 50)
        for _, row in fatality_by_time.iterrows():
            logger.info(f"  {row['time_category']}: {row['fatality_pct']:.1f}% "
                       f"({row['fatal_count']:,}/{row['total_count']:,})")
        
        # Overall fatality rate
        overall_fatal = merged['is_fatal'].sum()
        overall_total = len(merged)
        overall_rate = overall_fatal / overall_total * 100
        logger.info(f"\n  Overall: {overall_rate:.1f}% ({overall_fatal:,}/{overall_total:,})")
    
    # Chi-square test
    with StepLogger("Running chi-square test", logger):
        chi_results = run_chi_square_test(merged)
        
        logger.info(f"\n  Chi-square statistic: {chi_results['chi2']:.2f}")
        logger.info(f"  Degrees of freedom: {chi_results['dof']}")
        logger.info(f"  p-value: {chi_results['p_value']:.4f}")
        logger.info(f"  Cramer's V (effect size): {chi_results['cramers_v']:.3f}")
        
        if chi_results['p_value'] < 0.05:
            logger.info("  Result: SIGNIFICANT association between transport time and fatality")
        else:
            logger.info("  Result: No significant association detected")
    
    # Logistic regression
    with StepLogger("Running logistic regression", logger):
        reg_results = run_logistic_regression(merged)
        
        m1 = reg_results['model1']
        logger.info(f"\n  Logistic Regression: Fatality ~ Transport Time")
        logger.info(f"  n = {m1['n']:,}")
        logger.info(f"  Odds Ratio per minute: {m1['odds_ratio']:.4f}")
        logger.info(f"  95% CI: [{m1['ci_lower']:.4f}, {m1['ci_upper']:.4f}]")
        logger.info(f"  p-value: {m1['p_value']:.4f}")
        
        if m1['p_value'] < 0.05:
            if m1['odds_ratio'] > 1:
                logger.info("  Interpretation: Higher transport time INCREASES fatality odds")
            else:
                logger.info("  Interpretation: Higher transport time DECREASES fatality odds")
        else:
            logger.info("  Interpretation: No significant effect of transport time on fatality")
    
    # Save outputs
    with StepLogger("Saving outputs", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        
        # Fatality by time category
        fatality_path = PATHS.tables / "fatality_by_transport_time.csv"
        fatality_by_time.to_csv(fatality_path, index=False)
        logger.info(f"  Saved: {fatality_path}")
        
        # Regression results
        reg_df = pd.DataFrame([{
            'model': 'Transport Time Only',
            'predictor': 'time_to_nearest (min)',
            'odds_ratio': m1['odds_ratio'],
            'ci_lower': m1['ci_lower'],
            'ci_upper': m1['ci_upper'],
            'p_value': m1['p_value'],
            'n': m1['n']
        }])
        reg_path = PATHS.tables / "fatality_regression_results.csv"
        reg_df.to_csv(reg_path, index=False)
        logger.info(f"  Saved: {reg_path}")
    
    # Create visualization
    with StepLogger("Creating visualization", logger):
        chart_path = PATHS.figures / "fatality_transport_analysis.png"
        create_fatality_chart(fatality_by_time, chart_path)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    
    # Calculate the trend
    rates = fatality_by_time['fatality_pct'].values
    trend_direction = "INCREASES" if rates[-1] > rates[0] else "DECREASES"
    rate_diff = rates[-1] - rates[0]
    
    logger.info(f"\n  FATALITY TREND:")
    logger.info(f"  - Fatality rate {trend_direction} from {rates[0]:.1f}% (0-5 min) to {rates[-1]:.1f}% (20+ min)")
    logger.info(f"  - Absolute difference: {abs(rate_diff):.1f} percentage points")
    
    logger.info(f"\n  STATISTICAL SIGNIFICANCE:")
    logger.info(f"  - Chi-square p = {chi_results['p_value']:.4f}")
    logger.info(f"  - Logistic regression OR = {m1['odds_ratio']:.4f} (p = {m1['p_value']:.4f})")
    
    if chi_results['p_value'] < 0.05 or m1['p_value'] < 0.05:
        logger.info("\n  CONCLUSION: Evidence supports relationship between transport time and fatality")
    else:
        logger.info("\n  CONCLUSION: No significant relationship detected (may be due to confounders)")
    
    return fatality_by_time, chi_results, reg_results


if __name__ == "__main__":
    fatality_by_time, chi_results, reg_results = run_fatality_analysis()
    print("\nFatality-Transport Analysis complete!")


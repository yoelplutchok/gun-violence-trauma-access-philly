#!/usr/bin/env python3
"""
Oaxaca-Blinder Decomposition: Quantifying the Racial Disparity.

This script uses the Oaxaca-Blinder decomposition technique to answer:
"How much of the disparity in shooting density/transport time between 
predominantly Black and non-Black neighborhoods is explained by 
measurable factors vs. unexplained (potentially structural) factors?"

The decomposition breaks the gap into:
1. ENDOWMENTS (Explained): Differences due to different characteristics
   (e.g., Black tracts have higher poverty rates)
2. COEFFICIENTS (Unexplained): Differences in how characteristics translate
   to outcomes (e.g., same poverty rate → different outcomes by race)
3. INTERACTION: Combination of both effects

A large "unexplained" portion suggests structural/discriminatory factors
that can't be attributed to observable neighborhood characteristics.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Threshold for "predominantly Black" tract
BLACK_THRESHOLD = 50  # % Black population


def prepare_data(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Prepare data for Oaxaca-Blinder decomposition.
    """
    df = gdf.copy()
    
    # Create binary group indicator
    df['predominantly_black'] = (df['pct_black'] >= BLACK_THRESHOLD).astype(int)
    
    # Log-transform skewed variables for better regression fit
    df['log_shootings_per_sq_mi'] = np.log1p(df['annual_shootings_per_sq_mi'])
    
    # Standardize continuous predictors for interpretation
    for col in ['pct_poverty', 'median_household_income', 'total_population']:
        if col in df.columns:
            df[f'{col}_std'] = (df[col] - df[col].mean()) / df[col].std()
    
    # Clean missing values
    df = df.dropna(subset=['pct_black', 'pct_poverty', 'annual_shootings_per_sq_mi', 
                           'time_to_nearest'])
    
    return df


def run_oaxaca_decomposition(
    df: pd.DataFrame,
    outcome: str,
    predictors: list,
    group_col: str = 'predominantly_black'
) -> Dict:
    """
    Perform Oaxaca-Blinder decomposition.
    
    Args:
        df: DataFrame with outcome, predictors, and group indicator
        outcome: Name of outcome variable
        predictors: List of predictor variable names
        group_col: Name of binary group indicator (1 = disadvantaged group)
        
    Returns:
        Dictionary with decomposition results
    """
    # Split by group
    df_black = df[df[group_col] == 1].copy()
    df_other = df[df[group_col] == 0].copy()
    
    logger.info(f"  Group sizes: Black tracts = {len(df_black)}, Other = {len(df_other)}")
    
    # Calculate mean outcomes
    y_black = df_black[outcome].mean()
    y_other = df_other[outcome].mean()
    raw_gap = y_black - y_other
    
    logger.info(f"  Mean {outcome}: Black = {y_black:.3f}, Other = {y_other:.3f}")
    logger.info(f"  Raw gap: {raw_gap:.3f}")
    
    # Run regressions for each group
    X_black = sm.add_constant(df_black[predictors])
    X_other = sm.add_constant(df_other[predictors])
    
    model_black = OLS(df_black[outcome], X_black).fit()
    model_other = OLS(df_other[outcome], X_other).fit()
    
    # Calculate mean predictor values
    x_bar_black = X_black.mean()
    x_bar_other = X_other.mean()
    
    # Get coefficients
    beta_black = model_black.params
    beta_other = model_other.params
    
    # Threefold decomposition (Blinder, 1973)
    # Using non-discriminatory coefficients as reference (pooled model)
    X_pooled = sm.add_constant(df[predictors])
    model_pooled = OLS(df[outcome], X_pooled).fit()
    beta_pooled = model_pooled.params
    
    # Components:
    # 1. Endowments (E): (X_B - X_O) * β*
    endowments = (x_bar_black - x_bar_other) @ beta_pooled
    
    # 2. Coefficients (C): X_O * (β_B - β_O)
    coefficients = x_bar_other @ (beta_black - beta_other)
    
    # 3. Interaction (I): (X_B - X_O) * (β_B - β_O)
    interaction = (x_bar_black - x_bar_other) @ (beta_black - beta_other)
    
    # Verify: E + C + I should equal raw gap
    total_explained = endowments + coefficients + interaction
    
    # Alternative twofold decomposition (simpler interpretation)
    # Explained: (X_B - X_O) * β_O
    explained = (x_bar_black - x_bar_other) @ beta_other
    # Unexplained: X_B * (β_B - β_O)
    unexplained = x_bar_black @ (beta_black - beta_other)
    
    # Calculate contribution of each predictor to explained portion
    predictor_contributions = {}
    for i, pred in enumerate(['const'] + predictors):
        contrib = (x_bar_black[pred] - x_bar_other[pred]) * beta_other[pred]
        predictor_contributions[pred] = contrib
    
    results = {
        'outcome': outcome,
        'n_black': len(df_black),
        'n_other': len(df_other),
        'mean_black': y_black,
        'mean_other': y_other,
        'raw_gap': raw_gap,
        'endowments': endowments,
        'coefficients': coefficients,
        'interaction': interaction,
        'explained': explained,
        'unexplained': unexplained,
        'pct_explained': (explained / raw_gap * 100) if raw_gap != 0 else 0,
        'pct_unexplained': (unexplained / raw_gap * 100) if raw_gap != 0 else 0,
        'predictor_contributions': predictor_contributions,
        'model_black_r2': model_black.rsquared,
        'model_other_r2': model_other.rsquared,
    }
    
    return results


def create_decomposition_chart(
    results_shooting: Dict,
    results_time: Dict,
    output_path: Path
):
    """
    Create visualization of the decomposition results.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Colors
    explained_color = '#2166ac'  # Blue
    unexplained_color = '#b2182b'  # Red
    
    # Chart 1: Shooting Density Gap
    ax1 = axes[0]
    
    gap = results_shooting['raw_gap']
    explained = results_shooting['explained']
    unexplained = results_shooting['unexplained']
    
    # Stacked bar
    bars1 = ax1.bar(['Explained\n(Characteristics)', 'Unexplained\n(Structural)'], 
                    [explained, unexplained],
                    color=[explained_color, unexplained_color],
                    edgecolor='black', linewidth=1.5)
    
    # Add horizontal line for total gap
    ax1.axhline(y=gap, color='black', linestyle='--', linewidth=2, 
               label=f'Total Gap: {gap:.2f}')
    
    # Percentages
    ax1.text(0, explained/2, f'{results_shooting["pct_explained"]:.1f}%', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    ax1.text(1, unexplained/2, f'{results_shooting["pct_unexplained"]:.1f}%',
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    ax1.set_ylabel('Contribution to Gap (log shootings/sq mi)', fontsize=11)
    ax1.set_title('SHOOTING DENSITY GAP\nBlack vs Non-Black Tracts', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right')
    
    # Add interpretation text
    if results_shooting['pct_unexplained'] > 50:
        interp = "Majority UNEXPLAINED\n(structural factors)"
    else:
        interp = "Majority EXPLAINED\n(observable characteristics)"
    ax1.text(0.5, 0.95, interp, transform=ax1.transAxes, ha='center', va='top',
            fontsize=10, style='italic', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Chart 2: Transport Time Gap
    ax2 = axes[1]
    
    gap = results_time['raw_gap']
    explained = results_time['explained']
    unexplained = results_time['unexplained']
    
    # Handle negative values (if Black tracts are actually closer)
    if gap < 0:
        ax2.text(0.5, 0.5, f'Black tracts are CLOSER\nto trauma centers\n(gap = {gap:.2f} min)',
                transform=ax2.transAxes, ha='center', va='center',
                fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        ax2.set_xlim(-1, 1)
        ax2.set_ylim(-1, 1)
        ax2.axis('off')
    else:
        bars2 = ax2.bar(['Explained\n(Characteristics)', 'Unexplained\n(Structural)'],
                        [explained, unexplained],
                        color=[explained_color, unexplained_color],
                        edgecolor='black', linewidth=1.5)
        
        ax2.axhline(y=gap, color='black', linestyle='--', linewidth=2,
                   label=f'Total Gap: {gap:.2f} min')
        
        ax2.text(0, explained/2, f'{results_time["pct_explained"]:.1f}%',
                ha='center', va='center', fontsize=14, fontweight='bold', color='white')
        ax2.text(1, unexplained/2, f'{results_time["pct_unexplained"]:.1f}%',
                ha='center', va='center', fontsize=14, fontweight='bold', color='white')
        
        ax2.set_ylabel('Contribution to Gap (minutes)', fontsize=11)
        ax2.legend(loc='upper right')
    
    ax2.set_title('TRANSPORT TIME GAP\nBlack vs Non-Black Tracts', fontsize=12, fontweight='bold')
    
    plt.suptitle('Oaxaca-Blinder Decomposition: Quantifying the Racial Disparity',
                fontsize=14, fontweight='bold', y=1.02)
    
    # Add legend explanation
    fig.text(0.5, -0.05, 
            'EXPLAINED = Due to different neighborhood characteristics (poverty, income, etc.)\n'
            'UNEXPLAINED = Structural/systemic factors not captured by observable characteristics',
            ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved decomposition chart: {output_path}")


def create_predictor_contribution_chart(
    results: Dict,
    output_path: Path
):
    """
    Show which predictors contribute most to the explained portion.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    contributions = results['predictor_contributions']
    
    # Remove constant and sort by absolute contribution
    pred_contrib = {k: v for k, v in contributions.items() if k != 'const'}
    sorted_contribs = sorted(pred_contrib.items(), key=lambda x: abs(x[1]), reverse=True)
    
    predictors = [x[0].replace('_std', '').replace('_', ' ').title() for x in sorted_contribs]
    values = [x[1] for x in sorted_contribs]
    
    colors = ['#d73027' if v > 0 else '#4575b4' for v in values]
    
    bars = ax.barh(predictors, values, color=colors, edgecolor='black')
    
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('Contribution to Gap', fontsize=11)
    ax.set_title(f'Predictor Contributions to {results["outcome"]} Gap\n(Explained Portion Only)',
                fontsize=12, fontweight='bold')
    
    # Add legend
    red_patch = mpatches.Patch(color='#d73027', label='Widens gap (Black tracts worse)')
    blue_patch = mpatches.Patch(color='#4575b4', label='Narrows gap (Black tracts better)')
    ax.legend(handles=[red_patch, blue_patch], loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved predictor chart: {output_path}")


def run_oaxaca_analysis():
    """
    Main function to run the Oaxaca-Blinder decomposition analysis.
    """
    logger.info("=" * 60)
    logger.info("OAXACA-BLINDER DECOMPOSITION ANALYSIS")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts_file = PATHS.processed / "tracts_with_vulnerability.geojson"
        if not tracts_file.exists():
            tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
    
    # Prepare data
    with StepLogger("Preparing data", logger):
        df = prepare_data(gdf)
        n_black = (df['predominantly_black'] == 1).sum()
        n_other = (df['predominantly_black'] == 0).sum()
        logger.info(f"  Predominantly Black tracts (≥50%): {n_black}")
        logger.info(f"  Other tracts: {n_other}")
    
    # Define predictors
    predictors = ['pct_poverty_std', 'median_household_income_std', 'total_population_std']
    
    # Decomposition 1: Shooting Density
    with StepLogger("Decomposing SHOOTING DENSITY gap", logger):
        results_shooting = run_oaxaca_decomposition(
            df,
            outcome='log_shootings_per_sq_mi',
            predictors=predictors
        )
        
        logger.info(f"\n  📊 SHOOTING DENSITY DECOMPOSITION:")
        logger.info(f"     Raw gap: {results_shooting['raw_gap']:.3f} log units")
        logger.info(f"     Explained: {results_shooting['explained']:.3f} ({results_shooting['pct_explained']:.1f}%)")
        logger.info(f"     Unexplained: {results_shooting['unexplained']:.3f} ({results_shooting['pct_unexplained']:.1f}%)")
    
    # Decomposition 2: Transport Time
    with StepLogger("Decomposing TRANSPORT TIME gap", logger):
        results_time = run_oaxaca_decomposition(
            df,
            outcome='time_to_nearest',
            predictors=predictors
        )
        
        logger.info(f"\n  📊 TRANSPORT TIME DECOMPOSITION:")
        logger.info(f"     Raw gap: {results_time['raw_gap']:.2f} minutes")
        
        if results_time['raw_gap'] < 0:
            logger.info(f"     ⚠️ Black tracts are actually CLOSER to trauma centers!")
        else:
            logger.info(f"     Explained: {results_time['explained']:.3f} ({results_time['pct_explained']:.1f}%)")
            logger.info(f"     Unexplained: {results_time['unexplained']:.3f} ({results_time['pct_unexplained']:.1f}%)")
    
    # Save results
    with StepLogger("Saving results", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        
        # Summary table
        summary = pd.DataFrame([
            {
                'Outcome': 'Shooting Density (log)',
                'Mean_Black_Tracts': results_shooting['mean_black'],
                'Mean_Other_Tracts': results_shooting['mean_other'],
                'Raw_Gap': results_shooting['raw_gap'],
                'Explained': results_shooting['explained'],
                'Unexplained': results_shooting['unexplained'],
                'Pct_Explained': results_shooting['pct_explained'],
                'Pct_Unexplained': results_shooting['pct_unexplained'],
            },
            {
                'Outcome': 'Transport Time (min)',
                'Mean_Black_Tracts': results_time['mean_black'],
                'Mean_Other_Tracts': results_time['mean_other'],
                'Raw_Gap': results_time['raw_gap'],
                'Explained': results_time['explained'],
                'Unexplained': results_time['unexplained'],
                'Pct_Explained': results_time['pct_explained'],
                'Pct_Unexplained': results_time['pct_unexplained'],
            }
        ])
        
        summary_path = PATHS.tables / "oaxaca_decomposition_results.csv"
        summary.to_csv(summary_path, index=False)
        logger.info(f"  Saved: {summary_path}")
        
        # Predictor contributions
        contrib_df = pd.DataFrame([
            {'Predictor': k, 'Contribution': v}
            for k, v in results_shooting['predictor_contributions'].items()
        ])
        contrib_path = PATHS.tables / "oaxaca_predictor_contributions.csv"
        contrib_df.to_csv(contrib_path, index=False)
    
    # Create visualizations
    with StepLogger("Creating visualizations", logger):
        decomp_path = PATHS.figures / "oaxaca_decomposition.png"
        create_decomposition_chart(results_shooting, results_time, decomp_path)
        
        contrib_chart_path = PATHS.figures / "oaxaca_predictor_contributions.png"
        create_predictor_contribution_chart(results_shooting, contrib_chart_path)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    
    logger.info(f"\n  🎯 SHOOTING DENSITY GAP:")
    # Note: ratio is exp(mean(log1p(density))) - geometric mean ratio, not arithmetic
    logger.info(f"     Black tracts have {np.exp(results_shooting['raw_gap']):.1f}x higher shooting density (geometric mean ratio)")
    logger.info(f"     {results_shooting['pct_explained']:.1f}% explained by poverty/income")
    logger.info(f"     {results_shooting['pct_unexplained']:.1f}% UNEXPLAINED (structural factors)")
    
    logger.info(f"\n  🎯 TRANSPORT TIME GAP:")
    if results_time['raw_gap'] < 0:
        logger.info(f"     Black tracts are {abs(results_time['raw_gap']):.1f} min CLOSER to trauma")
        logger.info(f"     ✅ No access disparity against Black neighborhoods")
    else:
        logger.info(f"     Black tracts are {results_time['raw_gap']:.1f} min further from trauma")
        logger.info(f"     {results_time['pct_explained']:.1f}% explained by characteristics")
        logger.info(f"     {results_time['pct_unexplained']:.1f}% unexplained")
    
    return results_shooting, results_time


if __name__ == "__main__":
    results_shooting, results_time = run_oaxaca_analysis()
    print("\n✅ Oaxaca-Blinder decomposition complete!")


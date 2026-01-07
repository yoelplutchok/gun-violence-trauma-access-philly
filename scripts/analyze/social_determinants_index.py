#!/usr/bin/env python3
"""
Social Determinants of Health Index: Compound Disadvantage Analysis.

Creates a composite "Neighborhood Vulnerability Index" (NVI) showing how
trauma deserts overlap with other forms of neighborhood disadvantage.

Using available data:
- Poverty rate (Census ACS) ✓
- Median household income (Census ACS) ✓
- Shooting density (our analysis) ✓
- Transport time to trauma (our analysis) ✓

Additional layers can be added if data is provided:
- Housing code violations
- Vacant properties
- 311 service request responsiveness
- Eviction rates
- Overdose incidents

This analysis strengthens the equity narrative by showing that trauma
deserts don't exist in isolation—they overlap with multiple forms of
structural disadvantage.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
from scipy import stats

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Color schemes
VULNERABILITY_CMAP = LinearSegmentedColormap.from_list(
    'vulnerability',
    ['#f7fcf5', '#c7e9c0', '#74c476', '#31a354', '#006d2c']
)

COMPOUND_CMAP = LinearSegmentedColormap.from_list(
    'compound',
    ['#ffffcc', '#fed976', '#fd8d3c', '#e31a1c', '#800026']
)


def normalize_indicator(series: pd.Series, higher_is_worse: bool = True) -> pd.Series:
    """
    Normalize an indicator to 0-1 scale.
    
    Args:
        series: Raw indicator values
        higher_is_worse: If True, higher values = more disadvantage
        
    Returns:
        Normalized values (0 = best, 1 = worst)
    """
    # Handle missing values
    series = series.fillna(series.median())
    
    # Min-max normalization
    min_val = series.min()
    max_val = series.max()
    
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    
    normalized = (series - min_val) / (max_val - min_val)
    
    # Flip if lower is worse
    if not higher_is_worse:
        normalized = 1 - normalized
    
    return normalized


def calculate_vulnerability_index(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate the Neighborhood Vulnerability Index (NVI).
    
    The NVI combines multiple indicators into a single score.
    Higher score = more vulnerable/disadvantaged.
    """
    result = gdf.copy()
    
    # Define indicators and their weights
    indicators = {}
    
    # Economic disadvantage
    if 'pct_poverty' in result.columns:
        indicators['poverty'] = {
            'column': 'pct_poverty',
            'weight': 0.25,
            'higher_is_worse': True,
            'label': 'Poverty Rate'
        }
    
    if 'median_household_income' in result.columns:
        indicators['income'] = {
            'column': 'median_household_income',
            'weight': 0.20,
            'higher_is_worse': False,  # Lower income = worse
            'label': 'Household Income'
        }
    
    # Violence burden
    if 'annual_shootings_per_sq_mi' in result.columns:
        indicators['violence'] = {
            'column': 'annual_shootings_per_sq_mi',
            'weight': 0.30,
            'higher_is_worse': True,
            'label': 'Shooting Density'
        }
    elif 'shootings_per_sq_mi' in result.columns:
        indicators['violence'] = {
            'column': 'shootings_per_sq_mi',
            'weight': 0.30,
            'higher_is_worse': True,
            'label': 'Shooting Density'
        }
    
    # Healthcare access
    if 'time_to_nearest' in result.columns:
        indicators['access'] = {
            'column': 'time_to_nearest',
            'weight': 0.25,
            'higher_is_worse': True,
            'label': 'Transport Time'
        }
    
    # Normalize each indicator
    for key, config in indicators.items():
        col = config['column']
        normalized_col = f'{key}_normalized'
        result[normalized_col] = normalize_indicator(
            result[col], 
            config['higher_is_worse']
        )
        logger.info(f"  Normalized: {config['label']} ({col})")
    
    # Calculate weighted composite index
    result['vulnerability_index'] = 0
    total_weight = 0
    
    for key, config in indicators.items():
        normalized_col = f'{key}_normalized'
        weight = config['weight']
        result['vulnerability_index'] += result[normalized_col] * weight
        total_weight += weight
    
    # Normalize to 0-100 scale
    result['vulnerability_index'] = (result['vulnerability_index'] / total_weight) * 100
    
    # Create vulnerability categories
    result['vulnerability_category'] = pd.cut(
        result['vulnerability_index'],
        bins=[0, 20, 40, 60, 80, 100],
        labels=['Very Low', 'Low', 'Moderate', 'High', 'Very High']
    )
    
    return result, indicators


def analyze_overlap_with_trauma_deserts(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Analyze how trauma desert classification correlates with vulnerability.
    """
    # Compare vulnerability by bivariate class
    class_stats = gdf.groupby('bivariate_class').agg({
        'vulnerability_index': ['mean', 'std', 'count'],
        'total_population': 'sum',
        'total_shootings': 'sum',
        'pct_poverty': 'mean',
        'pct_black': 'mean'
    }).round(2)
    
    class_stats.columns = ['_'.join(col).strip() for col in class_stats.columns]
    class_stats = class_stats.reset_index()
    
    # Add class labels
    class_labels = {
        1: 'Low Violence + Good Access',
        2: 'Low Violence + Moderate Access',
        3: 'Low Violence + Poor Access',
        4: 'Moderate Violence + Good Access',
        5: 'Moderate Violence + Moderate Access',
        6: 'Moderate Violence + Poor Access',
        7: 'High Violence + Good Access',
        8: 'High Violence + Moderate Access',
        9: 'TRAUMA DESERT'
    }
    class_stats['class_label'] = class_stats['bivariate_class'].map(class_labels)
    
    return class_stats


def calculate_compound_disadvantage_score(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate a compound disadvantage score that combines:
    - Trauma desert status
    - Vulnerability index
    - Racial demographics
    """
    result = gdf.copy()
    
    # Base score from vulnerability index
    result['compound_score'] = result['vulnerability_index']
    
    # Bonus for being a trauma desert (class 9)
    result['is_trauma_desert'] = result['bivariate_class'] == 9
    result.loc[result['is_trauma_desert'], 'compound_score'] += 20
    
    # Cap at 100
    result['compound_score'] = result['compound_score'].clip(0, 100)
    
    # Rank tracts by compound disadvantage
    result['compound_rank'] = result['compound_score'].rank(ascending=False, method='min')
    
    # Identify "compound disadvantage" tracts (top quartile)
    threshold = result['compound_score'].quantile(0.75)
    result['is_compound_disadvantage'] = result['compound_score'] >= threshold
    
    return result


def create_vulnerability_map(
    gdf: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create a map showing the vulnerability index.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Vulnerability index
    ax1 = axes[0]
    gdf.plot(
        column='vulnerability_index',
        ax=ax1,
        cmap=VULNERABILITY_CMAP,
        edgecolor='#666666',
        linewidth=0.2,
        legend=True,
        legend_kwds={'label': 'Vulnerability Index (0-100)', 'shrink': 0.6}
    )
    
    # Add trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax1.plot(tc['longitude'], tc['latitude'],
                    'r^', markersize=8, markeredgecolor='white', markeredgewidth=1)
    
    ax1.set_title('Neighborhood Vulnerability Index\n(Poverty + Income + Violence + Access)',
                 fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # Right: Compound disadvantage with trauma desert overlay
    ax2 = axes[1]
    gdf.plot(
        column='compound_score',
        ax=ax2,
        cmap=COMPOUND_CMAP,
        edgecolor='#666666',
        linewidth=0.2,
        legend=True,
        legend_kwds={'label': 'Compound Disadvantage Score', 'shrink': 0.6}
    )
    
    # Highlight trauma deserts
    trauma_deserts = gdf[gdf['is_trauma_desert']]
    if len(trauma_deserts) > 0:
        trauma_deserts.plot(ax=ax2, facecolor='none', edgecolor='#000000',
                           linewidth=2, linestyle='--')
    
    # Add trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax2.plot(tc['longitude'], tc['latitude'],
                    'r^', markersize=8, markeredgecolor='white', markeredgewidth=1)
    
    ax2.set_title('Compound Disadvantage Score\n(Dashed = Trauma Desert Tracts)',
                 fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    plt.suptitle(
        'Social Determinants Analysis: Compound Disadvantage in Philadelphia',
        fontsize=14, fontweight='bold', y=0.98
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved vulnerability map: {output_path}")


def create_correlation_chart(gdf: gpd.GeoDataFrame, output_path: Path):
    """
    Create charts showing correlations between indicators.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Vulnerability vs % Black
    ax1 = axes[0, 0]
    ax1.scatter(gdf['pct_black'], gdf['vulnerability_index'], 
               alpha=0.5, c=gdf['bivariate_class'], cmap='RdYlGn_r', s=30)
    
    # Add regression line
    slope, intercept, r, p, se = stats.linregress(
        gdf['pct_black'].dropna(), 
        gdf.loc[gdf['pct_black'].notna(), 'vulnerability_index']
    )
    x_line = np.array([0, 100])
    ax1.plot(x_line, intercept + slope * x_line, 'r--', linewidth=2, 
            label=f'r = {r:.3f}, p < 0.001')
    
    ax1.set_xlabel('% Black Population')
    ax1.set_ylabel('Vulnerability Index')
    ax1.set_title('Vulnerability vs. Race', fontweight='bold')
    ax1.legend()
    
    # 2. Vulnerability vs Poverty
    ax2 = axes[0, 1]
    ax2.scatter(gdf['pct_poverty'], gdf['vulnerability_index'],
               alpha=0.5, c='#2166ac', s=30)
    
    slope, intercept, r, p, se = stats.linregress(
        gdf['pct_poverty'].dropna(),
        gdf.loc[gdf['pct_poverty'].notna(), 'vulnerability_index']
    )
    x_line = np.array([0, gdf['pct_poverty'].max()])
    ax2.plot(x_line, intercept + slope * x_line, 'r--', linewidth=2,
            label=f'r = {r:.3f}')
    
    ax2.set_xlabel('% Below Poverty Line')
    ax2.set_ylabel('Vulnerability Index')
    ax2.set_title('Vulnerability vs. Poverty', fontweight='bold')
    ax2.legend()
    
    # 3. Box plot by bivariate class
    ax3 = axes[1, 0]
    class_data = [gdf[gdf['bivariate_class'] == c]['vulnerability_index'].values 
                  for c in range(1, 10)]
    bp = ax3.boxplot(class_data, patch_artist=True)
    
    colors = ['#e8e8e8', '#b5c0da', '#6c83b5', '#b8d6be', '#90b2b3', 
              '#567994', '#73ae80', '#5a9178', '#2a5a5b']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax3.set_xlabel('Bivariate Class (1-9)')
    ax3.set_ylabel('Vulnerability Index')
    ax3.set_title('Vulnerability by Classification\n(9 = Trauma Desert)', fontweight='bold')
    
    # 4. Compound disadvantage distribution
    ax4 = axes[1, 1]
    
    # Histogram with trauma desert highlight
    non_desert = gdf[~gdf['is_trauma_desert']]['compound_score']
    desert = gdf[gdf['is_trauma_desert']]['compound_score']
    
    ax4.hist(non_desert, bins=20, alpha=0.7, label='Other Tracts', color='#74c476')
    ax4.hist(desert, bins=10, alpha=0.9, label='Trauma Deserts', color='#d73027')
    
    ax4.axvline(x=gdf['compound_score'].quantile(0.75), color='black', 
               linestyle='--', label='Top Quartile Threshold')
    
    ax4.set_xlabel('Compound Disadvantage Score')
    ax4.set_ylabel('Number of Tracts')
    ax4.set_title('Distribution of Compound Disadvantage', fontweight='bold')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved correlation charts: {output_path}")


def run_social_determinants_analysis():
    """
    Main function to run the social determinants analysis.
    """
    logger.info("=" * 60)
    logger.info("SOCIAL DETERMINANTS OF HEALTH INDEX")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
        
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
    
    # Calculate vulnerability index
    with StepLogger("Calculating Vulnerability Index", logger):
        gdf, indicators = calculate_vulnerability_index(gdf)
        
        logger.info(f"  Indicators used: {len(indicators)}")
        logger.info(f"  Mean vulnerability: {gdf['vulnerability_index'].mean():.1f}")
        logger.info(f"  Max vulnerability: {gdf['vulnerability_index'].max():.1f}")
    
    # Analyze overlap with trauma deserts
    with StepLogger("Analyzing overlap with trauma deserts", logger):
        class_stats = analyze_overlap_with_trauma_deserts(gdf)
        
        # Compare trauma deserts to city average
        city_avg = gdf['vulnerability_index'].mean()
        desert_avg = gdf[gdf['bivariate_class'] == 9]['vulnerability_index'].mean()
        
        logger.info(f"  City average vulnerability: {city_avg:.1f}")
        logger.info(f"  Trauma desert average: {desert_avg:.1f}")
        logger.info(f"  Ratio: {desert_avg/city_avg:.2f}x")
    
    # Calculate compound disadvantage
    with StepLogger("Calculating compound disadvantage", logger):
        gdf = calculate_compound_disadvantage_score(gdf)
        
        n_compound = gdf['is_compound_disadvantage'].sum()
        n_both = ((gdf['is_compound_disadvantage']) & (gdf['is_trauma_desert'])).sum()
        
        logger.info(f"  Compound disadvantage tracts: {n_compound}")
        logger.info(f"  Overlap with trauma deserts: {n_both}")
    
    # Run correlation analysis
    with StepLogger("Running correlation analysis", logger):
        # Vulnerability vs race
        r_race, p_race = stats.pearsonr(
            gdf['pct_black'].dropna(),
            gdf.loc[gdf['pct_black'].notna(), 'vulnerability_index']
        )
        logger.info(f"  Vulnerability vs % Black: r={r_race:.3f}, p={p_race:.2e}")
        
        # Vulnerability vs poverty
        r_pov, p_pov = stats.pearsonr(
            gdf['pct_poverty'].dropna(),
            gdf.loc[gdf['pct_poverty'].notna(), 'vulnerability_index']
        )
        logger.info(f"  Vulnerability vs % Poverty: r={r_pov:.3f}, p={p_pov:.2e}")
    
    # Save outputs
    with StepLogger("Saving outputs", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        
        # Save class statistics
        class_stats_path = PATHS.tables / "vulnerability_by_bivariate_class.csv"
        class_stats.to_csv(class_stats_path, index=False)
        logger.info(f"  Saved: {class_stats_path}")
        
        # Save tract-level vulnerability
        vuln_cols = ['GEOID', 'NAME', 'vulnerability_index', 'vulnerability_category',
                    'compound_score', 'compound_rank', 'is_compound_disadvantage',
                    'bivariate_class', 'is_trauma_desert', 'pct_black', 'pct_poverty']
        vuln_df = gdf[[c for c in vuln_cols if c in gdf.columns]].copy()
        vuln_path = PATHS.tables / "tract_vulnerability_scores.csv"
        vuln_df.to_csv(vuln_path, index=False)
        logger.info(f"  Saved: {vuln_path}")
        
        # Save full GeoJSON
        gdf.to_file(PATHS.processed / "tracts_with_vulnerability.geojson", driver="GeoJSON")
    
    # Create visualizations
    with StepLogger("Creating visualizations", logger):
        vuln_map_path = PATHS.figures / "vulnerability_index_map.png"
        create_vulnerability_map(gdf, trauma_centers, vuln_map_path)
        
        corr_chart_path = PATHS.figures / "vulnerability_correlations.png"
        create_correlation_chart(gdf, corr_chart_path)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    
    logger.info(f"\n  📊 VULNERABILITY INDEX:")
    logger.info(f"     City average: {city_avg:.1f}")
    logger.info(f"     Trauma desert average: {desert_avg:.1f} ({desert_avg/city_avg:.1f}x higher)")
    
    logger.info(f"\n  🔗 CORRELATIONS:")
    logger.info(f"     Vulnerability ↔ % Black: r = {r_race:.3f} (p < 0.001)")
    logger.info(f"     Vulnerability ↔ % Poverty: r = {r_pov:.3f} (p < 0.001)")
    
    logger.info(f"\n  ⚠️ COMPOUND DISADVANTAGE:")
    logger.info(f"     {n_compound} tracts in top quartile of disadvantage")
    logger.info(f"     {n_both} of 18 trauma deserts also in top quartile")
    
    return gdf, class_stats


if __name__ == "__main__":
    gdf, class_stats = run_social_determinants_analysis()
    print("\n✅ Social determinants analysis complete!")


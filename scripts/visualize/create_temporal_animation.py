#!/usr/bin/env python3
"""
Temporal Animation: Shooting Hotspot Migration Over Time.

Creates animated visualizations showing how shooting patterns have changed
from 2015 to present. Includes:
- Animated GIF of year-by-year choropleth
- Small-multiple static map grid
- Analysis of emerging vs. declining hotspots
- COVID-era spike visualization (2020-2021)

This is powerful for storytelling and presentations.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.animation import FuncAnimation, PillowWriter
import warnings

warnings.filterwarnings('ignore')

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Color scheme for shooting density (sequential)
DENSITY_CMAP = LinearSegmentedColormap.from_list(
    'shooting_density',
    ['#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f']
)


def calculate_annual_density(
    shootings_df: pd.DataFrame,
    tracts_gdf: gpd.GeoDataFrame
) -> Dict[int, gpd.GeoDataFrame]:
    """
    Calculate shooting density by tract for each year.
    
    Returns:
        Dictionary mapping year -> GeoDataFrame with density
    """
    # Ensure we have year column
    if 'year' not in shootings_df.columns:
        if 'date_' in shootings_df.columns:
            shootings_df['year'] = pd.to_datetime(shootings_df['date_']).dt.year
        elif 'date' in shootings_df.columns:
            shootings_df['year'] = pd.to_datetime(shootings_df['date']).dt.year
    
    # Normalize GEOID column name
    geoid_col = None
    for col in ['GEOID', 'tract_geoid', 'geoid']:
        if col in shootings_df.columns:
            geoid_col = col
            break
    
    if geoid_col is None:
        raise ValueError("No GEOID column found in shootings data")
    
    # Normalize to GEOID
    if geoid_col != 'GEOID':
        shootings_df['GEOID'] = shootings_df[geoid_col].astype(float).astype('Int64').astype(str)
    
    # Get unique years
    years = sorted(shootings_df['year'].dropna().unique())
    years = [int(y) for y in years if 2015 <= y <= 2025]
    
    annual_data = {}
    
    for year in years:
        year_shootings = shootings_df[shootings_df['year'] == year]
        
        # Count by tract
        tract_counts = year_shootings.groupby('GEOID').size().reset_index(name='shootings')
        
        # Merge with tracts
        year_gdf = tracts_gdf.copy()
        year_gdf['GEOID'] = year_gdf['GEOID'].astype(str)
        tract_counts['GEOID'] = tract_counts['GEOID'].astype(str)
        year_gdf = year_gdf.merge(tract_counts, on='GEOID', how='left')
        year_gdf['shootings'] = year_gdf['shootings'].fillna(0)
        
        # Calculate density (shootings per sq mi)
        year_gdf['density'] = year_gdf['shootings'] / year_gdf['area_sq_mi']
        
        annual_data[int(year)] = year_gdf
    
    return annual_data


def identify_hotspot_trends(
    annual_data: Dict[int, gpd.GeoDataFrame]
) -> pd.DataFrame:
    """
    Identify tracts with increasing, decreasing, or stable trends.
    """
    years = sorted(annual_data.keys())
    if len(years) < 3:
        return pd.DataFrame()
    
    # Get first 3 years and last 3 years for comparison
    early_years = years[:3]
    recent_years = years[-3:]
    
    # Calculate average density for each period
    trends = []
    
    first_gdf = annual_data[years[0]]
    
    for geoid in first_gdf['GEOID'].unique():
        early_avg = np.mean([
            annual_data[y][annual_data[y]['GEOID'] == geoid]['density'].values[0]
            for y in early_years if geoid in annual_data[y]['GEOID'].values
        ])
        
        recent_avg = np.mean([
            annual_data[y][annual_data[y]['GEOID'] == geoid]['density'].values[0]
            for y in recent_years if geoid in annual_data[y]['GEOID'].values
        ])
        
        # Calculate change
        if early_avg > 0:
            pct_change = ((recent_avg - early_avg) / early_avg) * 100
        else:
            pct_change = 100 if recent_avg > 0 else 0
        
        # Classify trend
        if pct_change > 25:
            trend = 'Increasing'
        elif pct_change < -25:
            trend = 'Decreasing'
        else:
            trend = 'Stable'
        
        # Get tract info
        tract_row = first_gdf[first_gdf['GEOID'] == geoid].iloc[0]
        
        trends.append({
            'GEOID': geoid,
            'NAME': tract_row.get('NAME', ''),
            'early_avg_density': early_avg,
            'recent_avg_density': recent_avg,
            'pct_change': pct_change,
            'trend': trend,
            'total_population': tract_row.get('total_population', 0)
        })
    
    return pd.DataFrame(trends)


def create_animated_gif(
    annual_data: Dict[int, gpd.GeoDataFrame],
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create an animated GIF showing year-by-year changes.
    """
    years = sorted(annual_data.keys())
    
    # Get global min/max for consistent color scale
    all_densities = []
    for gdf in annual_data.values():
        all_densities.extend(gdf['density'].values)
    vmax = np.percentile(all_densities, 98)  # Use 98th percentile to avoid outliers
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    
    def animate(frame):
        ax.clear()
        year = years[frame]
        gdf = annual_data[year]
        
        # Plot choropleth
        gdf.plot(
            column='density',
            ax=ax,
            cmap=DENSITY_CMAP,
            vmin=0,
            vmax=vmax,
            edgecolor='#666666',
            linewidth=0.2,
            legend=False
        )
        
        # Add trauma centers
        for _, tc in trauma_centers.iterrows():
            if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
                ax.plot(tc['longitude'], tc['latitude'], 
                       'k^', markersize=8, markeredgecolor='white', markeredgewidth=1)
        
        # Year-specific stats
        total_shootings = gdf['shootings'].sum()
        max_density = gdf['density'].max()
        
        # Title with stats
        ax.set_title(
            f'Philadelphia Shooting Density: {year}\n'
            f'Total: {int(total_shootings):,} shootings | Peak: {max_density:.0f}/sq mi',
            fontsize=14, fontweight='bold'
        )
        ax.axis('off')
        
        # Add colorbar on first frame
        if frame == 0:
            sm = plt.cm.ScalarMappable(cmap=DENSITY_CMAP, norm=Normalize(0, vmax))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, shrink=0.6, label='Shootings per sq mi')
        
        return ax
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(years), interval=1000, repeat=True)
    
    # Save as GIF
    writer = PillowWriter(fps=1)
    anim.save(str(output_path), writer=writer, dpi=150)
    plt.close()
    
    logger.info(f"Saved animated GIF: {output_path}")


def create_small_multiples(
    annual_data: Dict[int, gpd.GeoDataFrame],
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create small-multiple grid showing all years.
    """
    years = sorted(annual_data.keys())
    n_years = len(years)
    
    # Calculate grid size
    ncols = 4
    nrows = (n_years + ncols - 1) // ncols
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 4 * nrows))
    axes = axes.flatten()
    
    # Get global color scale
    all_densities = []
    for gdf in annual_data.values():
        all_densities.extend(gdf['density'].values)
    vmax = np.percentile(all_densities, 98)
    
    for idx, year in enumerate(years):
        ax = axes[idx]
        gdf = annual_data[year]
        
        gdf.plot(
            column='density',
            ax=ax,
            cmap=DENSITY_CMAP,
            vmin=0,
            vmax=vmax,
            edgecolor='#888888',
            linewidth=0.1,
            legend=False
        )
        
        # Add trauma centers
        for _, tc in trauma_centers.iterrows():
            if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
                ax.plot(tc['longitude'], tc['latitude'], 
                       'k^', markersize=5, markeredgecolor='white', markeredgewidth=0.5)
        
        total = int(gdf['shootings'].sum())
        ax.set_title(f'{year}\n({total:,} shootings)', fontsize=10, fontweight='bold')
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(len(years), len(axes)):
        axes[idx].axis('off')
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=DENSITY_CMAP, norm=Normalize(0, vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, shrink=0.5, location='bottom', 
                        label='Shootings per sq mi', pad=0.02)
    
    plt.suptitle(
        'Philadelphia Shooting Density by Year (2015-2024)\n'
        'Showing the COVID-era spike (2020-2021) and subsequent decline',
        fontsize=14, fontweight='bold', y=1.02
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved small multiples: {output_path}")


def create_trend_map(
    tracts_gdf: gpd.GeoDataFrame,
    trends_df: pd.DataFrame,
    output_path: Path
):
    """
    Create map showing which tracts are increasing vs decreasing.
    """
    # Merge trends with geometry
    trend_gdf = tracts_gdf.merge(trends_df[['GEOID', 'trend', 'pct_change']], on='GEOID', how='left')
    trend_gdf['trend'] = trend_gdf['trend'].fillna('No Data')
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    
    # Define colors
    trend_colors = {
        'Increasing': '#d73027',  # Red
        'Stable': '#fee08b',       # Yellow
        'Decreasing': '#1a9850',   # Green
        'No Data': '#cccccc'       # Gray
    }
    
    colors = trend_gdf['trend'].map(trend_colors)
    trend_gdf.plot(ax=ax, color=colors, edgecolor='#666666', linewidth=0.2)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=trend_colors['Increasing'], label='Increasing (>25% rise)'),
        mpatches.Patch(facecolor=trend_colors['Stable'], label='Stable (±25%)'),
        mpatches.Patch(facecolor=trend_colors['Decreasing'], label='Decreasing (>25% drop)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', title='Trend (2015-17 vs 2022-24)')
    
    # Stats
    n_increasing = (trend_gdf['trend'] == 'Increasing').sum()
    n_decreasing = (trend_gdf['trend'] == 'Decreasing').sum()
    n_stable = (trend_gdf['trend'] == 'Stable').sum()
    
    ax.set_title(
        f'Shooting Trend by Census Tract (2015-2024)\n'
        f'Increasing: {n_increasing} tracts | Stable: {n_stable} | Decreasing: {n_decreasing}',
        fontsize=14, fontweight='bold'
    )
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved trend map: {output_path}")


def create_annual_summary_chart(
    annual_data: Dict[int, gpd.GeoDataFrame],
    output_path: Path
):
    """
    Create bar chart showing annual shooting totals with trend line.
    """
    years = sorted(annual_data.keys())
    totals = [annual_data[y]['shootings'].sum() for y in years]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color bars by relative intensity
    max_total = max(totals)
    colors = [DENSITY_CMAP(t / max_total) for t in totals]
    
    bars = ax.bar(years, totals, color=colors, edgecolor='#333333', linewidth=0.5)
    
    # Add value labels
    for bar, total in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
               f'{int(total):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Highlight COVID years
    for i, year in enumerate(years):
        if year in [2020, 2021]:
            bars[i].set_edgecolor('#d73027')
            bars[i].set_linewidth(3)
    
    # Add annotations
    peak_year = years[totals.index(max(totals))]
    ax.annotate(
        f'Peak: {peak_year}',
        xy=(peak_year, max(totals)),
        xytext=(peak_year - 1, max(totals) + 200),
        arrowprops=dict(arrowstyle='->', color='red'),
        fontsize=10, color='red', fontweight='bold'
    )
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Shootings', fontsize=12)
    ax.set_title(
        'Philadelphia Annual Shooting Count (2015-2024)\n'
        'COVID-era spike (2020-2021) highlighted',
        fontsize=14, fontweight='bold'
    )
    
    ax.set_xticks(years)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved annual summary chart: {output_path}")


def run_temporal_animation():
    """
    Main function to create all temporal visualizations.
    """
    logger.info("=" * 60)
    logger.info("TEMPORAL ANIMATION: SHOOTING HOTSPOT MIGRATION")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        # Load shootings with tract assignments
        shootings_file = PATHS.processed / "shootings_with_tracts.csv"
        shootings_df = load_csv(shootings_file)
        logger.info(f"  Loaded {len(shootings_df)} shootings")
        
        # Load tract boundaries
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        tracts_gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(tracts_gdf)} tracts")
        
        # Load trauma centers
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
    
    # Calculate annual density
    with StepLogger("Calculating annual density by tract", logger):
        annual_data = calculate_annual_density(shootings_df, tracts_gdf)
        
        for year, gdf in sorted(annual_data.items()):
            total = int(gdf['shootings'].sum())
            logger.info(f"  {year}: {total:,} shootings")
    
    # Identify trends
    with StepLogger("Analyzing hotspot trends", logger):
        trends_df = identify_hotspot_trends(annual_data)
        
        if not trends_df.empty:
            n_increasing = (trends_df['trend'] == 'Increasing').sum()
            n_decreasing = (trends_df['trend'] == 'Decreasing').sum()
            n_stable = (trends_df['trend'] == 'Stable').sum()
            
            logger.info(f"  Increasing tracts: {n_increasing}")
            logger.info(f"  Stable tracts: {n_stable}")
            logger.info(f"  Decreasing tracts: {n_decreasing}")
    
    # Create visualizations
    with StepLogger("Creating animated GIF", logger):
        gif_path = PATHS.figures / "shooting_animation.gif"
        create_animated_gif(annual_data, trauma_centers, gif_path)
    
    with StepLogger("Creating small-multiple grid", logger):
        multiples_path = PATHS.figures / "shooting_small_multiples.png"
        create_small_multiples(annual_data, trauma_centers, multiples_path)
    
    with StepLogger("Creating trend map", logger):
        trend_path = PATHS.figures / "shooting_trend_map.png"
        create_trend_map(tracts_gdf, trends_df, trend_path)
    
    with StepLogger("Creating annual summary chart", logger):
        summary_path = PATHS.figures / "shooting_annual_summary.png"
        create_annual_summary_chart(annual_data, summary_path)
    
    # Save trend analysis
    with StepLogger("Saving trend analysis", logger):
        if not trends_df.empty:
            trends_path = PATHS.tables / "tract_shooting_trends.csv"
            trends_df.to_csv(trends_path, index=False)
            logger.info(f"  Saved: {trends_path}")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEMPORAL ANALYSIS SUMMARY")
    logger.info("=" * 60)
    
    years = sorted(annual_data.keys())
    totals = {y: int(annual_data[y]['shootings'].sum()) for y in years}
    
    peak_year = max(totals, key=totals.get)
    min_year = min(totals, key=totals.get)
    
    logger.info(f"  Peak year: {peak_year} ({totals[peak_year]:,} shootings)")
    logger.info(f"  Lowest year: {min_year} ({totals[min_year]:,} shootings)")
    
    if len(years) >= 2:
        first_year, last_year = years[0], years[-1]
        change = ((totals[last_year] - totals[first_year]) / totals[first_year]) * 100
        logger.info(f"  {first_year}→{last_year} change: {change:+.1f}%")
    
    return annual_data, trends_df


if __name__ == "__main__":
    annual_data, trends = run_temporal_animation()
    print("\n✅ Temporal animation complete!")
    print(f"\nCreated: animated GIF, small multiples, trend map, annual summary")


#!/usr/bin/env python3
"""
Stop the Bleed Training Prioritization Framework.

If transport time to trauma centers cannot be reduced, the next best intervention
is reducing bleed-out time through bystander hemorrhage control.

This script creates a data-driven framework for prioritizing Stop the Bleed
training deployment based on:
1. Shooting density (where violence occurs)
2. Transport time (where delays are longest)
3. Population density (where training reaches most people)

The output is a ranked list of priority zones and recommended training sites.
"""

import sys
from pathlib import Path
from typing import List, Tuple

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Color scheme for priority map
PRIORITY_CMAP = LinearSegmentedColormap.from_list(
    'priority',
    ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
)


def calculate_priority_score(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate Stop the Bleed priority score for each tract.
    
    Score = (Shooting Density Percentile) × (Transport Time Percentile) × (Population Factor)
    
    Higher score = higher priority for training deployment.
    """
    result = gdf.copy()
    
    # Calculate percentile ranks (0-100)
    result['density_percentile'] = result['annual_shootings_per_sq_mi'].rank(pct=True) * 100
    result['time_percentile'] = result['time_to_nearest'].rank(pct=True) * 100
    result['population_percentile'] = result['total_population'].rank(pct=True) * 100
    
    # Combined score (multiplicative to emphasize tracts high on BOTH dimensions)
    # Weight: 40% density, 40% time, 20% population
    result['stb_priority_score'] = (
        (result['density_percentile'] * 0.4) +
        (result['time_percentile'] * 0.4) +
        (result['population_percentile'] * 0.2)
    )
    
    # Also calculate a "urgency" score (density × time) for comparison
    result['urgency_score'] = (
        result['density_percentile'] * result['time_percentile'] / 100
    )
    
    # Rank tracts
    result['stb_priority_rank'] = result['stb_priority_score'].rank(ascending=False, method='min')
    result['urgency_rank'] = result['urgency_score'].rank(ascending=False, method='min')
    
    return result


def identify_priority_zones(gdf: gpd.GeoDataFrame, n_zones: int = 20) -> pd.DataFrame:
    """
    Identify top N priority zones for Stop the Bleed training.
    """
    # Sort by priority score
    priority_zones = gdf.nlargest(n_zones, 'stb_priority_score').copy()
    
    # Calculate potential impact metrics
    priority_zones['annual_shootings'] = priority_zones['total_shootings'] / 11  # Data spans 2015-2025 (11 years)
    
    # Estimate lives potentially saved (rough estimate based on literature)
    # Assumption: ~15% of GSW fatalities could be prevented with immediate hemorrhage control
    # Fatality rate ~20%, so potential lives saved = shootings × 0.20 × 0.15
    priority_zones['potential_lives_saved_annually'] = (
        priority_zones['annual_shootings'] * 0.20 * 0.15
    ).round(1)
    
    # Select columns for output
    output_cols = [
        'GEOID', 'NAME', 'stb_priority_rank', 'stb_priority_score',
        'total_shootings', 'annual_shootings', 'time_to_nearest',
        'total_population', 'potential_lives_saved_annually',
        'pct_black', 'pct_poverty'
    ]
    
    return priority_zones[[c for c in output_cols if c in priority_zones.columns]]


def suggest_training_sites(gdf: gpd.GeoDataFrame, n_zones: int = 20) -> pd.DataFrame:
    """
    Suggest specific training sites within priority zones.
    """
    priority_zones = gdf.nlargest(n_zones, 'stb_priority_score')
    
    # Generic site recommendations based on tract characteristics
    sites = []
    
    for _, zone in priority_zones.iterrows():
        geoid = zone['GEOID']
        pop = zone['total_population']
        
        # Recommend site types based on population and demographics
        recommended_sites = []
        
        # Always recommend schools (high reach, regular access)
        recommended_sites.append("Public schools (reach students + staff)")
        
        # High population areas: transit hubs, rec centers
        if pop > 4000:
            recommended_sites.append("Transit stations/bus terminals")
            recommended_sites.append("Recreation centers")
        
        # High poverty areas: community organizations
        if zone.get('pct_poverty', 0) > 25:
            recommended_sites.append("Community health centers")
            recommended_sites.append("Food banks/pantries")
        
        # All areas: religious institutions
        recommended_sites.append("Churches/mosques/temples")
        
        sites.append({
            'GEOID': geoid,
            'Tract_Name': zone.get('NAME', 'Unknown'),
            'Priority_Rank': int(zone['stb_priority_rank']),
            'Priority_Score': round(zone['stb_priority_score'], 1),
            'Population': int(pop),
            'Annual_Shootings': round(zone['total_shootings'] / 11, 1),  # 11 years of data
            'Transport_Time_Min': round(zone['time_to_nearest'], 1),
            'Recommended_Sites': '; '.join(recommended_sites[:4])  # Top 4
        })
    
    return pd.DataFrame(sites)


def create_priority_map(
    gdf: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path,
    n_highlight: int = 20
):
    """
    Create a map showing Stop the Bleed priority zones.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Plot all tracts by priority score
    gdf.plot(
        column='stb_priority_score',
        ax=ax,
        cmap=PRIORITY_CMAP,
        edgecolor='#666666',
        linewidth=0.2,
        legend=True,
        legend_kwds={
            'label': 'Stop the Bleed Priority Score',
            'shrink': 0.6,
            'orientation': 'horizontal',
            'pad': 0.05
        }
    )
    
    # Highlight top 20 priority zones
    top_zones = gdf.nlargest(n_highlight, 'stb_priority_score')
    top_zones.plot(
        ax=ax,
        facecolor='none',
        edgecolor='#000000',
        linewidth=2.5,
        linestyle='-'
    )
    
    # Add trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax.plot(tc['longitude'], tc['latitude'],
                   'r^', markersize=12, markeredgecolor='white', markeredgewidth=1.5,
                   zorder=10)
    
    # Add rank labels for top 10
    top_10 = gdf.nlargest(10, 'stb_priority_score')
    for _, zone in top_10.iterrows():
        centroid = zone.geometry.centroid
        ax.annotate(
            f"#{int(zone['stb_priority_rank'])}",
            xy=(centroid.x, centroid.y),
            fontsize=8,
            fontweight='bold',
            ha='center',
            va='center',
            color='white',
            bbox=dict(boxstyle='circle', facecolor='black', alpha=0.7, pad=0.3)
        )
    
    ax.set_title(
        'Stop the Bleed Training Priority Zones\n'
        'Top 20 zones outlined in black | Red triangles = Level I trauma centers',
        fontsize=12, fontweight='bold'
    )
    ax.axis('off')
    
    # Add summary stats
    total_pop_top20 = top_zones['total_population'].sum()
    total_shootings_top20 = top_zones['total_shootings'].sum()
    
    stats_text = (
        f"Top 20 Priority Zones:\n"
        f"• Population: {total_pop_top20:,}\n"
        f"• Total shootings: {total_shootings_top20:,}\n"
        f"• Avg transport time: {top_zones['time_to_nearest'].mean():.1f} min"
    )
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved priority map: {output_path}")


def create_impact_analysis_chart(priority_zones: pd.DataFrame, output_path: Path):
    """
    Create charts showing potential impact of training deployment.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Priority score components
    ax1 = axes[0]
    
    zones = priority_zones.head(15)
    x = range(len(zones))
    
    # Stacked bar showing score components
    ax1.barh(x, zones['stb_priority_score'], color='#bd0026', alpha=0.8, label='Priority Score')
    
    ax1.set_yticks(x)
    ax1.set_yticklabels([f"#{int(r)}: Tract {g}" 
                        for r, g in zip(zones['stb_priority_rank'], zones['GEOID'].str[-6:])])
    ax1.set_xlabel('Priority Score')
    ax1.set_title('Top 15 Priority Zones\nfor Stop the Bleed Training', fontweight='bold')
    ax1.invert_yaxis()
    
    # Chart 2: Potential impact
    ax2 = axes[1]
    
    # Calculate cumulative impact
    zones_sorted = priority_zones.sort_values('stb_priority_rank')
    zones_sorted['cumulative_pop'] = zones_sorted['total_population'].cumsum()
    zones_sorted['cumulative_shootings'] = zones_sorted['total_shootings'].cumsum()
    
    n_zones = range(1, len(zones_sorted) + 1)
    
    ax2.plot(n_zones, zones_sorted['cumulative_pop'] / 1000, 
            'b-', linewidth=2, label='Population (thousands)')
    ax2.plot(n_zones, zones_sorted['cumulative_shootings'] / 100,
            'r--', linewidth=2, label='Shootings (hundreds)')
    
    ax2.set_xlabel('Number of Priority Zones Trained')
    ax2.set_ylabel('Cumulative Reach')
    ax2.set_title('Cumulative Impact by Priority Zone\n(Deploying from highest to lowest priority)', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add annotations
    pop_10 = zones_sorted.head(10)['total_population'].sum()
    shootings_10 = zones_sorted.head(10)['total_shootings'].sum()
    ax2.annotate(
        f"Top 10 zones:\n{pop_10:,} people\n{shootings_10:,} shootings",
        xy=(10, pop_10/1000),
        xytext=(12, pop_10/1000 + 20),
        fontsize=9,
        arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7)
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved impact chart: {output_path}")


def run_stop_the_bleed_analysis():
    """
    Main function to run Stop the Bleed prioritization analysis.
    """
    logger.info("=" * 60)
    logger.info("STOP THE BLEED TRAINING PRIORITIZATION")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts_file = PATHS.processed / "tracts_with_vulnerability.geojson"
        if not tracts_file.exists():
            tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
        
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
    
    # Calculate priority scores
    with StepLogger("Calculating priority scores", logger):
        gdf = calculate_priority_score(gdf)
        
        logger.info(f"  Max priority score: {gdf['stb_priority_score'].max():.1f}")
        logger.info(f"  Mean priority score: {gdf['stb_priority_score'].mean():.1f}")
    
    # Identify priority zones
    with StepLogger("Identifying top 20 priority zones", logger):
        priority_zones = identify_priority_zones(gdf, n_zones=20)
        
        total_pop = priority_zones['total_population'].sum()
        total_shootings = priority_zones['total_shootings'].sum()
        avg_time = gdf[gdf['stb_priority_rank'] <= 20]['time_to_nearest'].mean()
        
        logger.info(f"  Total population in top 20: {total_pop:,}")
        logger.info(f"  Total shootings in top 20: {total_shootings:,}")
        logger.info(f"  Avg transport time in top 20: {avg_time:.1f} min")
    
    # Suggest training sites
    with StepLogger("Generating training site recommendations", logger):
        training_sites = suggest_training_sites(gdf, n_zones=20)
    
    # Calculate potential impact
    with StepLogger("Estimating potential impact", logger):
        # Rough estimate based on literature
        annual_shootings_top20 = total_shootings / 11  # Data spans 2015-2025 (11 years)
        potential_lives = annual_shootings_top20 * 0.20 * 0.15  # 20% fatal, 15% preventable
        
        logger.info(f"  Annual shootings in top 20 zones: ~{annual_shootings_top20:.0f}")
        logger.info(f"  Potential lives saved annually: ~{potential_lives:.0f}")
        logger.info(f"  (Assumes 15% of GSW fatalities preventable with bystander care)")
    
    # Save outputs
    with StepLogger("Saving outputs", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        
        # Priority zones
        priority_path = PATHS.tables / "stop_the_bleed_priority_zones.csv"
        priority_zones.to_csv(priority_path, index=False)
        logger.info(f"  Saved: {priority_path}")
        
        # Training site recommendations
        sites_path = PATHS.tables / "stop_the_bleed_training_sites.csv"
        training_sites.to_csv(sites_path, index=False)
        logger.info(f"  Saved: {sites_path}")
        
        # Full tract-level scores
        score_cols = ['GEOID', 'NAME', 'stb_priority_score', 'stb_priority_rank',
                     'urgency_score', 'urgency_rank', 'density_percentile',
                     'time_percentile', 'population_percentile']
        scores_df = gdf[[c for c in score_cols if c in gdf.columns]]
        scores_path = PATHS.tables / "tract_stb_priority_scores.csv"
        scores_df.to_csv(scores_path, index=False)
    
    # Create visualizations
    with StepLogger("Creating visualizations", logger):
        map_path = PATHS.figures / "stop_the_bleed_priority_map.png"
        create_priority_map(gdf, trauma_centers, map_path)
        
        impact_path = PATHS.figures / "stop_the_bleed_impact_analysis.png"
        create_impact_analysis_chart(priority_zones, impact_path)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TOP 10 PRIORITY ZONES")
    logger.info("=" * 60)
    
    for _, zone in priority_zones.head(10).iterrows():
        logger.info(f"\n  #{int(zone['stb_priority_rank'])}: Tract {zone['GEOID'][-6:]}")
        logger.info(f"      Population: {zone['total_population']:,.0f}")
        logger.info(f"      Total shootings: {zone['total_shootings']:.0f}")
        logger.info(f"      Transport time: {zone['time_to_nearest']:.1f} min")
    
    logger.info("\n" + "=" * 60)
    logger.info("IMPLEMENTATION RECOMMENDATIONS")
    logger.info("=" * 60)
    logger.info("""
  1. DEPLOY IN TOP 20 ZONES FIRST
     - Reaches {pop:,} residents
     - Covers {shoot:,} historical shootings
     
  2. PRIORITY TRAINING SITES:
     • Public schools (highest reach, regular access)
     • Transit hubs (SEPTA stations in high-traffic areas)
     • Recreation centers (community gathering points)
     • Churches/religious institutions (trusted community spaces)
     • Community health centers (existing health infrastructure)
     
  3. TARGET TRAINING GROUPS:
     • Teachers and school staff
     • Transit workers
     • Corner store employees
     • Community health workers
     • Family members of violence victims
     
  4. POTENTIAL IMPACT:
     • ~{lives:.0f} lives potentially saved annually
     • Empowers community members as first responders
     • Reduces bleed-out time before EMS arrival
""".format(
        pop=total_pop,
        shoot=total_shootings,
        lives=potential_lives
    ))
    
    return gdf, priority_zones


if __name__ == "__main__":
    gdf, priority_zones = run_stop_the_bleed_analysis()
    print("\n✅ Stop the Bleed prioritization complete!")


#!/usr/bin/env python3
"""
Time-of-Day Sensitivity Analysis for Trauma Desert Classification.

This script analyzes how trauma desert classifications change under different
traffic conditions (rush hour vs. off-peak). Since OpenRouteService free tier
doesn't include real-time traffic, we apply research-based traffic multipliers:

- Off-peak (baseline): 1.0x travel time (current isochrones)
- Morning rush (7-9am): 1.4x travel time
- Evening rush (4-7pm): 1.5x travel time  
- Weekend/overnight: 0.9x travel time (slightly faster)

Traffic multipliers based on:
- INRIX 2023 Urban Traffic Scorecard
- Philadelphia regional congestion studies
- FHWA travel time reliability research

Output:
- Adjusted transport times for each scenario
- Tracts that flip classification under traffic
- Small-multiple comparison maps
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Traffic multipliers based on research
TRAFFIC_SCENARIOS = {
    'off_peak': {
        'name': 'Off-Peak (Baseline)',
        'multiplier': 1.0,
        'description': 'Overnight, mid-day, weekends - free-flow conditions',
        'typical_hours': '10pm-6am, 10am-3pm, weekends'
    },
    'morning_rush': {
        'name': 'Morning Rush Hour',
        'multiplier': 1.4,
        'description': 'Commute-in traffic, moderate congestion',
        'typical_hours': '7am-9am weekdays'
    },
    'evening_rush': {
        'name': 'Evening Rush Hour',
        'multiplier': 1.5,
        'description': 'Peak congestion, commute-out + errands',
        'typical_hours': '4pm-7pm weekdays'
    },
    'overnight': {
        'name': 'Overnight',
        'multiplier': 0.9,
        'description': 'Minimal traffic, slightly faster than baseline',
        'typical_hours': '12am-5am'
    }
}

# Bivariate color scheme (from params.yml)
BIVARIATE_COLORS = {
    1: "#e8e8e8", 2: "#b5c0da", 3: "#6c83b5",
    4: "#b8d6be", 5: "#90b2b3", 6: "#567994",
    7: "#73ae80", 8: "#5a9178", 9: "#2a5a5b"
}


def calculate_terciles(series: pd.Series) -> tuple:
    """Calculate tercile thresholds for a series."""
    return series.quantile([0.333, 0.667]).values


def assign_tercile(value: float, thresholds: tuple) -> int:
    """Assign a value to a tercile (1=low, 2=med, 3=high)."""
    if value <= thresholds[0]:
        return 1
    elif value <= thresholds[1]:
        return 2
    else:
        return 3


def calculate_bivariate_class(density_tercile: int, time_tercile: int) -> int:
    """Calculate bivariate class (1-9) from terciles."""
    return (density_tercile - 1) * 3 + time_tercile


def tercile_label_to_int(label: str) -> int:
    """Convert tercile label to integer (1=Low, 2=Medium, 3=High)."""
    mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    if isinstance(label, (int, float)):
        return int(label)
    return mapping.get(str(label), 2)  # Default to medium if unknown


def apply_traffic_scenario(gdf: gpd.GeoDataFrame, scenario_key: str) -> gpd.GeoDataFrame:
    """
    Apply a traffic scenario multiplier and recalculate classifications.
    
    Args:
        gdf: GeoDataFrame with base transport times
        scenario_key: Key from TRAFFIC_SCENARIOS
        
    Returns:
        GeoDataFrame with adjusted times and new classifications
    """
    scenario = TRAFFIC_SCENARIOS[scenario_key]
    multiplier = scenario['multiplier']
    
    result = gdf.copy()
    
    # Apply multiplier to transport time
    result[f'time_adj_{scenario_key}'] = result['time_to_nearest_min'] * multiplier
    
    # Recalculate time terciles with adjusted times
    time_thresholds = calculate_terciles(result[f'time_adj_{scenario_key}'])
    result[f'time_tercile_{scenario_key}'] = result[f'time_adj_{scenario_key}'].apply(
        lambda x: assign_tercile(x, time_thresholds)
    )
    
    # Convert density tercile labels to integers
    result['density_tercile_int'] = result['density_tercile'].apply(tercile_label_to_int)
    
    # Calculate bivariate class for this scenario
    result[f'bivariate_class_{scenario_key}'] = result.apply(
        lambda row: calculate_bivariate_class(
            row['density_tercile_int'], 
            row[f'time_tercile_{scenario_key}']
        ),
        axis=1
    )
    
    # Mark if this is a trauma desert under this scenario
    result[f'is_desert_{scenario_key}'] = result[f'bivariate_class_{scenario_key}'] == 9
    
    return result


def analyze_classification_changes(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Analyze how tract classifications change across scenarios.
    
    Returns:
        DataFrame with tracts that change classification
    """
    changes = []
    
    for _, row in gdf.iterrows():
        base_class = int(row['bivariate_class'])
        
        for scenario_key in TRAFFIC_SCENARIOS.keys():
            scenario_class = int(row[f'bivariate_class_{scenario_key}'])
            
            if scenario_class != base_class:
                changes.append({
                    'GEOID': row['GEOID'],
                    'scenario': scenario_key,
                    'base_class': base_class,
                    'scenario_class': scenario_class,
                    'base_time': row['time_to_nearest_min'],
                    'scenario_time': row[f'time_adj_{scenario_key}'],
                    'became_desert': scenario_class == 9 and base_class != 9,
                    'left_desert': scenario_class != 9 and base_class == 9,
                    'shootings': row.get('total_shootings', 0),
                    'population': row.get('total_population', 0)
                })
    
    return pd.DataFrame(changes)


def create_comparison_visualization(gdf: gpd.GeoDataFrame, output_path: Path):
    """
    Create small-multiple maps comparing classifications across scenarios.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    scenarios = ['off_peak', 'morning_rush', 'evening_rush', 'overnight']
    
    for ax, scenario_key in zip(axes, scenarios):
        scenario = TRAFFIC_SCENARIOS[scenario_key]
        
        # Color by bivariate class
        class_col = f'bivariate_class_{scenario_key}'
        colors = gdf[class_col].map(BIVARIATE_COLORS)
        
        # Plot tracts
        gdf.plot(ax=ax, color=colors, edgecolor='#333333', linewidth=0.2)
        
        # Highlight trauma deserts with red border
        deserts = gdf[gdf[f'is_desert_{scenario_key}']]
        if len(deserts) > 0:
            deserts.plot(ax=ax, facecolor='none', edgecolor='#e41a1c', 
                        linewidth=2, linestyle='--')
        
        # Count deserts
        n_deserts = gdf[f'is_desert_{scenario_key}'].sum()
        pop_affected = gdf[gdf[f'is_desert_{scenario_key}']]['total_population'].sum()
        
        ax.set_title(
            f"{scenario['name']}\n"
            f"(×{scenario['multiplier']} travel time)\n"
            f"{n_deserts} trauma deserts | {pop_affected:,.0f} residents",
            fontsize=11, fontweight='bold'
        )
        ax.axis('off')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=BIVARIATE_COLORS[9], edgecolor='#e41a1c', 
                      linewidth=2, linestyle='--', label='Trauma Desert (Class 9)'),
        mpatches.Patch(facecolor=BIVARIATE_COLORS[7], label='High Violence, Good Access'),
        mpatches.Patch(facecolor=BIVARIATE_COLORS[3], label='Low Violence, Poor Access'),
        mpatches.Patch(facecolor=BIVARIATE_COLORS[1], label='Low Violence, Good Access'),
    ]
    
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, 
              fontsize=10, frameon=False, bbox_to_anchor=(0.5, 0.02))
    
    plt.suptitle(
        'Trauma Desert Classification by Time of Day\n'
        'How Traffic Conditions Affect Access to Level I Trauma Centers',
        fontsize=14, fontweight='bold', y=0.98
    )
    
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved comparison visualization to {output_path}")


def create_flip_analysis_chart(changes_df: pd.DataFrame, output_path: Path):
    """
    Create a chart showing tracts that flip classification.
    """
    if changes_df.empty:
        logger.info("No classification changes to visualize")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Count of changes by scenario
    ax1 = axes[0]
    scenario_counts = changes_df.groupby('scenario').size()
    scenario_labels = [TRAFFIC_SCENARIOS[s]['name'] for s in scenario_counts.index]
    colors = ['#2166ac', '#b2182b', '#d6604d', '#4393c3']
    
    bars = ax1.barh(scenario_labels, scenario_counts.values, color=colors[:len(scenario_counts)])
    ax1.set_xlabel('Number of Tracts That Change Classification', fontsize=11)
    ax1.set_title('Classification Changes by Traffic Scenario', fontsize=12, fontweight='bold')
    
    for bar, count in zip(bars, scenario_counts.values):
        ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                str(count), va='center', fontsize=10)
    
    # Right: Desert status changes
    ax2 = axes[1]
    became_desert = changes_df[changes_df['became_desert']].groupby('scenario').size()
    left_desert = changes_df[changes_df['left_desert']].groupby('scenario').size()
    
    x = np.arange(len(TRAFFIC_SCENARIOS))
    width = 0.35
    
    scenario_keys = list(TRAFFIC_SCENARIOS.keys())
    became_vals = [became_desert.get(s, 0) for s in scenario_keys]
    left_vals = [left_desert.get(s, 0) for s in scenario_keys]
    
    ax2.bar(x - width/2, became_vals, width, label='Became Trauma Desert', color='#b2182b')
    ax2.bar(x + width/2, left_vals, width, label='Left Trauma Desert', color='#2166ac')
    
    ax2.set_ylabel('Number of Tracts', fontsize=11)
    ax2.set_title('Trauma Desert Status Changes', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([TRAFFIC_SCENARIOS[s]['name'] for s in scenario_keys], 
                        rotation=15, ha='right', fontsize=9)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved flip analysis chart to {output_path}")


def run_sensitivity_analysis():
    """
    Main function to run the time-of-day sensitivity analysis.
    """
    logger.info("=" * 60)
    logger.info("TIME-OF-DAY SENSITIVITY ANALYSIS")
    logger.info("=" * 60)
    
    # Load the bivariate classified tracts
    with StepLogger("Loading classified tract data", logger):
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        if not tracts_file.exists():
            raise FileNotFoundError(
                f"Classified tracts not found at {tracts_file}. "
                "Run the bivariate classification first."
            )
        
        gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
        
        # Verify required columns exist
        required_cols = ['GEOID', 'time_to_nearest', 'density_tercile', 
                        'bivariate_class', 'total_population', 'total_shootings']
        missing = [c for c in required_cols if c not in gdf.columns]
        if missing:
            logger.warning(f"  Missing columns: {missing}")
        
        # Normalize column names for consistency
        if 'time_to_nearest' in gdf.columns:
            gdf['time_to_nearest_min'] = gdf['time_to_nearest']
        if 'shootings_total' in gdf.columns:
            gdf['total_shootings'] = gdf['shootings_total']
        if 'population' in gdf.columns:
            gdf['total_population'] = gdf['population']
    
    # Apply each traffic scenario
    with StepLogger("Applying traffic scenarios", logger):
        for scenario_key, scenario in TRAFFIC_SCENARIOS.items():
            logger.info(f"  {scenario['name']} (×{scenario['multiplier']})")
            gdf = apply_traffic_scenario(gdf, scenario_key)
            
            n_deserts = gdf[f'is_desert_{scenario_key}'].sum()
            logger.info(f"    → {n_deserts} trauma deserts")
    
    # Analyze classification changes
    with StepLogger("Analyzing classification changes", logger):
        changes_df = analyze_classification_changes(gdf)
        
        if not changes_df.empty:
            logger.info(f"  Total classification changes: {len(changes_df)}")
            logger.info(f"  Unique tracts affected: {changes_df['GEOID'].nunique()}")
            logger.info(f"  Tracts that become deserts: {changes_df['became_desert'].sum()}")
            logger.info(f"  Tracts that leave desert status: {changes_df['left_desert'].sum()}")
        else:
            logger.info("  No tracts change classification across scenarios")
    
    # Create summary statistics
    with StepLogger("Generating summary statistics", logger):
        summary_rows = []
        
        for scenario_key, scenario in TRAFFIC_SCENARIOS.items():
            desert_mask = gdf[f'is_desert_{scenario_key}']
            
            summary_rows.append({
                'scenario': scenario['name'],
                'multiplier': scenario['multiplier'],
                'trauma_desert_count': desert_mask.sum(),
                'population_affected': gdf[desert_mask]['total_population'].sum(),
                'shootings_in_deserts': gdf[desert_mask]['total_shootings'].sum(),
                'avg_transport_time': gdf[f'time_adj_{scenario_key}'].mean(),
                'max_transport_time': gdf[f'time_adj_{scenario_key}'].max(),
                'description': scenario['description']
            })
        
        summary_df = pd.DataFrame(summary_rows)
        logger.info("\n" + summary_df.to_string(index=False))
    
    # Save outputs
    with StepLogger("Saving outputs", logger):
        # Ensure output directories exist
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        PATHS.figures.mkdir(parents=True, exist_ok=True)
        
        # Save summary table
        summary_path = PATHS.tables / "time_of_day_sensitivity_summary.csv"
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"  Saved summary: {summary_path}")
        
        # Save classification changes
        if not changes_df.empty:
            changes_path = PATHS.tables / "tracts_that_flip_by_time.csv"
            changes_df.to_csv(changes_path, index=False)
            logger.info(f"  Saved changes: {changes_path}")
        
        # Save full classified GeoJSON
        output_geojson = PATHS.processed / "tracts_time_of_day_classified.geojson"
        gdf.to_file(output_geojson, driver="GeoJSON")
        logger.info(f"  Saved classified tracts: {output_geojson}")
    
    # Create visualizations
    with StepLogger("Creating visualizations", logger):
        comparison_path = PATHS.figures / "time_of_day_sensitivity.png"
        create_comparison_visualization(gdf, comparison_path)
        
        if not changes_df.empty:
            flip_chart_path = PATHS.figures / "classification_flip_analysis.png"
            create_flip_analysis_chart(changes_df, flip_chart_path)
    
    # Print key findings
    logger.info("\n" + "=" * 60)
    logger.info("KEY FINDINGS")
    logger.info("=" * 60)
    
    base_deserts = gdf['bivariate_class'].eq(9).sum()
    rush_deserts = gdf['is_desert_evening_rush'].sum()
    overnight_deserts = gdf['is_desert_overnight'].sum()
    
    logger.info(f"  Baseline trauma deserts: {base_deserts}")
    logger.info(f"  Evening rush hour deserts: {rush_deserts} "
               f"({rush_deserts - base_deserts:+d} change)")
    logger.info(f"  Overnight deserts: {overnight_deserts} "
               f"({overnight_deserts - base_deserts:+d} change)")
    
    if not changes_df.empty:
        worst_scenario = changes_df.groupby('scenario')['became_desert'].sum().idxmax()
        logger.info(f"  Worst scenario for access: {TRAFFIC_SCENARIOS[worst_scenario]['name']}")
    
    return gdf, summary_df, changes_df


if __name__ == "__main__":
    gdf, summary, changes = run_sensitivity_analysis()
    print("\n✅ Time-of-day sensitivity analysis complete!")
    print(f"\nSummary:\n{summary.to_string(index=False)}")


#!/usr/bin/env python3
"""
Create static figures for publication/presentation.

Generates high-quality PNG and PDF figures including:
- Bivariate choropleth map
- Summary statistics charts
- Temporal trends
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import geopandas as gpd
import pandas as pd
import numpy as np

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Set matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 150

# Bivariate color scheme
BIVARIATE_COLORS = {
    1: "#e8e8e8", 2: "#b5c0da", 3: "#6c83b5",
    4: "#b8d6be", 5: "#90b2b3", 6: "#567994",
    7: "#73ae80", 8: "#5a9178", 9: "#2a5a5b",
}


def create_bivariate_static_map() -> Path:
    """Create static bivariate choropleth map."""
    with StepLogger("Creating static bivariate map", logger):
        # Load data
        gdf = load_geojson(PATHS.processed / "tracts_bivariate_classified.geojson")
        tc_df = load_csv(PATHS.processed / "trauma_centers_geocoded.csv")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot tracts by bivariate class
        for cls in range(1, 10):
            subset = gdf[gdf['bivariate_class'] == cls]
            if len(subset) > 0:
                subset.plot(
                    ax=ax,
                    color=BIVARIATE_COLORS[cls],
                    edgecolor='white' if cls != 9 else '#e41a1c',
                    linewidth=0.3 if cls != 9 else 1.5,
                    alpha=0.85
                )
        
        # Add trauma centers
        for _, tc in tc_df.iterrows():
            if pd.notna(tc['latitude']) and 'Level I' in str(tc['trauma_level']):
                ax.scatter(
                    tc['longitude'], tc['latitude'],
                    s=200, c='#e41a1c', edgecolors='white',
                    linewidths=2, zorder=5, marker='o'
                )
                ax.annotate(
                    tc['hospital_name'].split()[0],  # First word
                    (tc['longitude'], tc['latitude']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, fontweight='bold', color='#e41a1c'
                )
        
        # Style
        ax.set_xlim(-75.30, -74.93)
        ax.set_ylim(39.86, 40.14)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Title
        ax.set_title(
            'Philadelphia Trauma Deserts\nGun Violence Burden vs. Level I Trauma Access',
            fontsize=16, fontweight='bold', pad=20
        )
        
        # Create bivariate legend
        legend_ax = fig.add_axes([0.12, 0.15, 0.15, 0.15])
        legend_data = np.array([
            [3, 6, 9],
            [2, 5, 8],
            [1, 4, 7]
        ])
        legend_colors = np.array([[BIVARIATE_COLORS[c] for c in row] for row in legend_data])
        
        for i in range(3):
            for j in range(3):
                legend_ax.add_patch(plt.Rectangle(
                    (j, i), 1, 1, 
                    facecolor=legend_colors[i, j],
                    edgecolor='white', linewidth=0.5
                ))
        
        # Highlight trauma desert cell
        legend_ax.add_patch(plt.Rectangle(
            (2, 0), 1, 1,
            facecolor='none', edgecolor='#e41a1c', linewidth=3
        ))
        
        legend_ax.set_xlim(0, 3)
        legend_ax.set_ylim(0, 3)
        legend_ax.set_xticks([])
        legend_ax.set_yticks([])
        legend_ax.set_xlabel('Violence Burden →', fontsize=9)
        legend_ax.set_ylabel('← Good Access', fontsize=9)
        legend_ax.xaxis.set_label_position('top')
        
        # Add note
        fig.text(
            0.5, 0.02,
            'Trauma Deserts (red outline): High violence + Poor trauma access | 🏥 Level I Adult Trauma Centers',
            ha='center', fontsize=10, style='italic'
        )
        
        plt.tight_layout()
        
        # Save
        output_file = PATHS.figures / "bivariate_map.png"
        PATHS.figures.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        fig.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"  Saved: {output_file}")
        return output_file


def create_summary_charts() -> Path:
    """Create summary statistics charts."""
    with StepLogger("Creating summary charts", logger):
        # Load data
        gdf = load_geojson(PATHS.processed / "tracts_bivariate_classified.geojson")
        annual = load_csv(PATHS.tables / "temporal_trends_annual.csv")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Bivariate class distribution (pie chart)
        ax1 = axes[0, 0]
        class_counts = gdf['priority_category'].value_counts()
        colors = ['#2a5a5b', '#73ae80', '#6c83b5', '#90b2b3', '#e8e8e8']
        wedges, texts, autotexts = ax1.pie(
            class_counts.values,
            labels=class_counts.index,
            autopct='%1.1f%%',
            colors=colors[:len(class_counts)],
            explode=[0.1 if 'Desert' in c else 0 for c in class_counts.index],
            shadow=True
        )
        ax1.set_title('Tract Classification Distribution', fontweight='bold')
        
        # 2. Annual shooting trends
        ax2 = axes[0, 1]
        ax2.fill_between(annual['year'], annual['total_shootings'], alpha=0.3, color='#e41a1c')
        ax2.plot(annual['year'], annual['total_shootings'], 'o-', color='#e41a1c', linewidth=2, markersize=8)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Total Shootings')
        ax2.set_title('Annual Shooting Trends', fontweight='bold')
        ax2.axhline(annual['total_shootings'].mean(), color='gray', linestyle='--', alpha=0.5, label='Mean')
        
        # Add annotations for peak
        peak_idx = annual['total_shootings'].idxmax()
        peak_year = annual.loc[peak_idx, 'year']
        peak_val = annual.loc[peak_idx, 'total_shootings']
        ax2.annotate(
            f'Peak: {int(peak_val)}',
            (peak_year, peak_val),
            xytext=(10, 10), textcoords='offset points',
            fontsize=9, fontweight='bold'
        )
        
        # 3. Demographics comparison (bar chart)
        ax3 = axes[1, 0]
        trauma_deserts = gdf[gdf['bivariate_class'] == 9]
        other = gdf[gdf['bivariate_class'] != 9]
        
        metrics = ['% Black', '% Poverty']
        td_values = [trauma_deserts['pct_black'].mean(), trauma_deserts['pct_poverty'].mean()]
        other_values = [other['pct_black'].mean(), other['pct_poverty'].mean()]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, td_values, width, label='Trauma Deserts', color='#2a5a5b')
        bars2 = ax3.bar(x + width/2, other_values, width, label='Other Tracts', color='#90b2b3')
        
        ax3.set_ylabel('Percentage')
        ax3.set_title('Demographic Disparities', fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(metrics)
        ax3.legend()
        ax3.set_ylim(0, 100)
        
        # Add value labels
        for bar in bars1:
            ax3.annotate(f'{bar.get_height():.1f}%',
                        (bar.get_x() + bar.get_width()/2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            ax3.annotate(f'{bar.get_height():.1f}%',
                        (bar.get_x() + bar.get_width()/2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)
        
        # 4. Key statistics text box
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        total_shootings = gdf['total_shootings'].sum()
        td_shootings = trauma_deserts['total_shootings'].sum()
        td_pop = trauma_deserts['total_population'].sum()
        city_pop = gdf['total_population'].sum()
        
        stats_text = f"""
        KEY FINDINGS
        ════════════════════════════════════
        
        TRAUMA DESERTS
        • Tracts identified: {len(trauma_deserts)} (4.4% of city)
        • Population affected: {td_pop:,} ({td_pop/city_pop*100:.1f}% of city)
        • Shootings: {int(td_shootings):,} ({td_shootings/total_shootings*100:.1f}% of total)
        
        DEMOGRAPHIC DISPARITIES
        • Avg % Black: {trauma_deserts['pct_black'].mean():.1f}% vs {other['pct_black'].mean():.1f}%
        • Disparity ratio: {trauma_deserts['pct_black'].mean()/other['pct_black'].mean():.1f}x higher
        
        VIOLENCE BURDEN
        • Density: {trauma_deserts['annual_shootings_per_sq_mi'].mean():.1f} vs {other['annual_shootings_per_sq_mi'].mean():.1f} shootings/sq mi/yr
        • Burden ratio: {trauma_deserts['annual_shootings_per_sq_mi'].mean()/other['annual_shootings_per_sq_mi'].mean():.1f}x higher
        
        ACCESS COVERAGE
        • 99.6% of shootings within 20 min of Level I
        • Average transport time: {gdf['time_to_nearest'].mean():.1f} min
        """
        
        ax4.text(0.1, 0.95, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
        
        plt.suptitle('Philadelphia Trauma Desert Analysis Summary', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # Save
        output_file = PATHS.figures / "summary_charts.png"
        fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        fig.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"  Saved: {output_file}")
        return output_file


def create_temporal_chart() -> Path:
    """Create detailed temporal trends chart."""
    with StepLogger("Creating temporal trends chart", logger):
        annual = load_csv(PATHS.tables / "temporal_trends_annual.csv")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Top: Total shootings
        ax1.bar(annual['year'], annual['total_shootings'], color='#e41a1c', alpha=0.7, edgecolor='#c00000')
        ax1.set_ylabel('Total Shootings', fontsize=12)
        ax1.set_title('Philadelphia Shooting Trends (2015-2025)', fontsize=14, fontweight='bold')
        
        # Add trend line
        z = np.polyfit(annual['year'], annual['total_shootings'], 1)
        p = np.poly1d(z)
        ax1.plot(annual['year'], p(annual['year']), 'k--', alpha=0.5, label='Trend')
        
        # Annotate COVID period
        ax1.axvspan(2020, 2022, alpha=0.15, color='gray')
        ax1.text(2021, ax1.get_ylim()[1] * 0.9, 'COVID Period', ha='center', fontsize=10, style='italic')
        
        # Bottom: Fatality rate
        ax2.plot(annual['year'], annual['fatality_rate'], 'o-', color='#2a5a5b', linewidth=2, markersize=8)
        ax2.fill_between(annual['year'], annual['fatality_rate'], alpha=0.3, color='#2a5a5b')
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Fatality Rate (%)', fontsize=12)
        ax2.set_ylim(15, 25)
        ax2.axhline(annual['fatality_rate'].mean(), color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        # Save
        output_file = PATHS.figures / "temporal_trends.png"
        fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        fig.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"  Saved: {output_file}")
        return output_file


def main():
    """Generate all static figures."""
    logger.info("=" * 60)
    logger.info("GENERATING STATIC FIGURES")
    logger.info("=" * 60)
    
    outputs = []
    outputs.append(create_bivariate_static_map())
    outputs.append(create_summary_charts())
    outputs.append(create_temporal_chart())
    
    logger.info("\n" + "=" * 60)
    logger.info("ALL FIGURES GENERATED")
    logger.info("=" * 60)
    
    for path in outputs:
        logger.info(f"  {path}")
    
    return outputs


if __name__ == "__main__":
    paths = main()
    print(f"\n✅ Static figures created in: {PATHS.figures}")


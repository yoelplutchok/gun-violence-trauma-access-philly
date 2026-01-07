#!/usr/bin/env python3
"""
Executive Dashboard: Comprehensive Visual Summary.

Creates a publication-quality multi-panel dashboard summarizing all key findings
from the Trauma Desert analysis. Designed for presentations, policy briefs,
and academic submissions.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

logger = get_logger(__name__)

# Typography
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica Neue', 'Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# Color palette - muted, professional
COLORS = {
    'primary': '#1a1a2e',      # Dark navy
    'secondary': '#16213e',    # Navy
    'accent': '#e94560',       # Coral red
    'accent2': '#0f3460',      # Deep blue
    'success': '#2ecc71',      # Green
    'warning': '#f39c12',      # Orange
    'light': '#f5f5f5',        # Light gray
    'text': '#333333',         # Dark gray
    'muted': '#888888',        # Muted gray
}

# Bivariate color scheme
BIVARIATE_COLORS = {
    1: '#e8e8e8', 2: '#b5c0da', 3: '#6c83b5',
    4: '#b8d6be', 5: '#90b2b3', 6: '#567994',
    7: '#73ae80', 8: '#5a9178', 9: '#2a5a5b'
}


def create_executive_dashboard(
    tracts: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create the main executive dashboard.
    """
    fig = plt.figure(figsize=(20, 14), facecolor='white')
    
    # Create grid layout
    gs = GridSpec(3, 4, figure=fig, height_ratios=[0.15, 1, 0.8],
                  hspace=0.3, wspace=0.25)
    
    # === HEADER ===
    ax_header = fig.add_subplot(gs[0, :])
    ax_header.axis('off')
    
    # Title
    ax_header.text(0.5, 0.7, 'THE TRAUMA DESERT',
                  fontsize=32, fontweight='bold', ha='center', va='center',
                  color=COLORS['primary'])
    ax_header.text(0.5, 0.25, 
                  'Mapping Gun Violence Burden Against Trauma System Capacity in Philadelphia',
                  fontsize=14, ha='center', va='center', color=COLORS['muted'])
    
    # Key stats bar
    stats = [
        ('17,383', 'Shootings\n(2015-2025)'),
        ('18', 'Trauma Desert\nTracts'),
        ('99.6%', 'Within 20 min\nof Level I'),
        ('54.9%', 'Handled by\nTemple Hospital'),
        ('68.5%', 'Disparity\nUnexplained'),
    ]
    
    for i, (value, label) in enumerate(stats):
        x = 0.1 + i * 0.2
        ax_header.text(x, -0.3, value, fontsize=24, fontweight='bold',
                      ha='center', va='center', color=COLORS['accent'])
        ax_header.text(x, -0.7, label, fontsize=9, ha='center', va='center',
                      color=COLORS['muted'])
    
    # === ROW 1: MAIN MAP AND HOSPITAL BURDEN ===
    
    # Panel A: Bivariate Choropleth Map
    ax_map = fig.add_subplot(gs[1, 0:2])
    
    # Plot tracts by bivariate class
    for bv_class in range(1, 10):
        class_tracts = tracts[tracts['bivariate_class'] == bv_class]
        if len(class_tracts) > 0:
            class_tracts.plot(ax=ax_map, color=BIVARIATE_COLORS[bv_class],
                            edgecolor='#cccccc', linewidth=0.3)
    
    # Highlight trauma deserts
    deserts = tracts[tracts['bivariate_class'] == 9]
    deserts.plot(ax=ax_map, facecolor='none', edgecolor=COLORS['accent'],
                linewidth=2)
    
    # Add trauma centers
    level1 = trauma_centers[(trauma_centers['trauma_level'] == 'I') & 
                            (trauma_centers['designation'] == 'Adult')]
    for _, tc in level1.iterrows():
        ax_map.plot(tc['longitude'], tc['latitude'], 
                   marker='^', markersize=12, color=COLORS['accent'],
                   markeredgecolor='white', markeredgewidth=1.5, zorder=10)
    
    ax_map.set_title('A. Bivariate Classification\nShooting Density vs Transport Time',
                    fontweight='bold', pad=10)
    ax_map.axis('off')
    
    # Add bivariate legend
    legend_ax = fig.add_axes([0.08, 0.42, 0.08, 0.08])
    legend_ax.set_xlim(0, 3)
    legend_ax.set_ylim(0, 3)
    
    for i in range(3):
        for j in range(3):
            bv_class = i * 3 + j + 1
            rect = plt.Rectangle((j, 2-i), 1, 1, facecolor=BIVARIATE_COLORS[bv_class],
                                 edgecolor='white', linewidth=0.5)
            legend_ax.add_patch(rect)
    
    legend_ax.set_xlabel('Transport Time', fontsize=8)
    legend_ax.set_ylabel('Shooting Density', fontsize=8)
    legend_ax.set_xticks([])
    legend_ax.set_yticks([])
    legend_ax.spines['top'].set_visible(False)
    legend_ax.spines['right'].set_visible(False)
    
    # Panel B: Hospital Burden
    ax_burden = fig.add_subplot(gs[1, 2])
    
    hospital_stats = load_csv(PATHS.tables / 'hospital_catchment_statistics.csv')
    hospitals = hospital_stats['hospital_name'].str.replace(' Hospital', '').str.replace(' Medical Center', '')
    shootings = hospital_stats['shootings_in_catchment']
    
    colors = [COLORS['accent'] if 'Temple' in h else COLORS['accent2'] 
              for h in hospital_stats['hospital_name']]
    
    bars = ax_burden.barh(range(len(hospitals)), shootings, color=colors, edgecolor='white')
    ax_burden.set_yticks(range(len(hospitals)))
    ax_burden.set_yticklabels(hospitals, fontsize=9)
    ax_burden.set_xlabel('Shootings in Catchment Area')
    ax_burden.set_title('B. Hospital Burden Distribution\n(Temple handles 55% of all shootings)',
                       fontweight='bold', pad=10)
    ax_burden.invert_yaxis()
    
    # Add percentage labels
    total = shootings.sum()
    for i, (bar, val) in enumerate(zip(bars, shootings)):
        ax_burden.text(val + 100, i, f'{val/total*100:.0f}%', 
                      va='center', fontsize=9, fontweight='bold')
    
    ax_burden.spines['top'].set_visible(False)
    ax_burden.spines['right'].set_visible(False)
    
    # Panel C: Temporal Trends
    ax_temporal = fig.add_subplot(gs[1, 3])
    
    trends = load_csv(PATHS.tables / 'temporal_trends_annual.csv')
    years = trends['year']
    shootings_annual = trends['total_shootings']
    
    ax_temporal.fill_between(years, shootings_annual, alpha=0.3, color=COLORS['accent2'])
    ax_temporal.plot(years, shootings_annual, color=COLORS['accent2'], linewidth=2.5)
    
    # Highlight COVID peak
    peak_idx = shootings_annual.idxmax()
    ax_temporal.scatter([years[peak_idx]], [shootings_annual[peak_idx]], 
                       s=100, color=COLORS['accent'], zorder=5)
    ax_temporal.annotate(f'Peak: {int(shootings_annual[peak_idx])}',
                        xy=(years[peak_idx], shootings_annual[peak_idx]),
                        xytext=(years[peak_idx]-1.5, shootings_annual[peak_idx]+200),
                        fontsize=9, fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=COLORS['accent']))
    
    # Add COVID period shading
    ax_temporal.axvspan(2020, 2021, alpha=0.15, color=COLORS['accent'], label='COVID Period')
    
    ax_temporal.set_xlabel('Year')
    ax_temporal.set_ylabel('Annual Shootings')
    ax_temporal.set_title('C. Temporal Trends\n(COVID spike 2020-2021)', fontweight='bold', pad=10)
    ax_temporal.spines['top'].set_visible(False)
    ax_temporal.spines['right'].set_visible(False)
    ax_temporal.set_xlim(2015, 2025)
    
    # === ROW 2: ANALYSIS RESULTS ===
    
    # Panel D: Oaxaca-Blinder Decomposition
    ax_oaxaca = fig.add_subplot(gs[2, 0])
    
    oaxaca = load_csv(PATHS.tables / 'oaxaca_decomposition_results.csv')
    shooting_row = oaxaca[oaxaca['Outcome'].str.contains('Shooting')].iloc[0]
    
    explained = shooting_row['Pct_Explained']
    unexplained = shooting_row['Pct_Unexplained']
    
    wedges, texts, autotexts = ax_oaxaca.pie(
        [explained, unexplained],
        labels=['Explained\n(Poverty/Income)', 'Unexplained\n(Structural)'],
        colors=[COLORS['accent2'], COLORS['accent']],
        autopct='%1.0f%%',
        startangle=90,
        explode=(0, 0.05),
        textprops={'fontsize': 9}
    )
    autotexts[1].set_fontweight('bold')
    autotexts[1].set_fontsize(14)
    
    ax_oaxaca.set_title('D. Racial Disparity Decomposition\n(Black tracts have 4.4x higher shooting density)',
                       fontweight='bold', pad=10)
    
    # Panel E: Golden Hour Coverage - compute from actual data
    ax_golden = fig.add_subplot(gs[2, 1])
    
    # Load golden hour distribution and calculate correct percentages
    golden_hour_file = PATHS.tables / 'golden_hour_distribution.csv'
    if golden_hour_file.exists():
        gh_df = load_csv(golden_hour_file)
        within_10 = gh_df[gh_df['time_interval'].isin(['0-5 min', '5-10 min'])]['percentage'].sum()
        within_10_20 = gh_df[gh_df['time_interval'].isin(['10-15 min', '15-20 min'])]['percentage'].sum()
        beyond_20 = gh_df[gh_df['time_interval'].isin(['20-30 min', '30+ min'])]['percentage'].sum()
        golden_data = [within_10, within_10_20, beyond_20]
        within_20_pct = 100 - beyond_20
    else:
        # Fallback values based on analysis
        golden_data = [90.5, 9.2, 0.4]
        within_20_pct = 99.6
    
    labels = [f'<10 min\n({golden_data[0]:.1f}%)', f'10-20 min\n({golden_data[1]:.1f}%)', f'>20 min\n({golden_data[2]:.1f}%)']
    colors_golden = [COLORS['success'], COLORS['warning'], COLORS['accent']]
    
    ax_golden.pie(golden_data, labels=labels, colors=colors_golden,
                 autopct='', startangle=90, textprops={'fontsize': 9})
    
    # Add center circle for donut
    centre_circle = plt.Circle((0, 0), 0.5, fc='white')
    ax_golden.add_patch(centre_circle)
    ax_golden.text(0, 0, f'{within_20_pct:.1f}%\nwithin\n20 min', ha='center', va='center',
                  fontsize=12, fontweight='bold')
    
    ax_golden.set_title('E. Golden Hour Coverage\n(Excellent geographic access)', fontweight='bold', pad=10)
    
    # Panel F: Vulnerability Overlap
    ax_vuln = fig.add_subplot(gs[2, 2])
    
    vuln = load_csv(PATHS.tables / 'vulnerability_by_bivariate_class.csv')
    classes = vuln['bivariate_class']
    vuln_scores = vuln['vulnerability_index_mean']
    
    bar_colors = [BIVARIATE_COLORS[c] for c in classes]
    bars = ax_vuln.bar(classes, vuln_scores, color=bar_colors, edgecolor='white', linewidth=0.5)
    
    # Highlight class 9
    bars[8].set_edgecolor(COLORS['accent'])
    bars[8].set_linewidth(3)
    
    ax_vuln.set_xlabel('Bivariate Class')
    ax_vuln.set_ylabel('Vulnerability Index')
    ax_vuln.set_title('F. Vulnerability by Classification\n(Trauma deserts have highest disadvantage)',
                     fontweight='bold', pad=10)
    ax_vuln.spines['top'].set_visible(False)
    ax_vuln.spines['right'].set_visible(False)
    
    # Add annotation for class 9
    ax_vuln.annotate('Trauma\nDeserts', xy=(9, vuln_scores.iloc[8]),
                    xytext=(9.5, vuln_scores.iloc[8] + 3),
                    fontsize=8, ha='center',
                    arrowprops=dict(arrowstyle='->', color=COLORS['accent']))
    
    # Panel G: Key Findings Text
    ax_findings = fig.add_subplot(gs[2, 3])
    ax_findings.axis('off')
    
    findings_text = """
KEY FINDINGS

1. THE DISPARITY IS VIOLENCE, NOT ACCESS
   Black neighborhoods are actually 3.2 min 
   CLOSER to trauma centers, but experience 
   4.4x higher shooting rates.

2. TEMPLE IS THE FRONTLINE
   Temple University Hospital handles more 
   than half of all shooting victims in 
   Philadelphia (54.9%).

3. STRUCTURAL FACTORS DOMINATE
   68.5% of the racial disparity in violence 
   cannot be explained by poverty or income.
   Historical/systemic factors are at play.

4. COVID DOUBLED VIOLENCE
   Shootings peaked at 2,338 in 2021, nearly 
   double pre-pandemic levels. Now declining.

5. COMPOUND DISADVANTAGE
   All 18 trauma deserts are also in the top 
   quartile of overall neighborhood vulnerability.
"""
    
    ax_findings.text(0.05, 0.95, findings_text, transform=ax_findings.transAxes,
                    fontsize=9, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor=COLORS['light'], 
                             edgecolor=COLORS['muted'], alpha=0.8))
    
    ax_findings.set_title('G. Summary', fontweight='bold', pad=10)
    
    # === FOOTER ===
    fig.text(0.5, 0.02, 
            'Data: OpenDataPhilly (shootings), Census ACS (demographics), OpenRouteService (isochrones) | '
            'Analysis: Trauma Desert Project, 2025',
            ha='center', fontsize=8, color=COLORS['muted'])
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved executive dashboard: {output_path}")


def create_key_findings_infographic(output_path: Path):
    """
    Create a vertical infographic summarizing key findings.
    """
    fig, axes = plt.subplots(5, 1, figsize=(10, 16), facecolor='white')
    
    findings = [
        {
            'title': 'THE PROBLEM IS VIOLENCE, NOT ACCESS',
            'stat': '99.6%',
            'desc': 'of shootings occur within 20 minutes of a Level I trauma center.\n'
                   'Philadelphia has excellent geographic coverage of trauma care.',
            'color': COLORS['success']
        },
        {
            'title': 'BLACK NEIGHBORHOODS BEAR THE BURDEN',
            'stat': '4.4x',
            'desc': 'higher shooting density in predominantly Black tracts.\n'
                   'Yet these neighborhoods are actually CLOSER to trauma centers.',
            'color': COLORS['accent']
        },
        {
            'title': 'TEMPLE IS THE SAFETY NET',
            'stat': '55%',
            'desc': 'of all shooting victims are served by Temple University Hospital.\n'
                   'Two hospitals (Temple + Penn) handle 82% of all cases.',
            'color': COLORS['accent2']
        },
        {
            'title': 'DISPARITY IS STRUCTURAL',
            'stat': '68%',
            'desc': 'of the racial gap in violence CANNOT be explained by\n'
                   'poverty or income. Historical/systemic factors are at play.',
            'color': COLORS['warning']
        },
        {
            'title': 'COMPOUND DISADVANTAGE',
            'stat': '100%',
            'desc': 'of trauma deserts are also in the top quartile of\n'
                   'overall neighborhood vulnerability.',
            'color': COLORS['primary']
        },
    ]
    
    for ax, finding in zip(axes, findings):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Background bar
        rect = FancyBboxPatch((0.5, 1), 9, 8, boxstyle="round,pad=0.1",
                             facecolor=finding['color'], alpha=0.1,
                             edgecolor=finding['color'], linewidth=2)
        ax.add_patch(rect)
        
        # Stat
        ax.text(2, 5, finding['stat'], fontsize=48, fontweight='bold',
               ha='center', va='center', color=finding['color'])
        
        # Title
        ax.text(5.5, 7.5, finding['title'], fontsize=14, fontweight='bold',
               ha='left', va='center', color=COLORS['primary'])
        
        # Description
        ax.text(5.5, 4.5, finding['desc'], fontsize=11,
               ha='left', va='center', color=COLORS['text'])
    
    # Title
    fig.suptitle('THE TRAUMA DESERT: Key Findings', fontsize=20, fontweight='bold',
                y=0.98, color=COLORS['primary'])
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved infographic: {output_path}")


def create_presentation_map(
    tracts: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create a clean, presentation-ready version of the bivariate map.
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 12), facecolor='white')
    
    # Plot tracts
    for bv_class in range(1, 10):
        class_tracts = tracts[tracts['bivariate_class'] == bv_class]
        if len(class_tracts) > 0:
            class_tracts.plot(ax=ax, color=BIVARIATE_COLORS[bv_class],
                            edgecolor='#999999', linewidth=0.2)
    
    # Highlight trauma deserts with thick border
    deserts = tracts[tracts['bivariate_class'] == 9]
    deserts.plot(ax=ax, facecolor='none', edgecolor='#000000', linewidth=2.5)
    
    # Add trauma centers
    level1 = trauma_centers[(trauma_centers['trauma_level'] == 'I') & 
                            (trauma_centers['designation'] == 'Adult')]
    
    for _, tc in level1.iterrows():
        ax.plot(tc['longitude'], tc['latitude'], 
               marker='^', markersize=14, color='#e41a1c',
               markeredgecolor='white', markeredgewidth=2, zorder=10)
        
        # Add label
        name = tc['hospital_name'].replace(' Hospital', '').replace(' Medical Center', '')
        ax.annotate(name, xy=(tc['longitude'], tc['latitude']),
                   xytext=(8, 8), textcoords='offset points',
                   fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor='gray', alpha=0.9))
    
    ax.axis('off')
    
    # Title
    ax.set_title('The Trauma Desert: Philadelphia, 2015-2025\n'
                'Bivariate Choropleth: Shooting Density vs Transport Time to Level I Trauma',
                fontsize=14, fontweight='bold', pad=20)
    
    # Add bivariate legend
    legend_ax = fig.add_axes([0.12, 0.15, 0.12, 0.12])
    legend_ax.set_xlim(0, 3)
    legend_ax.set_ylim(0, 3)
    
    for i in range(3):
        for j in range(3):
            bv_class = i * 3 + j + 1
            rect = plt.Rectangle((j, 2-i), 1, 1, facecolor=BIVARIATE_COLORS[bv_class],
                                 edgecolor='white', linewidth=1)
            legend_ax.add_patch(rect)
    
    legend_ax.set_xlabel('Transport Time', fontsize=10, labelpad=5)
    legend_ax.set_ylabel('Shooting Density', fontsize=10, labelpad=5)
    legend_ax.set_xticks([0.5, 2.5])
    legend_ax.set_xticklabels(['Low', 'High'], fontsize=8)
    legend_ax.set_yticks([0.5, 2.5])
    legend_ax.set_yticklabels(['High', 'Low'], fontsize=8)
    
    for spine in legend_ax.spines.values():
        spine.set_visible(False)
    
    # Add trauma desert indicator
    legend_ax.annotate('TRAUMA\nDESERT', xy=(2.5, 0.5), xytext=(3.5, 0.5),
                      fontsize=8, fontweight='bold', va='center',
                      arrowprops=dict(arrowstyle='->', color='black'))
    
    # Add marker legend
    ax.plot([], [], '^', markersize=10, color='#e41a1c', 
           markeredgecolor='white', label='Level I Trauma Center')
    ax.plot([], [], 's', markersize=10, color='none',
           markeredgecolor='black', markeredgewidth=2, label='Trauma Desert Tract')
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
    
    # Footer
    fig.text(0.5, 0.02,
            '18 trauma desert tracts identified | 83,159 residents affected | '
            'Data: OpenDataPhilly, Census ACS, OpenRouteService',
            ha='center', fontsize=9, color=COLORS['muted'])
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved presentation map: {output_path}")


def run_visualization_package():
    """
    Main function to create all presentation visualizations.
    """
    logger.info("=" * 60)
    logger.info("CREATING PRESENTATION VISUALIZATION PACKAGE")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts = load_geojson(PATHS.processed / 'tracts_bivariate_classified.geojson')
        trauma_centers = load_csv(PATHS.processed / 'trauma_centers_geocoded.csv')
    
    # Create output directory
    presentation_dir = PATHS.outputs / 'presentation'
    presentation_dir.mkdir(parents=True, exist_ok=True)
    
    # Create visualizations
    with StepLogger("Creating executive dashboard", logger):
        create_executive_dashboard(
            tracts, trauma_centers,
            presentation_dir / 'executive_dashboard.png'
        )
    
    with StepLogger("Creating key findings infographic", logger):
        create_key_findings_infographic(
            presentation_dir / 'key_findings_infographic.png'
        )
    
    with StepLogger("Creating presentation map", logger):
        create_presentation_map(
            tracts, trauma_centers,
            presentation_dir / 'presentation_map.png'
        )
    
    logger.info("\n" + "=" * 60)
    logger.info("PRESENTATION PACKAGE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nFiles created in: {presentation_dir}")
    logger.info("  - executive_dashboard.png/pdf")
    logger.info("  - key_findings_infographic.png/pdf")
    logger.info("  - presentation_map.png/pdf")
    
    return presentation_dir


if __name__ == "__main__":
    run_visualization_package()
    print("\nPresentation package complete!")


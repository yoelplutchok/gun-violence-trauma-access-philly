# Philadelphia Trauma Deserts

**Mapping Gun Violence Burden Against Trauma System Capacity**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Key Findings

| Metric | Value |
|--------|-------|
| **Trauma Desert Tracts** | 18 (4.4% of city) |
| **Affected Population** | 83,159 residents |
| **Shootings in Deserts** | 1,659 (9.5% of total) |
| **Temple Hospital Burden** | 54.9% of all shootings |
| **Unexplained Racial Disparity** | 68.5% |

### Critical Insight

> **The "trauma desert" problem in Philadelphia is driven primarily by the extreme concentration of gun violence, NOT by poor geographic access to trauma care.**
>
> - 99.6% of shootings occur within 20 minutes of Level I trauma
> - Black neighborhoods are actually 3.2 minutes *closer* to hospitals on average
> - Black tracts experience 4.4x higher shooting density
> - 68.5% of this disparity cannot be explained by poverty or income
> - The problem is **violence burden**, not distance to care

---

## Interactive Maps

- **[Bivariate Choropleth Map](outputs/interactive/bivariate_choropleth.html)** - 3x3 classification of violence vs access
- **[Isochrone Coverage Map](outputs/interactive/isochrone_coverage.html)** - Drive-time polygons with shooting heatmap
- **[Patient Flow Map](outputs/interactive/patient_flow_map.html)** - Hospital catchment areas and burden

![Bivariate Map Preview](outputs/figures/bivariate_map.png)

---

## What is a "Trauma Desert"?

A **trauma desert** is a census tract that experiences BOTH:
1. **High gun violence burden** (top tercile of shooting density)
2. **Poor access to Level I trauma care** (top tercile of transport time)

We use a bivariate classification matrix:

| | Good Access | Moderate | Poor Access |
|---|:---:|:---:|:---:|
| **Low Violence** | 1 | 2 | 3 |
| **Moderate** | 4 | 5 | 6 |
| **High Violence** | 7 | 8 | **9 = TRAUMA DESERT** |

---

## Project Structure

```
trauma-desert/
├── data/
│   ├── raw/              # Original downloaded data
│   ├── processed/        # Cleaned and transformed data
│   ├── geo/              # Geographic boundaries
│   ├── isochrones/       # Drive-time polygons
│   └── manual/           # Manually compiled data
├── scripts/
│   ├── collect/          # Data acquisition
│   ├── process/          # Data cleaning and transformation
│   ├── analyze/          # Statistical analysis
│   ├── visualize/        # Map and chart generation
│   └── validate/         # Quality assurance
├── src/trauma_desert/    # Core utilities
├── outputs/
│   ├── figures/          # Static PNG/PDF charts
│   ├── interactive/      # HTML maps
│   ├── presentation/     # Executive dashboard and infographics
│   ├── fact_sheets/      # Neighborhood-specific summaries
│   └── tables/           # CSV results
├── docs/                 # Documentation
└── configs/params.yml    # Analysis parameters
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Conda (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trauma-desert.git
cd trauma-desert

# Create environment (choose one)
conda env create -f environment.yml
conda activate trauma-desert

# OR with pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the Full Pipeline

```bash
# Using Makefile
make all

# Or step by step
make collect    # Download data
make process    # Clean and transform
make analyze    # Run analysis
make visualize  # Generate maps
make validate   # Quality checks
```

---

## Data Sources

| Dataset | Source | Records |
|---------|--------|---------|
| Shooting Incidents | [OpenDataPhilly](https://www.opendataphilly.org/datasets/shooting-victims/) | 17,383 |
| Trauma Centers | [PA Trauma Systems Foundation](https://www.ptsf.org/) | 7 |
| Census Tracts | [US Census TIGER/Line](https://www.census.gov/geographies/mapping-files.html) | 408 |
| Demographics | [ACS 5-Year Estimates](https://data.census.gov/) | 408 |
| Isochrones | [OpenRouteService API](https://openrouteservice.org/) | 20 |

---

## Methodology

### Analysis Pipeline
1. **Data Collection**: Download shooting data, geocode trauma centers, fetch census boundaries
2. **Spatial Join**: Assign each shooting to its containing census tract
3. **Density Calculation**: Annual shootings per square mile per tract
4. **Transport Time**: Drive-time isochrones from Level I trauma centers
5. **Bivariate Classification**: Tercile-based 3x3 matrix
6. **Statistical Analysis**: Disparity tests, golden hour coverage, temporal trends
7. **Extended Analysis**: Oaxaca-Blinder decomposition, scenario modeling, vulnerability indices

### Key Metrics
- **Shooting Density**: `(total_shootings / years) / tract_area_sq_mi`
- **Transport Time**: Minutes to nearest Level I trauma center (driving)
- **Golden Hour**: Percentage of shootings within 20 minutes of definitive care
- **Vulnerability Index**: Composite of poverty, income, violence, and access metrics

See [docs/methodology.md](docs/methodology.md) for complete details.

---

## Key Results

### Hospital Burden Distribution

| Hospital | Shootings | % of City |
|----------|-----------|-----------|
| Temple University Hospital | 9,544 | **54.9%** |
| Penn Presbyterian | 4,677 | 26.9% |
| Jefferson Einstein | 2,262 | 13.0% |
| Thomas Jefferson | 897 | 5.2% |

Temple University Hospital handles more than half of all gun violence victims in Philadelphia.

### Demographic Disparities

| Metric | Trauma Deserts | Other Tracts | p-value |
|--------|----------------|--------------|---------|
| % Black | 76.0% | 38.3% | <0.0001 |
| % Poverty | 30.8% | 21.8% | 0.009 |
| Shooting Rate | 4.4x higher | baseline | - |

### Oaxaca-Blinder Decomposition

The racial disparity in shooting density was decomposed:
- **31.5% Explained** by differences in poverty and income
- **68.5% Unexplained** - attributable to structural/historical factors

### Golden Hour Coverage

| Time Interval | Shootings | % of Total |
|---------------|-----------|------------|
| 0-10 min | 15,724 | 90.5% |
| 10-20 min | 1,594 | 9.2% |
| 20+ min | 62 | 0.4% |

### Temporal Trends
- **Peak Year**: 2021 (2,338 shootings - COVID-era spike)
- **2015 to 2025 Trend**: -27.4% (declining after peak)
- **Summer/Winter Ratio**: 1.41x more shootings in summer months

---

## Extended Analyses

This project includes several advanced analyses:

1. **Time-of-Day Sensitivity**: How rush hour affects trauma access
2. **Scenario Modeling**: Optimal locations for new trauma facilities
3. **Flow Lines Visualization**: Patient routing to nearest trauma centers
4. **Temporal Animation**: Year-by-year shooting hotspot migration
5. **Social Determinants Index**: Compound disadvantage scoring
6. **Oaxaca-Blinder Decomposition**: Quantifying unexplained disparity
7. **Stop the Bleed Prioritization**: Optimal training deployment locations
8. **Neighborhood Fact Sheets**: One-page summaries for advocacy

---

## Configuration

Edit `configs/params.yml` to customize:

```yaml
# Geographic bounds
geography:
  city: "Philadelphia"
  bbox:
    min_lat: 39.86
    max_lat: 40.14

# Isochrone settings
isochrones:
  intervals: [5, 10, 15, 20, 30]
  profile: "driving-car"

# Analysis parameters
analysis:
  golden_hour_threshold: 20
```

---

## Citation

If you use this analysis in your research, please cite:

```bibtex
@misc{trauma_desert_philly_2025,
  title={Philadelphia Trauma Deserts: Mapping Gun Violence Burden Against Trauma System Capacity},
  author={[Your Name]},
  year={2025},
  url={https://github.com/yourusername/trauma-desert}
}
```

---

## Limitations

1. **Transport times** use tract centroids; actual times vary within tracts
2. **Isochrones** assume average traffic; not real-time conditions
3. **Census data** from 2018-2022 may not reflect current demographics
4. **Tercile thresholds** are methodological choices; different cutoffs yield different results
5. **Oaxaca-Blinder decomposition** limited to available socioeconomic variables

See [docs/methodology.md](docs/methodology.md) for complete limitations discussion.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **OpenDataPhilly** for shooting incident data
- **Pennsylvania Trauma Systems Foundation** for trauma center information
- **OpenRouteService** for isochrone generation
- **US Census Bureau** for demographic data

---

*Analysis completed January 2025*

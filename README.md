# 🏥 Philadelphia Trauma Deserts

**Mapping Gun Violence Burden Against Trauma System Capacity**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| **Trauma Desert Tracts** | 18 (4.4% of city) |
| **Affected Population** | 83,159 residents |
| **Shootings in Deserts** | 1,659 (9.5% of total) |
| **Avg % Black** | 76% (vs 40% citywide) |
| **Disparity Ratio** | 1.89x higher Black population |

### Critical Insight

> **The "trauma desert" problem in Philadelphia is driven primarily by the extreme concentration of gun violence, NOT by poor geographic access to trauma care.**
>
> - 99.6% of shootings occur within 20 minutes of Level I trauma
> - Black neighborhoods are actually *closer* to hospitals on average
> - The disparity is in **violence burden**, not distance to care

---

## 🗺️ Interactive Maps

- **[Bivariate Choropleth Map](outputs/interactive/bivariate_choropleth.html)** - 3×3 classification of violence × access
- **[Isochrone Coverage Map](outputs/interactive/isochrone_coverage.html)** - Drive-time polygons with shooting heatmap

![Bivariate Map Preview](outputs/figures/bivariate_map.png)

---

## 🎯 What is a "Trauma Desert"?

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

## 📁 Project Structure

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
│   ├── process/          # Data cleaning & transformation
│   ├── analyze/          # Statistical analysis
│   ├── visualize/        # Map & chart generation
│   └── validate/         # Quality assurance
├── src/trauma_desert/    # Core utilities
├── outputs/
│   ├── figures/          # Static PNG/PDF charts
│   ├── interactive/      # HTML maps
│   └── tables/           # CSV results
├── docs/                 # Documentation
│   ├── data_dictionary.md
│   └── methodology.md
└── configs/params.yml    # Analysis parameters
```

---

## 🚀 Quick Start

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

## 📈 Data Sources

| Dataset | Source | Records |
|---------|--------|---------|
| Shooting Incidents | [OpenDataPhilly](https://www.opendataphilly.org/datasets/shooting-victims/) | 17,383 |
| Trauma Centers | [PA Trauma Systems Foundation](https://www.ptsf.org/) | 7 |
| Census Tracts | [US Census TIGER/Line](https://www.census.gov/geographies/mapping-files.html) | 408 |
| Demographics | [ACS 5-Year Estimates](https://data.census.gov/) | 408 |
| Isochrones | [OpenRouteService API](https://openrouteservice.org/) | 20 |

---

## 🔬 Methodology

### Analysis Pipeline
1. **Data Collection**: Download shooting data, geocode trauma centers, fetch census boundaries
2. **Spatial Join**: Assign each shooting to its containing census tract
3. **Density Calculation**: Annual shootings per square mile per tract
4. **Transport Time**: Drive-time isochrones from Level I trauma centers
5. **Bivariate Classification**: Tercile-based 3×3 matrix
6. **Statistical Analysis**: Disparity tests, golden hour coverage, temporal trends

### Key Metrics
- **Shooting Density**: `(total_shootings / years) / tract_area_sq_mi`
- **Transport Time**: Minutes to nearest Level I trauma center (driving)
- **Golden Hour**: Percentage of shootings within 20 minutes of definitive care

See [docs/methodology.md](docs/methodology.md) for complete details.

---

## 📊 Key Results

### Demographic Disparities

| Metric | Trauma Deserts | Other Tracts | p-value |
|--------|----------------|--------------|---------|
| % Black | 76.0% | 38.3% | <0.0001 |
| % Poverty | 30.8% | 21.8% | 0.009 |
| Shooting Rate | 2.26x higher | baseline | - |

### Golden Hour Coverage

| Time Interval | Shootings | % of Total |
|---------------|-----------|------------|
| 0-10 min | 15,724 | 90.5% |
| 10-20 min | 1,594 | 9.2% |
| 20+ min | 62 | 0.4% |

### Temporal Trends
- **Peak Year**: 2021 (2,338 shootings)
- **2015→2025 Trend**: -27.4% (declining)
- **Summer/Winter Ratio**: 1.41x more in summer

---

## 🛠️ Configuration

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

## 📝 Citation

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

## ⚠️ Limitations

1. **Transport times** use tract centroids; actual times vary within tracts
2. **Isochrones** assume average traffic; not real-time conditions
3. **Census data** from 2018-2022 may not reflect current demographics
4. **Tercile thresholds** are arbitrary; different cutoffs yield different results

See [docs/methodology.md](docs/methodology.md) for complete limitations.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **OpenDataPhilly** for shooting incident data
- **Pennsylvania Trauma Systems Foundation** for trauma center information
- **OpenRouteService** for isochrone generation
- **US Census Bureau** for demographic data

---

*Last updated: December 2025*

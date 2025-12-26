# Methodology

## Trauma Desert Analysis: Mapping Gun Violence Burden Against Trauma System Capacity in Philadelphia

---

## 1. Overview

This study uses a bivariate spatial analysis approach to identify "trauma deserts" - census tracts that experience both:
1. **High gun violence burden** (shooting density)
2. **Poor access to Level I trauma care** (long transport times)

The methodology combines shooting incident data, trauma center locations, drive-time analysis, and demographic data to create a 3×3 classification matrix.

---

## 2. Data Sources

### 2.1 Shooting Incidents
- **Source**: OpenDataPhilly Shooting Victims Database
- **Time Period**: January 2015 - December 2025
- **Records**: 17,383 validated incidents
- **Geography**: Philadelphia County, PA

### 2.2 Trauma Centers
- **Source**: Pennsylvania Trauma Systems Foundation
- **Centers Included**: 4 Level I Adult, 2 Level I Pediatric, 1 Level II
- **Analysis Focus**: Level I Adult centers only (definitive trauma care)

### 2.3 Census Tracts
- **Source**: US Census Bureau TIGER/Line Files (2023)
- **Geography**: Philadelphia County (FIPS 42101)
- **Units**: 408 census tracts

### 2.4 Demographics
- **Source**: American Community Survey 5-Year Estimates (2018-2022)
- **Variables**: Population, race/ethnicity, poverty status, median household income

---

## 3. Data Processing Pipeline

### 3.1 Shooting Data Cleaning
1. Parse and validate date fields
2. Validate coordinates within Philadelphia bounding box
3. Standardize categorical variables (race, sex, age groups)
4. Create binary flags (fatal, officer-involved)
5. Remove records with invalid coordinates (n=27, 0.2%)

### 3.2 Spatial Join
- Method: Point-in-polygon intersection
- CRS: EPSG:4326 (WGS84)
- Result: Each shooting assigned to containing census tract

### 3.3 Density Calculation
- Metric: Annual shootings per square mile
- Formula: `(total_shootings / years_in_dataset) / tract_area_sq_mi`
- Area calculation: Reprojected to EPSG:2272 (PA State Plane South) for accurate area

### 3.4 Transport Time Estimation
- Method: Drive-time isochrones from OpenRouteService API
- Profile: driving-car (typical traffic conditions)
- Intervals: 5, 10, 15, 20, 30 minutes
- Assignment: Tract centroid used to determine which isochrone contains it
- Limitation: Uses centroid; actual times may vary within tract

---

## 4. Bivariate Classification

### 4.1 Tercile Calculation
Both shooting density and transport time are divided into terciles:

| Tercile | Label | Criteria |
|---------|-------|----------|
| 1st | Low | Bottom 33% of distribution |
| 2nd | Medium | Middle 33% of distribution |
| 3rd | High | Top 33% of distribution |

Method: `pd.qcut()` with `rank(method='first')` to handle ties.

### 4.2 Classification Matrix

| | Low Time | Medium Time | High Time |
|---|---|---|---|
| **Low Density** | Class 1 | Class 2 | Class 3 |
| **Medium Density** | Class 4 | Class 5 | Class 6 |
| **High Density** | Class 7 | Class 8 | Class 9 |

**Class 9 = TRAUMA DESERT** (High violence + Poor access)

### 4.3 Priority Categories

| Category | Classes | Description |
|----------|---------|-------------|
| Trauma Desert | 9 | Highest priority - both dimensions critical |
| High Burden | 7, 8 | High violence, acceptable access |
| Access Gap | 3, 6 | Low/moderate violence, poor access |
| Moderate | 4, 5 | Middle on both dimensions |
| Low Priority | 1, 2 | Low violence, good/moderate access |

---

## 5. Statistical Analysis

### 5.1 Demographic Disparity
- **T-tests**: Compare trauma desert tracts to other tracts on % Black and % Poverty
- **Pearson correlation**: Relationship between demographics and violence/access
- **Rate ratios**: Compare shooting rates in predominantly Black vs other tracts

### 5.2 Golden Hour Analysis
- Assess what percentage of shootings occur within various time thresholds of Level I trauma
- Break down by victim demographics and fatality status

### 5.3 Temporal Trends
- Annual shooting counts and fatality rates
- Tract-level trend identification (improving/worsening)
- Seasonal patterns

---

## 6. Validation

### 6.1 Data Quality Checks
- Record retention (≥99%)
- Coordinate validity
- Population totals
- Join completeness
- Classification distribution

### 6.2 Spot Checks
- Manual verification of 3 trauma desert tracts
- Manual verification of 3 low-priority tracts
- Confirm classification logic matches data

---

## 7. Limitations

### 7.1 Temporal Limitations
- Isochrones represent average driving conditions, not real-time traffic
- Historical shooting patterns may not predict future violence
- Transport times assume immediate ambulance availability

### 7.2 Spatial Limitations
- Tract centroids used for transport time assignment
- Large tracts (e.g., Fairmount Park) may have significant intra-tract variation
- Isochrones assume direct travel; actual routes may differ

### 7.3 Data Limitations
- Census income data suppressed for some tracts
- Shooting data may undercount non-reported incidents
- Demographics from 2018-2022 ACS may not reflect current population

### 7.4 Methodological Limitations
- Tercile cutoffs are arbitrary; different thresholds would yield different results
- Equal weighting of density and time in composite score
- Does not account for EMS response time, only transport time

---

## 8. Reproducibility

### 8.1 Code Repository
All analysis code available at: `scripts/`
- `collect/`: Data acquisition scripts
- `process/`: Data cleaning and transformation
- `analyze/`: Statistical analysis
- `visualize/`: Map and chart generation
- `validate/`: Quality assurance

### 8.2 Dependencies
- Python 3.11+
- GeoPandas, Pandas, Folium, Matplotlib
- See `environment.yml` for full dependency list

### 8.3 API Keys Required
- OpenRouteService (isochrone generation)

---

## 9. Key Findings Summary

1. **18 trauma desert tracts** identified (4.4% of city)
2. **83,159 residents** affected
3. **1.89x** higher Black population percentage in trauma deserts
4. **99.6%** of shootings within 20 minutes of Level I trauma
5. Disparity is in **violence burden**, not geographic access

---

*Methodology version: 1.0*  
*Analysis date: December 2025*


# Data Dictionary

## Trauma Desert Project - Philadelphia Gun Violence Analysis

This document describes all data files, their sources, and field definitions.

---

## Raw Data (`data/raw/`)

### `shootings_YYYY-MM-DD.csv`
**Source:** OpenDataPhilly - Shooting Victims  
**URL:** https://www.opendataphilly.org/datasets/shooting-victims/  
**Update frequency:** Daily

| Field | Type | Description |
|-------|------|-------------|
| objectid | int | Unique incident identifier |
| year | int | Year of incident |
| date | date | Date of incident |
| time | time | Time of incident |
| race | str | Victim race (B=Black, W=White, A=Asian, H=Hispanic, etc.) |
| sex | str | Victim sex (M/F) |
| age | int | Victim age |
| wound | str | Wound location |
| fatal | int | 1=Fatal, 0=Non-fatal |
| lat | float | Latitude (WGS84) |
| lng | float | Longitude (WGS84) |
| officer_involved | str | Y/N - Officer-involved shooting |
| offender_injured | str | Y/N - Offender was injured |
| offender_deceased | str | Y/N - Offender was deceased |

---

## Manual Data (`data/manual/`)

### `trauma_centers_YYYY-MM-DD.csv`
**Source:** Pennsylvania Trauma Systems Foundation  
**URL:** https://www.ptsf.org/accreditation/trauma-center-list/  

| Field | Type | Description |
|-------|------|-------------|
| hospital_name | str | Full hospital name |
| address | str | Street address |
| trauma_level | str | Level I Adult/Pediatric, Level II, etc. |

---

## Geographic Data (`data/geo/`)

### `philadelphia_tracts.geojson`
**Source:** US Census Bureau TIGER/Line Files  
**Year:** 2023  

| Field | Type | Description |
|-------|------|-------------|
| GEOID | str | 11-digit census tract identifier (SSFFF + 6-digit tract) |
| NAME | str | Tract number (e.g., "300", "169.02") |
| ALAND | int | Land area in square meters |
| AWATER | int | Water area in square meters |
| geometry | polygon | Tract boundary |

---

## Isochrone Data (`data/isochrones/`)

### `trauma_center_isochrones.geojson`
**Source:** OpenRouteService API  
**Profile:** driving-car  

| Field | Type | Description |
|-------|------|-------------|
| hospital_name | str | Trauma center name |
| trauma_level | str | Trauma designation level |
| time_minutes | int | Drive time in minutes (5, 10, 15, 20, 30) |
| geometry | polygon | Isochrone boundary |

---

## Processed Data (`data/processed/`)

### `shootings_clean.csv`
Cleaned and validated shooting incidents.

| Field | Type | Description |
|-------|------|-------------|
| objectid | int | Unique incident identifier |
| date | datetime | Incident date |
| year | int | Incident year |
| lat | float | Validated latitude |
| lng | float | Validated longitude |
| race | str | Standardized race (Black, White, Asian, Hispanic, Unknown) |
| sex | str | Sex (Male, Female, Unknown) |
| age | int | Age (null if invalid) |
| age_group | str | Age category (<18, 18-24, 25-34, 35-44, 45-54, 55+) |
| is_fatal | bool | True if shooting was fatal |
| is_officer_involved | bool | True if officer-involved |

### `shootings_with_tracts.csv`
Shootings with assigned census tract.

| Field | Type | Description |
|-------|------|-------------|
| (all fields from shootings_clean) | | |
| tract_geoid | str | Census tract GEOID where shooting occurred |

### `tract_demographics.csv`
ACS 5-Year demographic estimates by tract.

| Field | Type | Description |
|-------|------|-------------|
| GEOID | str | Census tract identifier |
| tract_name | str | Census tract name |
| total_population | int | Total population |
| black_alone | int | Black population count |
| pct_black | float | Percent Black (0-100) |
| white_alone | int | White population count |
| pct_white | float | Percent White (0-100) |
| asian_alone | int | Asian population count |
| pct_asian | float | Percent Asian (0-100) |
| hispanic_latino | int | Hispanic/Latino population count |
| pct_hispanic | float | Percent Hispanic (0-100) |
| median_household_income | int | Median household income (null if suppressed) |
| below_poverty | int | Population below poverty level |
| pct_poverty | float | Percent in poverty (0-100) |

### `trauma_centers_geocoded.csv`
Trauma centers with coordinates.

| Field | Type | Description |
|-------|------|-------------|
| hospital_name | str | Hospital name |
| address | str | Street address |
| trauma_level | str | Trauma designation |
| latitude | float | Geocoded latitude |
| longitude | float | Geocoded longitude |

### `tract_shooting_density.geojson`
Shooting density metrics by tract.

| Field | Type | Description |
|-------|------|-------------|
| GEOID | str | Census tract identifier |
| NAME | str | Tract number |
| total_shootings | int | Total shootings 2015-present |
| fatal_shootings | int | Fatal shootings count |
| fatality_rate | float | Percent fatal (0-100) |
| area_sq_mi | float | Tract area in square miles |
| annual_shootings_per_sq_mi | float | Average annual shootings per sq mi |
| geometry | polygon | Tract boundary |

### `tract_transport_times.csv`
Transport time to nearest Level I trauma center.

| Field | Type | Description |
|-------|------|-------------|
| GEOID | str | Census tract identifier |
| time_to_nearest | int | Minutes to nearest Level I (5, 10, 15, 20, 30) |
| time_category | str | Descriptive category |
| within_golden_hour | bool | True if ≤20 min |
| nearest_trauma_center | str | Name of nearest Level I |

### `tracts_analysis_ready.geojson`
Master analysis dataset with all metrics.

| Field | Type | Description |
|-------|------|-------------|
| GEOID | str | Census tract identifier |
| NAME | str | Tract number |
| total_shootings | int | Total shootings |
| annual_shootings_per_sq_mi | float | Shooting density |
| fatality_rate | float | Percent fatal |
| time_to_nearest | int | Minutes to Level I |
| nearest_trauma_center | str | Nearest hospital name |
| total_population | int | Population |
| pct_black | float | Percent Black |
| pct_poverty | float | Percent poverty |
| density_tercile | str | Low/Medium/High |
| time_tercile | str | Low/Medium/High |
| geometry | polygon | Tract boundary |

### `tracts_bivariate_classified.geojson`
Final classified dataset.

| Field | Type | Description |
|-------|------|-------------|
| (all fields from tracts_analysis_ready) | | |
| bivariate_class | int | Classification 1-9 |
| bivariate_label | str | Human-readable label |
| priority_category | str | Trauma Desert, High Burden, Access Gap, Moderate, Low Priority |

---

## Output Tables (`outputs/tables/`)

### `trauma_desert_tracts.csv`
Ranked list of trauma desert tracts.

| Field | Type | Description |
|-------|------|-------------|
| priority_rank | int | Rank (1 = highest priority) |
| GEOID | str | Census tract identifier |
| NAME | str | Tract number |
| total_shootings | int | Total shootings |
| annual_shootings_per_sq_mi | float | Density metric |
| time_to_nearest | int | Minutes to Level I |
| nearest_trauma_center | str | Hospital name |
| total_population | int | Population |
| pct_black | float | Percent Black |
| pct_poverty | float | Percent poverty |
| trauma_desert_score | float | Composite ranking score (0-1) |

### `validation_report.csv`
Data quality validation results.

| Field | Type | Description |
|-------|------|-------------|
| category | str | Validation category |
| check | str | Check name |
| status | str | PASS/FAIL/WARN |
| message | str | Result message |

---

## Bivariate Classification Matrix

| Class | Density | Time | Label |
|-------|---------|------|-------|
| 1 | Low | Low | Low burden, Good access |
| 2 | Low | Medium | Low burden, Moderate access |
| 3 | Low | High | Low burden, Poor access |
| 4 | Medium | Low | Moderate burden, Good access |
| 5 | Medium | Medium | Moderate burden, Moderate access |
| 6 | Medium | High | Moderate burden, Poor access |
| 7 | High | Low | High burden, Good access |
| 8 | High | Medium | High burden, Moderate access |
| 9 | High | High | **TRAUMA DESERT** |

---

## Coordinate Reference Systems

- **WGS84 (EPSG:4326)**: Used for all geographic data storage
- **PA State Plane South (EPSG:2272)**: Used for area calculations (square miles)

---

## Data Quality Notes

1. **Census Income Suppression**: Tracts with suppressed income data show -666666666 in raw Census data; converted to null in processed data.

2. **Shooting Coordinate Validation**: Coordinates outside Philadelphia bounding box (39.86-40.14°N, 74.95-75.28°W) are excluded.

3. **Transport Time Approximation**: Times are based on centroid-to-hospital drive times; actual times may vary based on traffic and exact location within tract.

4. **Isochrone Generation**: Uses OpenRouteService driving-car profile; does not account for real-time traffic conditions.

---

*Last updated: December 2025*


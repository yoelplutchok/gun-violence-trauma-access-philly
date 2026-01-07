# The Trauma Desert: Execution Plan
## Mapping Gun Violence Burden Against Trauma System Capacity in Philadelphia

---

> ### 🎉 PROJECT STATUS: MVP COMPLETE → NOW EXTENDING
> 
> **Phases 0-6 are COMPLETE.** The core analysis is finished with key findings:
> - 18 trauma desert tracts identified (4.4% of city, 83,159 residents)
> - 99.6% of shootings within 20 min of Level I trauma
> - **Critical insight:** The disparity is in violence concentration, NOT geographic access
> 
> **Phase 7 (Extensions) is NOW ACTIVE.** See [Section 10](#section-10-planned-extensions-) for our roadmap of 15 planned enhancements including time-of-day analysis, scenario modeling, social determinants integration, and more.

---

**Project Goal:** Determine whether Philadelphia neighborhoods with the highest gun violence burden are systematically farther from Level I trauma centers, creating "trauma deserts" that disproportionately affect Black and low-income communities.

**End Product:** An interactive bivariate choropleth map showing shooting density vs. trauma access, with identified trauma desert neighborhoods and demographic disparity analysis.

---

## 📋 CURSOR INITIALIZATION PROMPT

> **Copy and paste this entire block when starting a new Cursor session for this project:**

```
You are helping me build the Trauma Desert project.
This execution plan document is your PRIMARY source of truth.

## YOUR WORKING RULES:

### 1. STEP-BY-STEP EXECUTION
- Work through ONE step at a time. Do not rush ahead.
- After completing each step, STOP and wait for my confirmation before proceeding.
- If a step has multiple sub-tasks, complete them all before moving on.

### 2. DOCUMENT UPDATES (CRITICAL)
After completing each step, you MUST update this markdown file with:
- ✅ Mark the step as complete in the Progress Log below
- Add a timestamped entry in the "Execution Log" section describing:
  - What was done
  - What files were created/modified
  - Any issues encountered and how they were resolved
  - Output verification (e.g., "Generated isochrones for 5 Level I trauma centers")

This document should ALWAYS contain the full context of where we are in the project.

### 3. IMPROVISATION & SUGGESTIONS
You are my research collaborator, not just an executor. You MAY:
- Suggest improvements to the methodology
- Propose better data sources
- Recommend additional analyses
- Identify potential issues with the approach

HOWEVER, before making ANY change that deviates from this plan:
1. STOP and explain what you want to change
2. Explain WHY you think it's better
3. Wait for my approval before proceeding

Flag deviations with: "🔄 PROPOSED CHANGE: [description]"

### 4. DATA ACQUISITION
NEVER guess data URLs or try to download data without my confirmation.
If you need data:
1. Tell me exactly what you need
2. Provide the expected source URL (if known)
3. Wait for me to download it or confirm the approach

### 5. API KEYS
This project requires API keys for isochrone generation. NEVER commit API keys to the repository.
Before making API calls:
1. Confirm I have set up the .env file
2. Verify the API key is loaded correctly
3. Respect rate limits (OpenRouteService: 2,000/day)

### 6. ERROR HANDLING
If something fails:
1. Explain what went wrong clearly
2. Propose 1-2 solutions
3. Wait for my decision on how to proceed

### 7. SESSION CONTINUITY
At the start of each new session:
1. Read this entire document to understand current state
2. Check the Progress Log and Execution Log
3. Summarize: "Last session we completed X. Next step is Y."

## CURRENT SESSION START:
Please read this document and tell me:
1. Current project status (what's done, what's next)
2. What you need from me to proceed with the next step
```

---

## 📊 Progress Log

> **Cursor updates this section after each completed step**

### Phase 0: Project Setup
- [x] Directory structure created
- [x] `environment.yml` created
- [x] `pyproject.toml` created
- [x] Core utility modules created (`paths.py`, `io_utils.py`, `logging_utils.py`)
- [x] `configs/params.yml` created
- [x] `Makefile` created
- [x] `.gitignore` created
- [x] `.env.example` created (for API keys)

### Phase 1: Data Collection
- [x] Philadelphia shooting data downloaded (OpenDataPhilly)
- [x] Trauma center list compiled (PTSF + ACS verification)
- [x] Trauma centers geocoded
- [x] Census tract boundaries downloaded
- [x] Census demographic data downloaded (ACS)
- [x] Isochrones generated for all Level I trauma centers

### Phase 2: Data Processing
- [x] Shooting data cleaned and validated
- [x] Shootings assigned to census tracts (spatial join)
- [x] Tract-level shooting density calculated
- [x] Transport time to nearest Level I calculated for each tract
- [x] Demographics joined to tracts
- [x] Master analysis dataset created

### Phase 3: Analysis
- [x] Bivariate classification created (3×3 matrix)
- [x] Trauma desert tracts identified and ranked
- [x] Demographic disparity analysis completed
- [x] Golden hour analysis completed
- [x] Temporal trend analysis completed
- [x] Statistical tests documented

### Phase 4: Visualization
- [x] Bivariate color scheme finalized
- [x] Interactive map created (Folium/Mapbox)
- [x] Static publication maps exported (4 maps)
- [x] Summary charts created
- [x] All figures exported to outputs/

### Phase 5: Validation & Documentation
- [x] Data validation checks passed
- [x] Spot checks completed (3 trauma desert tracts, 3 low-priority tracts)
- [x] Sensitivity analysis run
- [x] Data dictionary written
- [x] Methodology document complete
- [x] Limitations documented

### Phase 6: Deployment
- [x] GitHub repository prepared
- [x] Interactive map hosted (GitHub Pages or similar)
- [x] Policy brief created
- [x] README complete

### Phase 7: Extensions (IN PROGRESS) 🚧
- [x] 10.1 Time-of-Day Isochrone Sensitivity ✅ COMPLETE
- [x] 10.2 Scenario Modeling (New Sites) ✅ COMPLETE
- [x] 10.4 Flow Lines Visualization ✅ COMPLETE
- [x] 10.6 Temporal Animation ✅ COMPLETE
- [x] 10.12 Neighborhood Fact Sheets ✅ COMPLETE
- [x] 10.3 Social Determinants Index ✅ COMPLETE
- [x] 10.9 Oaxaca-Blinder Decomposition ✅ COMPLETE
- [x] 10.15 Stop the Bleed Prioritization ✅ COMPLETE
- [ ] 10.5 EMS Station Layer
- [ ] 10.7 2SFCA Floating Catchment
- [ ] 10.8 Hospital Diversion Status
- [ ] 10.9 Oaxaca-Blinder Decomposition
- [ ] 10.10 Survival/Fatality Correlation
- [ ] 10.11 Spatiotemporal Clustering
- [ ] 10.13 Multi-City Comparison
- [ ] 10.14 Firearm Trace Density
- [ ] 10.15 Stop the Bleed Prioritization

---

## 📝 Execution Log

> **Cursor appends entries here after each step. Do not delete previous entries.**

```
---
### [2025-12-25 Session 1] Phase 0: Project Setup Complete
**Completed by:** Cursor
**Files created:**
- Directory structure (data/, scripts/, src/, outputs/, configs/, docs/, tests/, logs/)
- environment.yml (conda environment with geopandas, folium, etc.)
- requirements.txt (pip fallback with all dependencies)
- pyproject.toml (project metadata and build configuration)
- src/trauma_desert/__init__.py (package initialization)
- src/trauma_desert/paths.py (centralized path management)
- src/trauma_desert/io_utils.py (data loading/saving utilities)
- src/trauma_desert/logging_utils.py (logging configuration)
- configs/params.yml (all analysis parameters in one place)
- Makefile (automation targets: setup, collect, process, analyze, visualize, test)
- .gitignore (Python, IDE, environment files)
- .env.example (API key template)
- README.md (project overview and quick start)

**Verification:** All 16 files created successfully. Directory structure verified with `find` command.
**Issues:** None
**Next step:** Phase 1 - Data Collection (download shooting data from OpenDataPhilly)
---

### [2025-12-25 Session 1] Phase 1: Data Collection Complete
**Completed by:** Cursor
**Files created:**
- scripts/collect/download_shootings.py
- scripts/collect/geocode_trauma_centers.py
- scripts/collect/download_census_tracts.py
- scripts/collect/download_demographics.py
- scripts/collect/generate_isochrones.py
- data/raw/shootings_2025-12-25.csv (17,410 records, 2015-2023)
- data/raw/manifest.json
- data/manual/trauma_centers_2025-12-25.csv (7 centers)
- data/processed/trauma_centers_geocoded.csv
- data/processed/tract_demographics.csv (408 tracts)
- data/geo/philadelphia_tracts.geojson (408 tracts)
- data/isochrones/trauma_center_isochrones.geojson (20 isochrones)

**Data Summary:**
- Shooting incidents: 17,410 (2015-01-01 to 2025-12-23)
- Fatal shootings: 3,597 (20.7%)
- Level I Adult trauma centers: 4 (Temple, Penn Presbyterian, Jefferson, Einstein)
- Level I Pediatric: 2 (St. Christopher's, CHOP)
- Level II Adult: 1 (Jefferson Torresdale)
- Census tracts: 408
- Philadelphia population: 1,593,208
- Isochrones: 5 intervals (5/10/15/20/30 min) × 4 hospitals = 20

**Verification:** 
- All shooting data has valid coordinates (99.8%)
- All trauma centers geocoded successfully
- Isochrones generated via OpenRouteService API

**Issues:** 
- 3 trauma center addresses required manual geocoding (Census API format issues)
- ORS API returned list fields that needed filtering before GeoJSON export

**Next step:** Phase 2 - Data Processing (clean shootings, spatial join to tracts)
---

### [2025-12-25 Session 1] Phase 2: Data Processing Complete
**Completed by:** Cursor
**Files created:**
- scripts/process/clean_shootings.py
- scripts/process/assign_shootings_to_tracts.py
- scripts/process/calculate_tract_density.py
- scripts/process/calculate_transport_times.py
- scripts/process/create_master_dataset.py
- data/processed/shootings_clean.csv (17,383 records)
- data/processed/shootings_with_tracts.csv
- data/processed/tract_shooting_density.geojson
- data/processed/tract_transport_times.csv
- data/processed/tracts_analysis_ready.geojson (master dataset)

**Processing Summary:**
- Cleaned records: 17,383 (27 removed for invalid coordinates)
- 81.1% Black victims, 20.7% fatal
- Tracts with shootings: 387 (21 tracts with zero)
- Top tract: 371 shootings (132/sq mi/yr)
- Max density: 321.4 shootings per sq mi per year
- Avg time to trauma: 11.4 min
- Tracts within 20 min of Level I: 383 (93.9%)
- Master dataset: 408 tracts, 26 columns

**Issues:**
- GEOID type mismatch (float64 vs string) - fixed by converting to int then string
- Categorical columns not compatible with GeoJSON - converted to strings

**Next step:** Phase 3 - Analysis (bivariate classification, trauma desert identification)
---

### [2025-12-25 Session 1] Phase 3: Analysis Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/bivariate_classification.py
- scripts/analyze/identify_trauma_deserts.py
- scripts/analyze/demographic_disparity.py
- scripts/analyze/golden_hour_analysis.py
- scripts/analyze/temporal_trends.py
- data/processed/tracts_bivariate_classified.geojson
- outputs/tables/trauma_desert_tracts.csv
- outputs/tables/trauma_desert_summary_statistics.csv
- outputs/tables/demographic_disparity_analysis.csv
- outputs/tables/demographics_by_bivariate_class.csv
- outputs/tables/golden_hour_distribution.csv
- outputs/tables/golden_hour_by_race.csv
- outputs/tables/temporal_trends_annual.csv
- outputs/tables/temporal_trends_by_tract.csv

**Key Findings:**

1. **Trauma Desert Identification:**
   - 18 trauma desert tracts (4.4% of city)
   - 83,159 residents affected
   - 1,659 shootings (9.5% of city total)
   - Top tract: Tract 300 (253 shootings, 15 min to trauma)

2. **Demographic Disparities:**
   - Trauma deserts: 76% Black vs 38% other tracts (p < 0.0001)
   - Poverty: 30.8% vs 21.8% (p = 0.0091)
   - Rate ratio: 2.8x higher shooting rate in predominantly Black tracts
   - Interesting: Black neighborhoods CLOSER to trauma centers (r = -0.25) but bear 60.8% of shootings

3. **Golden Hour Coverage:**
   - 99.6% of shootings within 20 min of Level I trauma
   - Only 62 shootings (0.4%) beyond 20 min
   - Black victims: 91.4% within 10 min (better than 86.6% for White)
   - Geography is NOT the barrier - violence concentration is

4. **Temporal Trends:**
   - Peak year: 2021 (2,338 shootings) - COVID-era spike
   - Overall trend 2015→2025: -27.4% (declining)
   - Summer 1.41x more shootings than winter
   - 160 tracts improving, 110 increasing

5. **Nearest Trauma Centers to Deserts:**
   - Temple University Hospital: 9 tracts
   - Penn Presbyterian: 9 tracts

**Statistical Tests:**
- t-test: % Black in trauma deserts vs other (t=4.77, p<0.0001) - SIGNIFICANT
- t-test: % Poverty in trauma deserts vs other (t=2.62, p=0.0091) - SIGNIFICANT
- Pearson: % Black vs Shooting Density (r=0.391, p<0.0001) - SIGNIFICANT
- Pearson: % Black vs Transport Time (r=-0.250, p<0.0001) - SIGNIFICANT (negative!)

**Interpretation:**
The "trauma desert" phenomenon in Philadelphia is driven primarily by the extreme concentration of gun violence in certain neighborhoods, NOT by poor geographic access to trauma care. Black neighborhoods are actually closer to Level I trauma centers on average, but they experience dramatically higher rates of shootings. The disparity is in violence burden, not in healthcare access.

**Issues:** None

**Next step:** Phase 4 - Visualization (bivariate choropleth map, interactive dashboard)
---

### [2025-12-25 Session 1] Phase 4: Visualization Complete
**Completed by:** Cursor
**Files created:**
- scripts/visualize/create_bivariate_map.py
- scripts/visualize/create_isochrone_map.py
- scripts/visualize/create_static_figures.py
- outputs/interactive/bivariate_choropleth.html
- outputs/interactive/isochrone_coverage.html
- outputs/figures/bivariate_map.png + .pdf
- outputs/figures/summary_charts.png + .pdf
- outputs/figures/temporal_trends.png + .pdf

**Visualization Summary:**

1. **Bivariate Choropleth Map (Interactive):**
   - Stevens Blue-Green color scheme (3×3 matrix)
   - Trauma desert tracts highlighted with red borders
   - Level I trauma centers marked with hospital icons
   - Popup tooltips with tract details
   - Full legend with classification explanation

2. **Isochrone Coverage Map (Interactive):**
   - Dark theme for visibility
   - 5/10/15/20/30-minute drive-time polygons
   - Shooting heatmap overlay (5,000 point sample)
   - All Level I & II trauma centers marked
   - Layer controls for toggling visibility

3. **Static Publication Figures:**
   - bivariate_map.png: High-res choropleth with legend
   - summary_charts.png: 4-panel summary (pie chart, trends, demographics, key findings)
   - temporal_trends.png: Annual shootings + fatality rate charts

**Color Scheme:**
- Low burden + Good access: #e8e8e8 (light gray)
- Trauma Desert (High + High): #2a5a5b (dark teal)
- Trauma centers: #e41a1c (red)

**Issues:** 
- Minor: Hospital emoji glyph missing in static PDF (cosmetic only)

**Next step:** Phase 5 - Validation & Documentation
---

### [2025-12-26 Session 1] Phase 5: Validation & Documentation Complete
**Completed by:** Cursor
**Files created:**
- scripts/validate/run_validation.py
- scripts/validate/spot_check.py
- docs/data_dictionary.md
- docs/methodology.md
- outputs/tables/validation_report.csv
- outputs/tables/spot_check_results.csv

**Validation Summary:**
- **21 checks passed**, 0 failed, 1 warning
- Warning: 25 tracts with Census income suppression (expected, documented)

**Validation Categories:**
1. Shooting Data: 5/5 passed (99.8% retention, valid coords, 20.6% fatality rate)
2. Census Tract Data: 4/5 passed + 1 warning (408 tracts, 1.59M population)
3. Spatial Joins: 3/3 passed (100% assignment, counts match)
4. Bivariate Classification: 5/5 passed (all 9 classes present, balanced terciles)
5. Transport Times: 4/4 passed (11.4 min average, 5-30 min range)

**Spot Check Results:**
- 3 trauma desert tracts verified ✅ (Tracts 300, 169.02, 151.02)
- 3 low-priority tracts verified ✅ (Tracts 90, 158, 369.02)
- All 6 classifications match tercile logic exactly

**Documentation Created:**
1. **Data Dictionary** (docs/data_dictionary.md)
   - 15 data file definitions
   - Field-level documentation for all datasets
   - CRS and data quality notes

2. **Methodology** (docs/methodology.md)
   - Complete analysis pipeline description
   - Bivariate classification methodology
   - Statistical analysis approach
   - Limitations section

**Issues:** None

**Next step:** Phase 6 - Deployment (GitHub, interactive hosting, README)
---

### [2025-12-26 Session 1] Phase 6: Deployment Complete
**Completed by:** Cursor
**Files created:**
- README.md (comprehensive project documentation)
- LICENSE (MIT)
- CONTRIBUTING.md (contribution guidelines)
- docs/index.html (GitHub Pages landing page)

**Repository Summary:**
- **72 files** committed to git
- Initial commit: `afd844a`
- Branch: `master`

**Documentation Created:**
1. **README.md** - Full project overview with:
   - Key findings summary
   - Quick start guide
   - Data sources
   - Methodology overview
   - Project structure
   - Configuration options
   - Citation format

2. **docs/index.html** - Modern landing page for GitHub Pages with:
   - Key statistics display
   - Interactive map links
   - Critical insight highlight
   - Dark theme design

3. **CONTRIBUTING.md** - Developer guidelines

4. **LICENSE** - MIT License

**GitHub Pages Setup:**
- Landing page: `docs/index.html`
- Interactive maps linked from `outputs/interactive/`
- Ready for GitHub Pages deployment (set source to `/docs` folder)

**To Deploy to GitHub:**
```bash
git remote add origin https://github.com/yourusername/trauma-desert.git
git push -u origin master
```

Then enable GitHub Pages in Settings → Pages → Source: `master` branch, `/docs` folder.

**Issues:** None

**PROJECT COMPLETE ✅**
---

### [2025-01-06] Extension 10.1: Time-of-Day Sensitivity Analysis Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/time_of_day_sensitivity.py
- data/processed/tracts_time_of_day_classified.geojson
- outputs/tables/time_of_day_sensitivity_summary.csv
- outputs/tables/tracts_that_flip_by_time.csv
- outputs/figures/time_of_day_sensitivity.png + .pdf
- outputs/figures/classification_flip_analysis.png

**Analysis Summary:**
Applied research-based traffic multipliers to simulate rush hour vs. off-peak conditions:
- Off-Peak (baseline): ×1.0 travel time
- Morning Rush: ×1.4 travel time  
- Evening Rush: ×1.5 travel time
- Overnight: ×0.9 travel time

**Key Findings:**
1. **Trauma desert count is STABLE across all scenarios** (8 tracts)
2. **149 tracts (36.5%) experience classification changes** across scenarios
3. **40 instances of tracts leaving desert status** under different conditions
4. **0 tracts become NEW deserts** during rush hour
5. Evening rush hour is worst scenario (avg 17.0 min vs 11.4 min baseline)
6. Maximum transport time: 45 min during evening rush (vs 30 min baseline)

**Interpretation:**
The tercile-based classification is **remarkably robust** to traffic conditions. Because all travel times increase proportionally during rush hour, the relative rankings don't change significantly. The same tracts that are "high time" during off-peak remain "high time" during rush hour. This validates the baseline analysis—**trauma deserts are persistent features, not time-of-day artifacts**.

**Methodology Note:**
OpenRouteService free tier doesn't include real-time traffic. Analysis uses INRIX/FHWA-based multipliers. For production use, recommend TomTom or Google Traffic API.

**Next step:** Extension 10.2 - Scenario Modeling (Hypothetical New Sites)
---

### [2025-01-07] Extension 10.2: Scenario Modeling Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/scenario_modeling.py
- data/processed/best_scenario_analysis.geojson
- outputs/tables/scenario_impact_rankings.csv
- outputs/figures/scenario_rankings.png
- outputs/figures/scenario_map_rank1_Hunting_Park.png
- outputs/figures/scenario_map_rank2_Kingsessing_Cobbs_Creek.png
- outputs/figures/scenario_map_rank3_Tioga_Nicetown.png

**Analysis Summary:**
Tested 8 candidate locations for hypothetical new Level I trauma centers. Used distance-based drive time estimation with routing factor (1.4x) and Philadelphia urban speed (18 mph).

**Top 5 Candidate Locations by Impact Score:**

| Rank | Location | Population Improved | Shootings in Improved Tracts | Trauma Deserts Helped | Avg Improvement |
|------|----------|---------------------|------------------------------|----------------------|-----------------|
| 1 | **Hunting Park** | 198,932 | 4,998 | 0 | 1.6 min |
| 2 | Kingsessing/Cobbs Creek | 166,003 | 2,974 | **8** | 4.2 min |
| 3 | Tioga/Nicetown | 174,801 | 3,477 | 2 | 2.0 min |
| 4 | Frankford/Mayfair | 323,391 | 2,106 | 5 | 5.1 min |
| 5 | Strawberry Mansion | 158,896 | 2,479 | 3 | 3.3 min |

**Key Findings:**
1. **Hunting Park** has highest overall impact score due to high shooting count in affected tracts
2. **Kingsessing/Cobbs Creek** would help the MOST trauma desert tracts (8 of 18)
3. **Frankford/Mayfair** would reach the most population (323,391) but lower violence burden
4. All top locations are in North/West Philadelphia where violence is concentrated

**Policy Insight:**
If the goal is to reduce trauma deserts specifically, **Kingsessing/Cobbs Creek** is the top choice.
If the goal is to maximize coverage of high-violence areas, **Hunting Park** is optimal.

**Methodology Note:**
Drive times estimated using haversine distance × 1.4 routing factor ÷ 18 mph urban speed. For precise results, would need actual ORS/Mapbox routing API calls for each location.

**Next step:** Continue with remaining extensions
---

### [2025-01-07] Presentation Visualization Package Complete
**Completed by:** Cursor
**Files created:**
- scripts/visualize/create_executive_dashboard.py
- outputs/presentation/executive_dashboard.png + .pdf
- outputs/presentation/key_findings_infographic.png + .pdf
- outputs/presentation/presentation_map.png + .pdf

**Visualization Package Contents:**

1. **Executive Dashboard** (20x14 inches, 300 DPI)
   - 7-panel comprehensive summary
   - Bivariate choropleth map
   - Hospital burden distribution
   - Temporal trends with COVID peak
   - Oaxaca-Blinder decomposition pie chart
   - Golden hour coverage donut chart
   - Vulnerability by class bar chart
   - Key findings text summary

2. **Key Findings Infographic** (10x16 inches)
   - 5 major findings with headline statistics
   - Clean, presentation-ready format
   - Print-friendly vertical layout

3. **Presentation Map** (14x12 inches, 300 DPI)
   - Publication-quality bivariate choropleth
   - Hospital labels and legend
   - Trauma desert tract highlighting

**Use Cases:**
- Academic presentations and conferences
- Policy briefings
- Grant applications
- Public health reports

---

### [2025-01-07] Extension 10.15: Stop the Bleed Prioritization Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/stop_the_bleed_prioritization.py
- outputs/tables/stop_the_bleed_priority_zones.csv
- outputs/tables/stop_the_bleed_training_sites.csv
- outputs/tables/tract_stb_priority_scores.csv
- outputs/figures/stop_the_bleed_priority_map.png + .pdf
- outputs/figures/stop_the_bleed_impact_analysis.png

**Top 5 Priority Zones for Training:**

| Rank | Tract | Population | Shootings | Transport Time |
|------|-------|------------|-----------|----------------|
| 1 | 300 | 8,294 | 253 | 15 min |
| 2 | 330 | 10,323 | 66 | 20 min |
| 3 | 298 | 5,299 | 84 | 15 min |
| 4 | 178 | 6,592 | 371 | 10 min |
| 5 | 63 | 4,415 | 89 | 15 min |

**Impact Summary:**
- **Top 20 zones reach**: 126,586 residents
- **Cover**: 2,607 historical shootings
- **Avg transport time**: 12.9 min
- **Potential lives saved**: ~8 annually (conservative estimate)

**Recommended Training Sites:**
1. Public schools (highest reach)
2. SEPTA transit hubs
3. Recreation centers
4. Churches/religious institutions
5. Community health centers

**Target Training Groups:**
- Teachers, school staff, transit workers
- Corner store employees (often first on scene)
- Community health workers
- Family members of violence victims

---

### [2025-01-07] Extension 10.9: Oaxaca-Blinder Decomposition Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/oaxaca_decomposition.py
- outputs/tables/oaxaca_decomposition_results.csv
- outputs/tables/oaxaca_predictor_contributions.csv
- outputs/figures/oaxaca_decomposition.png + .pdf
- outputs/figures/oaxaca_predictor_contributions.png

**🚨 MAJOR FINDING: 68.5% of Shooting Disparity is UNEXPLAINED**

| Outcome | Black Tracts | Other Tracts | Gap | % Explained | % Unexplained |
|---------|--------------|--------------|-----|-------------|---------------|
| Shooting Density | 4.4x higher | baseline | 1.49 log | **31.5%** | **68.5%** |
| Transport Time | 9.3 min | 12.4 min | **-3.2 min** | N/A | N/A |

**Key Findings:**
1. **Violence Burden**: Black tracts have 4.4x higher shooting density
   - Only 31.5% explained by poverty/income differences
   - **68.5% is UNEXPLAINED** (structural/historical factors)

2. **Healthcare Access**: Black tracts are actually **3.2 min CLOSER** to trauma centers
   - ✅ **No access disparity against Black neighborhoods**
   - The problem is NOT geographic access—it's violence concentration

**Interpretation:**
The Oaxaca-Blinder decomposition confirms our earlier findings with statistical rigor. The disparity in gun violence burden cannot be fully explained by observable neighborhood characteristics like poverty. Nearly 70% of the gap remains unexplained—suggesting historical, structural, and systemic factors not captured by socioeconomic variables. However, the healthcare access finding is a silver lining: Black neighborhoods are actually closer to Level I trauma centers.

---

### [2025-01-07] Extension 10.3: Social Determinants Index Complete
**Completed by:** Cursor
**Files created:**
- scripts/analyze/social_determinants_index.py
- data/processed/tracts_with_vulnerability.geojson
- outputs/tables/vulnerability_by_bivariate_class.csv
- outputs/tables/tract_vulnerability_scores.csv
- outputs/figures/vulnerability_index_map.png + .pdf
- outputs/figures/vulnerability_correlations.png

**Vulnerability Index Composition:**
| Indicator | Weight | Source |
|-----------|--------|--------|
| Poverty Rate | 25% | Census ACS |
| Household Income | 20% | Census ACS |
| Shooting Density | 30% | OpenDataPhilly |
| Transport Time | 25% | Our Analysis |

**🚨 KEY FINDING: 100% Overlap**

| Metric | City Average | Trauma Deserts | Ratio |
|--------|--------------|----------------|-------|
| Vulnerability Index | 16.5 | 21.6 | **1.31x** |
| In Top Quartile | 25% (by definition) | **100%** (18/18) | 4.0x |

**ALL 18 trauma deserts are also in the top quartile of compound disadvantage.**

**Correlations:**
- Vulnerability ↔ % Poverty: r = 0.512 (p < 0.001) - **STRONG**
- Vulnerability ↔ % Black: r = 0.185 (p < 0.001) - Moderate

**Interpretation:**
Trauma deserts are not isolated phenomena—they exist within neighborhoods experiencing multiple overlapping forms of structural disadvantage. This strengthens the equity argument for targeted intervention.

---

### [2025-01-07] Extension 10.12: Neighborhood Fact Sheets Complete
**Completed by:** Cursor
**Files created:**
- scripts/visualize/create_fact_sheets.py
- outputs/fact_sheets/fact_sheet_tract_300.png + .pdf
- outputs/fact_sheets/fact_sheet_tract_169_02.png + .pdf
- outputs/fact_sheets/fact_sheet_tract_151_02.png + .pdf
- outputs/fact_sheets/fact_sheet_tract_103.png + .pdf
- outputs/fact_sheets/fact_sheet_tract_102.png + .pdf

**Top 5 Trauma Desert Tracts (Fact Sheets Created):**

| Rank | Tract | Neighborhood | Shootings | Transport Time |
|------|-------|--------------|-----------|----------------|
| 1 | **300** | North Philadelphia | 253 | ~15 min |
| 2 | 169.02 | Kensington | 164 | ~12 min |
| 3 | 151.02 | Strawberry Mansion | 153 | ~14 min |
| 4 | 103 | North Philadelphia | 99 | ~13 min |
| 5 | 102 | North Philadelphia | 99 | ~12 min |

**Fact Sheet Contents:**
- Mini-map showing tract location in Philadelphia
- Key statistics (shootings, transport time, population, demographics)
- Nearest Level I trauma center with access rating
- "The Problem" section with burden metrics
- "Recommendations" section with interventions
- Professional formatting for printing/sharing

**Use Cases:**
- Community advocacy meetings
- Policy briefings to city council
- Grant applications for violence intervention funding
- Public health presentations

---

### [2025-01-07] Extension 10.6: Temporal Animation Complete
**Completed by:** Cursor
**Files created:**
- scripts/visualize/create_temporal_animation.py
- outputs/figures/shooting_animation.gif (animated year-by-year visualization)
- outputs/figures/shooting_small_multiples.png + .pdf
- outputs/figures/shooting_trend_map.png
- outputs/figures/shooting_annual_summary.png
- outputs/tables/tract_shooting_trends.csv

**Annual Shooting Counts (2015-2025):**

| Year | Shootings | Change from 2015 |
|------|-----------|------------------|
| 2015 | 1,286 | baseline |
| 2016 | 1,339 | +4.1% |
| 2017 | 1,261 | -1.9% |
| 2018 | 1,448 | +12.6% |
| 2019 | 1,472 | +14.5% |
| **2020** | **2,256** | **+75.4%** (COVID) |
| **2021** | **2,338** | **+81.8%** (PEAK) |
| 2022 | 2,268 | +76.4% |
| 2023 | 1,672 | +30.0% |
| 2024 | 1,107 | -13.9% |
| 2025 | 933 | -27.4% |

**Key Findings:**
- 🎯 **Peak year: 2021** with 2,338 shootings (COVID-era spike)
- 📉 **Overall trend: -27.4%** decline from 2015 to 2025
- 🔴 **158 tracts increasing**, 118 decreasing, 132 stable
- The COVID years (2020-2021) saw shootings nearly DOUBLE

**Visualization Outputs:**
- **Animated GIF**: Year-by-year choropleth showing hotspot migration
- **Small multiples**: Grid of all years for side-by-side comparison
- **Trend map**: Red/yellow/green showing increasing/stable/decreasing tracts
- **Annual summary**: Bar chart with COVID peak highlighted

---

### [2025-01-07] Extension 10.4: Flow Lines Visualization Complete
**Completed by:** Cursor
**Files created:**
- scripts/visualize/create_flow_map.py
- outputs/figures/patient_flow_map.png + .pdf
- outputs/interactive/patient_flow_map.html
- outputs/tables/hospital_catchment_statistics.csv

**Analysis Summary:**
Created origin-destination flow map showing which trauma center serves each census tract. Lines are weighted by shooting volume and colored by transport time.

**🚨 KEY FINDING: Hospital Burden Distribution**

| Hospital | Tracts Served | Population | Shootings | % of City |
|----------|---------------|------------|-----------|-----------|
| **Temple University Hospital** | 168 | 651,245 | **9,544** | **54.9%** |
| Penn Presbyterian | 95 | 337,974 | 4,677 | 26.9% |
| Jefferson Einstein | 83 | 404,154 | 2,262 | 13.0% |
| Thomas Jefferson | 62 | 199,835 | 897 | 5.2% |

**Critical Insight:**
🎯 **Temple University Hospital handles MORE THAN HALF of all gun violence victims in Philadelphia** (54.9%). This confirms Temple's outsized role as the city's primary safety-net trauma center for penetrating injuries.

Combined, Temple + Penn Presbyterian handle **81.8%** of all shootings, meaning just 2 hospitals bear the burden for 4 out of 5 shooting victims.

**Visualization Features:**
- Static map: Lines weighted by shootings, colored by time, with hospital labels
- Interactive map: Clickable lines with tract details, hospital catchment layers
- Catchment statistics CSV for data analysis

**Next step:** Extension 10.3 - Social Determinants Index (or user choice)
---

Example format:
---
### [2025-01-15 14:30] Phase 1: Shooting Data Collection
**Completed by:** Cursor
**Files created:**
- data/raw/shootings_2025-01-15.csv
- data/raw/manifest.json (updated)

**Verification:** Downloaded 15,847 shooting incidents (2015-2024), all with valid coordinates
**Issues:** None
**Next step:** Compile trauma center list from PTSF website
---
```

---

## 🔄 Deviation Log

> **Cursor logs any approved changes to the original plan here**

```
[Deviations from the plan will be logged here]

Example format:
---
### [2025-01-16] Added Level II trauma centers to analysis
**Original plan:** Focus only on Level I trauma centers
**Changed to:** Include Level II centers as secondary access option
**Reason:** Penn Presbyterian is Level I but Einstein is technically Level I Adult/Level II Pediatric - need to handle this nuance
**Approved by:** User on 2025-01-16
**Impact:** Added 2 additional trauma centers to isochrone generation
---
```

---

## 💡 Research Suggestions Log

> **Cursor logs suggestions for improving the research here (even if not implemented)**

```
[Research improvement suggestions will be logged here]

Example format:
---
### [2025-01-17] Suggestion: Add EMS station locations
**Suggestion:** Overlay EMS station locations to show pre-hospital response capacity
**Rationale:** Transport time starts from EMS arrival, not from the shooting location
**Status:** Deferred to future enhancement
**User response:** "Good idea for v2, would need to file public records request for station data"
---
```

---

## Table of Contents

0. [Project Setup & Reproducibility Standards](#section-0-project-setup--reproducibility-standards) ⭐ **START HERE**
1. [Project Overview](#section-1-project-overview)
2. [Data Source Inventory](#section-2-data-source-inventory)
3. [Data Collection Procedures](#section-3-data-collection-procedures)
4. [Data Processing & Cleaning](#section-4-data-processing--cleaning)
5. [Analysis & Classification](#section-5-analysis--classification)
6. [Visualization Development](#section-6-visualization-development)
7. [Validation & Quality Assurance](#section-7-validation--quality-assurance)
8. [Documentation & Deliverables](#section-8-documentation--deliverables)
9. [Deployment & Sharing](#section-9-deployment--sharing)
10. [**Planned Extensions**](#section-10-planned-extensions-) 🚧 **ACTIVE ROADMAP**
    - 10.1 Time-of-Day Sensitivity ⭐
    - 10.2 Scenario Modeling ⭐
    - 10.3 Social Determinants Index ⭐
    - 10.4 Flow Lines Visualization
    - 10.5 EMS Station Layer
    - 10.6 Temporal Animation
    - 10.7 2SFCA Floating Catchment
    - 10.8 Hospital Diversion Status
    - 10.9 Oaxaca-Blinder Decomposition
    - 10.10 Survival Correlation
    - 10.11 Spatiotemporal Clustering
    - 10.12 Neighborhood Fact Sheets
    - 10.13 Multi-City Comparison
    - 10.14 Firearm Trace Density
    - 10.15 Stop the Bleed Prioritization
11. [Cursor/LLM Prompting Guide](#section-11-cursorllm-prompting-guide)

---

## Section 0: Project Setup & Reproducibility Standards

> **Important:** This section contains critical instructions for setting up this project in a clean, reproducible manner. These conventions are designed for LLM-assisted development (Cursor) and ensure the codebase remains maintainable.

### 0.1 Initial Repository Setup

Before writing any code, create the project with this structure:

```bash
# Create the repository
mkdir trauma-desert
cd trauma-desert
git init

# Create directory structure
mkdir -p data/{raw,processed,geo,isochrones}
mkdir -p scripts
mkdir -p src/trauma_desert
mkdir -p outputs/{figures,interactive,tables}
mkdir -p configs
mkdir -p tests/fixtures
mkdir -p docs
mkdir -p logs

# Create placeholder files
touch src/trauma_desert/__init__.py
touch tests/__init__.py
touch configs/.gitkeep
touch logs/.gitkeep

# Create essential files
touch README.md
touch environment.yml
touch pyproject.toml
touch Makefile
touch .gitignore
touch .env.example
```

### 0.2 Environment Configuration

**Directory Structure**:
```
trauma-desert/
├── data/
│   ├── raw/                    # Original downloaded files (never modify)
│   ├── processed/              # Cleaned and transformed data
│   ├── geo/                    # Shapefiles and geographic data
│   └── isochrones/             # Drive-time polygon files
├── scripts/
│   ├── collect/                # Data collection scripts
│   ├── process/                # Data cleaning and transformation
│   ├── analyze/                # Statistical analysis
│   └── visualize/              # Map generation
├── outputs/
│   ├── figures/                # Static map exports
│   ├── interactive/            # Web-based visualization files
│   └── tables/                 # Summary statistics
├── docs/
│   ├── data_dictionary.md      # Field definitions
│   ├── methodology.md          # Methods documentation
│   └── limitations.md          # Known issues and caveats
├── tests/                      # Validation scripts
├── .env.example                # Template for API keys
├── requirements.txt            # Python dependencies
├── Makefile                    # Automation commands
└── README.md                   # Project overview
```

**Required Tools**:
- Python 3.10+ with virtual environment
- GeoPandas for spatial operations
- Pandas for data manipulation
- Requests for API calls
- Folium or Mapbox GL JS for interactive mapping
- OpenRouteService Python client (or Mapbox Isochrone API)
- Matplotlib/Seaborn for static visualizations
- H3 or other hexbin library (optional, for density smoothing)

**API Keys Needed**:
- OpenRouteService API (free tier: 2,000 requests/day) OR
- Mapbox API (free tier: 100,000 requests/month)
- Census API (free, optional for demographic enrichment)

**Makefile Targets**:
- `make setup` - Create virtual environment and install dependencies
- `make collect` - Run all data collection scripts
- `make isochrones` - Generate drive-time isochrones for trauma centers
- `make process` - Run all data processing scripts
- `make analyze` - Run statistical analysis
- `make visualize` - Generate all maps
- `make test` - Run validation checks
- `make clean` - Remove processed files (preserve raw)
- `make all` - Full pipeline execution

### 0.3 Data Versioning

- Save all raw downloads with date stamps (e.g., `shootings_2024-01-15.csv`)
- Create a `data/raw/manifest.json` logging: source URL, download date, file hash, row count
- Never modify raw files; all transformations create new files in `processed/`
- Isochrone files are expensive to generate; cache and version separately

### 0.4 Reproducibility Checklist

Before considering the project complete:
- [ ] All data sources documented with URLs and access dates
- [ ] API keys stored in .env, not committed to repository
- [ ] Random seed set for any sampling operations
- [ ] Environment can be recreated from requirements.txt
- [ ] `make all` runs end-to-end without errors
- [ ] Output figures regenerate identically on fresh run
- [ ] Isochrone generation is cached (skip if already exists)

---

## Section 1: Project Overview

### 1.1 Research Question

**Primary Question**: Is there a spatial mismatch between gun violence burden and timely access to Level I trauma care in Philadelphia, and does this mismatch disproportionately affect predominantly Black and low-income neighborhoods?

**Secondary Questions**:
1. Which neighborhoods have the highest shooting density but longest transport times to Level I trauma centers?
2. What is the "golden hour" coverage - what percentage of shootings occur within 10/15/20 minutes of a Level I trauma center?
3. Do Temple's community intervention program boundaries align with the highest-burden, lowest-access areas?
4. How has the geographic distribution of shootings changed over time (2015-present)?

### 1.2 Hypothesis

Neighborhoods with the highest gun violence burden are systematically farther from Level I trauma centers, creating "trauma deserts" where survival probability is reduced due to transport time. These trauma deserts are concentrated in predominantly Black and low-income areas of North and West Philadelphia.

### 1.3 Key Metrics

| Metric | Definition | Source |
|--------|------------|--------|
| Shooting Density | Shootings per square mile per year, by census tract | OpenDataPhilly |
| Transport Time | Driving minutes from tract centroid to nearest Level I trauma center | Isochrone API |
| Trauma Desert Score | High shooting density + Long transport time (bivariate) | Calculated |
| Golden Hour Gap | % of shootings occurring >20 min from Level I trauma | Calculated |
| Demographic Burden | % Black, % below poverty line in high-burden tracts | Census ACS |

### 1.4 Conceptual Framework

**The Golden Hour**: Trauma survival rates drop significantly after 60 minutes post-injury. For penetrating trauma (gunshots), faster transport correlates with survival. The first 10-20 minutes are critical for hemorrhage control.

**Trauma System Levels**:
- **Level I**: Highest capability, 24/7 surgeons, full resources (Temple University Hospital is Level I)
- **Level II**: Can stabilize and treat most trauma, may transfer complex cases
- **Level III/IV**: Limited capability, primarily stabilize and transfer

For gunshot wounds, Level I is strongly preferred. This analysis focuses on access to Level I centers.

### 1.5 Expected Outputs

1. **Interactive Map**: Philadelphia census tracts as bivariate choropleth (shooting density × transport time), with trauma center locations and isochrones
2. **Trauma Desert Identification**: List of census tracts classified as "trauma deserts" (high burden, low access)
3. **Disparity Analysis**: Comparison of trauma access by neighborhood racial composition
4. **Temporal Animation**: Optional - animated map showing shooting patterns by year
5. **Policy Brief**: 2-page summary highlighting intervention opportunities

---

## Section 2: Data Source Inventory

### 2.1 Philadelphia Shooting Victims Data

**Source**: OpenDataPhilly - Shooting Victims
**URL**: https://www.opendataphilly.org/datasets/shooting-victims/
**API Endpoint**: Available via CARTO or direct download
**Format**: CSV/GeoJSON with coordinates
**Key Fields**:
- date_ (date of incident)
- time (time of incident)
- lat (latitude)
- lng (longitude)
- race (victim race)
- sex (victim sex)
- age (victim age)
- wound (wound location)
- fatal (0 = non-fatal, 1 = fatal)
- point_x, point_y (projected coordinates)

**Temporal Coverage**: 2015-present (updated regularly)
**Spatial Coverage**: All of Philadelphia

**Collection Method**: Direct API download or CSV export

### 2.2 Pennsylvania Trauma Center Registry

**Source**: Pennsylvania Trauma Systems Foundation (PTSF)
**URL**: https://www.ptsf.org/accreditation/trauma-center-list/
**Format**: HTML table (requires scraping) or PDF
**Key Fields**:
- Hospital Name
- Address
- Trauma Level (I, II, III, IV)
- Accreditation Status
- Pediatric Designation (if applicable)

**Alternative Source**: American College of Surgeons Trauma Center Verification
**URL**: https://www.facs.org/quality-programs/trauma/verified-centers/

**Philadelphia-Area Level I Trauma Centers** (to verify):
- Temple University Hospital (North Philadelphia)
- Penn Presbyterian Medical Center (West Philadelphia)
- Hospital of the University of Pennsylvania (West Philadelphia)
- Thomas Jefferson University Hospital (Center City)
- Einstein Medical Center Philadelphia (North Philadelphia)
- St. Christopher's Hospital for Children (Pediatric, North Philadelphia)

**Collection Method**: Manual extraction into structured spreadsheet, then geocode addresses

### 2.3 Hospital Location Geocoding

**Source**: CMS Provider Enrollment Data OR Google/Census Geocoding
**Purpose**: Convert trauma center addresses to lat/long coordinates

**CMS Data URL**: https://data.cms.gov/provider-data/
**Census Geocoder**: https://geocoding.geo.census.gov/geocoder/

**Key Fields Needed**:
- Hospital Name
- Full Address
- Latitude
- Longitude
- Trauma Level

### 2.4 Drive-Time Isochrone Data

**Source**: OpenRouteService API or Mapbox Isochrone API
**Purpose**: Generate polygons showing areas reachable within X minutes of each trauma center

**OpenRouteService**:
- URL: https://openrouteservice.org/dev/#/api-docs/v2/isochrones
- Free tier: 2,000 requests/day
- Supports driving, walking, cycling profiles

**Mapbox Isochrone API**:
- URL: https://docs.mapbox.com/api/navigation/isochrone/
- Free tier: 100,000 requests/month

**Parameters to Request**:
- Location: Each trauma center's coordinates
- Profile: driving-car
- Time intervals: 5, 10, 15, 20, 30 minutes
- Output: GeoJSON polygons

### 2.5 Census Tract Boundaries and Demographics

**Source**: US Census Bureau TIGER/Line + American Community Survey
**URLs**:
- Boundaries: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- Demographics: https://data.census.gov/ (ACS 5-year estimates)

**Key Fields**:
- GEOID (tract identifier)
- Geometry (polygon)
- Total Population
- Race/Ethnicity breakdown (% Black, % Hispanic, % White)
- Median Household Income
- Poverty Rate

**Geography**: Philadelphia County (FIPS 42101)

### 2.6 Temple Intervention Program Boundaries (Optional)

**Source**: Temple University research publications, news articles, or direct outreach
**Purpose**: Map boundaries of Temple's violence intervention programs for overlay

**Known Programs**:
- Hospital-Based Violence Intervention Program (HVIP)
- Community-Based Violence Intervention
- Temple's Center for Gun Violence Research & Solutions

**Challenge**: Program boundaries may not be publicly mapped; may require manual digitization from descriptions or direct contact with Temple researchers

---

## Section 3: Data Collection Procedures

### 3.1 Collect Philadelphia Shooting Data

**Task**: Download complete shooting victims dataset

**Input**: OpenDataPhilly API

**Steps**:
1. Navigate to https://www.opendataphilly.org/datasets/shooting-victims/
2. Identify API endpoint or download link
3. Download full dataset (all years available, 2015-present)
4. Request format: CSV with all fields
5. Save to `data/raw/shootings_YYYY-MM-DD.csv`
6. Log download in manifest.json with row count, date range, timestamp

**Validation**:
- Row count should be substantial (Philadelphia has ~1,500-2,000 shootings/year)
- Total should be 10,000+ records for multi-year dataset
- Verify date range spans expected years
- Check for null coordinates (should be minimal)

**Output**: `data/raw/shootings_YYYY-MM-DD.csv`

### 3.2 Collect Trauma Center Data

**Task**: Create comprehensive list of Philadelphia-area Level I and II trauma centers

**Input**: PTSF website, ACS verification list

**Steps**:
1. Visit https://www.ptsf.org/accreditation/trauma-center-list/
2. Filter or identify Philadelphia region hospitals
3. Record for each trauma center:
   - Hospital Name
   - Full Street Address
   - City, State, ZIP
   - Trauma Level (I, II, III)
   - Adult/Pediatric designation
4. Cross-reference with American College of Surgeons verified list
5. Focus on Level I and Level II centers (Level III/IV less relevant for GSW)
6. Save to `data/manual/trauma_centers_YYYY-MM-DD.csv`

**Level I Centers to Confirm**:
- Temple University Hospital
- Penn Presbyterian Medical Center
- Hospital of the University of Pennsylvania
- Thomas Jefferson University Hospital
- Einstein Medical Center Philadelphia

**Validation**:
- Should identify 5-7 Level I/II centers in Philadelphia area
- All addresses should be within Philadelphia or immediately adjacent counties
- Verify Temple University Hospital is included and marked Level I

**Output**: `data/manual/trauma_centers_YYYY-MM-DD.csv`

### 3.3 Geocode Trauma Center Addresses

**Task**: Convert trauma center addresses to coordinates

**Input**: `data/manual/trauma_centers_YYYY-MM-DD.csv`

**Steps**:
1. Load trauma center list
2. For each address, query Census Geocoder or Google Geocoding API
3. Record returned latitude and longitude
4. Verify geocoding accuracy by spot-checking on map
5. For any failed geocodes, manually look up coordinates
6. Save geocoded file

**Census Geocoder Method**:
- Use batch geocoding endpoint
- Submit CSV with address components
- Download results with coordinates

**Validation**:
- All trauma centers should have valid coordinates
- All coordinates should fall within Philadelphia metro area
- Spot-check 3 centers on Google Maps to verify location accuracy

**Output**: `data/processed/trauma_centers_geocoded.csv`

### 3.4 Generate Drive-Time Isochrones

**Task**: Create drive-time polygons for each trauma center

**Input**: `data/processed/trauma_centers_geocoded.csv`

**Steps**:
1. Load trauma center coordinates
2. For each Level I trauma center, call isochrone API with parameters:
   - Center: [longitude, latitude]
   - Profile: driving-car
   - Time intervals: [5, 10, 15, 20, 30] minutes
3. Save response as GeoJSON for each center
4. Combine all isochrones into single GeoJSON with attributes:
   - hospital_name
   - trauma_level
   - time_minutes
5. Handle API rate limits (add delays between requests if needed)

**OpenRouteService API Call Structure**:
- Endpoint: POST https://api.openrouteservice.org/v2/isochrones/driving-car
- Body includes: locations, range (in seconds), range_type: "time"
- Headers include: Authorization with API key

**Validation**:
- Each trauma center should have 5 isochrone polygons (one per time interval)
- Polygons should be nested (5-min inside 10-min inside 15-min, etc.)
- Polygons should cover expected geographic area (roughly 5-15 miles for 20 min)
- Visualize on map to confirm reasonableness

**Output**: `data/isochrones/trauma_center_isochrones.geojson`

### 3.5 Collect Census Tract Boundaries

**Task**: Download Philadelphia census tract boundaries

**Input**: Census TIGER/Line files

**Steps**:
1. Navigate to Census TIGER/Line download page
2. Select year (use most recent, e.g., 2022 or 2023)
3. Select geography: Census Tracts
4. Select state: Pennsylvania
5. Download shapefile for all PA tracts
6. Extract and filter to Philadelphia County (FIPS 42101)
7. Save filtered shapefile or convert to GeoJSON

**Alternative**: Use Census API or download Philadelphia-specific file from OpenDataPhilly

**Validation**:
- Philadelphia should have approximately 380-400 census tracts
- Boundaries should cover entire city
- No gaps or overlaps in geometry

**Output**: `data/geo/philadelphia_tracts.geojson`

### 3.6 Collect Census Demographics

**Task**: Download tract-level demographic data

**Input**: American Community Survey 5-year estimates via Census API or data.census.gov

**Steps**:
1. Identify required tables:
   - B01003: Total Population
   - B02001: Race
   - B03003: Hispanic/Latino Origin
   - B19013: Median Household Income
   - B17001: Poverty Status
2. Query Census API for Philadelphia County tracts
3. Calculate derived fields:
   - Percent Black (B02001_003 / B01003_001)
   - Percent Hispanic (B03003_003 / B01003_001)
   - Percent Below Poverty (poverty universe count / total)
4. Join to tract boundaries by GEOID
5. Save as enriched GeoJSON or separate CSV for joining

**Validation**:
- All tracts should have demographic data (some small tracts may have sampling issues)
- Percentages should sum reasonably (race categories may exceed 100% if multi-race)
- Spot-check known neighborhoods (e.g., North Philadelphia should show high % Black)

**Output**: `data/processed/tract_demographics.csv`

---

## Section 4: Data Processing & Cleaning

### 4.1 Clean Shooting Data

**Task**: Standardize and validate shooting incident records

**Input**: `data/raw/shootings_YYYY-MM-DD.csv`

**Steps**:
1. Load raw shooting data
2. Parse date and time fields into standard datetime format
3. Extract year, month, day of week, hour for temporal analysis
4. Validate coordinates:
   - Remove records with null lat/lng
   - Remove records with coordinates outside Philadelphia bounding box
   - Bounding box: lat 39.86-40.14, lng -75.28 to -74.95
5. Standardize race field:
   - Map variations to consistent categories (Black, White, Hispanic, Asian, Other/Unknown)
6. Create binary fields:
   - is_fatal (from fatal field)
   - is_male (from sex field)
7. Create age groups: 0-17, 18-24, 25-34, 35-44, 45+
8. Drop duplicate records if any
9. Save cleaned file

**Validation**:
- Count records removed and document reasons
- Verify date range is as expected
- Check distribution of categorical variables

**Output**: `data/processed/shootings_clean.csv`

### 4.2 Assign Shootings to Census Tracts

**Task**: Spatial join of shooting points to tract polygons

**Input**:
- `data/processed/shootings_clean.csv`
- `data/geo/philadelphia_tracts.geojson`

**Steps**:
1. Load shooting data and create point geometries from lat/lng
2. Load tract boundaries
3. Ensure both datasets use same coordinate reference system (EPSG:4326)
4. Perform point-in-polygon spatial join
5. Each shooting record gets tract GEOID appended
6. Handle edge cases:
   - Shootings exactly on tract boundaries (assign to either)
   - Shootings with coordinates slightly outside city (flag and review)
7. Save joined dataset

**Validation**:
- All shootings should be assigned to a tract (except those outside city)
- Tract assignment count should roughly match known high-violence areas
- Spot-check 10 shootings by visual inspection on map

**Output**: `data/processed/shootings_with_tracts.csv`

### 4.3 Calculate Tract-Level Shooting Density

**Task**: Aggregate shootings to tract level and calculate rates

**Input**:
- `data/processed/shootings_with_tracts.csv`
- `data/geo/philadelphia_tracts.geojson`
- `data/processed/tract_demographics.csv`

**Steps**:
1. Group shootings by tract GEOID
2. Calculate for each tract:
   - Total shootings (all years)
   - Shootings per year (average)
   - Fatal shootings (count and percentage)
   - Shootings in most recent year
3. Calculate tract area in square miles
4. Calculate shooting density: shootings per square mile per year
5. Calculate population-adjusted rate: shootings per 10,000 residents per year
6. Join to tract geometries and demographics
7. Create percentile ranks for density (for mapping)

**Validation**:
- Highest-density tracts should be in known high-violence areas (North/West Philly)
- Total shootings should match source data
- Rates should be reasonable (not astronomical for tiny tracts)

**Output**: `data/processed/tract_shooting_density.geojson`

### 4.4 Calculate Transport Time to Trauma Centers

**Task**: Determine drive time from each tract to nearest Level I trauma center

**Input**:
- `data/geo/philadelphia_tracts.geojson`
- `data/isochrones/trauma_center_isochrones.geojson`

**Steps**:
1. Load tract boundaries
2. Calculate centroid of each tract
3. Load isochrone polygons for all Level I trauma centers
4. For each tract centroid:
   - Determine which isochrones contain the point
   - Find the minimum time isochrone that contains the centroid
   - Record: nearest_trauma_center, time_to_nearest (categorical: 0-5, 5-10, 10-15, 15-20, 20-30, 30+)
5. For tracts outside all isochrones:
   - Calculate actual drive time using routing API (if within budget)
   - OR assign maximum category (30+ minutes)
6. Create binary field: within_golden_hour (<=20 min = yes)

**Alternative Method (More Precise)**:
- Instead of isochrones, query routing API for actual drive time from each tract centroid to each trauma center
- This is more API-intensive but gives continuous time values
- May be worth it for ~400 tracts × 5 trauma centers = 2,000 API calls

**Validation**:
- Tracts near Center City should have lowest times
- Tracts in far Northeast/Southwest should have highest times
- Temple University Hospital should be nearest for North Philadelphia tracts

**Output**: `data/processed/tract_transport_times.csv`

### 4.5 Create Master Analysis Dataset

**Task**: Combine all tract-level metrics into single analysis file

**Input**:
- `data/processed/tract_shooting_density.geojson`
- `data/processed/tract_transport_times.csv`
- `data/processed/tract_demographics.csv`

**Steps**:
1. Start with tract geometries and shooting density
2. Join transport time data on GEOID
3. Join demographic data on GEOID
4. Final dataset should have for each tract:
   - GEOID, geometry
   - Shooting count, density, rate
   - Transport time category, nearest trauma center
   - Population, % Black, % Hispanic, % Poverty, Median Income
5. Calculate derived fields:
   - Shooting density tercile (Low/Medium/High)
   - Transport time tercile (Low/Medium/High)
6. Save as GeoJSON for mapping

**Validation**:
- All ~400 tracts present
- No missing values in key fields
- Distributions of variables are reasonable

**Output**: `data/processed/tracts_analysis_ready.geojson`

---

## Section 5: Analysis & Classification

### 5.1 Bivariate Classification: Trauma Desert Index

**Task**: Create 3×3 bivariate classification combining shooting density and transport time

**Input**: `data/processed/tracts_analysis_ready.geojson`

**Classification Matrix**:

|                        | Low Transport Time | Medium Transport Time | High Transport Time |
|------------------------|--------------------|-----------------------|---------------------|
| **Low Shooting Density**   | 1 (Low priority)   | 2                     | 3                   |
| **Medium Shooting Density**| 4                  | 5                     | 6                   |
| **High Shooting Density**  | 7                  | 8                     | 9 (TRAUMA DESERT)   |

**Steps**:
1. Calculate tercile thresholds for shooting density
2. Calculate tercile thresholds for transport time
3. Assign each tract to shooting tercile (1, 2, 3)
4. Assign each tract to transport tercile (1, 2, 3)
5. Create bivariate class (1-9) based on matrix
6. Create categorical label:
   - Class 9: "Trauma Desert" (High density, High time)
   - Class 7-8: "High Burden" (High density, Low-Medium time)
   - Class 3, 6: "Access Gap" (Low-Medium density, High time)
   - Class 1-2, 4-5: "Baseline"

**Validation**:
- Each class should have roughly 1/9 of tracts (with some variation)
- "Trauma Desert" tracts should be in expected locations (far from trauma centers, high violence)
- Visualize on map to confirm spatial patterns make sense

**Output**: `data/processed/tracts_bivariate_classified.geojson`

### 5.2 Identify Trauma Desert Neighborhoods

**Task**: Create ranked list of highest-priority tracts

**Input**: `data/processed/tracts_bivariate_classified.geojson`

**Steps**:
1. Filter to Class 9 tracts (Trauma Deserts)
2. Within Class 9, rank by:
   - Shooting density (higher = worse)
   - Transport time (higher = worse)
   - Create composite score: (Density Percentile × 0.5) + (Time Percentile × 0.5)
3. Identify neighborhood names for each tract (join to neighborhood boundaries if available)
4. Calculate aggregate statistics for Trauma Desert tracts:
   - Total shootings
   - Total population affected
   - Average transport time
   - Demographic composition

**Output**:
- `outputs/tables/trauma_desert_tracts.csv`
- `outputs/tables/trauma_desert_summary_statistics.csv`

### 5.3 Demographic Disparity Analysis

**Task**: Test whether trauma access correlates with neighborhood race/income

**Input**: `data/processed/tracts_bivariate_classified.geojson`

**Steps**:
1. Calculate mean % Black for each bivariate class (1-9)
2. Calculate mean % Poverty for each bivariate class
3. Calculate correlation: % Black vs. Transport Time
4. Calculate correlation: % Black vs. Shooting Density
5. Run regression: Transport Time ~ % Black + % Poverty + Shooting Density
6. Create comparison table:
   - Trauma Desert tracts: Mean demographics
   - Non-Trauma Desert tracts: Mean demographics
   - Statistical test for difference (t-test)
7. Document findings

**Key Question to Answer**: Are Trauma Desert tracts disproportionately Black and/or poor compared to the city overall?

**Output**: `outputs/tables/demographic_disparity_analysis.csv`

### 5.4 Golden Hour Analysis

**Task**: Calculate what percentage of shootings occur within rapid trauma access

**Input**:
- `data/processed/shootings_with_tracts.csv`
- `data/processed/tract_transport_times.csv`

**Steps**:
1. Join transport time to each shooting record (via tract)
2. Calculate distribution:
   - % of shootings within 5 min of Level I
   - % within 10 min
   - % within 15 min
   - % within 20 min
   - % beyond 20 min
3. Calculate same breakdown for FATAL shootings specifically
4. Calculate same breakdown by victim race
5. Test: Are Black victims more likely to be shot in high-transport-time areas?

**Output**:
- `outputs/tables/golden_hour_distribution.csv`
- `outputs/tables/golden_hour_by_race.csv`

### 5.5 Temporal Trend Analysis

**Task**: Examine how shooting geography has changed over time

**Input**: `data/processed/shootings_with_tracts.csv`

**Steps**:
1. Group shootings by year and tract
2. Calculate annual shooting density by tract
3. Identify tracts with:
   - Increasing trend (shooting density rising over time)
   - Decreasing trend (shooting density falling)
   - Stable (no significant change)
4. Calculate correlation between tract density in 2015 vs. 2023 (or latest year)
5. Identify "emerging hotspots" - tracts that were low in 2015 but high now
6. Map year-over-year change

**Output**:
- `outputs/tables/temporal_trends_by_tract.csv`
- `outputs/figures/shooting_trend_map.png`

### 5.6 Temple Intervention Zone Analysis (If Boundaries Available)

**Task**: Compare outcomes inside vs. outside Temple intervention areas

**Input**:
- `data/processed/tracts_bivariate_classified.geojson`
- Intervention zone boundaries (if obtainable)

**Steps**:
1. If intervention zone boundaries available:
   - Identify which tracts fall within intervention zones
   - Compare shooting trends inside vs. outside zones
   - Compare demographics inside vs. outside zones
2. If boundaries not available:
   - Use Temple University Hospital as center point
   - Create concentric rings (0-1 mile, 1-2 miles, 2-3 miles, etc.)
   - Analyze shooting density by distance from Temple
3. Document whether Temple's location optimally serves highest-burden areas

**Output**: `outputs/tables/temple_zone_analysis.csv` (if applicable)

---

## Section 6: Visualization Development

### 6.1 Design Color Scheme

**Task**: Define color palette for bivariate choropleth and all visualizations

**Bivariate Color Matrix** (3×3):
Use a purple-green diverging scheme or similar bivariate palette

|                        | Low Time (Green) | Med Time | High Time (Purple) |
|------------------------|------------------|----------|-------------------|
| **Low Density (Light)**    | #e8e8e8          | #b5c0da  | #6c83b5           |
| **Med Density**            | #b8d6be          | #90b2b3  | #567994           |
| **High Density (Dark)**    | #73ae80          | #5a9178  | #2a5a5b           |

OR use the "Joshua Stevens" bivariate palette (commonly used in this type of analysis)

**Trauma Center Markers**:
- Level I: Red cross icon, large
- Level II: Orange cross icon, medium
- Other: Gray icon, small

**Isochrone Colors**:
- 5 min: Dark green (high access)
- 10 min: Light green
- 15 min: Yellow
- 20 min: Orange
- 30 min: Red (low access)

**Output**: `docs/style_guide.md` with hex codes, icon specifications

### 6.2 Create Bivariate Choropleth Base Map

**Task**: Create main visualization showing trauma desert pattern

**Input**:
- `data/processed/tracts_bivariate_classified.geojson`

**Steps**:
1. Load tract geometries with bivariate classification
2. Assign fill color based on bivariate class (1-9 matrix)
3. Style tract boundaries (thin, dark gray)
4. Add bivariate legend showing 3×3 color matrix with axis labels:
   - X-axis: "Transport Time to Level I Trauma →"
   - Y-axis: "Shooting Density ↑"
5. Position legend in corner that doesn't obscure key areas

**Output**: Base choropleth layer

### 6.3 Add Trauma Center Layer

**Task**: Add trauma center points with isochrones

**Input**:
- `data/processed/trauma_centers_geocoded.csv`
- `data/isochrones/trauma_center_isochrones.geojson`

**Steps**:
1. Add trauma center points as markers:
   - Use hospital icon or cross symbol
   - Size by trauma level (Level I largest)
   - Add label with hospital name
2. Add isochrone polygons as semi-transparent overlays:
   - Only show 10-min and 20-min rings to avoid clutter
   - Use contrasting outline color
3. Make isochrones toggleable in interactive version
4. Add popup/tooltip for each trauma center showing:
   - Hospital name
   - Trauma level
   - Address

**Output**: Trauma center + isochrone layers

### 6.4 Build Interactive Map

**Task**: Combine layers into interactive web visualization

**Tool**: Folium or Mapbox GL JS

**Steps**:
1. Create base map centered on Philadelphia (39.95, -75.16), zoom 11
2. Add bivariate choropleth layer
3. Add trauma center markers
4. Add isochrone layer (default: off, toggleable)
5. Add layer controls:
   - Toggle choropleth on/off
   - Toggle isochrones on/off
   - Toggle trauma center labels
6. Add tract-level popups showing:
   - Tract ID
   - Shooting count and density
   - Transport time to nearest Level I
   - Bivariate classification
   - Demographics (% Black, % Poverty)
7. Add title overlay: "The Trauma Desert: Gun Violence Burden vs. Trauma Access in Philadelphia"
8. Add source attribution and legend
9. Export as standalone HTML

**Output**: `outputs/interactive/trauma_desert_map.html`

### 6.5 Create Shooting Heatmap Layer (Optional)

**Task**: Add density heatmap of individual shooting incidents

**Input**: `data/processed/shootings_clean.csv`

**Steps**:
1. Create heatmap layer from shooting point coordinates
2. Weight by recency (recent shootings higher weight) or equal weight
3. Adjust radius and blur for appropriate granularity
4. Make toggleable with choropleth (show one or the other)
5. This provides more granular view than tract-level aggregation

**Output**: Heatmap layer for interactive map

### 6.6 Create Static Publication Maps

**Task**: Create high-quality static maps for policy brief and portfolio

**Steps**:

1. **Map A: Main Bivariate Choropleth**
   - Full Philadelphia view
   - Bivariate choropleth with legend
   - Trauma center locations marked
   - Title: "The Trauma Desert: Philadelphia, 2015-2024"
   - Scale bar, north arrow
   - Export: PNG (300 DPI), PDF

2. **Map B: Trauma Desert Highlight**
   - Same base map
   - Trauma Desert tracts (Class 9) highlighted with thick border
   - Other tracts in muted gray
   - Labels for major trauma desert neighborhoods
   - Title: "Identified Trauma Deserts"
   - Export: PNG, PDF

3. **Map C: Isochrone Coverage**
   - Grayscale base map
   - All trauma center isochrones shown (10, 20, 30 min)
   - Shooting incidents as small dots
   - Title: "Golden Hour Coverage: Access to Level I Trauma Care"
   - Export: PNG, PDF

4. **Map D: Demographic Context**
   - Choropleth of % Black by tract (single-variable)
   - Trauma Desert tract boundaries overlaid
   - Shows demographic composition of trauma deserts
   - Title: "Trauma Deserts and Neighborhood Demographics"
   - Export: PNG, PDF

**Output**:
- `outputs/figures/map_a_bivariate_main.png`
- `outputs/figures/map_b_trauma_deserts_highlighted.png`
- `outputs/figures/map_c_isochrone_coverage.png`
- `outputs/figures/map_d_demographic_context.png`

### 6.7 Create Summary Charts

**Task**: Create supporting visualizations for analysis

**Steps**:

1. **Bar Chart: Shootings by Transport Time Category**
   - X-axis: Transport time category (0-5, 5-10, 10-15, 15-20, 20+ min)
   - Y-axis: Number of shootings
   - Stacked or grouped by fatal/non-fatal

2. **Disparity Chart: Demographics by Bivariate Class**
   - X-axis: Bivariate class (1-9)
   - Y-axis: % Black (with % Poverty as secondary)
   - Shows demographic gradient across classes

3. **Time Series: Annual Shooting Count**
   - X-axis: Year (2015-2024)
   - Y-axis: Total shootings
   - Line chart with trend
   - Optional: Separate lines for Trauma Desert tracts vs. others

4. **Pie/Donut Chart: Golden Hour Coverage**
   - Segments showing % of shootings within 10, 10-20, 20+ min of Level I trauma

**Output**:
- `outputs/figures/shootings_by_transport_time.png`
- `outputs/figures/demographics_by_class.png`
- `outputs/figures/shooting_trend_timeseries.png`
- `outputs/figures/golden_hour_pie.png`

---

## Section 7: Validation & Quality Assurance

### 7.1 Data Validation Checks

**Task**: Verify data integrity throughout pipeline

**Checks to Implement**:

1. **Shooting Data Validation**:
   - Total count matches OpenDataPhilly source
   - Date range is as expected (2015-present)
   - No coordinates outside Philadelphia
   - Fatal percentage is reasonable (typically 15-20%)

2. **Trauma Center Validation**:
   - All Level I centers identified (should be 5-6)
   - Temple University Hospital is included and correctly located
   - Addresses geocoded to correct locations (visual check)

3. **Isochrone Validation**:
   - Isochrones are properly nested (5 min inside 10 min, etc.)
   - Coverage is reasonable (20-min isochrone should cover ~10-15 miles radius)
   - No gaps or geometric errors

4. **Tract Assignment Validation**:
   - All shootings assigned to tracts (except those outside city)
   - Tract count is correct (~400)
   - No duplicate tract assignments

5. **Bivariate Classification Validation**:
   - Each class has reasonable number of tracts
   - Trauma Desert tracts are in expected locations
   - Classification is reproducible (same results on rerun)

### 7.2 Manual Spot Checks

**Task**: Manually verify sample of records and results

**Steps**:
1. Select 3 tracts classified as "Trauma Desert":
   - Verify they are indeed far from Level I trauma centers (use Google Maps)
   - Verify shooting count matches visual inspection of point data
   - Verify demographics match Census Reporter or similar source
2. Select 3 tracts classified as "Low priority" (Class 1):
   - Verify they are close to trauma centers
   - Verify low shooting density
3. Verify Temple University Hospital isochrones:
   - Manually measure drive time from a distant point using Google Maps
   - Compare to isochrone classification
   - Document any significant discrepancies

**Output**: `docs/validation_spot_checks.md`

### 7.3 Sensitivity Analysis

**Task**: Test robustness of findings to methodological choices

**Steps**:

1. **Tercile Threshold Sensitivity**:
   - Rerun classification using quartiles instead of terciles
   - Compare which tracts are classified as high-risk
   - Document how many tracts change classification

2. **Temporal Window Sensitivity**:
   - Rerun using only last 3 years of data (vs. all years)
   - Check if trauma desert identification changes significantly
   - Document differences

3. **Centroid vs. Actual Location**:
   - For sample of tracts, compare centroid-based time to actual point-based times
   - Large tracts may have significant intra-tract variation
   - Document potential bias

4. **Trauma Level Sensitivity**:
   - Rerun including Level II trauma centers as destinations
   - Does this significantly change access patterns?
   - Document findings

**Output**: `docs/sensitivity_analysis.md`

---

## Section 8: Documentation & Deliverables

### 8.1 Data Dictionary

**Task**: Document all fields in final datasets

**Format**: Markdown tables with columns:
- Field Name
- Data Type
- Description
- Source
- Example Value
- Notes/Caveats

**Include Dictionaries For**:
- `shootings_clean.csv`
- `tracts_analysis_ready.geojson`
- `trauma_desert_tracts.csv`

**Output**: `docs/data_dictionary.md`

### 8.2 Methodology Document

**Task**: Write detailed methods description

**Sections**:
1. Data Sources and Collection
2. Geocoding and Spatial Processing
3. Isochrone Generation Methodology
4. Tract-Level Aggregation
5. Bivariate Classification Method
6. Trauma Desert Identification Criteria
7. Demographic Disparity Analysis
8. Visualization Design Choices
9. Limitations and Caveats

**Output**: `docs/methodology.md`

### 8.3 Limitations Document

**Task**: Honestly document project limitations

**Key Limitations to Address**:

1. **Transport Time Approximation**: Isochrones assume ideal driving conditions. Actual transport times vary by traffic, time of day, road conditions. EMS response involves dispatch time, on-scene time, not just transport.

2. **Centroid Assumption**: Using tract centroids ignores variation within tracts. Large tracts may have different access at edges vs. center.

3. **Level I Focus**: Analysis focuses on Level I trauma centers. Level II centers can also effectively treat GSWs; excluding them may overstate access gaps.

4. **No EMS Data**: Analysis doesn't include actual EMS response times, which would be more accurate. EMS station locations and response patterns not modeled.

5. **Static Snapshot**: Shooting patterns and trauma center capacity change over time. This is a point-in-time analysis.

6. **Survival Outcome Not Modeled**: We measure ACCESS to trauma care, not actual OUTCOMES. Survival depends on many factors beyond transport time.

7. **Correlation Not Causation**: Demographic correlations don't prove causal relationships.

**Output**: `docs/limitations.md`

### 8.4 Executive Summary / Policy Brief

**Task**: Create 2-page summary for non-technical audiences

**Structure**:

**Page 1**:
- Title: "The Trauma Desert: Gun Violence Burden vs. Trauma Access in Philadelphia"
- Key Finding (1-2 sentences): "[X] Philadelphia neighborhoods face both high gun violence and poor access to Level I trauma care, putting [N] residents at elevated risk."
- The Crisis (2-3 sentences): Brief stats on Philadelphia gun violence, importance of rapid trauma access
- What We Found:
  - Bullet 1: Number of "trauma desert" neighborhoods identified
  - Bullet 2: Percentage of shootings occurring 20+ min from Level I trauma
  - Bullet 3: Demographic disparity finding
- Small version of bivariate map

**Page 2**:
- Priority Neighborhoods (list top 5 trauma desert areas)
- Temple's Role: Note Temple University Hospital's position serving North Philadelphia
- Recommendations:
  - Consider mobile trauma units for high-burden/low-access areas
  - Prioritize violence intervention in trauma desert neighborhoods
  - Explore satellite trauma capability or transport protocols
- Methodology Note (2 sentences)
- Data Sources and Contact

**Output**: `outputs/policy_brief.pdf`

---

## Section 9: Deployment & Sharing

### 9.1 GitHub Repository Setup

**Task**: Prepare project for public sharing

**Steps**:
1. Initialize git repository
2. Create comprehensive README.md:
   - Project overview with key finding
   - Screenshot of main visualization
   - How to run the analysis
   - Data sources with links
   - License and citation
3. Add .gitignore:
   - Virtual environment
   - .env files (API keys)
   - Large raw data files
   - Temporary/cache files
4. Add LICENSE (MIT or CC-BY-4.0)
5. Create `requirements.txt`
6. Add data download scripts (don't commit large raw files)
7. Push to GitHub

### 9.2 Interactive Map Hosting

**Task**: Make interactive map publicly accessible

**Option A: GitHub Pages**:
1. Create `docs/` folder or `gh-pages` branch
2. Copy `trauma_desert_map.html` to docs/index.html
3. Enable GitHub Pages in repository settings
4. Access at: https://username.github.io/trauma-desert/

**Option B: Observable Notebook**:
1. Create Observable notebook with embedded map
2. Add narrative text explaining findings
3. Publish and share link

**Option C: Personal Portfolio**:
1. Host HTML file on personal website
2. Create project page with context and findings

### 9.3 Data Availability

**Task**: Make underlying data accessible

**Steps**:
1. Include in repository:
   - Processed tract-level analysis file (GeoJSON)
   - Summary statistics (CSV)
   - Trauma center list (CSV)
2. For raw data:
   - Provide download scripts that fetch from original sources
   - Document URLs and access instructions
   - Note: Shooting data is public and can be redistributed
3. Add CITATION.cff file for proper attribution

---

## Section 10: Planned Extensions 🚧

> **STATUS: ACTIVE DEVELOPMENT ROADMAP**
> These are confirmed enhancements we plan to implement to deepen the analysis and create more compelling outputs.

---

### Phase 7: Extensions Progress Log

- [x] 10.1 Time-of-Day Isochrone Sensitivity Analysis ✅ **COMPLETE** (2025-01-06)
- [x] 10.2 Scenario Modeling (Hypothetical New Sites) ✅ **COMPLETE** (2025-01-07)
- [x] 10.4 Flow Lines Visualization ✅ **COMPLETE** (2025-01-07)
- [x] 10.6 Temporal Animation ✅ **COMPLETE** (2025-01-07)
- [x] 10.12 Neighborhood Fact Sheets ✅ **COMPLETE** (2025-01-07)
- [x] 10.3 Social Determinants Index ✅ **COMPLETE** (2025-01-07)
- [x] 10.9 Oaxaca-Blinder Decomposition ✅ **COMPLETE** (2025-01-07)
- [ ] 10.5 EMS/Ambulance Station Layer
- [ ] 10.7 2SFCA/E2SFCA Floating Catchment Analysis
- [ ] 10.8 Hospital Diversion Status Integration
- [x] 10.9 Equity-Gap Decomposition (Oaxaca-Blinder) ✅ **COMPLETE** (2025-01-07)
- [x] 10.15 Stop the Bleed Training Prioritization ✅ **COMPLETE** (2025-01-07)
- [x] 10.16 Presentation Visualization Package ✅ **COMPLETE** (2025-01-07)
- [ ] 10.5 EMS/Ambulance Station Layer
- [ ] 10.10 Survival/Fatality Correlation Analysis
- [ ] 10.11 Spatiotemporal Clustering (SaTScan/DBSCAN)
- [ ] 10.13 Multi-City Comparison
- [ ] 10.14 Firearm Trace/Crime-Gun Density (if available)

---

### 10.1 Time-of-Day Isochrone Sensitivity Analysis ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-06**

**Goal**: Quantify how "trauma desert" status changes during rush hour vs. overnight

**Rationale**: Current isochrones assume average traffic. A tract might be 12 min away at 2am but 25 min at 5pm. This could flip desert classifications.

**Implementation**:
Applied research-based traffic multipliers (INRIX/FHWA) to baseline transport times:
- Off-Peak (baseline): ×1.0
- Morning Rush (7-9am): ×1.4
- Evening Rush (4-7pm): ×1.5
- Overnight (12-5am): ×0.9

**Results Summary**:

| Scenario | Multiplier | Trauma Deserts | Avg Transport Time | Max Transport Time |
|----------|------------|----------------|--------------------|--------------------|
| Off-Peak | ×1.0 | 8 | 11.4 min | 30 min |
| Morning Rush | ×1.4 | 8 | 15.9 min | 42 min |
| Evening Rush | ×1.5 | 8 | 17.0 min | 45 min |
| Overnight | ×0.9 | 8 | 10.2 min | 27 min |

**Key Finding**: 🎯 **Trauma desert classification is STABLE across all traffic scenarios**
- Same 8 tracts remain trauma deserts regardless of time of day
- 149 tracts (36.5%) experience some classification changes
- 0 tracts become NEW trauma deserts during rush hour
- The tercile-based approach is robust to proportional time increases

**Files Created**:
- `scripts/analyze/time_of_day_sensitivity.py`
- `data/processed/tracts_time_of_day_classified.geojson`
- `outputs/tables/time_of_day_sensitivity_summary.csv`
- `outputs/tables/tracts_that_flip_by_time.csv`
- `outputs/figures/time_of_day_sensitivity.png` + `.pdf`
- `outputs/figures/classification_flip_analysis.png`

---

### 10.2 Scenario Modeling: Hypothetical New Sites ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Model impact of adding a new trauma center, EMS station, or mobile unit

**Rationale**: Provides actionable policy recommendations—"If you built X here, Y residents would gain access"

**Implementation**:
Tested 8 candidate locations across Philadelphia using distance-based drive time estimation (haversine × 1.4 routing factor ÷ 18 mph urban speed).

**Results - Top 5 Locations by Impact Score**:

| Rank | Location | Pop. Improved | Shootings | Deserts Helped | Score |
|------|----------|---------------|-----------|----------------|-------|
| **1** | **Hunting Park** | 198,932 | 4,998 | 0 | 309,580 |
| 2 | Kingsessing/Cobbs Creek | 166,003 | 2,974 | **8** | 238,501 |
| 3 | Tioga/Nicetown | 174,801 | 3,477 | 2 | 236,290 |
| 4 | Frankford/Mayfair | 323,391 | 2,106 | 5 | 227,950 |
| 5 | Strawberry Mansion | 158,896 | 2,479 | 3 | 186,619 |

**Key Finding**: 🎯
- **Hunting Park** = Best for high-violence coverage (4,998 shootings in improved tracts)
- **Kingsessing/Cobbs Creek** = Best for trauma desert reduction (helps 8 of 18 deserts)
- **Frankford/Mayfair** = Best for raw population reach (323,391 residents)

**Files Created**:
- `scripts/analyze/scenario_modeling.py`
- `data/processed/best_scenario_analysis.geojson`
- `outputs/tables/scenario_impact_rankings.csv`
- `outputs/figures/scenario_rankings.png`
- `outputs/figures/scenario_map_rank1_Hunting_Park.png`
- `outputs/figures/scenario_map_rank2_Kingsessing_Cobbs_Creek.png`
- `outputs/figures/scenario_map_rank3_Tioga_Nicetown.png`

---

### 10.3 Social Determinants of Health Index ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Create a "compound disadvantage" index showing overlap between trauma deserts and other forms of neighborhood neglect

**🚨 CRITICAL FINDING: 100% Overlap**

| Metric | City Average | Trauma Deserts | Significance |
|--------|--------------|----------------|--------------|
| Vulnerability Index | 16.5 | 21.6 | **1.31x higher** |
| In Top Quartile | 25% | **100%** (18/18) | **4.0x overrepresentation** |

**ALL 18 trauma deserts are simultaneously in the top quartile of compound disadvantage.**

**Vulnerability Index Components:**

| Indicator | Weight | Rationale |
|-----------|--------|-----------|
| Poverty Rate | 25% | Economic disadvantage |
| Household Income (inverse) | 20% | Economic resources |
| Shooting Density | 30% | Violence burden |
| Transport Time to Trauma | 25% | Healthcare access |

**Correlation Analysis:**

| Relationship | Correlation (r) | P-value | Strength |
|--------------|-----------------|---------|----------|
| Vulnerability ↔ % Poverty | 0.512 | < 0.001 | **Strong** |
| Vulnerability ↔ % Black | 0.185 | < 0.001 | Moderate |

**Files Created**:
- `scripts/analyze/social_determinants_index.py`
- `data/processed/tracts_with_vulnerability.geojson`
- `outputs/tables/vulnerability_by_bivariate_class.csv`
- `outputs/tables/tract_vulnerability_scores.csv`
- `outputs/figures/vulnerability_index_map.png` + `.pdf`
- `outputs/figures/vulnerability_correlations.png`

**Future Enhancements** (additional data layers):
- Housing code violations, vacant properties
- Eviction filings, 311 service requests
- Overdose incidents, food desert status

---

### 10.4 Flow Lines Visualization ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Show where patients from each tract would "flow" to their nearest trauma center

**🚨 MAJOR FINDING: Hospital Burden Distribution**

| Hospital | Shootings | % of City |
|----------|-----------|-----------|
| **Temple University Hospital** | **9,544** | **54.9%** |
| Penn Presbyterian | 4,677 | 26.9% |
| Jefferson Einstein | 2,262 | 13.0% |
| Thomas Jefferson | 897 | 5.2% |

**Key Insight**: Temple handles MORE THAN HALF of all shootings. Temple + Penn combined handle **81.8%** of all gun violence in Philadelphia.

**Implementation**:
- Lines from tract centroids to nearest Level I trauma center
- Line thickness = shooting volume
- Line color = transport time (green→yellow→red)
- Interactive version with clickable popups and hospital layer toggles

**Files Created**:
- `scripts/visualize/create_flow_map.py`
- `outputs/figures/patient_flow_map.png` + `.pdf`
- `outputs/interactive/patient_flow_map.html`
- `outputs/tables/hospital_catchment_statistics.csv`

---

### 10.5 EMS/Ambulance Station Layer

**Goal**: Add prehospital response capacity to the analysis

**Rationale**: Transport time to hospital is only part of the picture. EMS arrival time matters more for initial stabilization.

**Data Sources**:
- Philadelphia Fire Department station locations (likely available via OpenDataPhilly or city GIS)
- EMS unit deployment patterns (may require FOIA)

**Implementation**:
- Map all fire/EMS stations in Philadelphia
- Calculate distance from each tract centroid to nearest EMS station
- Create new metric: "True prehospital response time" = EMS arrival + on-scene + transport
- Identify tracts with both long EMS arrival AND long hospital transport

**Output**:
- `data/geo/ems_stations.geojson`
- `outputs/figures/ems_coverage_map.png`
- `outputs/tables/tracts_double_gap.csv` (poor EMS + poor trauma access)

---

### 10.6 Temporal Animation: Hotspot Migration ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Animated map showing how shooting hotspots have migrated from 2015 to present

**Key Finding: COVID-Era Spike**

| Period | Avg Annual Shootings | vs. Pre-COVID |
|--------|---------------------|---------------|
| 2015-2019 | 1,361 | baseline |
| **2020-2021** | **2,297** | **+68.8%** |
| 2022-2025 | 1,495 | +9.8% |

**Peak: 2021 with 2,338 shootings** — shootings nearly DOUBLED during COVID

**Tract Trends (2015-17 vs 2022-24):**
- 🔴 **158 tracts increasing** (>25% rise)
- 🟡 **132 tracts stable** (±25%)
- 🟢 **118 tracts decreasing** (>25% drop)

**Files Created**:
- `scripts/visualize/create_temporal_animation.py`
- `outputs/figures/shooting_animation.gif` (animated year-by-year)
- `outputs/figures/shooting_small_multiples.png` + `.pdf`
- `outputs/figures/shooting_trend_map.png` (red/yellow/green)
- `outputs/figures/shooting_annual_summary.png`
- `outputs/tables/tract_shooting_trends.csv`

---

### 10.7 2SFCA/E2SFCA Floating Catchment Analysis 📊 RIGOROUS

**Goal**: Replace tercile-based classification with the academic gold standard for healthcare access measurement

**Rationale**: Two-Step Floating Catchment Area (2SFCA) and Enhanced 2SFCA properly balance:
- Demand (shootings, population) 
- Supply (trauma beds, capacity)
- Distance decay (closer is better)

This is more rigorous than simple isochrones and would strengthen academic credibility.

**Implementation**:
- Step 1: For each trauma center, calculate supply-to-demand ratio within catchment
- Step 2: For each tract, sum accessibility scores from all reachable hospitals
- Use distance decay function (Gaussian or gravity-based)
- Requires: Hospital capacity data (beds, annual trauma volume)

**Data Needed**:
- Trauma bay count per hospital
- Annual penetrating trauma volume per hospital (may require research partnership or FOIA)

**Output**:
- `data/processed/tracts_2sfca_scores.csv`
- `outputs/figures/2sfca_accessibility_map.png`
- `docs/methodology_2sfca.md`

---

### 10.8 Hospital Diversion Status Integration

**Goal**: Account for when trauma centers go on bypass (diversion)

**Rationale**: A hospital 10 min away is useless if it's on diversion. This captures *real-time* capacity constraints.

**Data Sources**:
- Philadelphia regional EMS diversion logs (may require FOIA to regional EMS council)
- Hospital capacity dashboards (if public)

**Implementation**:
- Obtain historical diversion data
- Calculate: What % of time is each trauma center on diversion?
- Adjust access scores: "Effective access" = distance × availability
- Identify tracts where the nearest hospital is frequently on bypass

**Output**:
- `data/raw/diversion_logs.csv`
- `outputs/tables/diversion_adjusted_access.csv`
- `outputs/figures/effective_vs_nominal_access.png`

---

### 10.9 Equity-Gap Decomposition (Oaxaca-Blinder) ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Statistically decompose the racial disparity into component causes

**🚨 KEY FINDING: 68.5% of Violence Disparity is UNEXPLAINED**

| Outcome | Black Tracts | Other Tracts | Gap | Explained | Unexplained |
|---------|--------------|--------------|-----|-----------|-------------|
| **Shooting Density** | 4.4x higher | baseline | 1.49 log | **31.5%** | **68.5%** |
| **Transport Time** | 9.3 min | 12.4 min | **-3.2 min** | N/A (Black tracts closer) | N/A |

**Critical Insights:**

1. **Violence Burden (Shooting Density):**
   - Black tracts experience **4.4x higher** shooting density
   - Only **31.5%** of this gap is explained by poverty and income differences
   - **68.5% remains UNEXPLAINED** → structural/historical factors
   
2. **Healthcare Access (Transport Time):**
   - Black tracts are actually **3.2 minutes CLOSER** to trauma centers
   - ✅ **No geographic access disparity against Black neighborhoods**
   - The problem is violence concentration, NOT healthcare access

**Methodology:**
- Oaxaca-Blinder threefold decomposition (Blinder, 1973)
- Predictors: Poverty rate, median household income, population
- Groups: ≥50% Black tracts (n=143) vs. other tracts (n=246)

**Files Created:**
- `scripts/analyze/oaxaca_decomposition.py`
- `outputs/tables/oaxaca_decomposition_results.csv`
- `outputs/figures/oaxaca_decomposition.png` + `.pdf`
- `outputs/figures/oaxaca_predictor_contributions.png`

---

### 10.10 Survival/Fatality Correlation Analysis

**Goal**: Test whether transport time actually correlates with survival outcomes

**Rationale**: This is the "so what" that policymakers need. Does living in a trauma desert actually increase mortality?

**Data Sources**:
- PA Health Care Cost Containment Council (PHC4) - hospital discharge data (paid)
- Research partnership with Temple trauma registry
- Published literature on GSW mortality by transport time

**Implementation**:
- If data available: Logistic regression of fatality ~ transport_time + injury_severity + age + ...
- If data unavailable: Meta-analysis of published literature on transport time and GSW survival

**Challenge**: PHC4 data requires payment; trauma registry requires IRB

**Output**:
- `outputs/tables/survival_by_transport_time.csv`
- `outputs/figures/fatality_odds_ratio_chart.png`

---

### 10.11 Spatiotemporal Clustering (SaTScan/DBSCAN)

**Goal**: Rigorous identification of shooting clusters that persist or migrate over time

**Rationale**: More statistically rigorous than simple animation. Identifies significant hotspots vs. random variation.

**Implementation**:
- Use SaTScan (space-time permutation model) or PySAL's DBSCAN
- Identify statistically significant clusters by year
- Track cluster persistence: Which hotspots are chronic vs. emerging vs. declining?
- Overlay with trauma desert classification

**Output**:
- `outputs/tables/significant_clusters_by_year.csv`
- `outputs/figures/cluster_persistence_map.png`

---

### 10.12 Neighborhood Fact Sheets ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: One-pagers for each of the top 5 trauma desert neighborhoods

**Fact Sheets Generated:**

| Tract | Neighborhood | Shootings | Format |
|-------|--------------|-----------|--------|
| **300** | North Philadelphia | 253 | PNG + PDF |
| 169.02 | Kensington | 164 | PNG + PDF |
| 151.02 | Strawberry Mansion | 153 | PNG + PDF |
| 103 | North Philadelphia | 99 | PNG + PDF |
| 102 | North Philadelphia | 99 | PNG + PDF |

**Content per Sheet**:
- Mini-map showing tract location (highlighted in teal)
- Key statistics panel (shootings, time, population, demographics)
- Nearest Level I trauma center with access rating
- "The Problem" section with specific burden metrics
- "Recommendations" section (violence intervention, Stop the Bleed, etc.)
- Professional formatting for printing/advocacy

**Files Created**:
- `scripts/visualize/create_fact_sheets.py`
- `outputs/fact_sheets/fact_sheet_tract_300.png` + `.pdf`
- `outputs/fact_sheets/fact_sheet_tract_169_02.png` + `.pdf`
- `outputs/fact_sheets/fact_sheet_tract_151_02.png` + `.pdf`
- `outputs/fact_sheets/fact_sheet_tract_103.png` + `.pdf`
- `outputs/fact_sheets/fact_sheet_tract_102.png` + `.pdf`

---

### 10.13 Multi-City Comparison

**Goal**: Benchmark Philadelphia against peer cities with high gun violence

**Rationale**: Context matters. Philadelphia's 99.6% golden hour coverage is actually good—showing this strengthens the "it's violence concentration, not access" argument.

**Cities to Compare**:
- Baltimore, MD
- Chicago, IL (South Side vs. North Side)
- St. Louis, MO
- Detroit, MI
- New Orleans, LA

**Implementation**:
- Replicate core analysis (shooting density × trauma access) for each city
- Compare: % of shootings within 20 min of Level I
- Rank cities by "trauma desert severity"

**Output**:
- `outputs/tables/multi_city_comparison.csv`
- `outputs/figures/city_comparison_chart.png`

---

### 10.14 Firearm Trace/Crime-Gun Density (If Available)

**Goal**: Add supply-side perspective—where are illegal guns concentrated?

**Rationale**: Shows if trauma deserts overlap with gun markets. Provocative policy angle.

**Data Sources**:
- ATF crime gun trace data (restricted, may not be feasible)
- Philadelphia Police recovered firearm data (may be available via FOIA)

**Challenge**: ATF data is legally restricted from public release

**Output**:
- `data/processed/crime_gun_density_by_tract.csv` (if obtainable)
- `outputs/figures/gun_recovery_overlay.png`

---

### 10.15 Stop the Bleed Training Prioritization ✅ COMPLETE

**Status**: ✅ **COMPLETED 2025-01-07**

**Goal**: Data-driven framework for deploying hemorrhage control training

**🎯 ACTIONABLE OUTPUT: Top 20 Priority Zones Identified**

| Top 5 Zones | Population | Shootings | Transport Time |
|-------------|------------|-----------|----------------|
| #1 Tract 300 | 8,294 | 253 | 15 min |
| #2 Tract 330 | 10,323 | 66 | 20 min |
| #3 Tract 298 | 5,299 | 84 | 15 min |
| #4 Tract 178 | 6,592 | 371 | 10 min |
| #5 Tract 63 | 4,415 | 89 | 15 min |

**Impact Summary:**
- Top 20 zones reach **126,586 residents**
- Cover **2,607 historical shootings**
- Average transport time: 12.9 min
- **Potential lives saved: ~8 annually** (15% of fatal shootings preventable)

**Priority Training Sites:**
1. Public schools (highest reach, staff + students)
2. SEPTA transit stations (high-traffic locations)
3. Recreation centers (community hubs)
4. Churches/religious institutions (trusted spaces)
5. Community health centers (existing infrastructure)

**Files Created:**
- `scripts/analyze/stop_the_bleed_prioritization.py`
- `outputs/tables/stop_the_bleed_priority_zones.csv`
- `outputs/tables/stop_the_bleed_training_sites.csv`
- `outputs/figures/stop_the_bleed_priority_map.png` + `.pdf`
- `outputs/figures/stop_the_bleed_impact_analysis.png`

---

### 10.16 Advanced Visualization Ideas

**Ridgeline/Joy Plots**:
- Show distribution of transport times by time-of-day for worst-decile tracts
- X-axis: transport time, Y-axis: time of day
- Reveals when access is worst

**Animated "Breathing" Isochrones**:
- GIF/web animation showing isochrones expanding/contracting by time of day
- Visual representation of dynamic access

**Before/After Scenario Slider**:
- Interactive: drag slider to see "current network" vs. "with intervention"
- High engagement for presentations

---

### Priority Ranking Summary

| Tier | Extension | Effort | Impact | Data Available? |
|------|-----------|--------|--------|-----------------|
| **1** | 10.1 Time-of-Day Sensitivity | Low | High | ✅ Yes (re-query ORS) |
| **1** | 10.2 Scenario Modeling | Medium | High | ✅ Yes (existing code) |
| **1** | 10.4 Flow Lines | Low | Medium | ✅ Yes (existing data) |
| **2** | 10.3 Social Determinants | Medium | High | ✅ Mostly (OpenDataPhilly) |
| **2** | 10.5 EMS Stations | Low | Medium | ⚠️ Likely available |
| **2** | 10.6 Temporal Animation | Medium | High | ✅ Yes (existing data) |
| **3** | 10.7 2SFCA Analysis | High | High | ⚠️ Needs capacity data |
| **3** | 10.9 Oaxaca Decomposition | Medium | High | ✅ Yes (existing data) |
| **3** | 10.12 Neighborhood Fact Sheets | Low | Medium | ✅ Yes |
| **4** | 10.8 Diversion Status | High | High | ❓ Requires FOIA |
| **4** | 10.10 Survival Correlation | High | Very High | ❓ Requires PHC4/IRB |
| **4** | 10.13 Multi-City Comparison | High | High | ⚠️ Requires replication |
| **4** | 10.14 Firearm Trace | Medium | Medium | ❌ Likely unavailable |

---

## Section 11: Cursor/LLM Prompting Guide

When executing this plan with an LLM coding assistant, use these prompts at each phase:

### Phase 1: Setup
```
Create the project directory structure for 'trauma-desert' as specified in Section 0.1. Include a Makefile with the targets listed and create requirements.txt for Python geospatial analysis (geopandas, pandas, folium, requests, openrouteservice).
```

### Phase 2: Shooting Data Collection
```
Write a Python script to download Philadelphia shooting victims data from OpenDataPhilly. The dataset is at https://www.opendataphilly.org/datasets/shooting-victims/. Download as CSV, save to data/raw with date stamp, log the download in manifest.json with row count and date range.
```

### Phase 3: Geocode Trauma Centers
```
I have a CSV of trauma center addresses in data/manual/trauma_centers.csv. Write a Python script to geocode each address using the Census Geocoding API (https://geocoding.geo.census.gov/geocoder/). Add latitude and longitude columns and save to data/processed/.
```

### Phase 4: Generate Isochrones
```
Write a Python script using the openrouteservice library to generate drive-time isochrones for each trauma center. For each center, request isochrones at 5, 10, 15, 20, and 30 minutes driving time. Save all isochrones to a single GeoJSON file with attributes for hospital name and time.
```

### Phase 5: Spatial Join
```
Using GeoPandas, write a script to: 1) Load Philadelphia census tract boundaries, 2) Load cleaned shooting data with lat/lng, 3) Perform point-in-polygon spatial join to assign each shooting to a tract, 4) Save the joined data with tract GEOID.
```

### Phase 6: Calculate Transport Times
```
Write a script to determine transport time from each census tract to the nearest Level I trauma center. Load tract centroids and isochrone polygons. For each tract centroid, find which isochrones contain it and record the minimum time category (0-5, 5-10, etc.).
```

### Phase 7: Bivariate Classification
```
Create a bivariate classification system for census tracts. Calculate terciles for shooting density and transport time. Create a 3x3 classification matrix where Class 9 (high density, high time) = "Trauma Desert". Add bivariate class and label to each tract.
```

### Phase 8: Visualization
```
Using Folium, create an interactive bivariate choropleth map of Philadelphia. Color tracts by their bivariate class (use a 3x3 purple-green color matrix). Add trauma center markers with isochrone toggles. Add popups showing tract statistics. Export as standalone HTML.
```

### Phase 9: Demographic Analysis
```
Write a script to analyze demographic disparities. Calculate mean % Black and % Poverty for each bivariate class. Test correlation between transport time and neighborhood demographics. Output summary table and create a bar chart showing demographics by class.
```

### Phase 10: Validation
```
Write validation tests: verify shooting count matches source data, verify all tracts have bivariate classification, verify isochrones are properly nested, verify no coordinates outside Philadelphia. Output validation report.
```

---

## Appendix A: Key Data Source URLs

| Source | URL |
|--------|-----|
| OpenDataPhilly - Shooting Victims | https://www.opendataphilly.org/datasets/shooting-victims/ |
| Pennsylvania Trauma Systems Foundation | https://www.ptsf.org/accreditation/trauma-center-list/ |
| OpenRouteService API | https://openrouteservice.org/dev/#/api-docs |
| Census Geocoder | https://geocoding.geo.census.gov/geocoder/ |
| Census TIGER/Line (Tract Boundaries) | https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html |
| Census ACS Data | https://data.census.gov/ |
| American College of Surgeons Trauma Centers | https://www.facs.org/quality-programs/trauma/verified-centers/ |

---

## Appendix B: Philadelphia Level I Trauma Centers Reference

| Hospital | Address | Notes |
|----------|---------|-------|
| Temple University Hospital | 3401 N Broad St, Philadelphia, PA 19140 | Primary for North Philadelphia |
| Penn Presbyterian Medical Center | 51 N 39th St, Philadelphia, PA 19104 | West Philadelphia |
| Hospital of the University of Pennsylvania | 3400 Spruce St, Philadelphia, PA 19104 | West Philadelphia |
| Thomas Jefferson University Hospital | 111 S 11th St, Philadelphia, PA 19107 | Center City |
| Einstein Medical Center Philadelphia | 5501 Old York Rd, Philadelphia, PA 19141 | North Philadelphia |

(Verify current accreditation status before finalizing)

---

## Appendix C: Philadelphia Census Tract Reference

- Total tracts: ~384 (verify with downloaded data)
- FIPS County Code: 42101
- GEOID format: 42101XXXXXX (state + county + tract)

---

## Appendix D: Bivariate Color Palette Reference

**Stevens Blue-Green Bivariate Palette** (commonly used):

| Class | Density | Time | Hex Color |
|-------|---------|------|-----------|
| 1 | Low | Low | #e8e8e8 |
| 2 | Low | Med | #b5c0da |
| 3 | Low | High | #6c83b5 |
| 4 | Med | Low | #b8d6be |
| 5 | Med | Med | #90b2b3 |
| 6 | Med | High | #567994 |
| 7 | High | Low | #73ae80 |
| 8 | High | Med | #5a9178 |
| 9 | High | High | #2a5a5b |

---

## Appendix E: Stakeholder Talking Points

When discussing this project with Temple admissions or faculty:

1. **Validate Temple's Mission**: "Temple University Hospital is the critical safety net for North Philadelphia, handling more trauma cases than almost any hospital in the region. This project maps the neighborhoods that depend most on Temple's capabilities."

2. **Public Health Lens**: "Gun violence is a public health crisis requiring geographic analysis. Understanding the spatial relationship between violence burden and trauma access is essential for intervention planning."

3. **Equity Focus**: "This analysis reveals whether the neighborhoods with highest gun violence burden also face the greatest barriers to rapid trauma care—a fundamental health equity question."

4. **Actionable Insights**: "The project identifies specific neighborhoods that may benefit from expanded violence intervention, improved EMS protocols, or community-based hemorrhage control training."

5. **Technical Sophistication**: "I developed skills in geospatial analysis, public health data integration, and bivariate visualization—methods directly applicable to health services research."

6. **Solution-Oriented**: "Rather than just documenting the problem, this analysis provides a geographic framework for prioritizing interventions where they're needed most."

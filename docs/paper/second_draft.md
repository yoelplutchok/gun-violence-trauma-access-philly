# The Trauma Desert: Spatial Mismatch Between Gun Violence Burden and Level I Trauma Access in Philadelphia

**Yoel Y. Plutchok**

---

## Abstract

**Background:** The "golden hour" principle in trauma care asserts that survival rates for penetrating injuries decrease substantially with delays in definitive surgical intervention. This study investigates whether Philadelphia neighborhoods with the highest gun violence burden encounter systematic barriers to timely Level I trauma care, resulting in "trauma deserts" that exacerbate existing health disparities.

**Methods:** A total of 17,380 shooting incidents in Philadelphia (2015-2025) were analyzed using bivariate classification of shooting density and modeled transport time to the nearest Level I Adult trauma center. Drive-time isochrones were generated via the OpenRouteService API. Trauma desert tracts (high violence burden and poor access) were identified, their demographics characterized, and the association between transport time and fatality was tested using logistic regression.

**Results:** Eighteen census tracts (4.4% of the city) were identified as trauma deserts, encompassing 83,159 residents who experienced 1,659 shootings (9.5% of total). Notably, 99.6% of all shootings occurred within 20 minutes of Level I trauma care. Predominantly Black tracts were, on average, 3.2 minutes closer to trauma centers but experienced a 4.4-fold higher shooting density. Oaxaca-Blinder decomposition indicated that 68.5% of this disparity is unexplained by observable socioeconomic factors. Fatality rates increased from 20.0% in areas 0-5 minutes from trauma care to 30.6% in areas 20+ minutes away (OR=1.015 per minute, 95% CI: 1.005-1.025, p=0.005).

**Conclusions:** The "trauma desert" phenomenon in Philadelphia is primarily driven by the extreme concentration of gun violence rather than by geographic access barriers. Although transport time significantly affects mortality, the disparity in trauma burden, rather than distance to care, constitutes the primary equity concern. Interventions should prioritize violence prevention in affected neighborhoods and expand community-based hemorrhage control training.

**Keywords:** trauma systems, gun violence, health disparities, geographic access, golden hour, penetrating trauma, Philadelphia

---

## Introduction

### The Golden Hour and Trauma Care Access

The concept of the "golden hour" has guided trauma system development since its articulation by R. Adams Cowley in the 1970s. For penetrating trauma such as gunshot wounds, the critical window may be even narrower—the first 10-20 minutes are essential for hemorrhage control and definitive surgical intervention (Newgard et al., 2010). Level I trauma centers provide the highest capability for treating severe injuries, with 24/7 surgical coverage, comprehensive resources, and specialized teams (American College of Surgeons, 2022).

Geographic access to trauma care has emerged as a significant determinant of outcomes. Wandling et al. (2016) demonstrated that access to Level I trauma centers within 60 minutes significantly reduces mortality for severely injured patients. Brown et al. (2016) found that patients transported directly to Level I trauma centers had substantially lower mortality than those taken to non-trauma facilities, even after controlling for injury severity.

### Gun Violence as a Public Health Crisis

Philadelphia experiences among the highest rates of gun violence of any major American city. Between 2015 and 2025, the city recorded over 17,000 shooting incidents, with a pronounced spike during 2020-2021 when annual shootings nearly doubled from pre-pandemic levels. Gun violence is not distributed randomly across the city—it is heavily concentrated in specific neighborhoods that also experience other forms of structural disadvantage.

### Research Question

This study addresses whether a spatial mismatch exists between gun violence burden and timely access to Level I trauma care in Philadelphia, and whether this mismatch disproportionately affects predominantly Black and low-income communities.

This analysis operationalizes the concept of "trauma deserts" as census tracts that simultaneously experience high shooting density and extended transport times to Level I trauma centers.

---

## Methods

### Study Design and Setting

A retrospective geospatial analysis of shooting incidents in Philadelphia, Pennsylvania was conducted for the period January 1, 2015 through December 31, 2025. Philadelphia is a densely populated urban center (population 1.59 million) served by four Level I Adult trauma centers, two Level I Pediatric centers, and one Level II Adult trauma center.

### Data Sources

#### Shooting Incident Data

Shooting victim data were obtained from OpenDataPhilly, the City of Philadelphia's open data portal. The dataset includes all reported shooting incidents with geocoded coordinates, victim demographics (age, sex, race), wound location, and fatality status. After exclusion of 27 records with invalid coordinates, the analysis dataset comprised 17,383 shooting incidents.

#### Trauma Center Locations

Level I and Level II trauma centers were identified from the Pennsylvania Trauma Systems Foundation (PTSF) accreditation registry and verified against the American College of Surgeons trauma center verification database. The four Level I Adult trauma centers are:

- Temple University Hospital (North Philadelphia)
- Penn Presbyterian Medical Center (West Philadelphia)
- Thomas Jefferson University Hospital (Center City)
- Jefferson Einstein Philadelphia Hospital (North Philadelphia)

#### Drive-Time Isochrones

Travel time polygons were generated using the OpenRouteService API with a driving-car profile. For each Level I Adult trauma center, isochrones were computed at 5, 10, 15, 20, and 30 minute intervals to represent the geographic area reachable within each time threshold.

#### Census Geography and Demographics

Census tract boundaries (n=408) and demographic data were obtained from the U.S. Census Bureau American Community Survey 5-year estimates, including population, racial composition, median household income, and poverty rates.

### Spatial Analysis

Each shooting incident was assigned to a census tract using point-in-polygon spatial join (17,380 of 17,383 records successfully assigned). Transport time to the nearest Level I Adult trauma center was determined by identifying which isochrones contained each tract centroid, yielding categorical time estimates (0-5, 5-10, 10-15, 15-20, 20-30, 30+ minutes).

Shooting density was calculated as the total number of shootings per square mile per year for each tract, standardized for tract size and the 11-year study duration.

### Bivariate Classification

A 3×3 bivariate classification matrix was employed, combining shooting density terciles and transport time terciles (Table 1). "Trauma deserts" were defined as Class 9 tracts, representing those in the highest tercile for both shooting density and transport time.

**Table 1.** Bivariate Classification Matrix

|                          | Good Access (T1) | Moderate Access (T2) | Poor Access (T3) |
|--------------------------|:----------------:|:--------------------:|:----------------:|
| **Low Violence (D1)**    | Class 1          | Class 2              | Class 3          |
| **Moderate Violence (D2)**| Class 4         | Class 5              | Class 6          |
| **High Violence (D3)**   | Class 7          | Class 8              | **Class 9 (Trauma Desert)** |

### Statistical Analysis

Demographic comparisons between trauma desert and non-trauma desert tracts were conducted using Welch's t-test. The association between transport time and fatality was assessed using chi-square tests for categorical analysis and logistic regression for continuous estimation of odds ratios.

Oaxaca-Blinder decomposition was applied to quantify racial disparities, with tracts categorized as predominantly Black (≥50% Black population, n=143) or other tracts (n=246). Shooting density was log-transformed for the decomposition. All analyses used α=0.05 as the threshold for statistical significance.

### Ethical Considerations

This study utilized publicly available, de-identified administrative data and did not require IRB approval.

---

## Results

### Trauma Desert Identification

The bivariate classification identified 18 census tracts (4.4% of the city) as trauma deserts (Table 2). These tracts contain 83,159 residents (5.2% of the city population) and experienced 1,659 shootings during the study period (9.5% of total shootings).

**Table 2.** Trauma Desert Summary Statistics

| Metric | Value |
|--------|-------|
| Total trauma desert tracts | 18 of 408 (4.4%) |
| Population in trauma deserts | 83,159 (5.2% of city) |
| Shootings in trauma deserts | 1,659 (9.5% of total) |
| Average transport time (trauma deserts) | 12.5 minutes |
| Average transport time (other tracts) | 11.3 minutes |

The trauma deserts are concentrated in three geographic clusters: far North Philadelphia, Southwest Philadelphia, and portions of West Philadelphia distant from Penn Presbyterian Medical Center.

![Figure 1: Bivariate Choropleth Map](../figures/bivariate_map.png)

*Figure 1. Bivariate choropleth map of Philadelphia showing shooting density (vertical axis) versus transport time to Level I trauma (horizontal axis). Dark teal indicates trauma deserts (Class 9). Red markers indicate Level I Adult trauma center locations.*

### Golden Hour Coverage

Despite identifying trauma desert tracts, Philadelphia's overall geographic coverage is excellent. 99.6% of shootings with tract assignment occurred within 20 minutes of a Level I trauma center (Table 3).

**Table 3.** Distribution of Shootings by Transport Time

| Transport Time | Shootings | Percentage | Cumulative |
|----------------|-----------|------------|------------|
| 0-5 minutes    | 6,319     | 36.4%      | 36.4%      |
| 5-10 minutes   | 9,405     | 54.1%      | 90.5%      |
| 10-15 minutes  | 1,334     | 7.7%       | 98.2%      |
| 15-20 minutes  | 260       | 1.5%       | 99.6%      |
| 20+ minutes    | 62        | 0.4%       | 100.0%     |

Over 90% of shootings occur within 10 minutes of Level I trauma care, suggesting that geographic access is not the primary barrier to timely treatment.

### Transport Time and Fatality Outcomes

To validate the clinical relevance of transport time in this context, we analyzed the association between modeled transport time and shooting fatality (Table 4).

**Table 4.** Fatality Rate by Transport Time Category

| Transport Time | Fatal | Total | Fatality Rate |
|----------------|-------|-------|---------------|
| 0-5 minutes    | 1,263 | 6,319 | 20.0%         |
| 5-10 minutes   | 1,952 | 9,405 | 20.8%         |
| 10-15 minutes  | 285   | 1,334 | 21.4%         |
| 15-20 minutes  | 69    | 260   | 26.5%         |
| 20+ minutes    | 19    | 62    | **30.6%**     |

Fatality rate increased monotonically from 20.0% in areas closest to trauma care to 30.6% in areas 20 or more minutes away, representing an absolute difference of 10.7 percentage points. This association was statistically significant:

- **Chi-square test:** χ² = 11.46, df = 4, p = 0.022
- **Logistic regression:** OR = 1.015 per minute (95% CI: 1.005-1.025, p = 0.005)

Each additional minute of transport time was associated with a 1.5% increase in the odds of fatality.

![Figure 2: Fatality by Transport Time](../figures/fatality_transport_analysis.png)

*Figure 2. Shooting fatality rate by transport time category to nearest Level I trauma center. Left: Fatality rate increases monotonically with transport time. Right: Absolute counts of fatal and non-fatal shootings by category.*

### Demographic Disparities

Trauma deserts are disproportionately situated in predominantly Black and high-poverty neighborhoods (Table 5).

**Table 5.** Demographic Comparison: Trauma Deserts vs. Other Tracts

| Metric | Trauma Deserts | Other Tracts | t-statistic | p-value |
|--------|----------------|--------------|-------------|---------|
| Mean % Black | 76.0% | 38.3% | 4.77 | <0.0001 |
| Mean % Poverty | 30.8% | 21.8% | 2.62 | <0.001 |

A counterintuitive finding emerges in the citywide analysis: predominantly Black neighborhoods are, on average, closer to Level I trauma centers. The correlation between percent Black population and transport time is negative (r = -0.25, p < 0.0001).

This paradox is explained by Philadelphia's geography: the Level I trauma centers are located in or near predominantly Black neighborhoods (Temple in North Philadelphia, Einstein in North Philadelphia, Penn Presbyterian in West Philadelphia), resulting in shorter transport times for these communities.

### Oaxaca-Blinder Decomposition

To rigorously quantify the racial disparity in violence burden, we applied Oaxaca-Blinder decomposition (Table 6).

**Table 6.** Oaxaca-Blinder Decomposition Results

| Outcome | Black Tracts | Other Tracts | Gap | % Explained | % Unexplained |
|---------|--------------|--------------|-----|-------------|---------------|
| Shooting Density (log) | 3.22 | 1.72 | 1.49 | 31.5% | **68.5%** |
| Transport Time (min) | 9.3 | 12.4 | -3.2 | — | — |

Predominantly Black tracts experience a 4.4-fold higher shooting density (geometric mean ratio). Only 31.5% of this disparity is explained by differences in poverty rates and median household income. The remaining 68.5% of the gap is unexplained and likely attributable to structural and historical factors not captured by current socioeconomic indicators.

Regarding transport time, Black tracts are 3.2 minutes closer to Level I trauma centers, confirming that geographic access is not the mechanism of disparity.

![Figure 3: Oaxaca-Blinder Decomposition](../figures/oaxaca_decomposition.png)

*Figure 3. Oaxaca-Blinder decomposition of the shooting density gap between predominantly Black and other tracts. The majority of the disparity (68.5%) is unexplained by observable socioeconomic characteristics.*

### Hospital Burden Distribution

Using nearest-center assignment based on isochrone containment, we modeled the distribution of trauma burden across Level I centers (Table 7).

**Table 7.** Modeled Hospital Catchment and Burden

| Hospital | Tracts Served | Shootings in Catchment | % of City |
|----------|---------------|------------------------|-----------|
| Temple University Hospital | 168 | 9,544 | **54.9%** |
| Penn Presbyterian Medical Center | 95 | 4,677 | 26.9% |
| Jefferson Einstein Philadelphia | 83 | 2,262 | 13.0% |
| Thomas Jefferson University | 62 | 897 | 5.2% |

The catchment area of Temple University Hospital contains over half of all shootings in the city. Combined, Temple and Penn Presbyterian serve catchment areas that account for 81.8% of shootings.

![Figure 4: Patient Flow Map](../figures/patient_flow_map.png)

*Figure 4. Modeled patient flow from census tract centroids to nearest Level I trauma center. Line thickness proportional to shooting count; color indicates transport time.*

### Temporal Patterns

Shooting incidence exhibited substantial temporal variation, with a pronounced spike during 2020-2021 (Figure 5, Table 8).

**Table 8.** Temporal Trends in Shooting Incidence

| Period | Annual Average | Change from Baseline |
|--------|----------------|---------------------|
| 2015-2019 (Pre-COVID) | 1,361 | — |
| 2020-2021 (Pandemic peak) | 2,297 | +68.8% |
| 2022-2025 (Post-peak) | 1,495 | +9.8% |

The peak year was 2021, with 2,338 shootings, nearly double the pre-pandemic average. Although violence has since declined, it remains elevated above pre-2020 levels.

![Figure 5: Temporal Trends](../figures/temporal_trends.png)

*Figure 5. Annual shooting counts in Philadelphia, 2015-2025. The COVID-era spike (2020-2021) is prominent.*

### Vulnerability Index

A Neighborhood Vulnerability Index (NVI) was constructed by combining poverty rate, household income, shooting density, and transport time. Trauma deserts exhibited elevated vulnerability, with an average NVI of 21.6 compared to 16.5 citywide (1.31 times higher). Nine of 18 trauma deserts (50%) were in the top quartile of vulnerability.

![Figure 6: Vulnerability Index Map](../figures/vulnerability_index_map.png)

*Figure 6. Neighborhood Vulnerability Index across Philadelphia census tracts.*

---

## Discussion

### Principal Findings

This study reveals a paradox in Philadelphia's trauma desert geography: although 18 census tracts meet the bivariate criteria for trauma desert status, the primary driver of elevated trauma burden is violence concentration rather than geographic access barriers.

Three key findings support this interpretation:

1. **Excellent geographic coverage:** 99.6% of shootings occur within 20 minutes of Level I trauma care.
2. **Inverse access-race relationship:** Predominantly Black neighborhoods are actually closer to trauma centers, not farther.
3. **Violence concentration:** The 4.4-fold disparity in shooting density between Black and other tracts is largely unexplained by socioeconomic factors.

### Transport Time Still Matters

The finding that fatality rates increase from 20.0% to 30.6% across the transport time gradient confirms that transport time remains clinically relevant. This observation aligns with published literature on trauma transport and mortality (Newgard et al., 2010; Byrne et al., 2019). However, because only a small fraction of shootings occur in high-transport-time areas, improving geographic access alone would have limited population-level impact.

### The Unexplained Disparity

A significant finding is that 68.5% of the shooting density disparity between Black and other tracts cannot be explained by current poverty or income differences. This unexplained portion likely reflects:

- Historical patterns of residential segregation and disinvestment
- Differential policing and criminal justice involvement
- Concentrated disadvantage and "epidemic" violence transmission
- Structural factors accumulated over decades

### Policy Implications

The findings suggest that traditional approaches to improving trauma access, such as building new facilities or redistributing EMS resources, would have limited impact in Philadelphia given the already-excellent geographic coverage. Instead, interventions should focus on:

1. **Violence prevention:** Addressing the root causes of violence concentration in affected neighborhoods through community-based violence intervention programs, employment opportunities, and addressing structural determinants.
2. **Community hemorrhage control:** Expanding "Stop the Bleed" training in high-burden neighborhoods to reduce preventable deaths during the pre-hospital interval.
3. **Hospital capacity:** Ensuring that Temple University Hospital and Penn Presbyterian Medical Center—which bear the majority of the penetrating trauma burden—have adequate resources and capacity.

### Limitations

Several limitations warrant consideration:

1. **Transport time estimation:** We used tract centroids and isochrone containment rather than actual incident-to-hospital routing. This provides categorical estimates that may not capture within-tract variation.
2. **Fatality definition:** The shooting data records ultimate fatality status, not hospital outcome. Some decedents may have died at the scene before transport was possible.
3. **Confounders:** We cannot control for injury severity beyond wound location. More severely wounded individuals may be more likely to die regardless of transport time.
4. **Modeled catchment:** Hospital burden estimates reflect nearest-center assignment, not actual EMS destination decisions which may be influenced by hospital capacity, patient preference, or bypass protocols.
5. **Temporal scope:** Violence patterns change over time. Our analysis captures 11 years but may not reflect future conditions.

---

## Conclusion

The "trauma desert" phenomenon in Philadelphia is driven primarily by the extreme concentration of gun violence in specific neighborhoods rather than by inadequate geographic access to Level I trauma care. Although transport time significantly affects mortality outcomes, the overwhelming majority of shootings occur within close proximity to trauma centers.

The 4.4-fold disparity in shooting density between predominantly Black and other tracts, 68.5% of which is unexplained by observable socioeconomic factors, represents a fundamental health equity crisis that cannot be addressed through trauma system redesign alone. Reducing the gun violence burden in affected neighborhoods must be the primary policy objective.

---

## References

American College of Surgeons. (2022). Resources for optimal care of the injured patient. Chicago, IL: American College of Surgeons.

Beard, J. H., Ramsay, J., Sims, C. A., Schwab, C. W., Wiebe, D. J., & Reilly, P. M. (2019). Civilian active shooter incidents: An analysis of hospital preparedness. *Journal of Trauma and Acute Care Surgery*, 86(2), 303-311.

Branas, C. C., Jacoby, S., & Andreyeva, E. (2016). Firearm violence as a disease: A call to action. *Annals of Internal Medicine*, 165(9), 665-666.

Brown, J. B., Rosengart, M. R., Forsythe, R. M., Reynolds, B. R., Gestring, M. L., Hallinan, W. M., ... & Sperry, J. L. (2016). Not all prehospital time is equal: Influence of scene time on mortality. *Annals of Surgery*, 264(6), 1000-1007.

Byrne, J. P., Mann, N. C., Dai, M., Mason, S. A., Karanicolas, P., Rizoli, S., & Nathens, A. B. (2019). Association between emergency medical service response time and motor vehicle crash mortality in the United States. *JAMA Surgery*, 154(4), 286-293.

Goldstick, J. E., Cunningham, R. M., & Carter, P. M. (2022). Current causes of death in children and adolescents in the United States. *New England Journal of Medicine*, 386(20), 1955-1956.

Hsia, R. Y., Shen, Y. C., & Kanzaria, H. K. (2020). Trends in geographic access to trauma centers in the United States. *JAMA Network Open*, 3(10), e2016936.

Jacoby, S. F., Dong, B., Gresh, A., & Richmond, T. S. (2018). Risk factors for survival after gunshot wound injury: An ecologic study of neighborhood social determinants. *Journal of Urban Health*, 95(5), 614-623.

Kaufman, E. J., Wiebe, D. J., Xiong, R. A., Morrison, C. N., Seamon, M. J., & Delgado, M. K. (2021). Epidemiologic trends in fatal and nonfatal firearm injuries in the US, 2009-2017. *JAMA Internal Medicine*, 181(2), 237-244.

MacKenzie, E. J., Rivara, F. P., Jurkovich, G. J., Nathens, A. B., Frey, K. P., Egleston, B. L., ... & Scharfstein, D. O. (2006). A national evaluation of the effect of trauma-center care on mortality. *New England Journal of Medicine*, 354(4), 366-378.

Newgard, C. D., Schmicker, R. H., Hedges, J. R., Trickett, J. P., Davis, D. P., Bulger, E. M., ... & Resuscitation Outcomes Consortium Investigators. (2010). Emergency medical services intervals and survival in trauma: Assessment of the "golden hour" in a North American prospective cohort. *Annals of Emergency Medicine*, 55(3), 235-246.

Papachristos, A. V., & Wildeman, C. (2014). Network exposure and homicide victimization in an African American community. *American Journal of Public Health*, 104(1), 143-150.

Schuurman, N., Bell, N., Hameed, S. M., & Simons, R. (2008). A model for identifying and ranking need for trauma center services in a region. *The Journal of Emergency Medicine*, 35(4), 379-387.

Wandling, M., Nathens, A. B., Shapiro, M. B., & Haut, E. R. (2016). Police transport versus ground EMS: A trauma system-level evaluation of prehospital care policies and their effect on clinical outcomes. *Journal of Trauma and Acute Care Surgery*, 81(5), 931-935.

Wintemute, G. J. (2015). The epidemiology of firearm violence in the twenty-first century United States. *Annual Review of Public Health*, 36, 5-19.

---

## Acknowledgments

Data for this analysis were obtained from OpenDataPhilly, the Pennsylvania Trauma Systems Foundation, and the U.S. Census Bureau. Drive-time isochrones were generated using the OpenRouteService API.

---

## Data Availability

All code and processed data are available at: https://github.com/yoelplutchok/gun-violence-trauma-access-philly

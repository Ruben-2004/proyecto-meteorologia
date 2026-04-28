# 🔬 Methodology

## Data Sources

Two main data sources were used:

### Meteorological Data

- Source: Meteostat
- Type: Hourly temperature data
- Variables: Temperature (°C)
- Stations: Urban and rural locations for each city

### Land Use Data

- Source: CORINE Land Cover
- Resolution: European-scale land classification
- Categories: Urban, vegetation, agriculture, etc.

---

## Data Preprocessing

The raw data underwent several preprocessing steps:

- Removal of missing values (NaNs)
- Interpolation of small gaps
- Outlier detection and filtering
- Conversion to efficient data structures (Polars)

This ensures consistency and reliability of the analysis.

---

## UHI Calculation

The UHI was computed as:

UHI = T_urban − T_rural

For each city:

- Hourly UHI values were calculated
- Aggregated metrics were derived:
  - Mean UHI
  - Daytime UHI
  - Nighttime UHI

---

## Spatial Analysis

To analyse land use:

1. Buffers of 5 km were created around each station
2. These buffers were intersected with CORINE polygons
3. The proportion of each land use type was computed

This provides a quantitative measure of the environment surrounding each station.

---

## Feature Engineering

The final dataset includes:

- UHI metrics
- % urban land
- % vegetation
- Population
- Altitude difference
- Geographic coordinates
- Mean temperature

---

## Modeling

Two regression models were used:

### Linear Regression

- Interpretable coefficients
- Baseline model

### Ridge and Lasso Regression

- Regularization to reduce overfitting
- More stable estimates with small datasets

---

## Evaluation

Model performance was evaluated using:

- R² score
- Coefficient analysis

Given the limited number of cities, emphasis was placed on interpretability rather than predictive performance.
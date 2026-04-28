# 🔬 Methodology

## Data Sources

- Meteostat: hourly temperature data
- CORINE Land Cover: land use

## Preprocessing

- Missing values handled
- Outliers removed
- Data converted to Polars

## UHI Calculation

UHI is computed hourly and aggregated:

- Mean
- Daytime
- Nighttime

## Land Use

- Buffers of 5 km around stations
- Spatial intersection with CORINE
- Percentage of land types computed

## Modeling

- Linear Regression
- Ridge Regression

Variables used:

- % urban
- % vegetation
- population
- altitude difference
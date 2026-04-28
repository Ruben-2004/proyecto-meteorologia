# 📊 Analysis

## 🌡️ UHI Computation

The Urban Heat Island (UHI) effect is defined as the temperature difference between urban and rural environments:

UHI = T_urban − T_rural

Using hourly temperature data from Meteostat, UHI values were computed for each city over the study period. The resulting time series allow for both temporal and statistical analysis.

### Observations

- UHI values are generally positive, confirming the presence of the phenomenon
- The magnitude varies depending on the city and climatic conditions
- Seasonal patterns are observed, with stronger effects in summer months

---

## 🌙 Day vs Night Behaviour

A key aspect of the analysis is the distinction between daytime and nighttime UHI.

### Findings

- Nighttime UHI is consistently higher than daytime UHI
- This is due to:
  - Heat storage in urban materials (asphalt, concrete)
  - Reduced radiative cooling
  - Lower wind speeds and atmospheric mixing

### Implications

This suggests that urban areas retain heat more efficiently than rural areas, particularly after sunset, which has important consequences for energy consumption and human comfort.

---

## 🌍 Land Use Analysis

Land use data from the CORINE Land Cover dataset was used to quantify the composition of the area surrounding each meteorological station.

### Method

- Buffers of 5 km were created around each station
- Spatial intersections with CORINE polygons were computed
- Land use categories were aggregated into:
  - Urban
  - Vegetation
  - Agricultural
  - Other

### Results

- Cities with higher percentages of urban land show stronger UHI effects
- Vegetation has a clear cooling effect
- Agricultural areas show intermediate behaviour

---

## 📈 Correlation Analysis

Correlation matrices were computed to explore relationships between variables.

### Key relationships

- Positive correlation between % urban and UHI
- Negative correlation between % vegetation and UHI
- Population is often correlated with urbanization

---

## 🧠 Interpretation

The results confirm well-known physical mechanisms:

- Urban materials store and slowly release heat
- Lack of vegetation reduces evapotranspiration
- Urban geometry (buildings) affects airflow and radiation

Overall, the analysis supports the hypothesis that land use is a major driver of UHI intensity.
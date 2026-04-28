# 🌡️ Urban Heat Island Analysis in Spain

This project investigates the **Urban Heat Island (UHI)** effect across several Spanish cities by combining meteorological data with land use information. The UHI phenomenon refers to the temperature difference between urban and rural environments, typically caused by human activity, artificial surfaces, and reduced vegetation.

## 📌 Objectives

The main objectives of this project are:

- To compute the Urban Heat Island (UHI) intensity using hourly temperature data
- To compare UHI behaviour during daytime and nighttime
- To analyse the relationship between land use and temperature differences
- To evaluate the impact of urbanization and vegetation on UHI
- To build statistical models that explain UHI variability across cities

## 🌍 Study Area

The analysis focuses on a selection of Spanish cities representing different climatic and geographical conditions, including:

- Madrid
- Barcelona
- Sevilla
- Zaragoza
- Bilbao
- A Coruña
- Santander
- Tenerife

This diversity allows for a more comprehensive understanding of how UHI behaves under different environmental conditions.

## 🗂️ Project Structure

The repository is organised as follows:

- `src/`: Core implementation of the project, including data processing, UHI computation, modeling, and visualization
- `tests/`: Unit tests ensuring correctness and robustness of the code
- `docs/`: Project documentation built using MkDocs
- `data/`: Data files used in the analysis

## ⚙️ Technologies Used

This project relies on several modern Python tools:

- **Pandas / Polars** for data manipulation
- **GeoPandas** for spatial analysis
- **Meteostat** for meteorological data retrieval
- **Scikit-learn** for regression modeling
- **Matplotlib / Seaborn** for visualization

## 📊 Key Insights

Preliminary results suggest that:

- UHI is consistently positive across cities
- The effect is stronger during nighttime due to heat retention
- Urban areas significantly increase local temperatures
- Vegetation plays a mitigating role in reducing UHI intensity

## 📚 Documentation

For a detailed explanation of the methodology and results:

- 👉 [Methodology](methodology.md)
- 👉 [Analysis](analysis.md)
- 👉 [Results](results.md)
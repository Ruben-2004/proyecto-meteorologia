# Análisis de Datos Meteorológicos

> Proyecto final — Big Data · Grado en Matemáticas · UNIE Universidad

[![CI](https://github.com/Ruben-2004/proyecto-meteorologia/actions/workflows/ci.yml/badge.svg)](https://github.com/Ruben-2004/proyecto-meteorologia/actions/workflows/ci.yml)
[![Docs](https://github.com/Ruben-2004/proyecto-meteorologia/actions/workflows/docs.yml/badge.svg)](https://Ruben-2004.github.io/proyecto-meteorologia/)
[![Coverage](https://codecov.io/gh/Ruben-2004/proyecto-meteorologia/graph/badge.svg)](https://codecov.io/gh/Ruben-2004/proyecto-meteorologia)
[![Version](https://img.shields.io/github/v/release/Ruben-2004/proyecto-meteorologia)](https://github.com/Ruben-2004/proyecto-meteorologia/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Description

*Urban Heat Islands in Spanish Cities*
*Cuantification of the Urban Heat Island Effect (UHI) comparing records of urban-located metereological stations compared to nearby rural located ones. We'll select urban-rural pairs for a couple of Spanish cities, compute the UHI intensity, analyze their daily and seasonal variability, and finally look for corelations with variables such as population, urbanized surface or height.*

## Documentation

Full documentation at **[Ruben-2004.github.io/proyecto-meteorologia](https://Ruben-2004.github.io/proyecto-meteorologia/)**

## Installation

  ```bash
  git clone https://github.com/Ruben-2004/proyecto-meteorologia.git
  cd proyecto-meteorologia
  pip install uv
  uv sync --group dev
  ```

## Data Download

Data is not included in the repository. To download:

  ```bash
  # TODO: add your data download instructions
  ```

## Usage

  ```bash
  uv run pytest                          # run tests
  uv run pytest --cov=src -v     # tests with coverage
  uv run ruff check .                    # lint
  uv run ruff format .                   # format
  uv run mkdocs serve                    # preview docs at localhost:8000
  ```

## Project Structure

  ```
  proyecto-meteorologia/
  ├── .github/workflows/   # CI/CD pipelines
  ├── data/                # Data files (not committed — see .gitignore)
  ├── docs/                # MkDocs documentation sources
  ├── notebooks/           # Exploratory notebooks
  ├── src/weather/         # Source package
  ├── tests/               # Unit and integration tests
  ├── mkdocs.yml
  ├── pyproject.toml
  └── README.md
  ```

## Author

**Ruben Torres** · [github.com/Ruben-2004](https://github.com/Ruben-2004)

## Professor
**Álvaro Diez** · [github.com/alvarodiez20](https://github.com/alvarodiez20)

---

*Big Data · 4º Grado en Matemáticas · UNIE Universidad · 2025–2026*

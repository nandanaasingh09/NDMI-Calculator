# NDMI Calculator

This module calculates the Normalized Difference Moisture Index (NDMI) using Sentinel-2 data. The module handles cases where the specified date range does not have available data by pulling the latest available Sentinel-2 imagery.

## Features

- Fetches Sentinel-2 data within a specified date range and bounding box.
- Calculates NDMI using SWIR and NIR bands.
- Handles GeoJSON input with multiple geometries (FeatureCollection).
- Plots the NDMI using Matplotlib.
- Resamples the NDMI data for better visualization.

## Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone git@github.com:nandanaasingh09/NDMI-Calculator.git
cd NDMI-Calculator
conda env create -f environment.yml

```

### Script Description
- geojson_path: Path to the GeoJSON file containing the area of interest.
- start_date: Start date for the data search in YYYY-MM-DD format.
- end_date: End date for the data search in YYYY-MM-DD format.


## Output
- The module will display NDMI images for the specified date range. Each image will have a color bar indicating the NDMI values, ranging from -1 to 1.


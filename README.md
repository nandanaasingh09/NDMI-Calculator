# NDMI Calculator

This module calculates the Normalized Difference Moisture Index (NDMI) using Sentinel-2 data. The module handles cases where the specified date range does not have available data by pulling the latest available Sentinel-2 imagery. The Normalized Difference Moisture Index (NDMI) detects moisture levels in vegetation using a combination of near-infrared (NIR) and short-wave infrared (SWIR) spectral bands. It is a reliable indicator of water stress in crops. The NDMI range is -1 to +1, where the lowest values (white to pale brown) indicate low vegetation water content, and the highest ones (in blue) correspond to high water content. In other words, decrease in NDMI will indicate water stress, while abnormally high NDMI values could signal waterlogging.

## Features

- Fetches Sentinel-2 data within a specified date range and bounding box.
- Calculates NDMI using SWIR and NIR bands.
- Handles GeoJSON input with multiple geometries (FeatureCollection).
- Ensuring the NDMI is a 2D array by selecting the first band.
- Plots the NDMI (processed raster outputs) using Matplotlib.
- Computes and displays mean NDMI value on the output image.


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
- output_path: Path to save the NDMI output images

## Running the NDMI Calculator Script

Here is the example how to execute the NDMI calculator script with the specified parameters, by using the following command:

```bash
python src/ndmi_calculator.py --geojson_path /home/nandanaa/Projects/NDMI-Calculator/data/farm_p.geojson --start_date 2024-07-15 --end_date 2024-08-04 --output_path /home/nandanaa/Projects/NDMI-Calculator/Output/
```

## Output
- The module will display NDMI images for the specified date range. Each image will have a color bar indicating the NDMI values, ranging from -1 to 1.

![image info](/Output/ndmi_2024-07-25.png)



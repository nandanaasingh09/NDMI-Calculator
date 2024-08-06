import os
import json
import argparse
from datetime import datetime
import geopandas as gpd
import rioxarray
import matplotlib.pyplot as plt
from pystac_client import Client

def load_and_search_data(client, collection, bbox, start_date, end_date, cloud_cover=50):
    """
    Load and search for Sentinel-2 data within the specified bounding box and date range.

    Parameters:
    client (Client): STAC client for accessing Sentinel-2 data.
    collection (str): The collection ID to search within.
    bbox (tuple): Bounding box coordinates (minx, miny, maxx, maxy).
    start_date (str): Start date for the imagery search in YYYY-MM-DD format.
    end_date (str): End date for the imagery search in YYYY-MM-DD format.
    cloud_cover (int, optional): Maximum allowable cloud cover percentage. Default is 50.

    Returns:
    ItemCollection: A collection of items matching the search criteria.
    """
    search = client.search(
        collections=[collection],
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        query={"eo:cloud_cover": {"lt": cloud_cover}}
    )
    items = search.item_collection()
    return items

def calculate_ndmi(item, gdf):
    """
    Calculate the Normalized Difference Moisture Index (NDMI) for a given item and GeoDataFrame.

    Parameters:
    item (Item): STAC item containing the Sentinel-2 imagery.
    gdf (GeoDataFrame): GeoDataFrame containing the farm polygon.

    Returns:
    DataArray: NDMI values calculated from the Sentinel-2 imagery.

    Raises:
    ValueError: If the necessary assets (SWIR and NIR) are not available in the item.
    """
    # Check for necessary assets
    if "swir16" not in item.assets or "nir08" not in item.assets:
        raise ValueError(f"Item {item.id} missing necessary assets (SWIR and NIR).")

    # Open SWIR and NIR rasters
    SWIR_uri = item.assets["swir16"].href
    nir_uri = item.assets["nir08"].href
    red = rioxarray.open_rasterio(SWIR_uri, masked=True)
    nir = rioxarray.open_rasterio(nir_uri, masked=True)

    # Transform the GeoDataFrame to match the CRS of the rasters
    gdf = gdf.to_crs(red.rio.crs)

    # Cliping the rasters using the GeoDataFrame geometry
    geometries = gdf.geometry.values
    red_clip = red.rio.clip(geometries, gdf.crs)
    nir_clip = nir.rio.clip(geometries, gdf.crs)

    # Reproject red clip to match NIR clip if needed
    if red_clip.rio.crs != nir_clip.rio.crs:
        red_clip = red_clip.rio.reproject_match(nir_clip)

    # Calculate NDMI - Normalized Difference Moisture Index
    ndmi = (nir_clip - red_clip) / (nir_clip + red_clip)

    # Ensure the NDMI is a 2D array by selecting the first band 
    if ndmi.rio.count == 1:
        ndmi = ndmi.squeeze()

    return ndmi

def plot_and_save_ndmi(ndmi, output_path, date):
    """
    Plot and save the NDMI values as a PNG image.

    Parameters:
    ndmi (DataArray): NDMI values to plot.
    output_path (str): Directory to save the NDMI output images.
    date (str): Date of the NDMI calculation for labeling the plot.
    """
    mean_ndmi = ndmi.mean().item()  

    fig, ax = plt.subplots(figsize=(8, 10))
    im = ax.imshow(ndmi, cmap='RdYlGn', vmin=-1, vmax=1)
    cbar = plt.colorbar(im, ax=ax, label='NDMI', shrink=0.4)  
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    ax.set_xticks([])  
    ax.set_yticks([])  
    plt.title(f'NDMI - {date}\nMean NDMI: {mean_ndmi:.2f}')
    output_file = os.path.join(output_path, f'ndmi_{date}.png')
    plt.savefig(output_file)
    plt.close()

def main(geojson_path, start_date, end_date, output_path):
    """
    Main function to load data, calculate NDMI, and save the results.

    Parameters:
    geojson_path (str): Path to the GeoJSON file containing the farm polygon.
    start_date (str): Start date for the imagery search in YYYY-MM-DD format.
    end_date (str): End date for the imagery search in YYYY-MM-DD format.
    output_path (str): Directory to save the NDMI output images.
    """
    api_url = "https://earth-search.aws.element84.com/v1"
    client = Client.open(api_url)
    collection = "sentinel-2-l2a"

    gdf = gpd.read_file(geojson_path)
    bbox = gdf.geometry[0].bounds

    items = load_and_search_data(client, collection, bbox, start_date, end_date)

    if not items:
        print("No items found for the given date range. Searching for the latest available imagery.")
        items = load_and_search_data(client, collection, bbox, "2015-06-23", datetime.utcnow().strftime('%Y-%m-%d'))

        if not items:
            print("No Sentinel-2 data found.")
            return

    gdf = gdf.to_crs("EPSG:4326")  

    for item in items:
        try:
            ndmi = calculate_ndmi(item, gdf)
            item_date = item.properties['datetime'].split("T")[0]
            plot_and_save_ndmi(ndmi, output_path, item_date)
            print(f"NDMI calculated and saved for item {item.id} on {item_date}")
        except Exception as e:
            print(f"Error processing item {item.id}: {e}")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate NDMI from Sentinel-2 imagery.")
    parser.add_argument("--config", type=str, help="Path to the configuration JSON file.")
    parser.add_argument("--geojson_path", type=str, help="Path to the GeoJSON file containing the farm polygon.")
    parser.add_argument("--start_date", type=str, help="Start date for the imagery search (YYYY-MM-DD).")
    parser.add_argument("--end_date", type=str, help="End date for the imagery search (YYYY-MM-DD).")
    parser.add_argument("--output_path", type=str, help="Path to save the NDMI output images.")
    
    args = parser.parse_args()
    
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
            geojson_path = config.get("geojson_path")
            start_date = config.get("start_date")
            end_date = config.get("end_date")
            output_path = config.get("output_path")
    else:
        geojson_path = '/home/nandanaa/Projects/NDMI-Calculator/data/farm_p.geojson'
        start_date = '2024-07-16'
        end_date = '2024-08-02'
        output_path = '/home/nandanaa/Projects/NDMI-Calculator/Output/'

    main(geojson_path, start_date, end_date, output_path)

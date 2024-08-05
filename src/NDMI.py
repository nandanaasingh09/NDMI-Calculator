import geopandas as gpd
import rioxarray
import matplotlib.pyplot as plt
from pystac_client import Client
import pystac
from datetime import datetime

def load_and_search_data(client, collection, bbox, start_date, end_date, cloud_cover=50):
    search = client.search(
        collections=[collection],
        bbox=bbox,
        datetime=f"{start_date}/{end_date}",
        query={"eo:cloud_cover": {"lt": cloud_cover}}
    )
    items = search.item_collection()
    return items

def calculate_ndmi(item, gdf):
    # Check for necessary assets
    if "swir16" not in item.assets or "nir08" not in item.assets:
        raise ValueError(f"Item {item.id} missing necessary assets (SWIR and NIR).")

    # Open SWIR and NIR rasters
    SWIR_uri = item.assets["swir16"].href
    nir_uri = item.assets["nir08"].href
    red = rioxarray.open_rasterio(SWIR_uri, masked=True)
    nir = rioxarray.open_rasterio(nir_uri, masked=True)

    # Clip rasters using the GeoDataFrame geometry
    red_clip = red.rio.clip(gdf['geometry'], gdf.crs)
    nir_clip = nir.rio.clip(gdf['geometry'], gdf.crs)

    # Reproject red clip to match NIR clip if needed
    if red_clip.rio.crs != nir_clip.rio.crs:
        red_clip = red_clip.rio.reproject_match(nir_clip)

    # Calculate NDMI
    ndmi = (nir_clip - red_clip) / (nir_clip + red_clip)

    # Ensure the NDMI is a 2D array by selecting the first band (if it's a single-band raster)
    if ndmi.rio.count == 1:
        ndmi = ndmi.squeeze()

    return ndmi

def plot_and_save_ndmi(ndmi, output_path):
    fig, ax = plt.subplots(figsize=(8, 10))
    im = ax.imshow(ndmi, cmap='RdYlGn', vmin=-1, vmax=1)
    cbar = plt.colorbar(im, ax=ax, label='NDMI')
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    plt.title('NDMI')
    plt.savefig(output_path)
    plt.close()

def main(geojson_path, start_date, end_date, output_path):
    api_url = "https://earth-search.aws.element84.com/v1"
    client = Client.open(api_url)
    collection = "sentinel-2-l2a"

    gdf = gpd.read_file(geojson_path)
    bbox = gdf.geometry[0].bounds

    items = load_and_search_data(client, collection, bbox, start_date, end_date)

    if not items:
        print("No items found for the given date range.")
        return

    gdf = gdf.to_crs("EPSG:4326")  # Ensure the GeoDataFrame is in the correct CRS

    for item in items:
        try:
            ndmi = calculate_ndmi(item, gdf)
            plot_and_save_ndmi(ndmi, output_path)
            print(f"NDMI calculated and saved for item {item.id}")
            break  # Only process the first valid item
        except Exception as e:
            print(f"Error processing item {item.id}: {e}")
            continue

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Calculate NDMI from Sentinel-2 imagery.")
    parser.add_argument("geojson_path", type=str, help="Path to the GeoJSON file containing the farm polygon.")
    parser.add_argument("start_date", type=str, help="Start date for the imagery search (YYYY-MM-DD).")
    parser.add_argument("end_date", type=str, help="End date for the imagery search (YYYY-MM-DD).")
    parser.add_argument("output_path", type=str, help="Path to save the NDMI output image.")

    args = parser.parse_args()
    main(args.geojson_path, args.start_date, args.end_date, args.output_path)

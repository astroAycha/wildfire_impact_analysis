"""script to get the validation data from the Copernicus EMS API"""

import sys
import os
import shutil
import requests
import zipfile
import pandas as pd
import geopandas as gpd
from shapely import wkt


def get_ems_data(overwrite: bool = False):
    """
    Script to get the validation data from the Copernicus EMS API. 
    It downloads the data and extracts it to a folder called "product"
    """
    output_dir = "ems_data"

    if os.path.exists(output_dir):
        if overwrite:
            shutil.rmtree(output_dir)
            print(f"Removed existing '{output_dir}' folder.")
        else:
            print(f"Error: '{output_dir}' already exists. Run with overwrite=True to replace it.")
            sys.exit(1)

    url = "https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations/?code=EMSR811"

    data = requests.get(url).json()

    activation = data["results"][0]

    rows = []

    for aoi in activation["aois"]:
        for product in aoi["products"]:

            row = {
                "aoi_name": product["aoiName"],
                "aoi_number": product["aoiNumber"],
                "type": product["type"],
                "download_path": product["downloadPath"],
                "expected_delivery": product["expectedDelivery"],
                "geometry": wkt.loads(product["extent"])
            }

            # first acquisition date if available
            if product.get("images"):
                row["acquisition_time"] = product["images"][0]["acquisitionTime"]
                row["sensor"] = product["images"][0]["sensorName"]

            rows.append(row)

    ems_gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")

    # filter for the GRA products
    ems_gra_data = ems_gdf[ems_gdf['type'] == 'GRA']

    ems_data_url = ems_gra_data['download_path'].iloc[0]

    print(f"Downloading data from: {ems_data_url}")
    print(f"Acquisition time: {ems_gra_data['acquisition_time'].iloc[0]}")
    print(f"Sensor: {ems_gra_data['sensor'].iloc[0]}")

    # download the data and extract it
    with open("ems_data.zip", "wb") as f:
        f.write(requests.get(ems_data_url).content)

    with zipfile.ZipFile("ems_data.zip") as z:
        z.extractall("ems_data")
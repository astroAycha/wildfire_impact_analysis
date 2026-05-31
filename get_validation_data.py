"""script to get the validation data from the Copernicus EMS API"""

import requests
import zipfile
import pandas as pd
import geopandas as gpd
from shapely import wkt


def get_ems_data():
    """
    Script to get the validation data from the Copernicus EMS API. 
    It downloads the data and extracts it to a folder called "product"
    """

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

    # sort by acquisition time and get the first one
    ems_gdf.sort_values("acquisition_time", inplace=True)
    data_download_url = ems_gdf['download_path'].iloc[0]

    # download the data and extract it
    with open("product.zip", "wb") as f:
        f.write(requests.get(data_download_url).content)

    with zipfile.ZipFile("product.zip") as z:
        z.extractall("product")
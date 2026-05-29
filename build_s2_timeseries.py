"""Extract data from Sentinel-2 via STAC and calculate spectral indices time series"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
import pystac_client
import xarray
import odc.stac
import dask


from calc_spec_indices import SpectralIndices

from dotenv import load_dotenv

load_dotenv()


class BuildS2TimeSeries:
    """Class to handle data extraction and processing from Sentinel-2 via STAC API"""


    def __init__(self):

        self.api_url = os.getenv("AWS_STAC_API_URL")
        self.collection_id = "sentinel-2-l2a"
        
    def define_bbox(self, 
                    lat: float,
                    lon: float,
                    rad: float) -> list:
        """
        Define a buffer around a point given its coordinates and a radius

        Parameters
        ----------
        lat : float
            Latitude of the point
        lon : float
            Longitude of the point
        rad : float 
            Radius of the buffer in meters
        Returns
        -------
        bbox : tuple
            Tuple of coordinates defining the bounding box

        Example
        --------
        >>> builder = BuildS2TimeSeries()
        >>> bbox = builder.define_bbox(33.5138, 36.2765, 100)
        """

        point = Point(lon, lat)

        gdf = gpd.GeoDataFrame(crs='EPSG:4326', 
                               geometry=[point])
        
        gdf_proj = gdf.to_crs(gdf.estimate_utm_crs())

        if rad <= 0:
            raise ValueError("Radius must be a positive value.")
        
        # create a buffer around the point
        gdf_proj['geometry'] = gdf_proj.geometry.buffer(rad)

        # project back to WGS84
        gdf_buffer = gdf_proj.to_crs('EPSG:4326')

        bbox = gdf_buffer.geometry.total_bounds

        return list(bbox)

    def mask_invalid_data(self, 
                          ds: xarray.Dataset) -> tuple:
        """
        Mask invalid data based on the Scene Classification Layer (SCL) values
        
        Parameters
        ---------- 
        ds : xarray.Dataset
            Dataset containing the bands and the SCL layer
        Returns
        -------
        red_masked, blue_masked, nir_masked, swir1_masked, swir2_masked : xarray.DataArray
            Masked data arrays for the red, blue, nir, and swir1, and swir2 bands
        """
        print("Masking invalid data based on SCL values...")

        ds = ds.where(ds != 0)

        
        blue = ds['blue'] # B02
        red = ds['red'] # B04
        green = ds['green'] # B03
        nir = ds['nir'] # Band 08
        swir1 = ds['swir16'] # B11
        swir2 = ds['swir22'] # B12
        scl = ds['scl']

        mask = scl.isin([
                        3, # cloud_shadow
                        6, # water
                        8, # cloud_medium_probabability
                        9, # cloud_high_probabability
                        10 # thin_cirrus
                    ])
        

        # mask unwanted data
        blue_masked = blue.where(~mask)
        red_masked = red.where(~mask)
        green_masked = green.where(~mask)
        nir_masked = nir.where(~mask)
        swir1_masked = swir1.where(~mask)
        swir2_masked = swir2.where(~mask)

        return red_masked, blue_masked, green_masked, nir_masked, swir1_masked, swir2_masked
    

    def extract_time_series(self,
                            aoi_bbox: list,
                            aoi_name: str,
                            start_date: str,
                            end_date: str) -> gpd.GeoDataFrame:
        """
        Extract time series from the downloaded data

        Parameters
        ----------
        aoi_bbox : list
            List of coordinates defining the bounding box
        aoi_name : str
            Name of the area of interest (AOI) for logging and file naming purposes
        start_date : str
            Start date of the time series in the format 'YYYY-MM-DD'
        end_date : str
            End date of the time series in the format 'YYYY-MM-DD'
        Returns
        -------
        geopandas dataframe with the datetime, indices, and geometry
        
        Example
        --------
        >>> builder = BuildS2TimeSeries()
        >>> bbox = builder.define_bbox(33.5138, 36.2765, 100)
        >>> ts_gdp = builder.extract_time_series(bbox, 
                                                    "Damascus",
                                                    "2024-01-01", 
                                                    "2024-02-01")
        """

        print(f"Extracting time series for AOI: {aoi_name}, {aoi_bbox} from Sentinel-2 data...")
        client = pystac_client.Client.open(self.api_url)
        dataset_bands = ['blue', 'red', 'green', 'nir', 'swir16', 'swir22', 'scl']

        search = client.search(collections=self.collection_id,
                                datetime=f"{start_date}/{end_date}",
                                bbox=aoi_bbox,
                                query={"eo:cloud_cover": {"lt": 20}},
                                )
        
        item_collection = search.item_collection()

        print(f"Found {len(item_collection.items)} items in the STAC catalog for the given parameters.")

        if len(item_collection.items) == 0:
            raise ValueError("No data found for the given parameters.")

        ds = odc.stac.load(item_collection,
                            bands=dataset_bands,
                            group_by="solar_day",
                            chunks={'x': 1000, 'y': 1000},
                            resolution=20,
                            bbox=aoi_bbox
                            )

        red_masked, blue_masked, green_masked, nir_masked, swir1_masked, swir2_masked = self.mask_invalid_data(ds) 

        spec_indices_ts = []                                                                                 
        # get NDVI time series
        ndvi = SpectralIndices.calc_ndvi(nir_masked, red_masked)

        ndvi_median_ts = ndvi.resample(time="MS").median().interp(method='nearest')
        spec_indices_ts.append(ndvi_median_ts)
       
        # Bare Soil Index (BSI)        
        bsi = SpectralIndices.calc_bsi(swir1_masked, red_masked, nir_masked, blue_masked)
        
        bsi_median_ts = bsi.resample(time="MS").median().interp(method='nearest')
        spec_indices_ts.append(bsi_median_ts)
        
        # Normalized Difference Moisture Index (NDMI)
        ndmi = SpectralIndices.calc_ndmi(swir1_masked, nir_masked)
        ndmi_median_ts = ndmi.resample(time="MS").median().interp(method='nearest')
        spec_indices_ts.append(ndmi_median_ts)


        # Normalized Burn Ratio (NBR)
        nbr = SpectralIndices.calc_nbr(swir2_masked, nir_masked)
        nbr_median_ts = nbr.resample(time="MS").median().interp(method='nearest')
        spec_indices_ts.append(nbr_median_ts)

        ndvi_ts, bsi_ts, ndmi_ts, nbr_ts = dask.compute(
            ndvi_median_ts,
            bsi_median_ts,
            ndmi_median_ts,
            nbr_median_ts,
            scheduler="threads",
            num_workers=4,
            threads_per_worker=2
        )

        monthly_red = (red_masked.resample(time="MS").median().interp(method='nearest') * 1e-4).clip(0, 1)
        monthly_green = (green_masked.resample(time="MS").median().interp(method='nearest') * 1e-4).clip(0, 1)
        monthly_blue = (blue_masked.resample(time="MS").median().interp(method='nearest') * 1e-4).clip(0, 1)
        ds_monthly = xarray.merge([monthly_red.rename("red"), 
                                monthly_green.rename("green"), 
                                monthly_blue.rename("blue")])        

        indices_ds = xarray.merge([
            ndvi_ts.rename("NDVI"),
            bsi_ts.rename("BSI"),
            ndmi_ts.rename("NDMI"),
            nbr_ts.rename("NBR"),
        ])

        output = xarray.merge([ds_monthly, indices_ds])

        return output
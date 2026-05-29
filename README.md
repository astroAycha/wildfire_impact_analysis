# Wildfire Impact: Latakia, Syria - 2025

![alt text](image.png)

This repository analyzes wildfire impacts in Latakia, Syria using:

- Sentinel-2 Level-2A imagery from a STAC API
- FIRMS active fire detections
- Spectral indices (NDVI, NDMI, and NBR)
- Static and animated visual outputs for comparison over time

The workflow is centered around the notebook `wildfire_impact_latakia.ipynb`, with reusable helper scripts in this project root.

## Project Components

- `build_s2_timeseries.py`: queries Sentinel-2 from STAC, masks invalid pixels using SCL classes, and builds monthly composites plus index time series.
- `calc_spec_indices.py`: index formulas (NDVI, NDMI, NBR).
- `fetch_firms.py`: pulls FIRMS data in 5-day API windows and merges results.
- `plotting.py`: static plotting helpers for FRP, index trends, and before/after/now map comparisons.
- `*_aoi.geojson`: AOI boundaries.
- `*_time_series.csv`, `*_camp_forecast.csv`: previously generated outputs.

## Prerequisites

- Python 3.10+
- Access to a STAC endpoint serving `sentinel-2-l2a`
- NASA FIRMS API key

## Setup

1. Create and activate a virtual environment.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install required packages.

```bash
pip install pandas geopandas shapely pystac-client xarray odc-stac dask python-dotenv matplotlib seaborn pillow ipython
```

3. Create a `.env` file in the repository root:

```env
AWS_STAC_API_URL=https://your-stac-api.example.com
MAP_KEY=your_firms_map_key
```

Environment variables used by scripts:

- `AWS_STAC_API_URL`: used in `BuildS2TimeSeries` to open the STAC client.
- `MAP_KEY`: used by `fetch_firms.py` for FIRMS API requests.

## Typical Workflow

1. Define AOI and date range.
2. Build monthly Sentinel-2 composites and indices with `BuildS2TimeSeries.extract_time_series(...)`.
3. Fetch FIRMS detections with `fetch_firms(...)`.
4. Plot static comparisons with helpers in `plotting.py`.

## Minimal Usage Example

```python
from build_s2_timeseries import BuildS2TimeSeries
from fetch_firms import fetch_firms

builder = BuildS2TimeSeries()

# Option A: use AOI bounds from a GeoJSON.
# Option B: create a small bbox around a point.
bbox = builder.define_bbox(lat=35.0, lon=36.0, rad=500)

ds = builder.extract_time_series(
		aoi_bbox=bbox,
		aoi_name="example_aoi",
		start_date="2025-01-01",
		end_date="2025-12-31",
)

firms_df = fetch_firms(
		source=["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT"],
		bbox=bbox,
		start_date="2025-07-01",
		end_date="2025-08-01",
)
```

## Outputs

- `xarray.Dataset` from `extract_time_series(...)` containing:
	- monthly `red`, `green`, `blue`
	- monthly `NDVI`, `NDMI`, `NBR`
- FIRMS DataFrame with duplicate detections removed

## Notes

- Cloud and invalid pixel masking is based on Sentinel-2 SCL classes.
- Sentinel-2 search currently uses `eo:cloud_cover < 20`.
- Monthly values are aggregated using median and interpolated to monthly starts.

## Todo

- Add a pinned `requirements.txt`.
- Add tests for index calculations and basic STAC/FIRMS input validation.

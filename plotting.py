"""Scripts to make plots for the wildfire impact analysis notebook."""


from duckdb import df
import folium
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
import geopandas as gpd


def plot_firms_frp(input_df):
    """Plot the Fire Radiative Power (FRP) from the FIRMS dataset as a bar plot.
    Parameters
    ----------
    input_df : pandas.DataFrame
        DataFrame containing the FIRMS data with 'acq_date', 'frp', 
        and 'confidence' columns
    """

    input_df['acq_date'] = pd.to_datetime(input_df['acq_date'])
    filtered = input_df[input_df['acq_date'] >= "2025-07-01"].copy()
    filtered['date_only'] = filtered['acq_date'].dt.date

    palette = {"l": "#EFD9D1", "n": "#D8AC9C", "h": "#999B84"}

    # Aggregate FRP by date and confidence
    agg = (
        filtered.groupby(['date_only', 'confidence'])['frp']
        .mean()
        .reset_index()
    )
    agg['date_only'] = pd.to_datetime(agg['date_only'])
    agg['date_str'] = agg['date_only'].dt.strftime("%b %d")

    # Preserve chronological order
    date_order = agg.sort_values('date_only')['date_str'].unique().tolist()

    _, ax = plt.subplots(figsize=(9, 4))

    sns.barplot(
        data=agg,
        x='date_str',
        y='frp',
        hue='confidence',
        hue_order=['l', 'n', 'h'],
        palette=palette,
        order=date_order,
        ax=ax
    )

    ax.set_title("Fire Radiative Power over Time", fontsize=13)
    ax.set_xlabel("Acquisition Date")
    ax.set_ylabel("Average FRP (MW)")
    ax.grid(alpha=0.3)
    ax.tick_params(axis='x', rotation=30)
    ax.spines[["top", "right", "left"]].set_visible(False)

    plt.tight_layout()
    plt.show()

# ====================================

def plot_index_time_series(input_dataset, 
                          spec_index: list,
                          aoi_name: str):
    """Plot 3 subplots of the time series for the specified spectral index.
    
    Parameters
    ----------
    input_dataset : xarray.Dataset
        Dataset containing the time series of the spectral indices
    spec_index : list
        List of spectral indices to plot
    aoi_name : str
        Name of the area of interest for the plot title
    """

    fig, ax = plt.subplots(3, 1, figsize=(6, 6), sharex=True)

    ndvi_ts = input_dataset[spec_index[0]].mean(dim=['x', 'y']).interpolate_na(dim='time')
    ndvi_ts.plot(ax=ax[0], linestyle='-', lw=1, color='forestgreen')
    ndvi_ts.plot(ax=ax[0], marker='x', markersize=2, 
                 linestyle='none', color='#535757')

    nbr_ts = input_dataset[spec_index[1]].mean(dim=['x', 'y']).interpolate_na(dim='time')
    nbr_ts.plot(ax=ax[1], linestyle='-', lw=1, color='goldenrod')
    nbr_ts.plot(ax=ax[1], marker='x', markersize=2, 
                 linestyle='none', color='#535757')

    ndmi_ts = input_dataset[spec_index[2]].mean(dim=['x', 'y']).interpolate_na(dim='time')
    ndmi_ts.plot(ax=ax[2], linestyle='-', lw=1, color='dodgerblue')
    ndmi_ts.plot(ax=ax[2], marker='x', markersize=2, 
                 linestyle='none', color='#535757')

    ax[0].grid(alpha=0.3)
    ax[1].grid(alpha=0.3)
    ax[2].grid(alpha=0.3)

    ax[0].set_title("Normalized Difference Vegetation Index (NDVI)", fontsize=12)
    ax[1].set_title("Normalized Burn Ratio (NBR)", fontsize=12)
    ax[2].set_title("Normalized Difference Moisture Index (NDMI)", fontsize=12)

    ax[0].spines[["top", "right", "left"]].set_visible(False)
    ax[1].spines[["top", "right", "left"]].set_visible(False)
    ax[2].spines[["top", "right", "left"]].set_visible(False)


    fig.suptitle(f"Spectral Indices for {aoi_name}")
    plt.tight_layout()
    plt.show()

#===================================

def plot_rgb_before_after_now(input_dataset, 
                              before_date, 
                              after_date, 
                              now_date):
    """
    make a 1x3 plot of the RGB composite for before, after, and now.
    Parameters
    ----------
    input_dataset : xarray.Dataset
        Dataset containing the time series of the spectral indices and bands    
    before_date : str
        Date for the "before" image in the format 'YYYY-MM-DD'
    after_date : str
        Date for the "after" image in the format 'YYYY-MM-DD'
    now_date : str
        Date for the "current" image in the format 'YYYY-MM-DD'
    """

    composite = input_dataset[['red', 'green', 'blue']]

    _, ax = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    plt.suptitle("Qastal Maaf - RGB Composite")

    composite.sel(time=before_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[0])
    ax[0].set_title(f"Pre-Fire - {pd.to_datetime(before_date).strftime('%b %Y')}")

    ax[0].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[0].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))

    composite.sel(time=after_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[1])
    ax[1].set_title(f"Post-Fire - {pd.to_datetime(after_date).strftime('%b %Y')}")
    ax[1].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[1].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[1].sharey(ax[0])

    composite.sel(time=now_date).to_array().plot.imshow(robust=True, 
                                                        add_colorbar=False,
                                                        ax=ax[2])
    ax[2].set_title(f"Current - {pd.to_datetime(now_date).strftime('%b %Y')}")
    ax[2].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[2].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[2].sharey(ax[0])

    plt.tight_layout()
    plt.show()


# ====================================
# --- Spectral index maps and histograms
#=====================================

def plot_index_before_after_now(input_dataset, 
                        spec_index,
                        cmap,
                        before_date,
                        after_date, 
                        now_date,
                        range_min,
                        range_max):
    """
    make a 2x2 plot of the spectral index maps and histograms for 
    before, after, and now.
    Parameters
    ----------
    input_dataset : xarray.Dataset
        Dataset containing the time series of the spectral indices and bands
    spec_index : str
        Name of the spectral index to plot
    cmap : str
        Colormap to use for the plots
    before_date : str
        Date for the "before" image in the format 'YYYY-MM-DD'
    after_date : str
        Date for the "after" image in the format 'YYYY-MM-DD'
    now_date : str
        Date for the "current" image in the format 'YYYY-MM-DD'
    range_min : float
        Minimum value for the color scale
    range_max : float
        Maximum value for the color scale
    """

    _, ax = plt.subplots(2, 2, figsize=(13, 10))

    plt.suptitle(f"Qastal Maaf - {spec_index} Index", fontsize=16)

    # Share axes across the three map subplots only
    ax[0, 1].sharey(ax[0, 0])
    ax[1, 0].sharex(ax[0, 0])

    # --- Spectral index slices ---
    before_index = input_dataset[spec_index].sel(time=before_date)
    after_index = input_dataset[spec_index].sel(time=after_date)
    now_index = input_dataset[spec_index].sel(time=now_date)

    # --- Maps ---
    before_index.plot.imshow(
        cmap=cmap,
        vmin=range_min,
        vmax=range_max,
        add_colorbar=True,
        ax=ax[0, 0]
    )
    ax[0, 0].set_title(f"Pre-Fire - {pd.to_datetime(before_date).strftime('%b %Y')}")
    ax[0, 0].tick_params(axis='x', rotation=90)
    ax[0, 0].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[0, 0].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))

    after_index.plot.imshow(
        cmap=cmap,
        vmin=range_min,
        vmax=range_max,
        add_colorbar=True,
        ax=ax[1, 0]
    )
    ax[1, 0].set_title(f"Post-Fire - {pd.to_datetime(after_date).strftime('%b %Y')}")
    ax[1, 0].tick_params(axis='x', rotation=90)
    ax[1, 0].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[1, 0].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))

    now_index.plot.imshow(
        cmap=cmap,
        vmin=range_min,
        vmax=range_max,
        add_colorbar=True,
        ax=ax[0, 1]
    )
    ax[0, 1].set_title(f"Current - {pd.to_datetime(now_date).strftime('%b %Y')}")
    ax[0, 1].tick_params(axis='x', rotation=90)
    ax[0, 1].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[0, 1].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))


    # --- Histogram values ---
    before_vals = before_index.values.ravel()
    before_vals = before_vals[np.isfinite(before_vals)]

    after_vals = after_index.values.ravel()
    after_vals = after_vals[np.isfinite(after_vals)]

    now_vals = now_index.values.ravel()
    now_vals = now_vals[np.isfinite(now_vals)]

    # --- Histogram subplot ---
    hist_ax = ax[1, 1]

    hist_ax.hist(before_vals, bins=20, histtype='step', lw=2, 
                 color="#89BD86", label='Pre-Fire')
    hist_ax.hist(after_vals, bins=20, histtype='step', lw=2, 
                 color="#D56850", label='Post-Fire')
    hist_ax.hist(now_vals, bins=20, histtype='stepfilled', alpha=0.2, 
                 lw=2, ec='k', 
                 color='#D1D3D4', 
                 hatch='//',
                 label='Current')
    hist_ax.spines[["top", "right", "left"]].set_visible(False)

    hist_ax.set_xlim(range_min, range_max)
    hist_ax.set_title(f"{spec_index} Distribution")
    hist_ax.set_xlabel(f"{spec_index} Value")
    hist_ax.set_ylabel("Pixel Count")
    hist_ax.legend()
    hist_ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    # ==================

def plot_dnbr(dnbr):
    """Plot the dNBR map and histogram with summary statistics.
    Parameters
    ----------
    dnbr : xarray.DataArray
        DataArray containing the dNBR values
    """

    _, ax = plt.subplots(1, 2, figsize=(11, 4))
    dnbr.plot(cmap='BrBG_r', vmin=-.3, vmax=1.1, ax=ax[0])
    ax[0].set_title("dNBR Map")

    ax[0].xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))
    ax[0].yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}'))

    vals = dnbr.values.flatten()

    ax[1].hist(vals,
            bins=30,
            histtype='stepfilled',
            lw=1,
            ec='k',
            alpha=0.3,
            color="#9C8F69",
            )
    ax[1].set_title("dNBR Distribution")
    ax[1].set_xlabel('dNBR')
    ax[1].set_ylabel('Count')
    ax[1].grid(alpha=0.3)
    ax[1].spines[["top", "right", "left"]].set_visible(False)
    ax[1].set_xlim(-.3, 1.3)

    mean_dnbr   = float(dnbr.mean(skipna=True))
    median_dnbr = float(dnbr.median(skipna=True))
    q25, q75    = np.nanquantile(vals, [0.25, 0.75])

    ax[1].axvline(x=mean_dnbr, color="#535757",
                    linestyle='-', lw=.5, label=f'Mean: {mean_dnbr:.2f}')
    ax[1].axvline(x=median_dnbr, color="#A7630A", 
                    linestyle='--', lw=.5, label=f'Median: {median_dnbr:.2f}')
    ax[1].axvline(x=q25, color="#0AA7A7", 
                    linestyle=':', lw=.5, label=f'Q25: {q25:.2f}')
    ax[1].axvline(x=q75, color='#0AA7A7', 
                    linestyle=':', lw=.5, label=f'Q75: {q75:.2f}')

    ax[1].axvspan(q25, q75, alpha=0.1, color="#0AA7A7", label='IQR')

    ax[1].legend(fontsize=8)

    plt.tight_layout()
    plt.show()


#====================
# burn perimeter map
#====================

def plot_burn_perimeter_map(aoi_gdf, burn_perimeter, burn_perimeter_clipped):
    """Plot the burn perimeter and AOI on an interactive map using Folium.
    Parameters
    ----------
    aoi_gdf : geopandas.GeoDataFrame
        GeoDataFrame containing the geometry of the area of interest (AOI)
    burn_perimeter : geopandas.GeoDataFrame
        GeoDataFrame containing the geometry of the burn perimeter
    burn_perimeter_clipped : geopandas.GeoDataFrame
        GeoDataFrame containing the geometry of the burn perimeter clipped to the AOI
    """

    m = folium.Map(location=[35.85, 35.95],
                zoom_start=12)

    # Add basemap
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri World Imagery",
        overlay=False,
        control=True
    ).add_to(m)

    folium.GeoJson(aoi_gdf,
                name="AOI",
            style_function=lambda x: {
            "color": "orchid",
            "fillOpacity": 0.05,
            "weight": 2
        }).add_to(m)

    folium.GeoJson(
        burn_perimeter,
        name="Burn Perimeter",
        style_function=lambda x: {
            "color": "aquamarine",
            "fillOpacity": 0.1,
            "weight": 2,
            "dashArray": "5, 5"
        }
    ).add_to(m)

    folium.GeoJson(
        burn_perimeter_clipped,
        name="Burn Perimeter Clipped",
        style_function=lambda x: {
            "color": "gold",
            "fillOpacity": 0.1,
            "weight": 2,
            "dashArray": "5, 5"
        }
    ).add_to(m)

    # Add layer control (top right)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    map_path = "./maps/burn_perimeter_map.html"
    m.save(map_path)

#=====================
# plot comparison map
#=====================

def plot_comparison_map(burned_ref, 
                        burn_class_clipped, 
                        burn_perimeter_clipped, 
                        aoi_utm):

    inside_polygon = burned_ref == 1
    classified_as_burned = (burn_class_clipped.values == 1) 
    valid = ~np.isnan(burn_class_clipped.values)

    comparison = np.full_like(burned_ref, np.nan, dtype=float)
    comparison[inside_polygon & classified_as_burned & valid] = 1   # True positive
    comparison[inside_polygon & ~classified_as_burned & valid] = 2  # False negative (missed)
    comparison[~inside_polygon & classified_as_burned & valid] = 3  # False positive (over-mapped)

    from rasterio.features import shapes
    from shapely.geometry import shape

    def raster_to_geodataframe(array, transform, crs, value_col="value"):
        mask = ~np.isnan(array.astype(float))
        results = [
            {"geometry": shape(geom), value_col: val}
            for geom, val in shapes(array.astype(np.float32), mask=mask.astype(np.uint8), transform=transform)
        ]
        if not results:
            return gpd.GeoDataFrame()
        return gpd.GeoDataFrame(results, crs=crs)

    transform = burn_class_clipped.rio.transform()
    crs = burn_class_clipped.rio.crs

    comparison_gdf = raster_to_geodataframe(comparison, transform, crs)

    label_map = {1.0: "True Positive",  2.0: "False Negative", 3.0: "False Positive"}
    color_map  = {1.0: "#76d1f2",       2.0: "#f0ea7c",        3.0: "#ed855f"}
    comparison_gdf["label"] = comparison_gdf["value"].map(label_map)
    comparison_gdf["color"] = comparison_gdf["value"].map(color_map)
    comparison_gdf_4326 = comparison_gdf.to_crs("EPSG:4326")

    m = folium.Map(location=[35.825, 35.95], zoom_start=13)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Esri World Imagery"
    ).add_to(m)

    # --- One FeatureGroup per classification class ---
    for value, label in label_map.items():
        color = color_map[value]
        subset = comparison_gdf_4326[comparison_gdf_4326["value"] == value]
        if subset.empty:
            continue

        fg = folium.FeatureGroup(name=f'<span style="color:{color}">&#9632;</span> {label}')
        folium.GeoJson(
            subset,
            style_function=lambda x, c=color: {
                "fillColor": c,
                "color": "none",
                "fillOpacity": 0.6,
                "weight": 0
            }
        ).add_to(fg)
        fg.add_to(m)

    # Burn perimeter
    folium.GeoJson(
        burn_perimeter_clipped.to_crs("EPSG:4326"),
        name="Burn Perimeter (EMS)",
        style_function=lambda x: {
            "color": "white",
            "fillOpacity": 0.0,
            "weight": 1,
        }
    ).add_to(m)

    # AOI box
    folium.GeoJson(
        aoi_utm.to_crs("EPSG:4326"),
        name="AOI",
        style_function=lambda x: {
            "color": "orchid",
            "fillOpacity": 0.0,
            "weight": 2
        }
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    map_path = "./maps/comparison_map.html"
    m.save(map_path)
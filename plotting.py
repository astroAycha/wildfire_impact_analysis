"""Scripts to make plots for the wildfire impact analysis notebook."""


from duckdb import df
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_firms_frp(input_df):
    
    input_df['acq_date'] = pd.to_datetime(input_df['acq_date'])
    filtered = input_df[input_df['acq_date'] >= "2025-07-01"].copy()
    filtered['date_only'] = filtered['acq_date'].dt.date

    palette = {"l": "#87BAC3", "n": "#53629E", "h": "#473472"}

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

    _, ax = plt.subplots(figsize=(12, 5))

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
    ax.tick_params(axis='x', rotation=30)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.show()

# ====================================

def plot_index_time_series(input_dataset, 
                          spec_index: list,
                          aoi_name: str):
    """Plot 3 subplots of the time series for the specified spectral index."""

    fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    ndvi_ts = input_dataset[spec_index[0]].mean(dim=['x', 'y'])
    ndvi_ts.plot(ax=ax[0], linestyle='-', lw=2, color='forestgreen')

    nbr_ts = input_dataset[spec_index[1]].mean(dim=['x', 'y'])
    nbr_ts.plot(ax=ax[1], linestyle='-', lw=2, color='goldenrod')

    ndmi_ts = input_dataset[spec_index[2]].mean(dim=['x', 'y'])
    ndmi_ts.plot(ax=ax[2], linestyle='-', lw=2 , color='dodgerblue')

    ax[0].grid(alpha=0.3)
    ax[1].grid(alpha=0.3)
    ax[2].grid(alpha=0.3)

    ax[0].spines[["top", "right"]].set_visible(False)
    ax[1].spines[["top", "right"]].set_visible(False)
    ax[2].spines[["top", "right"]].set_visible(False)

    ax[0].ticklabel_format(style='plain', axis='both')
    ax[1].ticklabel_format(style='plain', axis='both')
    ax[2].ticklabel_format(style='plain', axis='both')

    
    fig.suptitle(f"Time Series of NDVI, NBR, and NDMI for {aoi_name}")
    plt.tight_layout()
    plt.show()


def plot_rgb_before_after_now(input_dataset, 
                              before_date, 
                              after_date, 
                              now_date):
    """
    make a 1x3 plot of the RGB composite for before, after, and now.
    """

    composite = input_dataset[['red', 'green', 'blue']]

    _, ax = plt.subplots(1, 3, figsize=(12, 4), sharex=True)
    plt.suptitle("Qastal Maaf - RGB Composite")

    composite.sel(time=before_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[0])
    ax[0].set_title("Before Fire")
    ax[0].ticklabel_format(style='plain', axis='both')

    composite.sel(time=after_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[1])
    ax[1].set_title("After Fire")
    ax[1].ticklabel_format(style='plain', axis='both')

    composite.sel(time=now_date).to_array().plot.imshow(robust=True, 
                                                        add_colorbar=False,
                                                        ax=ax[2])
    ax[2].set_title("Now")
    ax[2].ticklabel_format(style='plain', axis='both')

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
    """

    _, ax = plt.subplots(2, 2, figsize=(13, 9))

    plt.suptitle(f"Qastal Maaf - {spec_index} Index", fontsize=16)

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
    ax[0, 0].set_title("Before Fire")

    after_index.plot.imshow(
        cmap=cmap,
        vmin=range_min,
        vmax=range_max,
        add_colorbar=True,
        ax=ax[0, 1]
    )
    ax[0, 1].set_title("After Fire")

    now_index.plot.imshow(
        cmap=cmap,
        vmin=range_min,
        vmax=range_max,
        add_colorbar=True,
        ax=ax[1, 0]
    )
    ax[1, 0].set_title("Now")

    # --- Histogram values ---
    before_vals = before_index.values.ravel()
    before_vals = before_vals[np.isfinite(before_vals)]

    after_vals = after_index.values.ravel()
    after_vals = after_vals[np.isfinite(after_vals)]

    now_vals = now_index.values.ravel()
    now_vals = now_vals[np.isfinite(now_vals)]

    # --- Histogram subplot ---
    hist_ax = ax[1, 1]

    hist_ax.hist(before_vals, bins=20, histtype='step', lw=2, color='#86B0BD', label='Pre-Fire')
    hist_ax.hist(after_vals, bins=20, histtype='step', lw=2, color='#E2A16F', label='Post-Fire')
    hist_ax.hist(now_vals, bins=20, histtype='stepfilled', alpha=0.2, lw=2, ec='k', color='#D1D3D4', label='Current')

    hist_ax.set_xlim(range_min, range_max)
    hist_ax.set_title(f"{spec_index} Distribution")
    hist_ax.set_xlabel(f"{spec_index} Value")
    hist_ax.set_ylabel("Pixel Count")
    hist_ax.legend()

    plt.tight_layout()
    plt.show()
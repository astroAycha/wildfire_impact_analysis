"""Scripts to make plots for the tracking environment notebook."""


import numpy as np
import matplotlib.pyplot as plt


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

    fig, ax = plt.subplots(1, 3, figsize=(12, 4), sharex=True)
    plt.suptitle("Qastal Maaf - RGB Composite")

    composite.sel(time=before_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[0])
    ax[0].set_title("Before Fire")

    composite.sel(time=after_date).to_array().plot.imshow(robust=True,
                                                        add_colorbar=False, 
                                                        ax=ax[1])
    ax[1].set_title("After Fire")

    composite.sel(time=now_date).to_array().plot.imshow(robust=True, 
                                                        add_colorbar=False,
                                                        ax=ax[2])
    ax[2].set_title("Now")

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
                        now_date):
    """
    make a 2x2 plot of the spectral index maps and histograms for 
    before, after, and now.
    """

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))

    plt.suptitle(f"Qastal Maaf - {spec_index} Index", fontsize=16)

    # --- Spectral index slices ---
    before_index = input_dataset[spec_index].sel(time=before_date)
    after_index = input_dataset[spec_index].sel(time=after_date)
    now_index = input_dataset[spec_index].sel(time=now_date)

    # --- Maps ---
    before_index.plot.imshow(
        cmap=cmap,
        vmin=0,
        vmax=1,
        add_colorbar=True,
        ax=ax[0, 0]
    )
    ax[0, 0].set_title("Before Fire")

    after_index.plot.imshow(
        cmap=cmap,
        vmin=0,
        vmax=1,
        add_colorbar=True,
        ax=ax[0, 1]
    )
    ax[0, 1].set_title("After Fire")

    now_index.plot.imshow(
        cmap=cmap,
        vmin=0,
        vmax=1,
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

    hist_ax.hist(before_vals, bins=20, histtype='step', lw=1, color='darkseagreen', label='Pre-Fire')
    hist_ax.hist(after_vals, bins=20, histtype='step', lw=1, color='rosybrown', label='Post-Fire')
    hist_ax.hist(now_vals, bins=20, histtype='stepfilled', alpha=0.2, lw=2, ec='k', color='slategray', label='Current')

    # hist_ax.set_xlim(-.59, .59)
    hist_ax.set_title(f"{spec_index} Distribution")
    hist_ax.set_xlabel(f"{spec_index} Value")
    hist_ax.set_ylabel("Pixel Count")
    hist_ax.legend()

    plt.tight_layout()
    plt.show()
"""Fetch FIRMS data for a given bounding box and date range"""

from datetime import datetime, timedelta
import pandas as pd
import os
import dotenv
dotenv.load_dotenv()


def fetch_firms(source, 
                bbox, 
                start_date, 
                end_date):
    """Fetch FIRMS data for a given bounding box and date range, 
    handling API limits by splitting requests into 5-day intervals
    """
    firms_api_key = os.getenv("MAP_KEY")
    
    all_dfs = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Convert bbox to string format for API
    bbox_str = ",".join(map(str, bbox))
    print(f"Fetching FIRMS data from {start_date} to {end_date} for bbox: {bbox_str}")

    while current < end:
        days_remaining = (end - current).days
        day_range = min(5, days_remaining)

        for src in source:
            url = (
                f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
                f"{firms_api_key}/{src}/{bbox_str}/{day_range}/{current.strftime('%Y-%m-%d')}"
            )
            try:
                df = pd.read_csv(url)
                if not df.empty:
                    all_dfs.append(df)
                    print(f"[{src}] {current.strftime('%Y-%m-%d')} — {len(df)} rows")
            except Exception as e:
                print(f"Failed [{src}] {current.strftime('%Y-%m-%d')}: {e}")

        current += timedelta(days=day_range)  # ← outside the for loop

    if all_dfs:
        # Concatenate all dataframes and drop duplicates (in case of overlapping data)
        return pd.concat(all_dfs).drop_duplicates(subset=["latitude", "longitude", "acq_date", "acq_time"]) 
    return pd.DataFrame()

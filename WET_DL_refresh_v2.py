import pandas as pd
import numpy as np
import warnings
import json
from datetime import date, timedelta
from pathlib import Path
import streamlit as st
from supabase import create_client

warnings.filterwarnings('ignore')

# ── Config ────────────────────────────────────────────────────────────────────
client = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
user = "cpetrosi"
path = Path(f"C:/Users/{user}/Box/DATA_CUBBIES/Mina_S/Datalogger_Report_Files/WET_Stations")
sites = ["CAP_001", "CAP_002", "WIN_001", "OAK_001", "CHW_001", "GLE_001", "BAR_002"]

cols = [
    "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg", "VPD_Avg",
    "T_SOIL_Avg", "T_CANOPY_Avg", "WP_Avg", "SPEC_RED_REFL_Avg", "SPEC_NIR_REFL_Avg",
    "NDVI_Avg", "ARVI2_Avg", "IPVI_Avg", "DVI_Avg", "SR_Avg", "MSR_Avg",
    "SWC_1_1_1_Avg", "SWC_1_2_1_Avg", "SWC_1_3_1_Avg", "SWC_1_4_1_Avg", "SWC_1_5_1_Avg",
    "SWC_1_6_1_Avg", "SWC_1_7_1_Avg", "SWC_1_8_1_Avg", "SWC_1_9_1_Avg",
    "Ka_1_1_1_Avg",  "Ka_1_2_1_Avg",  "Ka_1_3_1_Avg",  "Ka_1_4_1_Avg",  "Ka_1_5_1_Avg",
    "Ka_1_6_1_Avg",  "Ka_1_7_1_Avg",  "Ka_1_8_1_Avg",  "Ka_1_9_1_Avg",
    "TS_1_1_1_Avg",  "TS_1_2_1_Avg",  "TS_1_3_1_Avg",  "TS_1_4_1_Avg",  "TS_1_5_1_Avg",
    "TS_1_6_1_Avg",  "TS_1_7_1_Avg",  "TS_1_8_1_Avg",  "TS_1_9_1_Avg",
    "SEC_1_1_1_Avg", "SEC_1_2_1_Avg", "SEC_1_3_1_Avg", "SEC_1_4_1_Avg", "SEC_1_5_1_Avg",
    "SEC_1_6_1_Avg", "SEC_1_7_1_Avg", "SEC_1_8_1_Avg", "SEC_1_9_1_Avg",
    "SW_IN_Avg", "SW_OUT_Avg", "LW_IN_Avg", "LW_OUT_Avg", "NETRAD_Avg",
    "PPFD_BC_IN_Avg", "PPFD_IN_Avg", "Water_Vol_Scan_Tot", "Flow_GPM_Avg", "Flow_GPM_Max"
]
avg_dict = {col: col.replace("_Avg", "") for col in cols}

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_dat(filepath: Path) -> pd.DataFrame:
    """Read a Campbell Scientific .dat file, dropping the RECORD column."""
    df = pd.read_csv(filepath, header=[0], skiprows=[0, 2, 3])
    return df.drop(columns=["RECORD"], errors="ignore")

def safe_merge(left: pd.DataFrame, right: pd.DataFrame, on="TIMESTAMP") -> pd.DataFrame:
    """Outer merge, dropping overlapping non-key columns from the right df to prevent duplication."""
    overlap = set(left.columns) & set(right.columns) - {on}
    if overlap:
        print(f"  Dropping overlapping columns from right df: {sorted(overlap)}")
        right = right.drop(columns=list(overlap))
    return pd.merge(left, right, on=on, how="outer")

# ── Main loop ─────────────────────────────────────────────────────────────────
all_site_dfs = []

for site in sites:
    print(f"{site}")
    dfs_to_merge = []

    for name in sorted(path.glob(f"*{site}*.dat")):  # sorted for deterministic order
        suffix = name.stem.split("_")[-1]
        if suffix in ("General", "HR", "IRT"):
            continue
        print(f"  Reading: {name.name}")
        dfs_to_merge.append(read_dat(name))

    if not dfs_to_merge:
        print(f"  WARNING: No data files found for {site}, skipping.")
        continue

    # Merge all sensor files for this site
    cur_df = dfs_to_merge[0]
    for df in dfs_to_merge[1:]:
        cur_df = safe_merge(cur_df, df)

    # Merge General file — only bring in columns not already present
    general_path = path / f"{site}_T_General.dat"
    if general_path.exists():
        general_df = read_dat(general_path)
        new_cols = list(set(general_df.columns) - set(cur_df.columns)) + ["TIMESTAMP"]
        cur_df = safe_merge(cur_df, general_df[new_cols])
    else:
        print(f"  WARNING: General file not found for {site}")

    cur_df["site"] = site
    cur_df.to_csv(path / f"C:/Users/{user}/Downloads/{site}_peek.csv", index=False)
    all_site_dfs.append(cur_df)

# ── Combine all sites ─────────────────────────────────────────────────────────
fin_df = pd.concat(all_site_dfs, ignore_index=True)  # concat rows, not merge!
fin_df = fin_df.rename(columns=avg_dict)
fin_df = fin_df.drop_duplicates()

# ── Filter to last 30 days ────────────────────────────────────────────────────
fin_df["TIMESTAMP"] = pd.to_datetime(fin_df["TIMESTAMP"])
cutoff = pd.Timestamp(date.today() - timedelta(days=30))
fin_df = fin_df[fin_df["TIMESTAMP"] > cutoff].reset_index(drop=True)

fin_df.to_csv(f"C:/Users/{user}/Downloads/wet_dashboard_data_test.csv")
# ── Upload to Supabase ────────────────────────────────────────────────────────
client.table("wet_dashboard").upsert({
    "id": 500,
    "data_name": "all_data",
    "data": json.loads(fin_df.to_json())
}).execute()

print(f"Done. Uploaded {len(fin_df)} rows across {fin_df['site'].nunique()} sites.")
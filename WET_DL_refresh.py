import fnmatch
import pandas as pd
import datetime
import os
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import numpy as np
import requests
import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import numpy as np
from pathlib import Path
import os
import sys
import shutil
import geopandas as gpd
from IPython.display import display
import plotly
import plotly.express as px
from shapely.geometry import Point
import datetime


avg_dict = dict()

cols = ["BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg", "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg", "WP_Avg",
        "SPEC_RED_REFL_Avg", "SPEC_NIR_REFL_Avg", "NDVI_Avg", "ARVI2_Avg", "IPVI_Avg", "DVI_Avg", "SR_Avg", "MSR_Avg",
        "SWC_1_1_1_Avg", "SWC_1_2_1_Avg", "SWC_1_3_1_Avg", "SWC_1_4_1_Avg", "SWC_1_5_1_Avg", "SWC_1_6_1_Avg",
        "SWC_1_7_1_Avg", "SWC_1_8_1_Avg", "SWC_1_9_1_Avg", "Ka_1_1_1_Avg", "Ka_1_2_1_Avg", "Ka_1_3_1_Avg", "Ka_1_4_1_Avg",
        "Ka_1_5_1_Avg", "Ka_1_6_1_Avg", "Ka_1_7_1_Avg", "Ka_1_8_1_Avg", "Ka_1_9_1_Avg", "TS_1_1_1_Avg", "TS_1_2_1_Avg",
        "TS_1_3_1_Avg", "TS_1_4_1_Avg", "TS_1_5_1_Avg", "TS_1_6_1_Avg", "TS_1_7_1_Avg", "TS_1_8_1_Avg", "TS_1_9_1_Avg",
        "SEC_1_1_1_Avg", "SEC_1_2_1_Avg", "SEC_1_3_1_Avg", "SEC_1_4_1_Avg", "SEC_1_5_1_Avg", "SEC_1_6_1_Avg",
        "SEC_1_7_1_Avg", "SEC_1_8_1_Avg", "SEC_1_9_1_Avg", "SW_IN_Avg", "SW_OUT_Avg", "LW_IN_Avg", "LW_OUT_Avg", "NETRAD_Avg",
        "PPFD_BC_IN_Avg", "PPFD_IN_Avg"]

for param_name in cols:
  avg_dict[param_name] = param_name.replace("_Avg", "")

site_dict = {
  "WET01": "CAP_001",
  "WET02": "CAP_002",
  "WET03": "WIN_001",
  "WET04": "OAK_001"
}

gen_df = pd.DataFrame()
ind_df = pd.DataFrame()
soil_df = pd.DataFrame()
rad_df = pd.DataFrame()

sites = ["WET01", "WET02", "WET03", "WET04"]
path = Path("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/")
for i in range(0, len(sites)):
  for name in path.glob("*"+sites[i]+"*.dat"):
    if str(name).split(".")[0].split("_")[-1] == "General":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      if sites[i] == "WET01":
        print(temp)
        temp = temp[["TIMESTAMP", "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg",
                        "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg", "WP_Avg", "PPFD_BC_IN_Avg", "PPFD_IN_Avg"]]
      else:
        temp = temp[["TIMESTAMP", "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg",
                        "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg"]]
      temp["site"] = site_dict[sites[i]]
      gen_df = pd.concat([gen_df, temp])
        
    elif str(name).split(".")[0].split("_")[-1] == "Indices":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      temp = temp[["TIMESTAMP", "SPEC_RED_REFL_Avg", "SPEC_NIR_REFL_Avg", "NDVI_Avg", "ARVI2_Avg",
                "IPVI_Avg", "DVI_Avg", "SR_Avg", "MSR_Avg"]]
      temp["site"] = site_dict[sites[i]]
      ind_df = pd.concat([ind_df, temp])

    elif str(name).split(".")[0].split("_")[-1] == "SOILVUE":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      temp = temp[["TIMESTAMP", "SWC_1_1_1_Avg", "SWC_1_2_1_Avg", "SWC_1_3_1_Avg", "SWC_1_4_1_Avg",
                "SWC_1_5_1_Avg", "SWC_1_6_1_Avg", "SWC_1_7_1_Avg", "SWC_1_8_1_Avg", "SWC_1_9_1_Avg",
                "Ka_1_1_1_Avg", "Ka_1_2_1_Avg", "Ka_1_3_1_Avg", "Ka_1_4_1_Avg",
                "Ka_1_5_1_Avg", "Ka_1_6_1_Avg", "Ka_1_7_1_Avg", "Ka_1_8_1_Avg", "Ka_1_9_1_Avg",
                "TS_1_1_1_Avg", "TS_1_2_1_Avg", "TS_1_3_1_Avg", "TS_1_4_1_Avg",
                "TS_1_5_1_Avg", "TS_1_6_1_Avg", "TS_1_7_1_Avg", "TS_1_8_1_Avg", "TS_1_9_1_Avg",
                "SEC_1_1_1_Avg", "SEC_1_2_1_Avg", "SEC_1_3_1_Avg", "SEC_1_4_1_Avg",
                "SEC_1_5_1_Avg", "SEC_1_6_1_Avg", "SEC_1_7_1_Avg", "SEC_1_8_1_Avg", "SEC_1_9_1_Avg"]]
      temp["site"] = site_dict[sites[i]]
      soil_df = pd.concat([soil_df, temp])

    elif str(name).split(".")[0].split("_")[-1] == "Rad":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      temp = temp[["TIMESTAMP", "SW_IN_Avg", "SW_OUT_Avg",
                "LW_IN_Avg", "LW_OUT_Avg", "NETRAD_Avg"]]
      temp["site"] = site_dict[sites[i]]
      rad_df = pd.concat([rad_df, temp])
    

p1 = gen_df.merge(ind_df, on = ["TIMESTAMP", "site"], how = "outer")
p2 = rad_df.merge(soil_df, on = ["TIMESTAMP", "site"], how = "outer")

fin = p1.merge(p2, on = ["TIMESTAMP", "site"], how = "outer")

for col in fin.columns:
  if col not in ["TIMESTAMP", "site"]:
    fin = fin.rename(columns = {col: avg_dict[col]})


fin.to_csv("C:/Users/cpetrosi/Documents/GitHub/WET-Dashboard/Static_Files/WET_dashboard_data.csv")

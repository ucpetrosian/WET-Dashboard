import fnmatch
import pandas as pd
import datetime
import os
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import numpy as np
import requests
import numpy as np
from pathlib import Path
import os
from IPython.display import display
import datetime
import warnings
from supabase import create_client
import json
import streamlit as st
warnings.filterwarnings('ignore')

client = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

user = "cpetrosi"

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

sites = ["CAP_001", "CAP_002", "WIN_001", "OAK_001", "CHW_001", "GLE_001"]

path = Path(f"C:/Users/{user}/Box/DATA_CUBBIES/Mina_S/Datalogger_Report_Files/WET_Stations")

fin_df = pd.DataFrame()
for site in sites:
  cur_df = pd.DataFrame()
  for name in path.glob("*"+site+"*.dat"):
    if str(name).split(".")[0].split("_")[-1] == "General":
      continue
    else:
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      temp = temp.drop("RECORD", axis = 1)
    if cur_df.empty == True:
      cur_df = temp
    else:
      cur_df = pd.merge(cur_df, temp, on = "TIMESTAMP", how = "outer")
    
  temp = pd.read_csv(f"{path}/{site}_T_General.dat", header = [0], skiprows = [0,2,3])
  temp = temp.drop("RECORD", axis = 1)
  port_cols = list(set(temp.columns) - set(cur_df.columns)) + ["TIMESTAMP"]
  cur_df = pd.merge(cur_df, temp[port_cols], on = "TIMESTAMP", how = "outer")
  cur_df["site"] = site
  fin_df = pd.concat([fin_df, cur_df], ignore_index=True)

for col in fin_df.columns:
  if col not in ["TIMESTAMP", "site"]:
    fin_df = fin_df.rename(columns = {col: avg_dict[col]})
fin_df = fin_df.drop_duplicates()


fin_df["TIMESTAMP"] = pd.to_datetime(fin_df["TIMESTAMP"])
last_month = date.today() - timedelta(days=30)
last_month = np.datetime64(last_month)
fin_df = fin_df[fin_df["TIMESTAMP"] > last_month]
fin_df.reset_index(inplace=True)
fin_df = fin_df.drop("index", axis = 1)

json_data = json.loads(fin_df.to_json())
client.table("wet_dashboard").upsert({
    "id": 500,
    "data_name": "all_data",
    "data": json_data
}).execute()
    

    
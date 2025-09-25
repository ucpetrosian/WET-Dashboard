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

template = pd.read_csv(f"C:/Users/{user}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/WETS/CAP_001_T_General.dat", header = [0], skiprows = [0,2,3])
template = pd.to_datetime(template["TIMESTAMP"])
fin_df = pd.DataFrame()

sites = ["CAP_001", "CAP_002", "WIN_001", "OAK_001"]
path = Path(f"C:/Users/{user}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/WETS")
for i in range(0, len(sites)):
  gen_df = template
  ind_df = template
  soil_df = template
  rad_df = template
  flora_df = pd.DataFrame()
  indices = False
  for name in path.glob("*"+sites[i]+"*.dat"):
    if str(name).split(".")[0].split("_")[-1] == "General":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      if sites[i] == "CAP_001":
        gen_df = temp[["TIMESTAMP", "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg",
                        "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg", "PPFD_BC_IN_Avg", "PPFD_IN_Avg"]]
      elif sites[i] == "CAP_002" or sites[i] == "WIN_001":
        gen_df = temp[["TIMESTAMP", "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg",
                        "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg", "SPEC_RED_REFL_Avg", "SPEC_NIR_REFL_Avg",
                        "NDVI_Avg", "ARVI2_Avg", "IPVI_Avg", "DVI_Avg", "SR_Avg", "MSR_Avg"]]
      else:
        gen_df = temp[["TIMESTAMP", "BattV_Avg", "RH_Avg", "TA_Avg", "e_sat_probe_Avg", "e_probe_Avg",
                        "VPD_Avg", "T_SOIL_Avg", "T_CANOPY_Avg"]]
      gen_df["TIMESTAMP"] = pd.to_datetime(gen_df["TIMESTAMP"])
    elif str(name).split(".")[0].split("_")[-1] == "Indices":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      ind_df = temp[["TIMESTAMP", "SPEC_RED_REFL_Avg", "SPEC_NIR_REFL_Avg", "NDVI_Avg", "ARVI2_Avg",
                "IPVI_Avg", "DVI_Avg", "SR_Avg", "MSR_Avg"]]
      ind_df["TIMESTAMP"] = pd.to_datetime(ind_df["TIMESTAMP"])
      indices = True

    elif str(name).split(".")[0].split("_")[-1] == "SOILVUE":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      soil_df = temp[["TIMESTAMP", "SWC_1_1_1_Avg", "SWC_1_2_1_Avg", "SWC_1_3_1_Avg", "SWC_1_4_1_Avg",
                "SWC_1_5_1_Avg", "SWC_1_6_1_Avg", "SWC_1_7_1_Avg", "SWC_1_8_1_Avg", "SWC_1_9_1_Avg",
                "Ka_1_1_1_Avg", "Ka_1_2_1_Avg", "Ka_1_3_1_Avg", "Ka_1_4_1_Avg",
                "Ka_1_5_1_Avg", "Ka_1_6_1_Avg", "Ka_1_7_1_Avg", "Ka_1_8_1_Avg", "Ka_1_9_1_Avg",
                "TS_1_1_1_Avg", "TS_1_2_1_Avg", "TS_1_3_1_Avg", "TS_1_4_1_Avg",
                "TS_1_5_1_Avg", "TS_1_6_1_Avg", "TS_1_7_1_Avg", "TS_1_8_1_Avg", "TS_1_9_1_Avg",
                "SEC_1_1_1_Avg", "SEC_1_2_1_Avg", "SEC_1_3_1_Avg", "SEC_1_4_1_Avg",
                "SEC_1_5_1_Avg", "SEC_1_6_1_Avg", "SEC_1_7_1_Avg", "SEC_1_8_1_Avg", "SEC_1_9_1_Avg"]]
      soil_df["TIMESTAMP"] = pd.to_datetime(soil_df["TIMESTAMP"])

    elif str(name).split(".")[0].split("_")[-1] == "Rad":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      rad_df = temp[["TIMESTAMP", "SW_IN_Avg", "SW_OUT_Avg",
                "LW_IN_Avg", "LW_OUT_Avg", "NETRAD_Avg"]]
      rad_df["TIMESTAMP"] = pd.to_datetime(rad_df["TIMESTAMP"])
    elif str(name).split(".")[0].split("_")[-1] == "FLORAP":
      temp = pd.read_csv(name, header = [0], skiprows = [0,2,3])
      flora_df = temp[["TIMESTAMP", "WP_Avg"]]
      flora_df["TIMESTAMP"] = pd.to_datetime(flora_df["TIMESTAMP"])
  if indices == True:
    print(i)
    p1 = gen_df.merge(ind_df, on = ["TIMESTAMP"], how = "outer")
    p1 = p1.merge(flora_df, on = ["TIMESTAMP"], how = "outer")
    p2 = rad_df.merge(soil_df, on = ["TIMESTAMP"], how = "outer")
    fin = p1.merge(p2, on = ["TIMESTAMP"], how = "outer")
    fin["site"] = sites[i]
    fin_df = pd.concat([fin_df, fin])
  elif i != 1:
    p1 = gen_df.merge(flora_df, on = ["TIMESTAMP"], how = "outer")
    p2 = rad_df.merge(soil_df, on = ["TIMESTAMP"], how = "outer")
    fin = p1.merge(p2, on = ["TIMESTAMP"], how = "outer")
    fin["site"] = sites[i]
    fin_df = pd.concat([fin_df, fin])
  else:
    p1 = gen_df.merge(flora_df, on = ["TIMESTAMP"], how = "outer")
    p2 = p1.merge(soil_df, on = ["TIMESTAMP"], how = "outer")
    fin = p2
    fin["site"] = sites[i]
    fin_df = pd.concat([fin_df, fin])

for col in fin.columns:
  if col not in ["TIMESTAMP", "site"]:
    fin_df = fin_df.rename(columns = {col: avg_dict[col]})


fin_df.to_csv(f"C:/Users/{user}/Documents/Github/WET-Dashboard/Static_Files/WET_dashboard_data.csv")

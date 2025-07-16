import fnmatch
import pandas as pd
import datetime
import os
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import requests
import folium as fl
from streamlit_folium import st_folium
import streamlit as st
import numpy as np
import os
import glob
import geopandas as gpd
from IPython.display import display
import plotly
import plotly.express as px
from shapely.geometry import Point
import datetime

st.set_page_config(layout = "wide")

st.title("WET Dashboard Demo")

VAC_flux = pd.read_csv("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_Flux_Notes.dat", header = [0], skiprows = [0,2,3])
VAC_soil = pd.read_csv("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
VAC_soil= VAC_soil.reset_index(drop=True)
VAC_soil.TIMESTAMP= pd.to_datetime(VAC_soil['TIMESTAMP'], format= 'mixed')
VAC_soil["station_id"] = "VAC_001"

OLA_soil = pd.read_csv("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/OLA_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
OLA_soil= OLA_soil.reset_index(drop=True)
OLA_soil.TIMESTAMP= pd.to_datetime(OLA_soil['TIMESTAMP'], format= 'mixed')
OLA_soil["station_id"] = "OLA_001"

all_soil = pd.concat([VAC_soil, OLA_soil], ignore_index=True)

def return_options(param):
    if param == "VWC":
        return ["VWC_5cm_Avg", "VWC_10cm_Avg", "VWC_20cm_Avg", "VWC_30cm_Avg", "VWC_40cm_Avg", "VWC_50cm_Avg",
                            "VWC_60cm_Avg", "VWC_75cm_Avg", "VWC_100cm_Avg"]
    elif param == "Ka":
        return ["Ka_5cm_Avg", "Ka_10cm_Avg", "Ka_20cm_Avg", "Ka_30cm_Avg", "Ka_40cm_Avg", "Ka_50cm_Avg",
                      "Ka_60cm_Avg", "Ka_75cm_Avg", "Ka_100cm_Avg"]
    elif param == "T":
        return ["T_5cm_Avg", "T_10cm_Avg", "T_20cm_Avg", "T_30cm_Avg", "T_40cm_Avg", "T_50cm_Avg",
                      "T_60cm_Avg", "T_75cm_Avg", "T_100cm_Avg"]
    elif param == "BulkEC":
        return ["BulkEC_5cm_Avg", "BulkEC_10cm_Avg", "BulkEC_20cm_Avg", "BulkEC_30cm_Avg", "BulkEC_40cm_Avg", "BulkEC_50cm_Avg",
                      "BulkEC_60cm_Avg", "BulkEC_75cm_Avg", "BulkEC_100cm_Avg"]



st.sidebar.header("Plot Adjustments")

site = st.sidebar.selectbox("Select Station:",
                            ["VAC_001", "OLA_001"], index = 0)

param_type = st.sidebar.selectbox("Select Parameter Type:",
                                  ["VWC", "Ka", "T", "BulkEC"], index = 0)

option = st.sidebar.multiselect("Select Measurement:",
                                return_options(param_type))


st.plotly_chart(px.line(all_soil.loc[all_soil.station_id == site], x = "TIMESTAMP", y = option, labels = {"value": param_type}))

st.dataframe(data = all_soil.loc[all_soil.station_id == site, ["TIMESTAMP"] + option])
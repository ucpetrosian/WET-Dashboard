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

user_path = "cpetrosi"

VAC_flux = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_Flux_Notes.dat", header = [0], skiprows = [0,2,3])
VAC_soil = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
VAC_soil= VAC_soil.reset_index(drop=True)
VAC_soil.TIMESTAMP= pd.to_datetime(VAC_soil['TIMESTAMP'], format= 'mixed')
VAC_soil["station_id"] = "VAC_001"

OLA_soil = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/OLA_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
OLA_soil= OLA_soil.reset_index(drop=True)
OLA_soil.TIMESTAMP= pd.to_datetime(OLA_soil['TIMESTAMP'], format= 'mixed')
OLA_soil["station_id"] = "OLA_001"

range_names = pd.read_csv("C:/Users/cpetrosi/Documents/GitHub/WET-Dashboard/Static_Files/MET_station_ranges.csv")

all_soil = pd.concat([VAC_soil, OLA_soil], ignore_index=True)
all_soil = all_soil.rename(columns = {"VWC_10cm_Avg": "SWC_1_1_1"})

def return_options(sensor, df):
    return df.loc[df.Sensor == sensor].Variable_Name.unique()



st.sidebar.header("Plot Adjustments")

site = st.sidebar.selectbox("Select Station:",
                            ["VAC_001", "OLA_001"], index = 0)

sensor_type = st.sidebar.selectbox("Select Sensor Type:",
                                  range_names.Sensor.unique(), index = 0)

option = st.sidebar.multiselect("Select Measurement:",
                                return_options(sensor_type, range_names))


st.plotly_chart(px.line(all_soil.loc[all_soil.station_id == site], x = "TIMESTAMP", y = option, labels = {"value": " / ".join(option)},
                        range_y = [min(range_names.loc[range_names.Variable_Name.isin(option)].Range_Low),
                                   max(range_names.loc[range_names.Variable_Name.isin(option)].Range_High)]
                                   ))

st.dataframe(data = all_soil.loc[all_soil.station_id == site, ["TIMESTAMP"] + option])
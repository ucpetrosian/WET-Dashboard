import fnmatch
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
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
import os
import glob
import geopandas as gpd
from IPython.display import display
import plotly
import plotly.express as px
from shapely.geometry import Point
import datetime



## Default makes elements wide on dashboard
st.set_page_config(layout = "wide")  


st.title("WET Dashboard Demo")

user_path = "cpetrosi"

range_names = pd.read_csv("C:/Users/cpetrosi/Documents/GitHub/WET-Dashboard/Static_Files/MET_station_ranges.csv")

## Call each tower DF, set up proper datetime column, combine at end

VAC_flux = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_Flux_Notes.dat", header = [0], skiprows = [0,2,3])
VAC_soil = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
VAC_soil= VAC_soil.reset_index(drop=True)
VAC_soil.TIMESTAMP= pd.to_datetime(VAC_soil['TIMESTAMP'], format= 'mixed')
VAC_soil["station_id"] = "VAC_001"

OLA_soil = pd.read_csv(f"C:/Users/{user_path}/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/OLA_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
OLA_soil= OLA_soil.reset_index(drop=True)
OLA_soil.TIMESTAMP= pd.to_datetime(OLA_soil['TIMESTAMP'], format= 'mixed')
OLA_soil["station_id"] = "OLA_001"

all_soil = pd.concat([VAC_soil, OLA_soil], ignore_index=True)
all_soil = all_soil.rename(columns = {"VWC_10cm_Avg": "SWC_1_1_1",
                                      "VWC_20cm_Avg": "SWC_1_2_1",
                                      "VWC_30cm_Avg": "SWC_1_3_1"}) ## Wont need rename once real data comes through


## Only keeps data from last 30 days
last_month = date.today() - timedelta(days=30)
last_month = np.datetime64(last_month)
all_soil = all_soil[all_soil["TIMESTAMP"] > last_month]

## Sets up dictionary to add units to legend in plot,
## Also sets up range dictionary
unit_dict = dict()
range_dict = dict()
for name in range_names.Variable_Name.unique():
    unit_dict[name] = name + " (" + range_names.loc[range_names.Variable_Name == name, "Units"].iloc[0] + ")"
    low = range_names.loc[range_names.Variable_Name == name, ["Range_Low"]].iloc[0]
    high = range_names.loc[range_names.Variable_Name == name, ["Range_High"]].iloc[0]
    range_dict[name] = (float(low), float(high))


## When called, fills multiselect with options based on sensor
def return_options(sensor, df):
    return df.loc[df.Sensor == sensor].Variable_Name.unique()

## Trims main DF to only selected tower, then renames columns to add units
def update_df(df, site, option, unit_dict = unit_dict):
    plot_df = df.loc[df.station_id == site]
    for col in option:
        plot_df = plot_df.rename(columns = {col: unit_dict[col]})
    return plot_df

## Adds units to columns to pass through plot
def update_col_names(option, unit_dict = unit_dict):
    out = []
    for name in option:
        out.append(unit_dict[name])
    return out

## Create and name sidebar
st.sidebar.header("Plot Adjustments")

## Puts station selector in sidebar, returns selected station
site = st.sidebar.selectbox("Select Station:",
                            ["VAC_001", "OLA_001"], index = 0)

## Puts sensor selector in sidebar, returns selected sensor, options populated by range_names csv
sensor_type = st.sidebar.selectbox("Select Sensor Type:",
                                  range_names.Sensor.unique(), index = 0)

## Puts parameter selector in sidebar, fills option via aforementioned function,
## returns parameters to be put in plot
option = st.sidebar.multiselect("Select Measurement:",
                                return_options(sensor_type, range_names))

## Uses plotly chart to plot data, uses aforementioned functions for label/DF setup
## Y-axis labels set using passed columns via multiselector
## Range is set using range_names csv
st.plotly_chart(px.line(update_df(all_soil, site, option), x = "TIMESTAMP", y = update_col_names(option), labels = {"value": " / ".join(option)},
                        range_y = [min(range_names.loc[range_names.Variable_Name.isin(option)].Range_Low),
                                max(range_names.loc[range_names.Variable_Name.isin(option)].Range_High)]
                                ))


## Grabs ranges for relevant columns, highlights any values that fall outside of range for given column
def highlight_outliers(row):
    styles = []
    for col in row.index:
        if col != "TIMESTAMP":
            min_val, max_val = range_dict[col]
            if float(row[col]) < min_val or float(row[col]) > max_val:
                styles.append('background-color: #930707')
            else:
                styles.append('')
        else:
            styles.append("")
    return styles

## Trims DF based on station, applies style function
def dataframe_styler(df):
    ret_df = df.loc[df.station_id == site, ["TIMESTAMP"] + option]
    return ret_df.style.apply(highlight_outliers, axis = 1)


st.dataframe(data = dataframe_styler(all_soil))
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import pandas as pd
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import numpy as np
import requests, io
import streamlit as st
import numpy as np
import os
from IPython.display import display
import plotly
import plotly.express as px


## Default makes elements wide on dashboard
st.set_page_config(layout = "wide")  


st.title("WET Dashboard")

@st.cache_resource
def import_data():
  github_session = requests.Session()
  csv_url = 'https://raw.githubusercontent.com/ucpetrosian/WET-Dashboard/master/Static_Files/WET_dashboard_data.csv'
  download = github_session.get(csv_url).content
  all_data = pd.read_csv(io.StringIO(download.decode('utf-8')), index_col = [0], na_values = ["NAN", "inf"])
  # all_data = pd.read_csv("C:/Users/cpetrosi/Documents/GitHub/WET-Dashboard/Static_Files/WET_dashboard_data.csv", na_values = "NAN")
  # print(all_data.loc[all_data.site == "CAP_002", "NDVI"])
  
  
  csv_url2 = 'https://raw.githubusercontent.com/ucpetrosian/WET-Dashboard/master/Static_Files/MET_station_ranges.csv'
  download = github_session.get(csv_url2).content
  range_names = pd.read_csv(io.StringIO(download.decode('utf-8')))
  # range_names = pd.read_csv("C:/Users/cpetrosi/Documents/GitHub/WET-Dashboard/Static_Files/MET_station_ranges.csv")
  return all_data, range_names

all_data, range_names = import_data()

## Only keeps data from last 30 days
all_data["TIMESTAMP"] = pd.to_datetime(all_data["TIMESTAMP"])
last_month = date.today() - timedelta(days=30)
last_month = np.datetime64(last_month)
all_data = all_data[all_data["TIMESTAMP"] > last_month]


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
def return_options(sensor, df, site):
    df = df.loc[df["Site"] == site]
    if sensor != "MET_SOIL":
      return df.loc[df.Sensor == sensor].Variable_Name.unique()
    else:
      return ["SWC", "TS", "SEC", "T_SOIL"]

## Trims main DF to only selected tower, then renames columns to add units
def update_df(df, site, option, unit_dict = unit_dict):
    plot_df = df.loc[df.site == site]
    for col in option:
        if col in ["SWC", "TS", "SEC"]:
            for num in range(1,10):
                temp_str = col + "_1_"+str(num)+"_1"
                plot_df = plot_df.rename(columns = {temp_str: unit_dict[temp_str]})
        else:
            plot_df = plot_df.rename(columns = {col: unit_dict[col]})
    plot_df = plot_df.fillna(method = "ffill")
    return plot_df

## Adds units to columns to pass through plot
def update_col_names(option, unit_dict = unit_dict):
    out = []
    for name in option:
        if name in ["SWC", "TS", "SEC"]:
            for num in range(1,10):
                temp_str = name + "_1_"+str(num)+"_1"
                out.append(unit_dict[temp_str])
        else:
            out.append(unit_dict[name])
    return out

## Create and name sidebar
st.sidebar.header("Plot Adjustments")

## Puts station selector in sidebar, returns selected station
site = st.sidebar.selectbox("Select Station:",
                            ["CAP_001", "CAP_002", "WIN_001", "OAK_001"], index = 0)

## Puts sensor selector in sidebar, returns selected sensor, options populated by range_names csv
sensor_type = st.sidebar.selectbox("Select Sensor Type:",
                                  range_names.loc[range_names["Site"] == site].Sensor.unique(), index = 0)

## Puts parameter selector in sidebar, fills option via aforementioned function,
## returns parameters to be put in plot
option = st.sidebar.multiselect("Select Measurement:",
                                return_options(sensor_type, range_names, site))

## Uses plotly chart to plot data, uses aforementioned functions for label/DF setup
## Y-axis labels set using passed columns via multiselector
## Range is set using range_names csv
fig = px.line(update_df(all_data, site, option), x = "TIMESTAMP", y = update_col_names(option))
fig.update_layout(dragmode = "pan")
st.plotly_chart(fig)
                        # labels = {"value": " / ".join(option)},
                        # range_y = [min(range_names.loc[range_names.Variable_Name.isin(option)].Range_Low),
                        #         max(range_names.loc[range_names.Variable_Name.isin(option)].Range_High)]
                                


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
def dataframe_styler(df, option = option, site = site):
    revis_col = []
    for col in option:
        if col in ["SWC", "TS", "SEC"]:
            for num in range(1,10):
                temp_str = col + "_1_"+str(num)+"_1"
                revis_col.append(temp_str)
        else:
            revis_col.append(col)
    ret_df = df.loc[df.site == site, ["TIMESTAMP"] + revis_col]
    ret_df = ret_df.fillna(method = "ffill")
    ret_df = ret_df.dropna(how = "all", subset = revis_col)
    return ret_df.style.apply(highlight_outliers, axis = 1)


st.dataframe(data = dataframe_styler(all_data))
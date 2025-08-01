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

github_session = requests.Session()
csv_url = 'https://raw.githubusercontent.com/ucpetrosian/WET-Dashboard/master/Static_Files/WET_dashboard_data.csv'
download = github_session.get(csv_url).content
all_data = pd.read_csv(io.StringIO(download.decode('utf-8')), index_col = [0])


csv_url = 'https://raw.githubusercontent.com/ucpetrosian/WET-Dashboard/master/Static_Files/MET_station_ranges.csv'
download = github_session.get(csv_url).content
range_names = pd.read_csv(io.StringIO(download.decode('utf-8')))



# user_path = "mrcoo"

# range_names = pd.read_csv(f"C:/Users/{user_path}/Documents/GitHub/WET-Dashboard/Static_Files/MET_station_ranges.csv")

# all_data = pd.read_csv(f"C:/Users/{user_path}/Documents/GitHub/WET-Dashboard/Static_Files/WET_dashboard_data.csv", na_values = "NAN")


## Only keeps data from last 30 days
all_data["TIMESTAMP"] = pd.to_datetime(all_data["TIMESTAMP"])
last_month = date.today() - timedelta(days=30)
last_month = np.datetime64(last_month)
all_data = all_data[all_data["TIMESTAMP"] > last_month]
# all_data = all_data.interpolate(method = "pad")    #########
all_data = all_data.fillna(method = "ffill")
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
    plot_df = df.loc[df.site == site]
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
                            ["CAP_001", "CAP_002", "WET_003", "WET_004"], index = 0)

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
st.plotly_chart(px.line(update_df(all_data, site, option), x = "TIMESTAMP", y = update_col_names(option),
                        # labels = {"value": " / ".join(option)},
                        # range_y = [min(range_names.loc[range_names.Variable_Name.isin(option)].Range_Low),
                        #         max(range_names.loc[range_names.Variable_Name.isin(option)].Range_High)]
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
    ret_df = df.loc[df.site == site, ["TIMESTAMP"] + option]
    return ret_df.style.apply(highlight_outliers, axis = 1)


st.dataframe(data = dataframe_styler(all_data))
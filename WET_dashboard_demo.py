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

WWF_flux = pd.read_csv("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_Flux_Notes.dat", header = [0], skiprows = [0,2,3])
WWF_soil = pd.read_csv("C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/suplementary/flux_notes_and_soilvue/VAC_SoilVUE_Daily.dat", header = [0], skiprows = [0,2,3])
WWF_soil= WWF_soil.reset_index(drop=True)
WWF_soil.TIMESTAMP= pd.to_datetime(WWF_soil['TIMESTAMP'], format= 'mixed')

st.sidebar.header("Plot Adjustments")

option = st.sidebar.selectbox("Select Parameter:",
                     ["VWC_5cm_Avg", "VWC_10cm_Avg", "VWC_20cm_Avg", "VWC_30cm_Avg", "VWC_40cm_Avg", "VWC_50cm_Avg",
                      "VWC_60cm_Avg", "VWC_75cm_Avg", "VWC_100cm_Avg"])

st.plotly_chart(px.line(WWF_soil, x = "TIMESTAMP", y = option))
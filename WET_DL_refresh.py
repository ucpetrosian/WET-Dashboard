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
import os
import glob
import geopandas as gpd
from IPython.display import display
import plotly
import plotly.express as px
from shapely.geometry import Point
import datetime


sites = ["WET01", "WET02", "WET03"]
columns = []
path = "C:/Users/cpetrosi/Box/TREX/MISCELLANEOUS/Datalogger_Report_Files/"
for i in range(0, len(sites)):
  for name in glob.glob(path + "*"+sites[2]+"*"):
    print(name)
    columns.append(pd.read_csv(name, header = [0], skiprows = [0,2,3]).columns)
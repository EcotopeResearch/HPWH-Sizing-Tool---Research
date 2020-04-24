# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 16:27:38 2020

@author: scott
"""

# dataframe imports
import pandas as pd

# datetime imports
from datetime import datetime
import holidays
us_holidays = holidays.UnitedStates()

# database imports
import sqlite3
import os

# custom functions import
from functions import (get_weekdays_df, remove_incomplete_days, day_box, group_days_dict, 
                       day_lines, normalize, day_sums, df_iwf, df_peakyness)

# =============================================================================
# #### CSV Exports for Grow A ###
# =============================================================================

df = pd.read_csv('GrowA_hourly.csv')
df = df.rename(columns={"Total.Flow": "value"})

### SORT DATAFRAME SO TIMESTAMP IS INDEX
# create timestamps
timestamps = []

for i in range(0, len(df)):
    ndt = datetime # create a datetime object
    ndt = ndt.fromisoformat(df['date'][i]) # add date
    ndt = ndt.replace(hour=df['hour'][i]) # add hour
    timestamps.append(ndt) # append to timestamps list
    
df['time stamp'] = timestamps        
# set index to time stamp
df = df.set_index(['time stamp']).sort_index()

df = remove_incomplete_days(df)
growA_flows = df.reset_index()

# look at weekdays only
weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

growA_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(growA_peakyness)):
    site.append('growA')

growA_peakyness['site'] = site



# =============================================================================
# #### CSV Exports for Grow B ###
# =============================================================================

df = pd.read_csv('growB_hourly.csv')
df = df.rename(columns={"Total.Flow": "value"})

### SORT DATAFRAME SO TIMESTAMP IS INDEX
# create timestamps
timestamps = []

for i in range(0, len(df)):
    ndt = datetime # create a datetime object
    ndt = ndt.fromisoformat(df['date'][i]) # add date
    ndt = ndt.replace(hour=df['hour'][i]) # add hour
    timestamps.append(ndt) # append to timestamps list
    
df['time stamp'] = timestamps        
# set index to time stamp
df = df.set_index(['time stamp']).sort_index()

df = remove_incomplete_days(df)
growB_flows = df.reset_index()

# look at weekdays only
weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

growB_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(growB_peakyness)):
    site.append('growB')

growB_peakyness['site'] = site

# =============================================================================
# #### Convert GPM to Gals
# =============================================================================
growA_volume = growA_flows
growA_volume['value'] = growA_volume['value']*60 # convert to gallons

growB_volume = growB_flows
growB_volume['value'] = growB_volume['value']*60 # convert to gallons

# =============================================================================
# #### Export data
# =============================================================================

growA_volume.to_csv('growA_volume.csv')
growB_volume.to_csv('growB_volume.csv')

growA_peakyness.to_csv('growA_peakyness.csv')
growB_peakyness.to_csv('growB_peakyness.csv')










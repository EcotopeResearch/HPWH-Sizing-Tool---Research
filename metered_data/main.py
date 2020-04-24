# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 17:09:50 2020

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


path = "F:\\client\\BPA_E3T\\RCC\\RCCViewer\\"
filename = "RCC_MV.db"
# make connection
con = sqlite3.connect(os.path.join(path, filename))

# =============================================================================
# #### Peakyness Plot For Sunset ###
# =============================================================================

df = df_iwf(con, 'sunset')  # custom function to query db
df = df['2015-01-01':'2020-02-01'] # filter for fully occupied days
df = remove_incomplete_days(df)
sunset_flows = df.reset_index()

weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

sunset_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(sunset_peakyness)):
    site.append('sunset')

sunset_peakyness['site'] = site

# =============================================================================
# #### Peakyness Plot For Stream ###
# =============================================================================

df = df_iwf(con, 'stream')  # custom function to query db
df = df['2014-01-01':'2020-02-01'] # filter for fully occupied days
df = remove_incomplete_days(df)
stream_flows = df.reset_index()

weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date


# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)


# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

stream_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(stream_peakyness)):
    site.append('stream')

stream_peakyness['site'] = site

# =============================================================================
# #### Peakyness Plot For Yesler ###
# =============================================================================

df = df_iwf(con, 'yesler')  # custom function to query db
df = df['2019-07-10':'2020-02-01'] # filter for fully occupied days
df = remove_incomplete_days(df)
yesler_flows = df.reset_index()

weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

yesler_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(yesler_peakyness)):
    site.append('yesler')

yesler_peakyness = sums_df.reset_index()
yesler_peakyness['site'] = site

# =============================================================================
# #### Peakyness Plot For Block 11 ###
# =============================================================================

# block 11 needs a custom query because more flows are measured.
sql_query = 'SELECT * FROM block11_hourly WHERE var = "Flow_CityWater"'
df = pd.read_sql_query(sql_query, con)

### SORT DATAFRAME SO TIMESTAMP IS INDEX
# create timestamps
timestamps = []

for i in range(0, len(df)):
    # create a datetime object
    timestamps.append(datetime.fromisoformat(df['time_pt'][i]))
    
df['time stamp'] = timestamps        
# set index to time stamp
df = df.set_index(['time stamp']).sort_index()

#df = df['2015-01-01':'2020-02-01'] # filter for fully occupied days
df = remove_incomplete_days(df)
block11_flows = df.reset_index()

weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

block11_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(block11_peakyness)):
    site.append('block11')

block11_peakyness['site'] = site

# =============================================================================
# #### Peakyness Plot For Eliz James ###
# =============================================================================

df = pd.read_csv('ejh_hrly_cwf.csv')

### SORT DATAFRAME SO TIMESTAMP IS INDEX
# create timestamps
timestamps = []

for i in range(0, len(df)):
    # create a datetime object
    timestamps.append(datetime.fromisoformat(df['time_pt'][i]))
    
df['time stamp'] = timestamps        
# set index to time stamp
df = df.set_index(['time stamp']).sort_index()
df = df[:'2019-06-01'].append(df['2019-06-19':'2020-02-01']) # remove flood event
df = remove_incomplete_days(df)
ejames_flows = df.reset_index()

# look at weekdays only
weekdays = get_weekdays_df(df) # filter for weekdays
sums_df = day_sums(weekdays) # sum on date

# add three hour peak, volumes, times, and normalized volumes to sums_df
sums_df = df_peakyness(sums_df, weekdays)

# convert to gallons
# must be after peakyness function for proper normalization
sums_df['value'] = sums_df['value']*60 

ejames_peakyness = sums_df.reset_index()
site = []
for i in range(0,len(ejames_peakyness)):
    site.append('ejames')

ejames_peakyness['site'] = site

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
ejames_volume = ejames_flows
ejames_volume['value'] = ejames_volume['value']*60 # convert to gallons

yesler_volume = yesler_flows
yesler_volume['value'] = yesler_volume['value']*60 # convert to gallons

stream_volume = stream_flows
stream_volume['value'] = stream_volume['value']*60 # convert to gallons

sunset_volume = sunset_flows
sunset_volume['value'] = sunset_volume['value']*60 # convert to gallons

block11_volume = block11_flows
block11_volume['value'] = block11_volume['value']*60 # convert to gallons

growA_volume = growA_flows
growA_volume['value'] = growA_volume['value']*60 # convert to gallons

growB_volume = growB_flows
growB_volume['value'] = growB_volume['value']*60 # convert to gallons

# =============================================================================
# #### Export data
# =============================================================================

ejames_volume.to_csv('ejames_volume.csv')
yesler_volume.to_csv('yesler_volume.csv')
stream_volume.to_csv('stream_volume.csv')
sunset_volume.to_csv('sunset_volume.csv')
block11_volume.to_csv('block11_volume.csv')
growA_volume.to_csv('growA_volume.csv')
growB_volume.to_csv('growB_volume.csv')

ejames_peakyness.to_csv('ejames_peakyness.csv')
yesler_peakyness.to_csv('yesler_peakyness.csv')
stream_peakyness.to_csv('stream_peakyness.csv')
sunset_peakyness.to_csv('sunset_peakyness.csv')
block11_peakyness.to_csv('block11_peakyness.csv')
growA_peakyness.to_csv('growA_peakyness.csv')
growB_peakyness.to_csv('growB_peakyness.csv')

# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 16:58:48 2020

@author: scott
"""

from __future__ import division, absolute_import, print_function

# dataframe imports
import pandas as pd

# datetime imports
from datetime import datetime
import holidays
us_holidays = holidays.UnitedStates()

# ploting imports
import plotly.graph_objects as go
import plotly.express as px

def remove_incomplete_days(df):
    '''
    Remove days were not all hours are recorded in the dataset.
    This function is not very efficient right now and could use some work.
    
    Parameters
    ----------
    df : dataframe
    '''
    
    # create empty lists to add dataframe columns
    dates = []
    timestep = []
    drop_dates = []
    
    for i in range(0, len(df)):        
        dates.append(df.index[i].date()) # append date datetime object
        timestep.append(1) # append a 1 to sum later
             
    # add df columns
    df['dates'] = dates # create dates column    
    df['timestep_sum'] = timestep # create column to sum, will be 24 if all hours are recorded.
       
    # sumby date, timstep sum should equal 24 with hourly data     
    sums=df.groupby(['dates']).sum()
        
    # loop to find dates where timestep does not equal 24
    for i in range(0,len(sums)):
        if sums['timestep_sum'][i] != 24:
            drop_dates.append(sums.index[i]) 
    
    #reset index, needed in case an hour was recorded more than once.
    df = df.reset_index()
    
    # delete rows where date is in drop_dates
    for index, row in df.iterrows():
        if row['dates'] in drop_dates:
            df.drop(index, inplace=True)
    
    # set index back to time stamp
    df = df.set_index(['time stamp']).sort_index()
    
    return df

def df_peakyness(sums_df, weekdays):
    
    '''
    Creates daily dataframe with peak three hour period identified,
    total recorded, and peak norm recorded.
    
    Parameters
    ----------
    sums_df : dataframe, required
        Daily sums flow for timeseries dataframe
    weekdays : dataframe, required
        Time sercies dataframe of flow values
    '''
    
    peak_volumes = []
    peak_hours = []
    peak_norm = []
    
    for i in range(0, len(sums_df)):    
        # slice dataframe on date
        date_str = str(sums_df.index[i])
        day = weekdays[date_str:date_str]
        
        # find peak in that day
        peak = 0
        hr = 0
        for j in range(1,len(day)-1):
            
            # caluclate volumes for hours
            hr0 = day['value'][j-1] # volume at previous hour
            hr1 = day['value'][j] # volume at hour
            hr2 = day['value'][j+1] # volume at furture hour
            
            # potential new peak
            new = hr0 + hr1 + hr2
            
            if new > peak:
                peak = new
                hr = j
            
        peak_volumes.append(peak)
        peak_hours.append(hr)
        peak_norm.append(peak/sums_df['value'][i])    
        
    sums_df['peak_volumes'] = peak_volumes
    sums_df['peak_volumes'] = sums_df['peak_volumes']*60 # convert to gallons
    sums_df['peak_hours'] = peak_hours
    sums_df['peak_norm'] = peak_norm
    
    return sums_df

def df_iwf(con, site):
    '''
    Creates time series index dataframe of flows from SQL query.
    
    Parameters
    ----------
    con : SQL connection, required
    site : string, required
        Site name for query
    '''
    
    sql_query = 'SELECT * FROM '+ site +'_hourly WHERE var = "GPM"'
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
    return df

def day_sums(df):
    '''
    Sum time series index dataframe by dates
    
    Parameters
    ----------
    df : dataframe, required
    '''
    # create dates list
    dates = []
    
    # append date strings to list
    for i in range(0,len(df)):
        dates.append(df.index[i].date())
        
    # add dates to df
    df['dates'] = dates    
    # groupby sum() on dates
    sums=df.groupby(['dates']).sum()
        
    return(sums)

def normalize(df):
    '''
    Normalized time series index dataframe by sum of daily values.
    
    Parameters
    ----------
    df : dataframe, required
    '''
    # create dates list
    dates = []
    
    # append date strings to list
    for i in range(0,len(df)):
        dates.append(df.index[i].date())
        
    # add dates to df
    df['dates'] = dates    
    # groupby sum() on dates
    sums=df.groupby(['dates']).sum()
    
    # create list to store normal values
    norm_val = []
    
    # loop through df and normalize values
    for i in range(0,len(df)):
        
        df_index=df.index[i]
        date = df.index[i].date()
        
        value = df.loc[df_index]['value']
        total = sums.loc[date]['value']
        
        norm_val.append(value/total)
        
    df['value']=norm_val
    
    return(df)

def get_weekdays_df(df):
    '''
    Filter time series index dataframe for weekdays
    
    Parameters
    ----------
    df : dataframe, required
    '''    
    
    weekdays_list = []
    weekends_list = []
    holidays_list = []
    
    for i in range(0,len(df)):
        date = df.index[i].date()

        if date in us_holidays:
            holidays_list.append(df.index[i])
        
        elif date.isoweekday()>1 and date.isoweekday()<7:
            weekdays_list.append(df.index[i])
        else:
            weekends_list.append(df.index[i])
    
    # create weekdays dataframe
    weekdays = df[~df.index.isin(weekends_list)]
    weekdays = weekdays[~weekdays.index.isin(holidays_list)]
    
    return weekdays

def get_weekends_df(df):
    '''
    Filter time series index dataframe for weekdends
    
    Parameters
    ----------
    df : dataframe, required
    '''            
    weekdays_list = []
    weekends_list = []
    holidays_list = []
    
    for i in range(0,len(df)):
        date = df.index[i].date()

        if date in us_holidays:
            holidays_list.append(df.index[i])
        
        elif date.isoweekday()>1 and date.isoweekday()<7:
            weekdays_list.append(df.index[i])
        else:
            weekends_list.append(df.index[i])
    
    # create weekdays dataframe
    weekends = df[~df.index.isin(weekdays_list)]
    weekends = weekends[~weekends.index.isin(holidays_list)]
    
    return weekends

def get_holidays_df(df):
    '''
    Filter time series index dataframe for holidays
    
    Parameters
    ----------
    df : dataframe, required
    '''    
    weekdays_list = []
    weekends_list = []
    holidays_list = []
    
    for i in range(0,len(df)):
        date = df.index[i].date()

        if date in us_holidays:
            holidays_list.append(df.index[i])
        
        elif date.isoweekday()>1 and date.isoweekday()<7:
            weekdays_list.append(df.index[i])
        else:
            weekends_list.append(df.index[i])
    
    # create weekdays dataframe
    holidays = df[~df.index.isin(weekdays_list)]
    holidays = holidays[~holidays.index.isin(weekends_list)]
    
    return holidays

### GROUPING

def group_days_dict(df):
    '''
    Returns dictionary where keys are dates (string), and values are time series index 
    dataframes sliced from full dataframe for that date only. Used for creating line plot
    of all weekdays plotted on the same 24 hours. 
    
    Parameters
    ----------
    df : dataframe, required
    '''    
    days = {}    
    for i in range(0,len(df)):     
        days[str(df.index[i].date())] = df[str(df.index[i].date()):str(df.index[i].date())]
        
    return days

### PLOTTING
    
def day_lines(days, title):
    '''
    Creates line plot in plotly of days dictionary.
    
    Parameters
    ----------
    days : dictionary, required
    title : string, required
    '''    
    fig = go.Figure()      
    
    for key in days:
        
        # create times and values lists
        times=[]
        values=[]
        
        # identify times and values
        for i in range(0, len(days[key])):    
            times.append(days[key].index[i].time())
            values.append(days[key]['value'][i])
            
        # plot times and values
        fig.add_trace(go.Scatter(x=times, y=values,
                        mode='lines',
                        name=key))

    fig.write_html(title + ".html")

#### PLOTTING

def day_box(df, title):
    '''
    Creates box plot from time index dataframe.
    
    Parameters
    ----------
    df : dataframe, required
    title : string, required
    '''    
    times = []
    for i in range(0, len(df)):
        times.append(df.index[i].time())
    
    df['times'] = times
    
    fig = px.box(df, x="times", y="value")
    fig.write_html(title+".html")
'''
Created on Mar 13, 2013

@author: bill
'''
import datetime as dt
from pylab import *    
    
def datestr_to_datetime(datestr):
    return dt.datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")

def continuous_periods(df, d_seconds=2):
    '''
    returns a list of tuples of (datetime_start,datetime_end)
    for continuous periods (each sample is no more than d_seconds
    apart)
    '''
    periods = []
    t1 = 0
    t2 = 0
    for t in range(1,df.index.shape[0]-1):
        dlt = (df.index[t] - df.index[t-1]).seconds
        if dlt > d_seconds:
            t2 = t-1
            periods.append((df.index[t1],df.index[t2]))
            t1 = t
    return periods

def remove_short_periods(periods, min_len_timedelta):
    '''
    remove periods that are shorter than min_len_timedelta
    '''
    new_periods = []
    for t1,t2 in periods:
        if t2 - t1 >= min_len_timedelta:
            new_periods.append((t1,t2))
    return new_periods

def collect_sequences(contin_periods, df, col_name = 'vector_norm', seq_len = 20, shift = 10):
    '''
    returns a list sequences of length seq_len from column 
    col_name of dataframe df

    contin_periods: is a list of datetime tuples,
    [(datetime_start,datetime_end),...]

    df: is the data frame that the continuous periods refer to

    col_name: is the name of the column in the df to use for 
    sequence data

    seq_len: length of sequence to extract
    
    shift: how many samples to shift each successive sequence window by
    '''
    sequences = []
    for t1,t2 in contin_periods:
        period_data = df[col_name][t1:t2]
        period_len = period_data.shape[0]
        
        start,end = 0,seq_len
        while end < period_len:
            sequences.append(period_data[start:end].values)
            start += shift
            end += shift
    return sequences




####################################
############  OLD  #################
####################################
def plot_recording_times(subject, y=1.):
    starttimes, endtimes = [], []
    for sub,start,end in DG.subject_dirs.iterkeys():
        delta = dt.timedelta(0,0,1)
        if sub != subject: continue
        starttimes.append(start)
        endtimes.append(end)
    hlines(y*ones_like(starttimes),date2num(starttimes),date2num(endtimes))
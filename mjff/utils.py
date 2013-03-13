'''
Created on Mar 13, 2013

@author: bill
'''
import datetime as dt
    
    
def datestr_to_datetime(datestr):
    return dt.datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")
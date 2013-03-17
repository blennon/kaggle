import os
import datetime as dt
from pandas import *

class DataGrabber(object):
    '''Utility for retrieving data from the directories'''
    
    def __init__(self, data_dir='/home/bill/personal/MJFF-Data/'):
        
        self.data_dir = data_dir
        self.subjects = {'IRIS':'PD',
                         'SWEETPEA':'CONTROL',
                         'FLOX':'PD',
                         'SUNFLOWER':'CONTROL',
                         'APPLE':'CONTROL',
                         'PEONY':'PD',
                         'ROSE':'CONTROL',
                         'CHERRY':'PD',
                         'VIOLET':'PD',
                         'CROCUS':'PD',
                         'DAFODIL':'CONTROL',
                         'DAISY':'PD',
                         'ORANGE':'CONTROL',
                         'LILLY':'CONTROL',
                         'MAPLE':'PD',
                         'ORCHID':'PD'}
        self.subject_dirs = self.build_subject_dir_dict()
        self.sensor_list = ['accel','audio','batt','cmpss','comms','gps',
                            'light','main','meta','prox','recorder']

    def build_dataframe_for(self, subject, sensor):
        '''
        return a dataframe indexed by Pandas DatetimeIndex
        for all measurements for a particular subject and sensor
        '''
        dfs = []
        for sub,start,end in self.subject_dirs.iterkeys():
            if sub != subject: continue
            df = self.load_dataframe_for(subject, sensor, start, end)
            if df is not None:
                dfs.append(df)
        return concat(dfs).sort_index()
            
    def load_dataframe_for(self, subject, sensor, start_time, end_time):
        '''
        return a pandas data frame using read_csv() for 
        subject, sensor, time
        
        subject: str
        sensor: str
        start_time: datetime object
        end_time: datetime object
        '''
        dfs = []
        dir = self.data_dir + self.subject_dirs[(subject,start_time,end_time)]
        for f in os.listdir(dir):
            if sensor in f and 'log' not in f and 'raw' not in f:
                dfs.append(read_csv(dir+'/'+f, parse_dates=True, index_col=-1))
        if len(dfs) > 0:
            return concat(dfs)
        else:
            return None

    def get_start_times_for(self, subject):
        """"return a list of times when recordings were made for 'subject'"""
        times = []
        for s,start,stop in self.subject_dirs.iterkeys():
            if s == subject:
                times.append(start)
        return times
            
    def build_subject_dir_dict(self):
        '''
        build a dictionary of subject, time folder names
        {(subject,start time, stop time):folder path)}
        '''
        subject_dir = {}
        for f in os.listdir(self.data_dir):
            if f[0] == '.' or '_' not in f:
                continue
            flist = f.split('_')
            if len(flist) < 7: continue
            name = DataGrabber.correct_name(flist[1])
            if name not in self.subjects: continue
            startdate, starttime = flist[-4:-2]
            enddate,endtime = flist[-2:]
            start = DataGrabber.str_to_datetime(startdate, starttime)
            end = DataGrabber.str_to_datetime(enddate, endtime)
            subject_dir[(name,start,end)] = f
        return subject_dir
    
    @staticmethod
    def correct_name(name):
        '''
        Fix name spelling errors in data set file names
        '''
        if name == 'DAISEY': return 'DAISY'
        if name == 'LILY': return 'LILLY'
        return name
        
    @staticmethod
    def str_to_datetime(ymd, hms):
        '''
        parse foldername strings to datetime objects
    
        ymd - year month day string
        hms - hour minute second string
        '''
        y,mo,d = int(ymd[0:4]),int(ymd[4:6]),int(ymd[6:])
        h,min,s = int(hms[0:2]),int(hms[2:4]),int(hms[4:])
        return dt.datetime(y,mo,d,h,min,s)

    
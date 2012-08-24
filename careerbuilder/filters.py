import datetime
from itertools import izip
from scipy.io import mmread
from numpy.lib.arraysetops import setdiff1d
from pylab import *

class Filter(object):
       
    def filter(self):
        raise NotImplementedError("Not Implemented")
    
    
class JobsAppliedFilter(Filter):
    
    def __init__(self, user_job_occurs_f):
        self.UserJobOccurs = mmread(user_job_occurs_f).tocsr()
    
    def filter(self, u_ind, job_inds, return_appd=False):
        '''
        Removes the jobs the user has already applied to.

        Parameters
        ----------
        u_ind: int
               The index in the User-Job application co-occur matrix
        job_inds: list of ints
                  This is a list of job indices   
        return_appd: boolean
                     if True, return the jobs applied to by u_ind as well
                     
        Returns
        -------
        A filted list of job indices excluding the indices to jobs the user
        has already applied for.
        
        Optionally, returns the jobs the user applied to as well.
        '''
        
        applied_inds = nonzero(self.UserJobOccurs[u_ind,:])[1]
        filtered = setdiff1d(job_inds,applied_inds)
        if return_appd:
            return filtered, applied_inds
        else:
            return filtered 
        
    def get_occurs(self):
        '''
        Returns
        -------
        self.UserJobOccurs: CSR Scipy Sparse Matrix
                            User-Jobs applied matrix
        '''
        return self.UserJobOccurs
    
class JobDistanceFilter(Filter):
    
    def __init__(self, Users, Jobs, JobTokens, Zips):
        self.Users = Users
        self.Jobs, self.JobTokens = Jobs, JobTokens
        self.Zips = Zips
        self.job_latlong = self.job_inds_to_latlong()
    
    def filter(self, u_tok, j_inds, max_dist=None, return_dists=False):
        '''
        Filter a list of job indices by their distance from the user

        Parameters
        ----------
        u_tok: int
               The user token (ID, not index)
        j_inds: numpy array of ints
                a list of the job indices (not tokens)
        max_dist: float
                  the maximum distance from the user that a job is allowed to be
                  in order to pass through the filter
        return_dists: boolean
                      if true, return a list of tuples, e.g. [(j_ind, dist),...]  
        
        Returns
        -------
        list - of job indices; or, (job index, distance) tuples
        '''
        if max_dist is None and return_dists == False:
            raise Exception('must set max_dist to float or return_dists to True')
            
        u_lat_long = self.find_lat_long(u_tok, self.Users)
        if u_lat_long is None:
            return []
        u_lat, u_long = u_lat_long
        j_lats, j_longs = self.job_latlong[j_inds,0], self.job_latlong[j_inds,1]
        dists = self.Zips.lat_long_dist(u_lat,u_long,j_lats,j_longs)
        dists[j_lats == 0.0] = -1
        dists[j_longs == 0.0] = -1
        if not return_dists:
            dists[dists > max_dist] = -1
            return list(j_inds[dists >= 0.0])
        else:
            return izip(list(j_inds[dists >= 0.0]), list(dists[dists >= 0.0]))
    
    def job_inds_to_latlong(self):
        '''
        Create an array containing lat/long info corresponding to each job (by index)
        
        Returns
        -------
        numpy array - rows correspond to job indices, col1 = lat, col2 = long
        '''
        self.bad_loc = 0
        job_latlong = zeros((self.JobTokens.token_count(),2))
        for j_tok, j_ind in self.JobTokens.tokens2ids.iteritems():
            j_lat_long = self.find_lat_long(j_tok, self.Jobs)
            if j_lat_long is not None:
                j_lat, j_long = j_lat_long
                job_latlong[j_ind,:] += array([j_lat,j_long])
            else:
                self.bad_loc += 1
        return job_latlong
    
    def find_lat_long(self, tok, Thing):
        '''
        Parameters
        ----------
        tok: int
             token (e.g. user or job token corresponding to Thign)
        Thing: a Thing instance
               (e.g. Users, Jobs) 
        
        Returns
        -------
        (lat,long) coordinate tuple
        '''
        t = Thing[tok]
        tzip,tcity,tstate = t['Zip'],t['City'],t['State']
        if tzip is not None:
            try:
                return self.Zips.lat_long_lookup(tzip)
            except KeyError:
                pass
        try:
            return self.Zips.lat_long_lookup((tcity,tstate))
        except KeyError:
            return None
        

class WindowIndices(object):
    
    def __init__(self, wind_dates_f, Thing, ThingTokens):
        self.wind_dates = self.load_window_dates(wind_dates_f)
        self.wid_to_jind = self.wind2ind(Thing, ThingTokens)
    
    def __getitem__(self, window_id):
        return self.wid_to_jind[window_id]
    
    def wind2ind(self, Thing, Tokens, test_period_only=True):
        '''
        Builds a mapping from windowIDs to list of indices

        Parameters
        ----------
        Thing: a Thing instance
               (e.g. Users, Jobs)
        Tokens: a Tokens instance
                (e.g. UserTokens, JobTokens)  
        test_period_only: boolean
                          if true, only return the indices to jobs in WindowID
                          where the job's end date is after the test period start date.
        
        Returns
        -------
        dict - a dictionary mapping windowIDs (int) to a list of indices (list of ints)
        '''
        w2ind = {}
        for token,ind in Tokens.tokens2ids.iteritems():
            w_id = Thing[token]['WindowID']
            # only want jobs that are available during the test period
            end_date = WindowIndices.to_date(Thing[token]['EndDate'])
            if end_date < self.wind_dates[w_id]['train_stop_test_start']:
                continue
            try:
                w2ind[w_id].append(ind)
            except KeyError:
                w2ind[w_id] = [ind]
        return w2ind
    
    def load_window_dates(self, wind_file):
        '''
        Builds a mapping from windowIDs to list of indices

        Parameters
        ----------
        Thing: a Thing instance
               (e.g. Users, Jobs)
        Tokens: a Tokens instance
                (e.g. UserTokens, JobTokens)  
        test_period_only: boolean
                          if true, only return the indices to jobs in WindowID
                          where the job's end date is after the test period start date.
        
        Returns
        -------
        dict - a dictionary mapping windowIDs (int) to a list of indices (list of ints)
        '''
        win_f = open(wind_file)
        header = win_f.readline()
        window_dates = {}
        for l in win_f:
            l = l.strip().split('\t')
            window_dates[int(l[0])] = {'train_start':WindowIndices.to_date(l[1]),
                                       'train_stop_test_start':WindowIndices.to_date(l[2]),
                                       'test_stop':WindowIndices.to_date(l[3])}
        return window_dates
            
    @staticmethod
    def to_date(date_str):
        '''converts a date formatted string to datetime instance'''
        try:
            return datetime.datetime.strptime(date_str,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.datetime.strptime(date_str,'%Y-%m-%d %H:%M:%S.%f')
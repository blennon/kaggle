from generalized_occurs import Occurs
from tokens import Tokens
from things_loaders import *
from filters import *
from zips import Zips
from pylab import *

class Recommender(object):
    
    def __init__(self, UsersMat, JobsMat, Users, Jobs, UserTokens, JobTokens, Zips,
                 wind_dates_f = '/media/kaggle/careerbuilder/data/window_dates.tsv',
                 user_job_occurs_f = '/media/kaggle/careerbuilder/occurs_mm/user_job_train_occurs.mtx'):
        self.UsersMat, self.JobsMat = UsersMat, JobsMat
        self.Users, self.Jobs = Users, Jobs
        self.UserTokens, self.JobTokens = UserTokens, JobTokens
        self.Zips = Zips
        self.JobsAppFilt = JobsAppliedFilter(user_job_occurs_f)
        self.JobWindInds = WindowIndices(wind_dates_f, Jobs, JobTokens)
        self.JobDistFilt = JobDistanceFilter(Users,Jobs,JobTokens,Zips)
      
    def recommend(self, u_ind, k, max_dist=30):
        '''
        k: number of predictions to make
        
        returns a list of indices corresponding to columns
        in the user-job co-occur matrix
        '''
        u_vec = self.UsersMat[u_ind,:]
        u_tok = self.UserTokens.id2token(u_ind)
        cnd_inds = self.job_candidates(u_tok)
        job_inds,sims = Recommender.order_similarity(self.JobsMat,u_vec,array(cnd_inds))
        return self.filter(u_tok, job_inds, max_dist, k)
    
    def job_candidates(self, u_tok):
        '''
        return a list of valid jobs a user could be recommended
        '''
        job_inds = self.JobWindInds[self.Users[u_tok]['WindowID']]
        return self.JobsAppFilt.filter(self.UserTokens.token2id(u_tok),job_inds)
      
    def filter(self, u_tok, pred_inds, max_dist, k):
        '''filter a list of predictions preds, return the best k of them'''
        
        filt_inds = self.JobDistFilt.filter(u_tok,pred_inds,max_dist)
        if len(filt_inds) >= k:
            filtered = filt_inds[0:k]
        elif len(filt_inds) > 0 and len(filt_inds) < k:
            # need to add functionality to append unqiue pred_inds
            # to filt_inds -- but doesn't seem to improve things
            filtered = list(filt_inds)
        else:
            filtered = pred_inds[0:k]
        return filtered
    
    @staticmethod
    def order_similarity(mat, vec, inds):
        '''
        return a list of similarity values and their indices in the SimSpace

        inds: is an array of indices that correspond to a subset of rows of mat
        '''
        sims = dot(mat,vec)[inds,:]
        sort_index = np.argsort(sims)[::-1] #descend order
        return inds[sort_index],sims[sort_index]
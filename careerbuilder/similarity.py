import sys
execfile('/media/lib/python/set_paths.py')
sys.path.append('/media/git/wordsim/src/')
from scipy.io import mmread
from pylab import *

class UserJobSimilarity(object):
    
    def __init__(self, mat_dir, sval_name = 'stitched_occurs.mtx.singular_values',
                 svec_prefix = 'stitched_occurs.mtx', n_svs=200, norm=True):
        self.U, self.J = self.load_mats(mat_dir, sval_name, svec_prefix, n_svs)
        if norm:
            self.U = UserJobSimilarity._norm_mat(self.U)
            self.J = UserJobSimilarity._norm_mat(self.J)
        
    def load_mats(self, mat_dir, sval_name, svec_prefix, n_svs):
        '''
        Loads the Users and Jobs matrices

        Parameters
        ----------
        mat_dir: str
                 the directory containing user/job data
        sval_name: str
                   the name of the file for singular values
        svec_prefix: str
                     the prefix name for singular vector files
        n_svs: int
               number of singular vectors to load

        ordered: boolean, default=False
                 if true, orders the similarity and j_inds from
                 highest (most similar) to lowest.

        Returns
        -------
        UsersMat, JobsMat -- numpy arrays
        '''
        # load singular values
        D = mmread(mat_dir+sval_name)[0:n_svs]
        D = diag(D[:,0])
        
        # load SVD output matrices
        def load_eigenmat(name_prefix,num):
            eigenvectors = []
            for i in range(num):
                eigenvectors.append(mmread(name_prefix+str(i)))
            return hstack(eigenvectors)
            
        U = load_eigenmat(mat_dir+svec_prefix+'.U.',n_svs)
        V = load_eigenmat(mat_dir+svec_prefix+'.V.',n_svs).T
        UsersMat, JobsMat = dot(V.T,D), dot(D,U.T).T
        del U, V, D
        
        return UsersMat, JobsMat
    
    def user_jobs_sim(self, u_ind, j_inds, ordered=False):
        '''
        Computes similarity between a user and jobs

        Parameters
        ----------
        u_ind: int
               the user index in the User matrix
        j_inds: list or numpy array
                list of job indices to calculate similarity to
        ordered: boolean, default=False
                 if true, orders the similarity and j_inds from
                 highest (most similar) to lowest.

        Returns
        -------
        sims - numpy array; optionally: (inds, sims) [ordered]
        '''
        sims = dot(self.J,self.U[u_ind,:])[j_inds,:]
        if ordered:
            return UserJobSimilarity.order_similarity(sims,j_inds)
        else:
            return sims
    
    @staticmethod
    def order_similarity(sims, inds):
        sort_index = np.argsort(sims)[::-1] # descending order
        return inds[sort_index],sims[sort_index]

    @staticmethod
    def _norm_mat(mat, nan_check=True):
        '''normalizes each row in 'mat' by their l2 norm'''
        if nan_check:
            if np.isnan(mat).any():
                raise Exception('NaNs detected in matrix to be normalized')
        norm = (mat**2).sum(axis=1)**.5
        mat[norm>0,:] /= norm[norm>0][...,None]
        if nan_check:
            if np.isnan(mat).any():
                raise Exception('NaNs detected in normalized matrix')
        return mat

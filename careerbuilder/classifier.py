sys.path.append('/media/git/kaggle/')
from careerbuilder import *
from scipy.io import mmread
numpy.seterr(all='raise')
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression

class Classifier(object):
    '''
    A classifier trained on user-job feature vectors

    Features
    --------
    - User-Job similarity score
    - User-Job distance
    - User currently employed
    - User time at last/current position
    - User career length
    - User percentage of career at last position
    - User number of jobs applied to
    - User max/min/median/std distance applied to
    - Job popularity
    - Job post duration
    '''
    
    def __init__(self, Users, UserTokens, Jobs, JobTokens, UserJobSim, Zips,
                 job_occurs_f, wind_dates_f):
        '''
        Parameters
        ----------
        job_occurs_f: str
                      location of user-job occurs file
        wind_dates_f: str
                      location of window dates file (came with kaggle CB data)
        '''
        self.Users = Users
        self.UserTokens = UserTokens
        self.Jobs = Jobs
        self.JobTokens = JobTokens
        self.UserJobSim = UserJobSim
        self.JobDistFilt = JobDistanceFilter(Users,Jobs,JobTokens,Zips)
        self.JobsAppd = JobsAppliedFilter(job_occurs_f)
        self.WindInds = WindowIndices(wind_dates_f, self.Jobs, self.JobTokens)

    def classify_user(self, u_ind):
        jobs_features, jobs = self.user_jobs_features(u_ind)
        return self.classify(jobs_features), jobs
    
    def classify(self, samples):
        '''
        Parameters
        ----------
        samples: np array
                 (n_samples,n_features)
           
        Returns
        -------
        probs: np array
        (n_samples,) - the probability applying to a job
        '''
        samples[:,self.scaled_cols] = self.scaler.transform(samples[:,self.scaled_cols])
        return self.model.predict_proba(samples)
    
    def train(self, model=LogisticRegression()):
        self.model = model
        self.model.fit(self.train_set,self.train_labels)
           
    def build_set(self, set_type = 'Train', set_size=1e10):
        features = []
        labels = []
        u_ind = 0
        while u_ind < set_size and u_ind < self.JobsAppd.get_shape()[0]:
            u_tok = self.UserTokens.id2token(u_ind)
            u = self.Users[u_tok]
            if u['Split'] != set_type:
                u_ind += 1
                continue         
            if u['Split'] == 'Train':
                u_jobs_feats = self.user_jobs_features(u_ind, train=True)
                if u_jobs_feats is not None:
                    features.append(u_jobs_feats[0])
                    labels.append(u_jobs_feats[1])
            else:
                jobs_features, jobs = self.user_jobs_features(u_ind)
                features.append(jobs_features)          
            u_ind += 1
        if set_type == 'Train':
            self.train_set = vstack(features)
            self.train_labels = hstack(labels)
        elif set_type == 'Test':
            self.test_set = vstack(features)
        else:
            raise Exception('set_type should be Train or Test')
    
    def user_jobs_features(self, u_ind, train=False):
        '''
        Builds features vectors for jobs relative to a user
        '''
        # user info
        u_tok = self.UserTokens.id2token(u_ind)
        u = self.Users[u_tok]

        # get valid jobs
        wind_jobs = self.WindInds[u['WindowID']]
        not_appd, appd = self.JobsAppd.filter(u_ind,wind_jobs,return_appd=True)

        if train:
            if len(appd) == 0:
                return None
            not_appd = self.random_subset(not_appd,len(appd))
            labels = hstack([ones_like(appd),-1.0 * ones_like(not_appd)])
            jobs = hstack([appd,not_appd])
        else:
            jobs = not_appd
        
        # get user-job similarity
        sims = self.UserJobSim.user_jobs_sim(u_ind,jobs)
        assert sims.shape == jobs.shape
        
        # get user-job distance
        jobs, dists = self.JobDistFilt.filter(u_tok, jobs, return_dists=True, return_all=True)
        max_d, min_d, med_d, std_d = max(dists), min(dists), median(dists), std(dists)
        
        # get user info
        u_employed = self.user_empl(u)
        u_num_apps = max(len(appd) - 1, 0)

        # assemble into (jobs,features) array
        singletons = [max_d, min_d, med_d, std_d, u_employed, u_num_apps]
        job_features = vstack([sims,dists]+[s*ones_like(jobs) for s in singletons]).T
        if train:
            return job_features, labels
        return job_features, jobs

    def scale_features(self, cols=[0,1,2,3,4,5,7]):
        '''
        Scale the features corresponding to columns of self.train_set

        Removes the mean and scales to unit variance
        '''
        self.scaled_cols = cols
        self.scaler = preprocessing.Scaler()
        self.train_set[:,cols] = self.scaler.fit_transform(self.train_set[:,cols])
    
    def user_empl(self, user):
        '''Returns values for whether the user is employed, not or unknown'''
        u_emp = user['CurrentlyEmployed']
        if u_emp == 'Yes':
            u_employed = 1.0
        elif u_emp == 'No':
            u_employed = 0.0
        else:
            u_employed = -1.0
        return u_employed
    
    def random_subset(self, inds, n):
        '''
        return a random subset of inds of length n
        '''
        subset = arange(len(inds))
        numpy.random.shuffle(subset)
        return inds[subset[0:n]]
    
    
    '''functions for testing'''
    def train_test(self, perc_test, model=LogisticRegression(), pos_only=True):
        '''
        Splits the training data into training and test sets, trains model
        and prints the score on the test set
        '''
        n_test = int(perc_test * self.train_set.shape[0])
        self.test_set = self.train_set[-n_test:,:]
        self.test_labels = self.train_labels[-n_test:]
        
        if pos_only:
            self.test_set = self.test_set[self.test_labels>0.0,:]
            self.test_labels = self.test_labels[self.test_labels>0.0]

        self.train_set = self.train_set[0:-n_test,:]
        self.train_labels = self.train_labels[0:-n_test]
        self.train(model)
        return self.test()
    
    def test(self):
        self.test_set[:,self.scaled_cols] = self.scaler.transform(self.test_set[:,self.scaled_cols])
        print 'test set score: ', self.model.score(self.test_set, self.test_labels)
        return self.model.predict_proba(self.test_set), self.test_labels
    
    
if __name__ == "__main__":
    # load tokens
    token_dir = '/media/kaggle/careerbuilder/tokens/'
    data_dir = '/media/kaggle/careerbuilder/data'
    UT = Tokens()
    UT.load_tokens_flat(token_dir+'users.tok')
    JT = Tokens()
    JT.load_tokens_flat(token_dir+'./partial/jobs.tok')
    # load data
    Z = Zips()
    U, J = Users(), Jobs()
    Sim = UserJobSimilarity('/media/kaggle/careerbuilder/graphlab_out/SVD200_temporal_stitched/v2/', n_svs=2)
    
    C = Classifier(U,UT,J,JT,Sim,Z,'/media/kaggle/careerbuilder/occurs_mm/user_job_train_occurs.mtx',
               '/media/kaggle/careerbuilder/data/window_dates.tsv')
    C.build_set(set_type = 'Train', set_size=1000)
    C.scale_features()
    C.train()
    C.classify_user(1800)
    
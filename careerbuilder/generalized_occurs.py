'''
This is a general occurrence class where each dimension of the co-occurrence
matrix can have a different set of tokens (mapped to their unique row/col number)

It currently supports making co-occurrences from a flat file
'''
from pylab import *
from scipy.sparse import dok_matrix
from scipy.io import mmwrite

class Occurs(object):
    '''An object for storing and counting co-occurrence between tokens'''
    
    def __init__(self,tokens1,tokens2):
        '''tokens are instances of Tokens class'''
        self.tokens1 = tokens1
        self.tokens2 = tokens2
        self.occurs = dok_matrix((tokens1.token_count(),tokens2.token_count()))
    
    def co_occur_flat_file(self, flat_file, token1_column, token2_column, delim='\t',
                           header=True, token_as_int = True):
        '''Iterates through a flat file and co-occurs the tokens in their respective columns'''
        f = open(flat_file)
        if header: 
            f.readline()
        for l in f:
            l = l.strip().split(delim)
            token1, token2 = l[token1_column], l[token2_column]
            if token_as_int:
                token1, token2 = int(token1), int(token2)
            id1, id2 = self.tokens1.token2id(token1), self.tokens2.token2id(token2)
            self.occurs[id1,id2] += 1
            
    def get_occurs(self):
        return self.occurs
        
    def save_occurs(self,outfile,format='mm'):
        '''save the occurs to disk'''
        if format == 'mm':
            mmwrite(outfile,self.occurs)
        elif format == 'graphlab':
            f = open(outfile,'w')
            occurs = self.occurs.tocoo()
            for i in range(occurs.row.shape[0]):
                # GL likes 1-indexing
                f.write('%s %s  %s\n' % (occurs.row[i]+1,occurs.col[i]+1,occurs.data[i]))
            f.close()
        else:
            raise Exception('format must be mm or graphlab')
        
        
class UserAttributeOccurs(Occurs):
    
    def __init__(self, Users, UserTokens, AttTokens, attr_str):
        self.Users = Users
        self.UserTokens, self.AttTokens = UserTokens, AttTokens
        self.occurs = dok_matrix((UserTokens.token_count(),AttTokens.token_count()))
        self.co_occur(attr_str)
        
    def co_occur(self, attr_str):
        for u_tok, u_id in self.UserTokens.tokens2ids.iteritems():
            u_attr = self.Users[u_tok][attr_str]
            if u_attr is not None:
                try:
                    self.occurs[u_id,self.AttTokens.token2id(u_attr)] = 1.0
                except KeyError:
                    continue
              
                
class UserMajorOccurs(Occurs):
    
    def __init__(self, Users, UserTokens, MajorTokens, StringCleaner):
        self.Users = Users
        self.UserTokens, self.MajorTokens = UserTokens, MajorTokens
        self.StringCleaner = StringCleaner
        self.occurs = dok_matrix((UserTokens.token_count(),MajorTokens.token_count()))
        self.occur()
        
    def occur(self):
        for u_tok, u_ind in self.UserTokens.tokens2ids.iteritems():
            u_major = self.StringCleaner.clean(self.Users[u_tok]['Major'])
            for w in u_major.split(' '):
                try:
                    w_ind = self.MajorTokens.token2id(w)
                except KeyError:
                    continue
                self.occurs[u_ind,w_ind] += 1
             
                
class UserTitleAppliedOccurs(Occurs):
    
    def __init__(self, Jobs, UserTokens, TitleTokens, StringCleaner):
        self.Jobs = Jobs
        self.UserTokens, self.TitleTokens = UserTokens, TitleTokens
        self.StringCleaner = StringCleaner
        self.occurs = dok_matrix((UserTokens.token_count(),TitleTokens.token_count()))
        
    def occur(self, apps_f='/media/kaggle/careerbuilder/data/apps.tsv'):
        f = open(apps_f)
        f.readline()
        for l in f:
            l = l.strip().split('\t')
            u_tok, j_tok = int(l[0]), int(l[-1])
            u_ind = self.UserTokens.token2id(u_tok)
            j_title = self.Jobs[j_tok]['Title']
            j_title = self.StringCleaner.clean(j_title)
            for w in j_title.split(' '):
                try:
                    w_ind = self.TitleTokens.token2id(w)
                except KeyError:
                    continue
                self.occurs[u_ind,w_ind] += 1


class UserTitleHistoricalOccurs(Occurs):
    
    def __init__(self, UserTokens, TitleTokens, StringCleaner):
        self.UserTokens, self.TitleTokens = UserTokens, TitleTokens
        self.StringCleaner = StringCleaner
        self.occurs = dok_matrix((UserTokens.token_count(),TitleTokens.token_count()))
        
    def occur(self, apps_f='/media/kaggle/careerbuilder/data/user_history.tsv'):
        f = open(apps_f)
        f.readline()
        for l in f:
            l = l.strip().split('\t')
            if len(l) < 5: continue
            u_tok, u_title = int(l[0]), l[4]
            try:
                u_ind = self.UserTokens.token2id(u_tok)
            except KeyError:
                continue
            u_title = self.StringCleaner.clean(u_title)
            for w in u_title.split(' '):
                try:
                    w_ind = self.TitleTokens.token2id(w)
                except KeyError:
                    continue
                self.occurs[u_ind,w_ind] += 1
           
                
class UserWindowOccurs(Occurs):
    
    def __init__(self, Users, UserTokens, WindowTokens):
        self.Users = Users
        self.UserTokens, self.WindowTokens = UserTokens, WindowTokens
        self.occurs = dok_matrix((UserTokens.token_count(),WindowTokens.token_count()))
        self.co_occur()
        
    def co_occur(self):
        for u_tok, u_id in self.UserTokens.tokens2ids.iteritems():
            u_win = self.Users[u_tok]['WindowID']
            self.occurs[u_id,self.WindowTokens.token2id(u_win)] = 1.0


class UserZipOccurs(Occurs):
    
    def __init__(self, Users, UserTokens, ZipTokens):
        self.Users = Users
        self.UserTokens, self.ZipTokens = UserTokens, ZipTokens
        self.occurs = dok_matrix((UserTokens.token_count(),ZipTokens.token_count()))
        self.co_occur()
        
    def co_occur(self):
        for u_tok, u_id in self.UserTokens.tokens2ids.iteritems():
            u_zip = self.Users[u_tok]['ZipCode']
            if u_zip is not None:
                try:
                    self.occurs[u_id,self.ZipTokens.token2id(u_zip)] = 1.0
                except KeyError:
                    continue
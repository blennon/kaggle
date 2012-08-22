'''
This loads things from tsv files for careerbuilder from disk
'''
from pylab import *

class Things(object):
    '''stores information associated with things (e.g. users, jobs, etc)'''
        
    def load_things(self,things_file,delim):
        '''load things from flatfile with format thing\tattrib\tattrib'''
        things = {}
        header = things_file.readline().strip().split(delim)
        for l in things_file:
            thing_id, thing_dict = self.parse_thing(l.strip().split(delim))
            things[thing_id] = thing_dict
        return things
    
    def parse_thing(self,line):
        pass
    
    @staticmethod
    def try_int_none(i):
        '''try to convert to int, otherwise return None'''
        try:
            return int(i)
        except ValueError:
            return None
        
    @staticmethod
    def parse_zip(zip_str):
        # need to implement zip lookup by city, state
        try:
            zip = int(zip_str)
        except ValueError:
            if '-' in zip_str:
                zip = int(zip_str.split('-')[0])
            else:
                zip = None
        return zip
    
    def __getitem__(self,thing_id):
        return self.things[thing_id]
    
    def __len__(self):
        return len(self.things)

class Users(Things):
    '''stores users information'''
    
    def __init__(self, users_file='/media/kaggle/careerbuilder/data/users.tsv', delim='\t'):
        self.things = self.load_things(open(users_file),delim)
        
    def parse_thing(self, line):
        u = {}
        u['WindowID'] = Users.try_int_none(line[1])
        u['Split'] = line[2]
        u['City'] = line[3]
        u['State'] = line[4]
        u['Country'] = line[5]
        u['Zip'] = Users.parse_zip(line[6])
        u['DegreeType'] = line[7]
        u['Major'] = line[8]
        u['GraduationDate'] = line[9]
        u['WorkHistoryCount'] = Users.try_int_none(line[10])
        u['TotalYearsExperience'] = Users.try_int_none(line[11])
        u['CurrentlyEmployed'] = line[12]
        u['ManagedOthers'] = line[13]
        u['ManagedHowMany'] = Users.try_int_none(line[14])
        return int(line[0]),u
    
class Jobs(Things):
    '''stores jobs information'''
    
    def __init__(self, jobs_file='/media/kaggle/careerbuilder/data/jobs.tsv', delim='\t'):
        self.things = self.load_things(open(jobs_file),delim)
        
    def parse_thing(self, line):
        j = {}
        j['WindowID'] = Jobs.try_int_none(line[1])
        j['Title'] = line[2]
        j['Description'] = line[3]
        j['Requirements'] = line[4]
        j['City'] = line[5]
        j['State'] = line[6]
        j['Country'] = line[7]
        j['Zip'] = Jobs.parse_zip(line[8])
        j['StartDate'] = line[9]
        j['EndDate'] = line[10]
        return int(line[0]),j
    
if __name__ == "__main__":
    U = Users()
    assert U[547]['ZipCode'] == 6460

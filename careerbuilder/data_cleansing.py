import re
from pylab import *

class StringCleaner(object):
    
    def __init__(self):
        self.bad_list = ['of','for','and','by','the','in','at']
        
    def clean(self, s):
        s = re.sub(r'[A-Z][A-Z0-9 .\?\,\(\)]{6,}\s+',' ',s) # remove boilerplate
        s = re.sub("([a-z])([A-Z])","\g<1> \g<2>",s) #split camelCase words
        s = s.lower()
        s = self.remove_bad(s)
        s = re.sub('[^a-zA-Z ]',' ',s)
        s = re.sub(' {2,}',' ',s) # remove extra spaces
        s = ' '.join([w for w in s.split(' ') if len(w)>1]) #remove single letters
        return s
    
    def remove_bad(self, s):
        for b in self.bad_list:
            bs = ' %s ' % b
            if bs in s:
                s = s.replace(bs,'')
        return s


class WordCounter(object):
    '''
    This class keeps track of word frequencies and provides
    utilities for pruning the list and analysis
    '''
    
    def __init__(self):
        self.words = {}
        
    def count_words(self, s):
        for w in s.strip().split(' '):
            self.words[w] = self.words.get(w,0) + 1
    
    def hist(self):
        '''Plot a histogram of word distributions'''
        self.hist = []
        for w in self.words.itervalues():
            self.hist.append(w)
        hist(self.hist, bins=50, log=True)
        
    def plot_ordered_freq(self):
        plot([f for w,f in self.get_ordered_list()])
        yscale('log')
        
    def prune_by_count(self, count):
        '''remove words in self.words with counts less than count'''
        words = self.get_ordered_list()
        for w,c in words:
            if c < count:
                self.words.pop(w)
                
    def keep_top_N(self, N):
        '''keep only the top N most freq words in self.words'''
        pop_words = self.get_ordered_list()[N:]
        for w,v in pop_words:
            self.words.pop(w)
        
    def get_ordered_list(self):
        '''return an ordered list (greatest to fewest) of words and
        their counts'''
        w_list = sorted(self.words.iteritems(), key=operator.itemgetter(1))
        w_list.reverse()
        return w_list
    
    def get_word_list(self):
        return [w for w in self.words.iterkeys()]
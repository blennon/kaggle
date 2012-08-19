import re
import operator
from pylab import *

class StringCleaner(object):
    
    def __init__(self, stopwords_f=None):
        if stopwords_f is not None:
            self.stop_words = self.load_stop_words(stopwords_f)
        
    def clean(self, s, rem_stopwords=True, badlist=None):
        s = re.sub(r'[A-Z][A-Z0-9 .\?\,\(\)]{6,}\s+',' ',s) # remove boilerplate
        s = re.sub("([a-z])([A-Z])","\g<1> \g<2>",s) #split camelCase words
        s = s.lower()
        if badlist is not None:
            s = self.remove_bad(s, badlist)
        s = re.sub('[^a-zA-Z ]',' ',s)
        s = re.sub(' [a-z] ', ' ', s) #remove single letters
        if rem_stopwords:
            s = self.remove_stop_words(s)
        s = re.sub(' {2,}',' ',s) # remove extra spaces
        return s
    
    def remove_bad(self, s, badlist):
        for b in badlist:
            s = s.replace(b,' ')
        return s
    
    def load_stop_words(self, stop_words_f):
        '''load the list of stop words from a text file'''
        stop_words = set()
        for l in open(stop_words_f):
            l = l.strip()
            if l != '':
                stop_words.add(l)
        return stop_words
    
    def remove_stop_words(self, s):
        '''remove stop words from self.words'''
        for w in self.stop_words:
            w_s = ' %s ' % w
            if w_s in s:
                s = s.replace(w_s,' ')
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
'''
Created on Mar 13, 2013

@author: bill
'''
import unittest
import sys
sys.path.append('../')
import datetime as dt
from data_grabber import *

class Test(unittest.TestCase):


    def setUp(self):
        self.DG = DataGrabber()


    def tearDown(self):
        pass


    def test_build_dataframe(self):
        df = self.DG.build_dataframe_for('CROCUS','accel')
        t = dt.datetime.strptime('2011-11-29 14:55:16',"%Y-%m-%d %H:%M:%S")
        self.assertAlmostEqual(df['x.mean'][t],0.754802346229553,delta=1e-15)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
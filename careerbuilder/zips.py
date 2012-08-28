import numpy
numpy.seterr(all='raise')
from pylab import *


class Zips(object):
    
    def __init__(self, zips_csv='/media/data/zips/zips.csv'):
        self.zips, self.cities = self.load(zips_csv)
        
    def load(self, zips_csv):
        '''load the zipcode data into a dictionary from a csv'''
        zips_dict, city_dict = {}, {}
        zips_f = open(zips_csv)
        header = zips_f.readline().strip().split(',')
        for l in zips_f:
            zip,state_abr,lat,long_,city,state = l.strip().split('", "')
            lat,long_ = float(lat), float(long_)
            state = state[0:-1]
            city, state_abr = city.lower(), state_abr.lower()
            city_dict[(city,state_abr)] = {'lat':lat,'long':long_}
            try:
                zip = int(zip[1:])
            except ValueError:
                continue
            city_dict[(city,state_abr)]['zip'] = zip
            zips_dict[zip] = {'lat':lat,'long':long_,'city':city,'state':state,
                              'state_abr':state_abr}
        return zips_dict, city_dict
                       
    def zip_dist(self, zip1, zip2):
        '''find the distance (miles) between zip1 and zip2'''
        if zip1 == zip2:
            return 0
        lat1,long1 = self.lat_long_lookup(zip1)
        lat2,long2 = self.lat_long_lookup(zip2)
        
        return Zips.lat_long_dist(lat1,long1,lat2,long2)
    
    def lat_long_lookup(self, place):
        '''
        return lat/long values for a place
        place can be either a zip (int) or (city,state_abr) tuple
        '''
        if isinstance(place,int):
            z = self.zips[place]
            return z['lat'], z['long']
        elif isinstance(place,tuple):
            (city,state) = place[0].lower(),place[1].lower()
            c = self.cities[(city,state)]
            return c['lat'], c['long']
        else:
            raise Exception('place can be either a zip (int) or (city,state_abr) tuple')    
            
    @staticmethod
    def lat_long_dist(lat_A, long_A, lat_B, long_B):
        '''return distance in miles between two lat/long coordinates'''
        distance = (sin(radians(lat_A)) *
                    sin(radians(lat_B)) +
                    cos(radians(lat_A)) *
                    cos(radians(lat_B)) *
                    cos(radians(long_A - long_B)))

        try:
            return (degrees(arccos(distance))) * 69.09
        except FloatingPointError:
            if isinstance(distance,float):
                distance = 1.0
            else:
                distance[distance>1.0] = 1.0
            return (degrees(arccos(distance))) * 69.09

if __name__ == "__main__":
    Zips = Zips()
    assert int(Zips.zip_dist(92064,93313)) == 192
    assert Zips.cities[('poway','ca')]['zip'] == 92064

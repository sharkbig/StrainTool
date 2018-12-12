#! /usr/bin/python3
#-*- coding: utf-8 -*-

from __future__ import print_function
import sys, os, time, random, math
from datetime import datetime
from copy import deepcopy
import numpy
from pystrain.strain import *
from pystrain.geodesy.utm import *
from pystrain.iotools.iparser import *
import pystrain.grid
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

gps_file = sys.argv[1]
xmin, xmax, ymin, ymax = 2, 12, 41, 49 # 18.75,30.25,32.75,42.25
cut_sta_out_of_region = True

##  Parse stations from input file; at input, station coordinates are in decimal
##+ degrees and velocities are in mm/yr.
##  After reading, station coordinates are in radians and velocities are in
##+ m/yr.
if not os.path.isfile(gps_file):
    print('[ERROR] Cannot find input file \'{}\'.'.format(gps_file), file=sys.stderr)
    sys.exit(1)
sta_list_ell = parse_ascii_input(gps_file)
print('[DEBUG] Reading station coordinates and velocities from {}'.format(gps_file))
print('[DEBUG] Number of stations parsed: {}'.format(len(sta_list_ell)))

if cut_sta_out_of_region:
    newl = []
    for s in sta_list_ell:
        dlon = math.degrees(s.lon)
        dlat = math.degrees(s.lat)
        if dlon > xmin and dlon < xmax and dlat > ymin and dlat < ymax:
            newl.append(s)
    sta_list_ell = newl

##  Make a new station list (copy of the original one), where all coordinates
##+ are in UTM. All points should belong to the same ZONE.
##  Note that station ellipsoidal coordinates are in radians while the cartesian
##+ coordinates are in meters.
##
##  TODO is this mean_lon the optimal?? or should it be the region's mean longtitude
##
mean_lon = degrees(sum([ x.lon for x in sta_list_ell ]) / len(sta_list_ell))
utm_zone = floor(mean_lon/6)+31
utm_zone = utm_zone + int(utm_zone<=0)*60 - int(utm_zone>60)*60
print('[DEBUG] Mean longtitude is {} deg.; using Zone = {} for UTM'.format(mean_lon, utm_zone))
sta_list_utm = deepcopy(sta_list_ell)
for idx, sta in enumerate(sta_list_utm):
    N, E, Zone, lcm = ell2utm(sta.lat, sta.lon, Ellipsoid("wgs84"), utm_zone)
    sta_list_utm[idx].lon = E
    sta_list_utm[idx].lat = N
    assert Zone == utm_zone, "[ERROR] Invalid UTM Zone."
print('[DEBUG] Station list transformed to UTM.')

## Random point within limits
slon = 6 #random.uniform(xmin, xmax)
slat = 44 #random.uniform(ymin, ymax)
clat, clon = radians(slat), radians(slon)
N, E, ZN, _ = ell2utm(clat, clon, Ellipsoid("wgs84"), utm_zone)
assert ZN == utm_zone

dargs = {
    'ltype': 'gaussian',
    'Wt': 12, 
    'dmin': 1,
    'dmax': 500,
    'dstep': 2,
    'd_coef': None,
    'cutoff_dis': None,
    'weighting_function': 'shen',
    'verbose_mode': False
}
sstr = ShenStrain(E, N, sta_list_utm, **dargs)
print("Max beta angle is {:6.1f} deg.".format(degrees(max(sstr.beta_angles()))))

sstr.estimate()
cc  = Station(lon=sstr.__xcmp__, lat=sstr.__ycmp__)
thetas = sstr.compute_theta_angles()
W = sstr.make_weight_matrix()
meanW = {}
print("{:>4s} {:>10s} ({:>5s},{:>5s}) {:>10s} {:>10s} {:>5s} {:>7s} {:>7s} {:>7s}".format("name", "lweight", "exp", "div", "zweight", "distance","θ", "Wx", "Wy", "Wsum"))
for idx, sta in enumerate(sstr.__stalst__):
    D = sstr.__options__['d_coef']
    dr  = cc.distance_from(sta)[2]/1e3
    wsum = sum([ x[0]*x[1] for x in zip(sstr.__lweights__,sstr.__zweights__) ])*2
    li = sstr.__lweights__[idx]
    li_1 = exp(-dr*dr/(D*D))
    li_2 = 1e0/(1e0+(dr*dr/(D*D)))
    print("{:} {:10.3f} ({:5.3f},{:5.3f}) {:10.3f} {:10.1f} {:5.1f} {:7.3f} {:7.3f} {:7.2f}".format(sta.name, li, li_1, li_2, sstr.__zweights__[idx], dr, degrees(thetas[idx]), float(W[idx*2]), float(W[idx*2+1]), wsum))
    meanW[sta.name] = (float(W[idx*2])+float(W[idx*2+1])) / 2e0

#print("Stations not used")
#names = [ s.name for s in sstr.__stalst__ ]
#for s in sta_list_ell:
#    if s.name not in names:
#        dr  = cc.distance_from(s)[2]/1e3
#        print("{:} {:10.1f}".format(s.name, dr))

names = [ s.name for s in sstr.__stalst__ ]
sta_list_ell = [ s for s in sta_list_ell if s.name in names ]

lat0    = degrees(sum([ x.lat for x in sta_list_ell ])/len(sta_list_ell))
lon0    = degrees(sum([ x.lon for x in sta_list_ell ])/len(sta_list_ell))
lons    = [ degrees(x.lon) for x in sta_list_ell ]
lats    = [ degrees(x.lat) for x in sta_list_ell ]
lon_off = (max(lons)-min(lons))/10
lat_off = (max(lats)-min(lats))/10
my_map = Basemap(projection='merc', lat_0 = lat0, lon_0 = lon0, resolution = 'c', llcrnrlon=min(lons)-lon_off, llcrnrlat=min(lats)-lat_off, urcrnrlon=max(lons)+lon_off, urcrnrlat=max(lats)+lat_off)
my_map.drawcoastlines()
my_map.drawcountries()
my_map.fillcontinents(color = 'coral')
my_map.drawmapboundary()
my_map.drawmeridians(numpy.arange(floor(min(lons)), math.ceil(max(lons)), 2), labels=[True,False,False,True])
my_map.drawparallels(numpy.arange(floor(min(lats)), math.ceil(max(lats)), 2), labels=[False,True,True,False], fontsize=10)
my_map.plot(clon, clat, markersize=12)
for sta in sta_list_ell:
    x, y = my_map(degrees(sta.lon), degrees(sta.lat))
    my_map.plot(x, y, 'bo', markersize=10)
    plt.text(x, y, sta.name+" {:5.2f}".format(meanW[sta.name]))
    my_map.drawgreatcircle(slon,slat,degrees(sta.lon),degrees(sta.lat), linewidth=2,color='g')
plt.show()

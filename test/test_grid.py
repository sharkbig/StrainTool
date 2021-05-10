#! /usr/bin/python

from __future__ import print_function
import sys
import pystrain.grid2
import pystrain.grid
import random

# seed random number generator
random.seed()

def lists_equal(lst1, lst2):
    if len(lst1) != len(lst2):
        print('Invalid grid sizes! {:} vs {:}'.format(len(lst1), len(lst2)))
        return False
    for elmnt in lst1:
        if elmnt not in lst2:
            print('Failed to match element: {:}'.format(elmnt))
            return False
    return True

def choose_step_size(num_steps=1, ifrom=0.01, ito=15e0):
    steps = []
    for i in range(num_steps):
        steps.append((round(random.uniform(ifrom, ito), 2), round(random.uniform(ifrom, ito), 2)))
    return steps

def print_matching(lst1, lst2):
    matched_idx = []
    if len(lst1) > len(lst2):
        master = lst1
        slave = lst2
        print('Max list is list1')
    else:
        master = lst2
        slave = lst1
        print('Max list is list2')
    for i in master:
        print('\n\t{:}'.format(i), end='')
        try:
            idx = slave.index(i)
            print('|{:}'.format(slave[idx]), end='')
            matched_idx.append(idx)
        except ValueError:
            pass
    for i in range(len(slave)):
        if i not in matched_idx:
            print('\tunmatched: {:}'.format(slave[i]))

lat_range = (-90e0, 90e0)
lon_range = (-180, 180)
lat_width = 15e0
lon_width = 15e0

grid_xy0 = []
grid_xy1 = []
grid_xy2 = []
test_nr = 0
# for lat_start in range(lat_range[0], lat_range[1], lat_range[2]):
lat_start = lat_range[0]
while lat_start < lat_range[1]:
    lat_from = float(lat_start)
    lat_to = lat_from + lat_width
    for lon_start in range(lon_range[0], lon_range[1], random.randint(1, 25)):
        lon_from = float(lon_start)
        lon_to = lon_from + round(random.uniform(7.0, 25.0), 2)
        for step_sizes in choose_step_size(3):
            print('<-------------------------------------------------------------------------------TEST->')
            print('Longtitude {:} to {:} with step={:}'.format(lon_from, lon_to, step_sizes[0]))
            print('Latitude   {:} to {:} with step={:}'.format(lat_from, lat_to, step_sizes[1]))
            grd = pystrain.grid2.Grid(lon_from, lon_to, step_sizes[0], lat_from, lat_to, step_sizes[1])
            for x, y in grd:
                grid_xy1.append('{:+12.3f}{:+12.3f}'.format(x,y))
            try:
                g1, g2, g3, g4 = grd.split_four()
                for g in [g1, g2, g3, g4]:
                    for x,y in g:
                        grid_xy2.append('{:+12.3f}{:+12.3f}'.format(x,y))
                if not lists_equal(grid_xy1, grid_xy2):
                    #print_matching(grid_xy1, grid_xy2)
                    sys.exit(1)
            except RuntimeError as err:
                print('WARNING! Failed to split grid {:}'.format(grd))
                print('         Msg: {:}'.format(err))
            #grd0 = pystrain.grid.Grid(lon_from, lon_to, step_sizes[0], lat_from, lat_to, step_sizes[1])
            #for x, y in grd0:
            #    grid_xy0.append('{:+12.3f}{:+12.3f}'.format(x,y))
            #if not lists_equal(grid_xy0, grid_xy1):
            #    print('[ERROR] Version 1 grid is different!')
            #    print_matching(grid_xy0, grid_xy1)
            #    sys.exit(1)
            grid_xy0 = []
            grid_xy1 = []
            grid_xy2 = []
    lat_start += round(random.uniform(0.01, 15e0), 2)

#! /usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
import math
import numpy as np
from sys import float_info


class Grid:

    def __init__(self,
                 xmin,
                 x__,
                 xstep,
                 ymin,
                 y__,
                 ystep,
                 init_from_num_pts=False):
        if not init_from_num_pts:
            self.__init_from_limits__(xmin, x__, xstep, ymin, y__, ystep)
        else:
            self.__init_from_numpts__(xmin, x__, xstep, ymin, y__, ystep)

    def __init_from_limits__(self, xmin, xmax, xstep, ymin, ymax, ystep):
        assert (xmin <= xmax and ymin <= ymax)
        assert (xstep > 0 and ystep > 0)
        self.xmin = xmin
        self.xstep = xstep
        self.xlength = math.ceil((xmax - xmin) / xstep)
        self.ymin = ymin
        self.ystep = ystep
        self.ylength = math.ceil((ymax - ymin) / ystep)
        """
        ## redundant tests .... delete
        self.xrange = np.arange(xmin, xmax, xstep)
        self.yrange = np.arange(ymin, ymax, ystep)
        if not self.xlength == self.xrange.size:
            print('Computed x-length: {:} np-length: {:}'.format(self.xlength, self.xrange.size))
        if not self.ylength == self.yrange.size:
            print('Computed y-length: {:} np-length: {:}'.format(self.ylength, self.yrange.size))
        assert(self.xlength == self.xrange.size)
        assert(self.ylength == self.yrange.size)
        print('\tGrid initialized! NP sizes match aka {:}/{:} and {:}/{:}'.format(self.xlength, self.xrange.size, self.ylength, self.yrange.size))
        """

    def __init_from_numpts__(self, xmin, xpts, xstep, ymin, ypts, ystep):
        assert (xstep > 0 and ystep > 0)
        assert (isinstance(xpts, int) and isinstance(ypts, int))
        self.xmin = xmin
        self.xstep = xstep
        self.xlength = xpts
        self.ymin = ymin
        self.ystep = ystep
        self.ylength = ypts

    def xmax(self): return self.xmin + self.xlength * self.xstep
    def ymax(self): return self.ymin + self.ylength * self.ystep
    def num_nodes(self): return self.xlength * self.ylength

    def __repr__(self):
        return 'Grid xaxis-> from:{:}, step:{:}, points:{:}\n     yaxis-> from:{:}, step:{:}, points:{:}'.format(
            self.xmin, self.xstep, self.xlength, self.ymin, self.ystep,
            self.ylength)

    def __str__(self):
        xstop = self.xmin + self.xlength * self.xstep
        ystop = self.ymin + self.ylength * self.ystep
        return '{:+12.7f}/{:+12.7f}/{:+12.7f}/{:+12.7f}'.format(
            self.xmin, xstop, self.ymin, ystop)

    def __iter__(self):
        self.x_idx = 0
        self.y_idx = 0
        return self

    def index2point(self, xidx, yidx):
        assert (xidx < self.xlength and yidx < self.ylength)
        xpt = self.xmin + xidx * self.xstep + self.xstep / 2e0
        ypt = self.ymin + yidx * self.ystep + self.ystep / 2e0
        return xpt, ypt

    def __next__(self):
        if self.y_idx >= self.ylength:
            self.x_idx += 1
            if self.x_idx >= self.xlength:
                raise StopIteration
            self.y_idx = 0
        pt = self.index2point(self.x_idx, self.y_idx)
        self.y_idx += 1
        return pt

    def split_four(self):
        if self.xlength < 2 or self.ylength < 2:
            print(
                '[ERROR] Trying to split grid which is a block! Cannot do that!'
            )
            error_msg = 'Grid [{:}] is a block; cannot split it'.format(
                self.__repr__())
            raise RuntimeError(error_msg)
        xhalf_pts = self.xlength // 2
        yhalf_pts = self.ylength // 2
        xmiddle_pt = self.xmin + xhalf_pts * self.xstep
        ymiddle_pt = self.ymin + yhalf_pts * self.ystep
        xrest_pts = self.xlength - xhalf_pts
        yrest_pts = self.ylength - yhalf_pts
        g1, g2, g3, g4 = Grid(
            self.xmin, xhalf_pts, self.xstep, self.ymin, yhalf_pts, self.ystep,
            True), Grid(xmiddle_pt, xrest_pts, self.xstep, self.ymin, yhalf_pts,
                        self.ystep,
                        True), Grid(self.xmin, xhalf_pts, self.xstep,
                                    ymiddle_pt, yrest_pts, self.ystep,
                                    True), Grid(xmiddle_pt, xrest_pts,
                                                self.xstep, ymiddle_pt,
                                                yrest_pts, self.ystep, True)
        """
        print('DEBUG:: [X-lengths: {:}, {:}, {:}, {:}] -> {:}'.format(g1.xlength, g2.xlength, g3.xlength, g4.xlength, self.xlength))
        print('DEBUG:: [Y-lengths: {:}, {:}, {:}, {:}] -> {:}'.format(g1.ylength, g2.ylength, g3.ylength, g4.ylength, self.ylength))
        if not (g1.xlength + g2.xlength == self.xlength) or not (g1.ylength + g3.ylength == self.ylength):
            print('Master: {:}'.format(self.__repr__()))
            print('G1    : {:}'.format(g1.__repr__()))
            print('G2    : {:}'.format(g2.__repr__()))
            print('G3    : {:}'.format(g3.__repr__()))
            print('G4    : {:}'.format(g4.__repr__()))
            print('\nX\'s   :', end='')
            for i in range(self.xlength):
                print('{:+8.3f},'.format(self.xmin + i*self.xstep + self.xstep/2e0),end='')
            print('\nX\'s   :', end='')
            for g in [g1, g2]:
                for i in range(g.xlength): print('{:+8.3f},'.format(g.xmin + i*g.xstep + g.xstep/2e0),end='')
            print('\nY\'s   :', end='')
            for i in range(self.ylength): print('{:+8.3f},'.format(self.ymin + i*self.ystep + self.ystep/2e0),end='')
            print('\nY\'s   :', end='')
            for g in [g1, g3]:
                for i in range(g.ylength): print('{:+8.3f},'.format(g.ymin + i*g.ystep + g.ystep/2e0),end='')
        """
        assert (g1.xlength + g2.xlength == self.xlength)
        assert (g1.ylength + g3.ylength == self.ylength)
        return g1, g2, g3, g4

def generate_grid(station_lst, x_step, y_step, **kwargs):
    #rad2deg = False 
    #if 'rad2deg' in kwargs and kwargs['rad2deg'] is True: rad2deg = True
    rad2deg = kwargs.get('rad2deg', False)
    y_min = float_info.max
    y_max = float_info.min
    x_min = float_info.max
    x_max = float_info.min
    for station in station_lst:
        if rad2deg:
            slon = math.degrees(s.lon)
            slat = math.degrees(s.lat)
        else:
            slon = s.lon
            slat = s.lat
        if slon > x_max:
            x_max = slon
        if slon < x_min:
            x_min = slon
        if slat > y_max:
            y_max = slat
        if slat < y_min:
            y_min = slat
    # Adjust max and min to step.
    s = float((floor((y_max - y_min) / y_step) + 1e0) * y_step)
    r = s - (y_max - y_min)
    y_min -= r / 2
    y_max += r / 2
    s = float((floor((x_max - x_min) / x_step) + 1e0) * x_step)
    r = s - (x_max - x_min)
    x_min -= r / 2
    x_max += r / 2
    return Grid(x_min, x_max, x_step, y_min, y_max, y_step)

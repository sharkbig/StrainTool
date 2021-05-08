#! /usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
import math
import numpy as np

class Grid:
    def __init__(self, xmin, x__, xstep, ymin, y__, ystep, init_from_num_pts=False):
        if not init_from_num_pts:
            self.__init_from_limits__(xmin, x__, xstep, ymin, y__, ystep)
        else:
            self.__init_from_numpts__(xmin, x__, xstep, ymin, y__, ystep)

    def __init_from_limits__(self, xmin, xmax, xstep, ymin, ymax, ystep):
        assert(xmin<=xmax and ymin<=ymax)
        assert(xstep>0 and ystep>0)
        self.xmin = xmin
        self.xstep = xstep
        self.xlength = math.ceil((xmax - xmin)/xstep)
        self.ymin = ymin
        self.ystep = ystep
        self.ylength = math.ceil((ymax - ymin)/ystep)
        ## redundant tests .... delete
        self.xrange = np.arange(xmin, xmax, xstep)
        self.yrange = np.arange(ymin, ymax, ystep)
        if not self.xlength == self.xrange.size:
            print('Computed x-length: {:} np-length: {:}'.format(self.xlength, self.xrange.size))
        if not self.ylength == self.yrange.size:
            print('Computed y-length: {:} np-length: {:}'.format(self.ylength, self.yrange.size))
        assert(self.xlength == self.xrange.size)
        assert(self.ylength == self.yrange.size)

    def __init_from_numpts__(self, xmin, xpts, xstep, ymin, ypts, ystep):
        assert(xstep>0 and ystep>0)
        assert(isinstance(xpts, int) and isinstance(ypts, int))
        self.xmin = xmin
        self.xstep = xstep
        self.xlength = xpts
        self.ymin = ymin
        self.ystep = ystep
        self.ylength = ypts

    def __repr__(self):
        return 'Grid xaxis-> from{:}, step:{:}, points: {:} yaxis-> from{:}, step:{:}, points: {:}'.format(self.xmin, self.xstep, self.xlength, self.ymin, self.ystep, self.ylength)

    def __str__(self):
        xstop = self.xmin + self.xlength*self.xstep
        ystop = self.ymin + self.ylength*self.ystep
        return '{:+12.7f}/{:+12.7f}/{:+12.7f}/{:+12.7f}'.format(self.xmin, xstop, self.ymin, ystop)

    def __iter__(self):
        self.x_idx = 0
        self.y_idx = 0
        return self

    def index2point(self, xidx, yidx):
        assert(xidx<self.xlength and yidx<self.ylength)
        xpt = self.xmin + xidx*self.xstep + self.xstep/2e0
        ypt = self.ymin + yidx*self.ystep + self.ystep/2e0
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
        if self.xlength < 2 and self.ylength < 2:
            print('[ERROR] Trying to split grid which is a block! Cannot do that!')
            error_msg = 'Grid [{:}] is a block; cannot split it'.format(self.__repr__())
            raise RuntimeError(error_msg)
        xhalf_pts = self.xlength // 2
        yhalf_pts = self.ylength // 2
        xmiddle_pt = self.xmin + xhalf_pts * self.xstep
        ymiddle_pt = self.ymin + yhalf_pts * self.ystep
        xrest_pts = self.xlength - xhalf_pts
        yrest_pts = self.ylength - yhalf_pts
        g1, g2, g3, g4 =  Grid(self.xmin, xhalf_pts, self.xstep, self.ymin, yhalf_pts, self.ystep, True), Grid(xmiddle_pt, xrest_pts, self.xstep, self.ymin, yhalf_pts, self.ystep, True), Grid(self.xmin, xhalf_pts, self.xstep, ymiddle_pt, yrest_pts, self.ystep, True), Grid(xmiddle_pt, xrest_pts, self.xstep, ymiddle_pt, yrest_pts, self.ystep, True)
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
        assert(g1.xlength + g2.xlength == self.xlength)
        assert(g1.ylength + g3.ylength == self.ylength)
        return g1, g2, g3, g4


    def split_four2(self):
        xhalf_pts = self.xlength // 2
        yhalf_pts = self.ylength // 2
        xmiddle = self.xmin + xhalf_pts*self.xstep
        ymiddle = self.ymin + yhalf_pts*self.ystep
        g1, g2, g3, g4 = Grid(self.xmin, xmiddle, self.xstep, self.ymin, ymiddle, self.ystep), Grid(xmiddle, self.xmin+self.xlength*self.xstep, self.xstep, self.ymin, ymiddle, self.ystep), Grid(self.xmin, xmiddle, self.xstep, ymiddle, self.ymin+self.ylength*self.ystep, self.ystep), Grid(xmiddle, self.xmin+self.xlength*self.xstep, self.xstep, ymiddle, self.ymin+self.ylength*self.ystep, self.ystep)
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
        #assert(g1.xlength + g2.xlength == self.xlength)
        #assert(g1.ylength + g3.ylength == self.ylength)
        return g1, g2, g3, g4

if __name__ == "__main__":
    grd = Grid(19.25e0, 20.75e0, 0.5e0, 34.25e0, 40.75e0, 0.5e0)
    print('Initializing grid with: grd = Grid(19.25e0, 20.75e0, 0.5e0, 34.25e0, 40.75e0, 0.5e0)')
    print('{:}'.format(grd))
    grid_pts1 = []
    for x,y in grd:
        print('\t{:}, {:}'.format(x,y))
        assert(x<20.75e0 and y<40.75e0)
        grid_pts1.append( (x,y) )
    grid_pts2 = []
    print('-----------------------------------------------------------------------------')
    g1, g2, g3, g4 = grd.split_four()
    for g in [g1, g2, g3, g4]:
        for x,y in g:
            print('\t{:}, {:}'.format(x,y))
            assert(x<20.75e0 and y<40.75e0)
            grid_pts2.append( (x,y) )
    assert(len(grid_pts1) == len(grid_pts2))
    for xy in grid_pts1:
        assert( xy in grid_pts2)

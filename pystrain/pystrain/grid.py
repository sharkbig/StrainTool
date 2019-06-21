#! /usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
from sys  import float_info
from math import floor, radians, degrees, ceil, floor
import numpy as np

class Grid:
    """A dead simple grid class.

        A very simple grid class to be used within the StrainTensor project.
        A Grid instance has x- and y- axis limits and step sizes (i.e x_min,
        x_max, x_step, y_min, y_max, y_step).
        It is iterable; when iterating, the instance will return the center
        of each cell, starting from the bottom left corner and ending at the
        top right. The iteration is performed row-wise (i.e.
        > [x0+xstep/2, y0+ystep/2]
        > [x0+xstep/2, y0+ystep/2+ystep]
        > [x0+xstep/2, y0+ystep/2+2*ystep]
        > ...
        > [x0+xstep/2, ymax-ystep/2]
        > [x0+xstep/2+xstep, y0+ystep/2]
        > [x0+xstep/2+xstep, y0+ystep/2+ystep]
        > [x0+xstep/2+xstep, y0+ystep/2+2*ystep]

        Attributes:
            x_min : minimum value in x-axis.
            x_max : maximum value in x-axis.
            x_step: x-axis step size.
            y_min : minimum value in y-axis.
            y_max : maximum value in y-axis.
            y_step: y-axis step size.
            cxi   : current x-axis tick / index
            cyi   : current y-axis tick / index
            xpts  : number of ticks on x-axis
            ypts  : number of ticks on y-axis
    """

    def split2four(self):
        """ Split the grid to four indipendent, same-size grids
        """
        x2 = self.x_min + (self.xpts/2)*self.x_step
        y2 = self.y_min + (self.ypts/2)*self.y_step
        g1 = Grid(self.x_min, x2, self.x_step, self.y_min, y2, self.y_step)
        g2 = Grid(x2, self.x_max, self.x_step, self.y_min, y2, self.y_step) 
        g3 = Grid(self.x_min, x2, self.x_step, y2, self.y_max, self.y_step)
        g4 = Grid(x2, self.x_max, self.x_step, y2, self.y_max, self.y_step)
        return g1, g2, g3, g4

    ## TODO write about ceil/floor and [x|y]_max in documentation
    def __init__(self, x_min, x_max, x_step, y_min, y_max, y_step, strict_upper_limit=False, upper_limit_epsilon=1e-10):
        """Constructor via x- and y- axis limits.

            The __init__ method will assign all of the instance's attributes.
            The x- and y- tick indexes will be set to 0 (ready for iterating).

            Args:
                x_min : minimum value in x-axis.
                x_max : maximum value in x-axis.
                x_step: x-axis step size.
                y_min : minimum value in y-axis.
                y_max : maximum value in y-axis.
                y_step: y-axis step size.
                strict_upper_limit: see Note
                upper_limit_epsilon: see Note

            Note:
                To find the number of points between the min and max values for
                each of the axis (aka x and y), the function will perform a
                computation of the type:
                xpts = int(floor((x_max-x_min) / float(x_step)))
                This is quite accurate, but due to roundoff errors, it may 
                happen that the quantity x_min + xpts * x_step is just a bit 
                larger than x_max.
                If the user definitely wants the formula:
                x_min + self.xpts * x_step <= x_max to hold, then the option
                strict_upper_limit must be set to true.
                If strict_upper_limit is false, then the above relationship
                will hold up to the given accuracy, aka upper_limit_epsilon,
                that is:
                x_min + self.xpts * x_step <= x_max + upper_limit_epsilon

        """
        self.x_min = x_min
        self.x_max = x_max
        self.x_step= x_step
        self.y_min = y_min
        self.y_max = y_max
        self.y_step= y_step
        self.cxi    = 0      # current x-axis tick / index
        self.cyi    = 0      # current y-axis tick / index
        self.xpts   = int(floor((x_max-x_min) / float(x_step)))
        self.ypts   = int(floor((y_max-y_min) / float(y_step)))
        if strict_upper_limit:
            while x_min + self.xpts * x_step > x_max:
                self.xpts -= 1
            while y_min + self.ypts * y_step > y_max:
                self.ypts -= 1
            upper_limit_epsilon = 0e0
        else:
            assert x_step > upper_limit_epsilon/2e0 and y_step > upper_limit_epsilon/2e0
        # if using ceil for pts number
        #assert x_min + self.xpts * x_step >= x_max and abs(x_min + self.xpts * x_step - x_max) < x_step/float(2)
        #assert y_min + self.ypts * y_step >= y_max and abs(y_min + self.ypts * y_step - y_max) < y_step/float(2)
        # if using floor for pts number
        assert self.xpts > 0 and self.ypts > 0
        assert x_min + self.xpts * x_step <= x_max + upper_limit_epsilon
        assert y_min + self.ypts * y_step <= y_max + upper_limit_epsilon

    def __iter__(self):
        self.cxi = 0
        self.cyi = 0
        return self

    def xidx2xval(self, idx):
        """Index to value for x-axis.
         
            Given an index (on x-axis), return the value at the centre of this
            cell. The index represents the number of a cell (starting from
            zero).

            Args:
                idx (int): the index; should be in range (0, self.xpts]
        """
        assert idx >= 0 and idx < self.xpts
        return self.x_min + self.x_step/2e0 + self.x_step*float(idx)
    
    def yidx2yval(self, idx):
        """Index to value for y-axis.
         
            Given an index (on y-axis), return the value at the centre of this
            cell. The index represents the number of a cell (starting from
            zero).

            Args:
                idx (int): the index; should be in range (0, self.ypts]
        """
        assert idx >= 0 and idx < self.ypts
        return self.y_min + self.y_step/2e0 + self.y_step*float(idx)

    def next(self):
        """Return the centre of the next cell.

            Return the (centre of the) next cell (aka x,y coordinate pair). Next
            actually means the cell on the right (if there is one), or else the
            leftmost cell in the above row.

            Raises:
                StopIteration: if there are not more cell we can get to.
        """
        xi, yi = self.cxi, self.cyi
        if self.cxi >= self.xpts - 1:
            if self.cyi >= self.ypts - 1:
                # last element iin iteration!
                if self.cxi == self.xpts - 1 and self.cyi == self.ypts - 1:
                    self.cxi += 1
                    self.cyi += 1
                    return self.xidx2xval(xi), \
                           self.y_min + self.y_step/2e0 + self.y_step*float(yi)
                else:
                    raise StopIteration
            self.cxi  = 0
            self.cyi += 1
        else:
            xi, yi = self.cxi, self.cyi
            self.cxi += 1
        return self.xidx2xval(xi), self.yidx2yval(yi)

    # Python 3.X compatibility
    __next__ = next

def generate_grid(sta_lst, x_step, y_step, sta_lst_to_deg=False):
    """Grid generator.

        Given a list of Stations and x- and y-axis step sizes, compute and
        return a Grid instance. The max/min x and y values (of the Grid) are
        extracted from the station coordinates; if needed, they are adjusted
        so that (xmax-xmin) is divisible (without remainder) with xstep.
        Obsviously, sta_lst coordinates (assesed by .lon and .lat) must match
        the x_step and y_step values respectively (same units and reference
        system).

        Args:
            sta_lst (list): list of Station instances. Coordinates of the stations are
                     used, using the 'lon' and 'lat' instance variables. Longtitude
                     values are matched to 'x_step' and latitude values are matched
                     to 'ystep'
            x_step  (float): value of step for the x-axis of the grid.
            y_step  (float): value of step for the y-axis of the grid.
            sta_lst_to_deg: If set to True, then the input parameters are first
                            converted to degrees (they are assumed to be radians)

        Returns:
            A Grid instance: the min and max values of the Grid are computed from
            the input coordinates (i.e. the sta_lst input list) and then adjusted
            so that the range (xmax-xmin) is divisible with x_step (same goes for
            the y-axis)

        Todo:
            The lines 
            assert divmod(y_max-y_min, y_step)[1] == 0e0 and
            assert divmod(x_max-x_min, x_step)[1] == 0e0
            may throw dues to rounding errors; how can i fix that?

    """
    #  Get min/max values of the stations (also transform from radians to degrees
    #+ if needed.
    y_min = float_info.max
    y_max = float_info.min
    x_min = float_info.max
    x_max = float_info.min
    for s in sta_lst:
        if sta_lst_to_deg:
            slon = degrees(s.lon)
            slat = degrees(s.lat)
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
    #print("\t[DEBUG] Region: Easting: {:}/{:} Northing: {:}/{:}".format(x_min, x_max, y_min, y_max))
    s      = float((floor((y_max-y_min)/y_step)+1e0)*y_step)
    r      = s-(y_max-y_min)
    y_min -= r/2
    y_max += r/2
    # assert divmod(y_max-y_min, y_step)[1] == 0e0
    s      = float((floor((x_max-x_min)/x_step)+1e0)*x_step)
    r      = s-(x_max-x_min)
    x_min -= r/2
    x_max += r/2
    # assert divmod(x_max-x_min, x_step)[1] == 0e0
    # return a Grid instance
    return Grid(x_min, x_max, x_step, y_min, y_max, y_step)

class IrregularGrid:
    
    def __init__(self, station_list, x_min, x_max, x_step, y_min, y_max, y_step, sta_list_to_degrees=False, strict_upper_limit=False, upper_limit_epsilon=1e-10):
        print("[DEBUG PYSTRAIN] called __init__ for IrregularGrid")
        grd = Grid(x_min, x_max, x_step, y_min, y_max, y_step, strict_upper_limit, upper_limit_epsilon)
        self.x_min = grd.x_min
        self.x_max = grd.x_max
        self.y_min = grd.y_min
        self.y_max = grd.y_max
        self.x_maxstep = grd.x_step*10e0
        self.y_maxstep = grd.y_step*10e0
        self.x_minstep = grd.x_step/5e0
        self.y_minstep = grd.y_step/5e0
        if sta_list_to_degrees:
            for sta in station_list:
                sta.lon, sta.lat = degrees(sta.lon), degrees(sta.lat)
        print("[DEBUG PYSTRAIN] calling self.__make_ticks__ for x axis (IrregularGrid)")
        self.x_ticks = self.__make_ticks__('x', station_list)
        print("[DEBUG PYSTRAIN] calling self.__make_ticks__ for y axis (IrregularGrid)")
        self.y_ticks = self.__make_ticks__('y', station_list)
        self.xpts = len(self.x_ticks)
        self.ypts = len(self.y_ticks)
        self.cxi = 0
        self.cyi = 0
        print("[DEBUG PYSTRAIN] # of x-ticks: {:5d}, # of y-ticks {:5d}".format(self.xpts, self.ypts))
        """
        print("[DEBUG PYSTRAIN] Ticks on x-axis (IrregularGrid):")
        for t in self.x_ticks: print("\t[DEBUG PYSTRAIN] {:10.7f}".format(t))
        print("[DEBUG PYSTRAIN] Ticks on y-axis (IrregularGrid):")
        for t in self.y_ticks: print("\t[DEBUG PYSTRAIN] {:10.7f}".format(t))
        """

    def __make_ticks__(self, axis, station_list):
        print("[DEBUG PYSTRAIN] called self.__make_ticks__ (IrregularGrid)")
        if axis == 'x':
            sta_lst = sorted(station_list, key=lambda x: x.lon, reverse=False)
            minx, maxx = self.x_min, self.x_max
            foo = lambda sta : sta.lon
            maxstep = self.x_maxstep
            minstep = self.x_minstep
        else:
            sta_lst = sorted(station_list, key=lambda x: x.lat, reverse=False)
            minx, maxx = self.y_min, self.y_max
            foo = lambda sta : sta.lat
            maxstep = self.y_maxstep
            minstep = self.y_minstep
        ##  Iterate through axis every with step = maxstep, from minx to maxx
        ##  Record number of stations that fall in every node (sta_per_cell)
        ##  Save max number of stations in node (max_sta_in_cell)
        sta_per_cell = []
        max_sta_in_cell = 0
        curx = minx
        while curx < maxx:
            cur_spl = 0
            c_minx, c_maxx = curx, curx+maxstep
            for sta in sta_lst:
                if foo(sta) >= c_minx and foo(sta) <= c_maxx:
                    cur_spl += 1
                elif foo(sta) > c_maxx:
                    break
            sta_per_cell.append(cur_spl)
            if cur_spl > max_sta_in_cell: max_sta_in_cell = cur_spl
            # print("\t[DEBUG PYSTRAIN] cell {:10.5f} to {:10.5f} stations: {:3d}".format(c_minx, c_maxx, cur_spl))
            curx += maxstep
        assert max_sta_in_cell > 0
        #print("[DEBUG PYSTRAIN] ticks per node:")
        #for n in sta_per_cell:
        #    print("\t[DEBUG PYSTRAIN] {:10.7f}*{:10.7f}/{:3d} = {:10.7f}".format(minstep,n,max_sta_in_cell,n*minstep/max_sta_in_cell))
        ##  Iterate through axis every with step = maxstep, from minx to maxx
        ##  For each cell, compute the annotation interval (annot_intrvl), as
        ##+ annot_intrvl(i) = sta_per_cell(i) * minstep / max_sta_in_cell
        ##+ so that the cell with the maximum number of stations has an annotation
        ##+ interval equal to minstep.
        ##  Now for each cell, we have a seperate annotation interval
        annot_intrvl = [ minstep+(x*minstep)/max_sta_in_cell if x>0 else maxstep for x in sta_per_cell ]
        ##  Iterate through axis every with step = maxstep, from minx to maxx
        ##  For each cell use the computed annotation interval to compute the
        ##+ cell annotation and store them in an array
        curx = minx
        ticks2return = []
        it = 0
        while curx < maxx:
            c_minx, c_maxx = curx, curx+maxstep
            an_int = annot_intrvl[it]
            print("\t[DEBUG PYSTRAIN] Node from {:10.7f} to {:10.7f} tick_every {:10.7f}".format(c_minx, c_maxx, an_int))
            assert an_int >= minstep
            annot = curx
            while annot < c_maxx:
                ticks2return.append(annot)
                annot += an_int
            curx += maxstep
            it += 1
        print("[DEBUG PYSTRAIN] returning from self.__make_ticks__ (IrregularGrid)")
        return ticks2return
    
    def __iter__(self):
        self.cxi = 0
        self.cyi = 0
        return self

    def xidx2xval(self, idx):
        """Index to value for x-axis.
         
            Given an index (on x-axis), return the value at the centre of this
            cell. The index represents the number of a cell (starting from
            zero).

            Args:
                idx (int): the index; should be in range (0, self.xpts]
        """
        assert idx >= 0 and idx < self.xpts
        #return self.x_min + self.x_step/2e0 + self.x_step*float(idx)
        return self.x_ticks[idx]
    
    def yidx2yval(self, idx):
        """Index to value for y-axis.
         
            Given an index (on y-axis), return the value at the centre of this
            cell. The index represents the number of a cell (starting from
            zero).

            Args:
                idx (int): the index; should be in range (0, self.ypts]
        """
        assert idx >= 0 and idx < self.ypts
        #return self.y_min + self.y_step/2e0 + self.y_step*float(idx)
        return self.y_ticks[idx]

    def next(self):
        """Return the centre of the next cell.

            Return the (centre of the) next cell (aka x,y coordinate pair). Next
            actually means the cell on the right (if there is one), or else the
            leftmost cell in the above row.

            Raises:
                StopIteration: if there are not more cell we can get to.
        """
        xi, yi = self.cxi, self.cyi
        if self.cxi >= self.xpts - 1:
            if self.cyi >= self.ypts - 1:
                # last element iin iteration!
                if self.cxi == self.xpts - 1 and self.cyi == self.ypts - 1:
                    self.cxi += 1
                    self.cyi += 1
                    return self.xidx2xval(xi), self.yidx2yval(yi)
                else:
                    raise StopIteration
            self.cxi  = 0
            self.cyi += 1
        else:
            xi, yi = self.cxi, self.cyi
            self.cxi += 1
        return self.xidx2xval(xi), self.yidx2yval(yi)

    # Python 3.X compatibility
    __next__ = next

def generate_irregular_grid(sta_lst, x_step, y_step, sta_lst_to_deg=False):
    grd = generate_grid(sta_lst, x_step, y_step, sta_lst_to_deg)
    return IrregularGrid(sta_lst, grd.x_min, grd.x_max, grd.x_step, grd.y_min, grd.y_max, grd.y_step)


if __name__ == "__main__":
    #grd = Grid(19.25e0, 30.75e0, 0.5e0, 34.25e0, 42.75e0, 0.5e0)
    grd = Grid(19.25e0, 20.75e0, 0.5e0, 34.25e0, 40.75e0, 0.5e0)
    print('Constructed grid with axis:')
    print('\tX: from {} to {} with step {}'.format(grd.x_min, grd.x_max, grd.x_step))
    print('\tY: from {} to {} with step {}'.format(grd.y_min, grd.y_max, grd.y_step))
    idx = 0
    for x, y in grd:
        idx += 1
        print('index {:3d}/{:4d}: Cell centre is at: {:}, {:}'.format(idx, grd.xpts*grd.ypts, x, y))
    dummy = np.arange(grd.x_min+grd.x_step/2e0, grd.x_max, grd.x_step)
    assert len(dummy) == grd.xpts
    dummy = np.arange(grd.y_min+grd.y_step/2e0, grd.y_max, grd.y_step)
    assert len(dummy) == grd.ypts
    assert grd.xpts*grd.ypts == idx


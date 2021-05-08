#! /usr/bin/python

import subprocess
import os
import datetime

script_path = os.path.dirname(os.path.abspath(__file__))
bin_path = os.path.join(script_path, '../bin')
data_path = os.path.join(script_path, '../data')
data_file = os.path.join(data_path, 'CNRS_midas.vel')
assert (os.path.isfile(os.path.join(bin_path, 'StrainTensor.py')))
assert (os.path.isfile(data_file))

##
lat_range = (0, 80, 10)
lon_range = (-80, 75, 10)
lat_width = 15e0
lon_width = 15e0
#lat_range = (73, 80, 8)
#lon_range = (70, 75, 8)

test_nr = 0
for lat_start in range(lat_range[0], lat_range[1], lat_range[2]):
    lat_from = float(lat_start)
    lat_to = lat_from + lat_width
    for lon_start in range(lon_range[0], lon_range[1], lon_range[2]):
        lon_from = float(lon_start)
        lon_to = lon_from + lon_width
        for step_sizes in [(0.4, 0.4), (0.7, 0.7),
                           (1e0, 1e0), (2e0, 2e0),
                           (1.5e0, 0.5e0),
                           (float(lon_range[2]), float(lat_range[2]))]:
            options = [
                '--input-file={:}'.format(data_file),
                '--x-grid-step={:}'.format(step_sizes[1]),
                '--y-grid-step={:}'.format(step_sizes[0]),
                '--region={:}/{:}/{:}/{:}'.format(lon_from, lon_to, lat_from,
                                                  lat_to), '--dmin=1',
                '--dmax=500', '--dstep=1', '--Wt=24', '-c', '-g'
            ]
            options = [os.path.join(bin_path, 'StrainTensor.py')] + options
            print('--> Performing test #{:}'.format(test_nr))
            subprocess.run(options, stdout=subprocess.DEVNULL)
            filename_ext = '{:}{:}{:}{:}.{:}'.format(
                step_sizes[1], step_sizes[0], lon_from, lat_from,
                datetime.datetime.now().strftime('%y%m%d%H%M%S'))
            for fl in ['strain_info.dat', 'strain_stats.dat']:
                src_fl = os.path.join(script_path, fl)
                if os.path.isfile(src_fl):
                    os.rename(src_fl,
                              os.path.join(script_path, fl + filename_ext))
            test_nr += 1

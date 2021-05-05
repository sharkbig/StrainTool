#! /usr/bin/python

import subprocess
import os
import datetime
import filecmp
import argparse
import sys
from random import randrange

#test_cases_dir = '/home/xanthos/Builds/StrainTool/test'
pwd = os.getcwd()

parser = argparse.ArgumentParser(description='Check StrainTool results based on already computed output files.')
parser.add_argument('-d', '--test-dir', default=pwd, metavar='TEST_DIR', dest='test_cases_dir', help='Directory where test output result files are located.')
parser.add_argument('-n', '--num-tests', default=None, metavar='NUM_OF_TESTS', dest='num_tests', type=int, help='Do not check against all result files found; insted perform this number of tests.')
parser.add_argument('-e', '--exit-at-error', dest='exit_at_error', action='store_true', help='Exit with error when the first test fails to pass.')
parser.add_argument('-m', '--multicore', dest='enable_multicore', action='store_true', help='Run tests in mutlicore mode.')

def print_error(strain_stats_ref, command, exit_status):
  print('ErrorInfo:: Command resolved using the strain_stats result file {:}'.format(strain_stats_ref))
  print('ErrorInfo:: Command used was: {:}'.format(command))
  sys.exit(exit_status)

def strain_info_is_empty(strain_info):
  if os.stat(strain_info).st_size == 0: return True
  with open(strain_info, 'r') as f:
    lines = f.readlines()
    if len(lines)>2: return False
    if lines[0].strip() == 'Latitude  Longtitude     vx+dvx          vy+dvy           w+dw          exx+dexx        exy+dexy        eyy+deyy       emax+demax      emin+demin       shr+dshr        azi+dazi      dilat+ddilat   sec. invariant+dsec inv.':
      if lines[1].strip() == 'deg       deg         mm/yr           mm/yr          deg/Myr       nstrain/yr      nstrain/yr      nstrain/yr      nstrain/yr      nstrain/yr      nstrain/yr         deg.         nstrain/yr      nstrain/yr':
        return True
    return False

##
## the contents of the two files must be equal AND in the same order
##
def compare_strain_stats(file1, file2):
    ## ignore first 5 lines:
    with open(file1, 'r') as fref:
        with open(file2, 'r') as fcmp:
            for i in range(5):
                line_cmp = fcmp.readline()
            for i in range(5):
                line_ref = fref.readline()
            line_nr = 5
            while line_ref:
                if line_ref != line_cmp and (line_ref.strip()!='multiproc_mode       -> True' and line_cmp.strip()!='multiproc_mode       -> True'):
                    return False
                line_cmp = fcmp.readline()
                line_ref = fref.readline()
                line_nr + 1
    return True

##
## Compare contents of two files, ignoring order in which they are written
## 
def compare_unordered_files(file1, file2, header_lines = 0):
    with open(file1, 'r') as f1:
      lines1 = f1.readlines()
    with open(file2, 'r') as f2:
      lines2 = f2.readlines()
    if len(lines1) != len(lines2):
      print('\tfiles {:} and {:} have unequal lengths!'.format(file1, file2))
      return False
    for line in lines1[header_lines:]:
      if line not in lines2[header_lines:] and not line.lstrip().startswith('multiproc_mode'):
        print('\tfailed to match line: \'{:}\''.format(line))
        return False
    return True


def resolve_cmd(strain_stats_file):
    with open(strain_stats_file, 'r') as fin:
        line = fin.readline()
        # StrainTensor.py Version: 1.0-r1
        assert (line.lstrip().startswith('StrainTensor.py Version:'))
        version = line.split(':')[1].strip()
        # Command used:
        line = fin.readline()
        assert (line.strip() == 'Command used:')
        command = fin.readline().strip()
        return version, command

args = parser.parse_args()

test_files = []
for fl in os.listdir(args.test_cases_dir):
    if os.path.basename(fl).startswith('strain_stats.dat'):
      test_files.append(fl)

if args.num_tests and args.num_tests < len(test_files):
  tmp = []
  while len(tmp) < args.num_tests:
    idx = randrange(len(test_files))
    tmp.append(test_files[idx]) if test_files[idx] not in tmp else None
  test_files = tmp

test_nr = 1
for fl in test_files:
    version, command = resolve_cmd(fl)
    if os.path.isfile('strain_info.dat'):
        os.remove('strain_info.dat')
    if os.path.isfile('strain_stats.dat'):
        os.remove('strain_stats.dat')
    print('Running test #{:}'.format(test_nr))
    if args.enable_multicore: command += ' --multicore'
    subprocess.run(command.split(), stdout=subprocess.DEVNULL)
    stats_ref = fl
    ## Compare strain_info.dat files (if any)
    info_ref = os.path.join(os.path.dirname(stats_ref), os.path.basename(stats_ref).replace('strain_stats', 'strain_info'))
    info_ref_exists = info_ref if os.path.isfile(info_ref) and not strain_info_is_empty(info_ref) else None
    info_test = os.path.join(pwd, 'strain_info.dat')
    info_test_exists = info_test if os.path.isfile(info_test) and not strain_info_is_empty(info_test) else None
    if info_ref_exists and not info_test_exists:
        print(
            '[ERROR] Strain Info reference file {:} exists but none created in test run!'
            .format(info_ref))
        print('        Aka, no file named {:} created in test run'.format(
            info_test))
        if args.exit_at_error: print_error(fl, command, 1)
    elif info_test_exists and not info_ref_exists:
        print(
            '[ERROR] No Strain Info reference file found, but test run produced one!'
        )
        print(
            '        Aka, file {:} created but not matched to any reference ({:})'
            .format(info_test, info_ref if info_ref_exists else None))
        if args.exit_at_error: print_error(fl, command, 1)
    elif info_test_exists and info_ref_exists:
        cmp_result = filecmp.cmp(info_ref, info_test, shallow=False) if not args.enable_multicore else compare_unordered_files(info_ref, info_test)
        if not cmp_result:
            print('[ERROR] Files {:} and {:} do not seem equal!'.format(
                info_ref, info_test))
            if args.exit_at_error: print_error(fl, command, 1)
    else:
        assert (not info_ref_exists and not info_test_exists)
    ## Compare strain_stats.dat files
    stats_test = os.path.join(pwd, 'strain_stats.dat')
    cmp_result = compare_strain_stats(stats_ref, stats_test) if not args.enable_multicore else compare_unordered_files(stats_ref, stats_test, 5)
    if not cmp_result:
        print('ERROR] Strain Stats file differ! {:} vs {:}'.format(
            stats_ref, stats_test))
        if args.exit_at_error: print_error(fl, command, 1)
    test_nr += 1

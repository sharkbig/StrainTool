#! /usr/bin/python

import os, sys

file1 = sys.argv[1]
file2 = sys.argv[2]

if not os .path.isfile(file1) or not os.path.isfile(file2):
    print('[ERROR] Errouous input files')
    sys.exit(1)

with open(file1, 'r') as f: lines1 = f.readlines()
with open(file2, 'r') as f: lines2 = f.readlines()

if len(lines1) > len(lines2):
  ref = lines1
  cmp = lines2
else:
  ref = lines2
  cmp = lines1

dif_lines = 0
line_nr = 1
for line in ref:
  if line not in cmp:
    print('Missing line: \'{:}\' line_nr {:}'.format(line, line_nr-2))
    dif_lines += 1
  line_nr += 1

print('Number of lines mmissing: {:}, number of different lines: {:}'.format(len(ref)-len(cmp), dif_lines))

#! /usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import print_function
try:
    import urllib.request
except:
    import urllib
import shutil
import sys
import re

analysis_centres = [ 'bfkh', 'ingv', 'uga', 'rob' ]
url_start = 'https://glass.epos.ubi.pt:8080/GlassFramework/webresources/products/velocities/file'

def epos_download(station, ac, form="pbo"):
    if form.lower() == "pbo":
        ext = "vel"
        url_stop = "xyz/pbo"
    elif form.lower() == "xml":
        ext = "xml"
        url_stop = "enu/xml"
    else:
        raise ValueError("[ERROR] Invalid file type to download")
    url = "/".join([url_start, station.upper(), ac.upper(), url_stop])
    localf = "{:}.{:}".format(station.upper(), ext)
    print('[DEBUG] Downloading file: {:} to {:}'.format(url, localf))
    if sys.version_info >= (3, 0):
        with urllib.request.urlopen(url) as response, open(localf, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    else:
        ufile = urllib.URLopener()
        ufile.retrieve(url, localf)
    return localf

def xml2dict(xmlin):
    xdict = { "n": None, "e": None, "u": None,
            "SNd": None, "SEd": None, "SUd": None }
    with open(xmlin, "r") as fin:
        xmlstr = fin.read()
    ## match any tag with flost attribute
    for key in xdict:
        try:
            regex = r"<{:}>[-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?</{:}>".format(key, key)
            match = re.search(regex, xmlstr).group(0)
            xdict[key] = float(re.sub(r"</?[a-zA-Z]+>", "", match))
        except:
            msg = "[ERROR] Failed to parse value for {:} in xml file {:}".format(key, xmlin)
            raise ValueError(msg)
    return xdict

def pbo2dict(pboin):
    xdict = { "n": None, "e": None, "u": None,
            "SNd": None, "SEd": None, "SUd": None }
    with open(pboin, "r") as fin: lines = fin.readlines()
    ## Make sure we have the right units
    for unit_line in [ r"^dN/dt North component of station velocity, meters/yr$",\
        r"^dE/dt East component of station velocity, meters/yr$", \
        r"^dU/dt Vertical component of station velocity, meters/yr$", \
        r"^SNd Standard deviation of North velocity, meters/yr$", \
        r"^SEd Standard deviation of East velocity, meters/yr$", \
        r"^SUd Standard deviation of vertical velocity, meters/yr$" ]:
        for line in lines:
            line_found = False
            if re.match(unit_line, line):
                line_found = True
                break
        if not line_found:
            print("[ERROR] Cannot find unit line \"{:}\"".format(unit_line))
            raise ValueError
    ## Identify the title line
    assert lines[-2].strip() == "Marker      Name          Ref_epoch    Ref_jday       Ref_X              Ref_Y            Ref_Z           Ref_Nlat       Ref_Elong        Ref_Up...    dX/dt      dY/dt    dZ/dt      SXd       SYd       SZd      Rxy     Rxz     Rzy     dN/dt     dE/dt     dU/dt      SNd       SEd       SUd      Rne     Rnu     Reu     first_epoch     last_epoch"
    ## Resolve fields from last line
    line = lines[-1]
    xdict["name"] = line[0:4]
    cols = line[20:].split()
    try:
        xdict["lat"] = float(cols[5])
        xdict["lon"] = float(cols[6])
        xdict["n"]   = float(cols[17])
        xdict["e"]   = float(cols[18])
        xdict["u"]   = float(cols[19])
        xdict["SNd"] = float(cols[20])
        xdict["SEd"] = float(cols[21])
        xdict["SUd"] = float(cols[22])
    except:
        raise ValueError("[ERROR] Failed to resolve station information from pbo file")
    for key in xdict: print("{:} -> {:}".format(key, xdict[key]))

def dict2gpsvel(dct, velf):
    if isinstance(dct, dict):
        dct = [dct]
    with open(velf, "w") as fout:
        for d in dct:
            print("{:} {:+10.5f} {:10.5f} {:+7.3f} {:+7.3f} {:7.3f} {:7.3f}".\
            format(d["name"], d["lon"], d["lat"], \
            d["e"]*1e3, d["n"]*1e3, d["SNd"]*1e3, d["SEd"]*1e3))
    return

if __name__ == "__main__":
    #fl  = xml_download("noa1", "bfkh")
    inf = xml2dict("NOA1.xml")
    print("-------------------------------------------------------------")
    print('{:}'.format(inf))
    fl = "RAMO.vel"
    pbo2dict(fl)

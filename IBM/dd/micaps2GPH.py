# coding: utf8

from __future__ import unicode_literals

import os
import numpy as np
import pandas as pd
from datetime import datetime

import pygrib
from ncepgrib2 import Grib2Decode, Grib2Encode

inputDir = "/home/enso/max_micaps/"

def read_micaps_iv(m4_fn):
    #从文件名中提取时间、预报时效信息
    fn = os.path.basename(m4_fn)
    year, month, day, hour, prep = fn[0:2], fn[2:4], fn[4:6], fn[6:8], fn[9:12]
    #从文件的头文件中提取经度、纬度、网格等信息
    with open(m4_fn, 'r') as info:
        fl = info.readlines()[2].split()
        xdelta, ydelta = float(fl[0]), float(fl[1])
        stlon, edlon = float(fl[2]), float(fl[3])
        stlat, edlat = float(fl[4]), float(fl[5])
        xnum, ynum = int(fl[6]), int(fl[7])        
    xx = np.linspace(stlon, edlon, xnum)
    yy = np.linspace(stlat, edlat, ynum)
    X, Y = np.meshgrid(xx, yy)
    #读取数据
    df = pd.read_table(m4_fn, skiprows=5, header=None, delim_whitespace=True, nrows=121)
    data = df.as_matrix(columns=None).ravel()
    data = [_ for _ in data if not np.isnan(_)]
    data = [_ if _ != 9999.00 else np.nan for _ in data]
    data = np.reshape(np.array(data), (ynum, xnum))
    return data, X, Y, year, month, day, hour, prep, xx, yy, stlon, edlon, stlat, edlat, xnum, ynum, xdelta, ydelta


# grbo = Grib2Encode(discipline_code, identification_section)
discipline_code = 0  # 0 for meteorlogical, 1 for hydrological, 2 for land surface, 3 for space, 10 for oceanographic products
identification_section = [
    7,           #@ 7 for NCEP, 38 for Beijing, 98 for ECMWF. http://www.nws.noaa.gov/tg/GRIB_C1.php
    0,           # Id of orginating sub-centre (local table)
    2,           # GRIB Master Tables Version Number
    1,           # http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table1-1.shtml
    1,           #@ 1 for Start of Forecast. 
    2011,        #@ year
    1,           #@ month
    10,          #@ day
    12,          #@ hour
    0,           # minute
    0,           # second
    0,           #@ 0 for Operational Products. http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table1-3.shtml
    1            #@ 1 for Forecast Products. http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table1-4.shtml
]

# grbo.addgrid(grid_definition_info, grid_definition_template)
grid_definition_info = [
    0,           #@ 0 for Latitude/Longitude. http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table3-1.shtml
    10512,       #@ Number of grid points in the defined grid
    0,           #@ 0 for regular grids. Number of octets needed for each additional grid points defn. Used to define number of points in each row for non-reg grids (=0 for regular grid).
    0,           # http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table3-11.shtml
    0            #@ 0 for Latitude/Longitude. http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table3-1.shtml
]
grid_definition_template = [
    6,           #@ 6 for Earth assumed spherical with radius = 6,371,229.0 m. Shape of the Earth (See Code Table 3.2)
    0,           # Scale Factor of radius of spherical Earth
    0,           # Scale value of radius of spherical Earth
    0,           # Scale factor of major axis of oblate spheroid Earth
    0,           # Scaled value of major axis of oblate spheroid Earth
    0,           # Scale factor of minor axis of oblate spheroid Earth
    0,           # Scaled value of minor axis of oblate spheroid Earth
    144,         #@ Ni—number of points along a parallel
    73,          #@ Nj—number of points along a meridian
    0,           # Basic angle of the initial production domain (see Note 1)
    0,           # Subdivisions of basic angle used to define extreme longitudes and latitudes, and direction increments (see Note 1)
    90000000,    #@ La1—latitude of first grid point (see Note 1)
    0,           #@ Lo1—longitude of first grid point (see Note 1)
    48,          # Resolution and component flags (see Flag Table 3.3)
    -90000000,   #@ La2—latitude of last grid point (see Note 1)
    357500000,   #@ Lo2—longitude of last grid point (see Note 1)
    2500000,     #@ Di—i direction increment (see Notes 1 and 5)
    2500000,     #@ Dj—j direction increment (see Note 1 and 5)
    0            # Scanning mode (flags — see Flag Table 3.4 and Note 6)
]

# grbo.addfield(product_definition_template_number, product_definition_template, data_representation_template_number, data_representation_template, data)
product_definition_template_number = 0  # http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table4-0.shtml
product_definition_template = [
    0,          #@ Parameter category (see Code table 4.1)
    0,          #@ Parameter number (see Code table 4.2)
    2,          #@ 2 for Forecast. Type of generating process (see Code table 4.3)
    0,          # Background generating process identifier (defined by originating centre)
    96,         # Analysis or forecast generating process identified (see Code ON388 Table A)
    0,          # Hours of observational data cutoff after reference time (see Note)
    0,          # Minutes of observational data cutoff after reference time (see Note)
    1,          #@ 1 for hour. Indicator of unit of time range (see Code table 4.4)
    120,        #@ fcst valid for 120 hours. Forecast time in units defined by octet 18
    100,        #@ 100 for isobar, 1 for Ground or water surface, 103 for height about ground. Type of first fixed surface (see Code table 4.5)
    0,          #@ Scale factor of first fixed surface
    1000,       #@ 1000 for 1000hPa. Scaled value of first fixed surface
    255,        # Type of second fixed surfaced (see Code table 4.5)
    0,          # Scale factor of second fixed surface
    0           # Scaled value of second fixed surfaces
]
data_representation_template_number = 3
data_representation_template = [1156603904, 0, 1, 8, 0, 1, 0, 0, 0, 696, 0, 3, 1, 1, 32, 5, 1, 1]


def test(
        discipline_code = discipline_code,
        identification_section = identification_section,
        grid_definition_info = grid_definition_info,
        grid_definition_template = grid_definition_template,
        product_definition_template_number = product_definition_template_number,
        product_definition_template = product_definition_template,
        data_representation_template_number = data_representation_template_number,
        data_representation_template = data_representation_template):


    files = os.listdir(os.path.join(inputDir, 'ecmwf_thin', 'dt', '1000', '4'))
    files = sorted(files, key=lambda i:-int(i.split('.')[1]))
    count = 0
    for ff in files:    
        m4_fn = os.path.join(inputDir, 'ecmwf_thin', 'dt', '1000', '4', ff)
        (
            data, X, Y, year, month, day, hour, prep, xx, yy, 
            stlon, edlon, stlat, edlat, xnum, ynum, xdelta, ydelta
        ) = read_micaps_iv(m4_fn)
        
        identification_section[0] = 98
        identification_section[5] = 2000 + int(year)
        identification_section[6] = month
        identification_section[7] = day
        identification_section[8] = hour

        grid_definition_info[1] = xnum * ynum

        grid_definition_template[7] = xnum
        grid_definition_template[8] = ynum
        grid_definition_template[11] = stlat * 1000000
        grid_definition_template[12] = (stlon+360) * 1000000
        grid_definition_template[14] = edlat * 1000000
        grid_definition_template[15] = (edlon+360) * 1000000
        grid_definition_template[16] = xdelta * 1000000
        grid_definition_template[17] = ydelta * 1000000

        product_definition_template[0] = 0
        product_definition_template[1] = 9
        product_definition_template[8] = int(prep)
        product_definition_template[9] = 100
        product_definition_template[10] = 0
        product_definition_template[11] = 1000*100

        (
            identification_section,
            grid_definition_info,
            grid_definition_template,
            product_definition_template,
            data_representation_template
        ) = [np.array(_, dtype=np.int32) for _ in [
            identification_section,
            grid_definition_info,
            grid_definition_template,
            product_definition_template,
            data_representation_template
        ]]
        if count < 10:
            tt = '0%s' %count
        else:
            tt =count
            
        if int(hour)-8 == 0:
            hh = '00'
        else:
            hh = int(hour) - 8
        fn = "20%s%s%s%s%s_EC-1000hpa24hTemperature_CHINA_27km" %(year, month, day, hh, tt)
        f=open(fn + '.grib2','wb')
        grbo = Grib2Encode(
            discipline_code,
            identification_section)
        grbo.addgrid(
            grid_definition_info,
            grid_definition_template)
        grbo.addfield(
            product_definition_template_number,
            product_definition_template,
            data_representation_template_number,
            data_representation_template,
            data)
        grbo.end()
        f.write(grbo.msg)
        f.close()
        count +=1


if __name__ == '__main__':
    test()

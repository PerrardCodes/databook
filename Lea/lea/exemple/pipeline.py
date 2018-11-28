# -*- coding: utf-8 -*-
import lea.data.Data as ldata
import lea.data.Param as lparam

import lea.mesure.Piv3D as lpiv3d
import lea.mesure.Mesure as lmesure
import lea.mesure.Volume_SP as lvolume

import lea.hdf5.routine as routine


import lea.hdf5.h5py_convert as lh5py

import stephane.analysis.cdata as cdata
import numpy as np

import os
import glob
import time

import sys

def ask(folder,ext='*.cine'):
    l=glob.glob(folder+ext)
    if len(l)>1:
        for i,name in enumerate(l):
            print(str(i)+' : '+os.path.basename(name))
    
        s = input()
        try:
            i = int(s)
        except:
            print("cannot be converted to an integer")
        return l[i]
    else:
        if len(l)==1:
            return l[0]
        else:
            print('no file found in '+folder)
            return None
            

base = '/Volumes/Diderot/DATA_Princeton_November2018/'
date = '20181127'
datafolder = base+date+'/'

savefolder = '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/'+date


#generate the data file associated to all cine in the datafolder
routine.convert_arbo(datafolder, savefolder)

#stophere
#get the cinefile to be processed 
cinefile = ask(datafolder)

# get the datafile associated to that cine. If the cine was not found, just look for it in the list
if cinefile is not None:
    datafile = ask(datafolder,ext='/20*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')
else:
    datafile = ask(datafolder,ext='20*'+'.hdf5')

# load the datafile
f = lh5py.ouverture_fichier(datafile)
d = lh5py.h5py_in_Data(f)
f.close()

#compute the volume on the first 200 frames
m = lmesure.Mesure(d)
v = lvolume.Volume(d)
v = v.volume()

Nt = len(v.m['tV'])

temp = {}
temp['instantV'] = []
temp['tV'] = []

for n in range(len(v.m['instantV'])) :
    temp['instantV'].append(v.m['instantV'][n])#.decode('UTF-8')
for n in range(len(v.m['tV'])) :
    temp['tV'].append(v.m['tV'][n])#.decode('UTF-8')

print(temp['tV'])

for i in range(Nt):
    print(temp['tV'])

    Vol,instant,t = v.get_volume(i)

    v0 = lvolume.Volume(d)
    v0.m['volume'] = Vol
    v0.m['instant'] = instant
    v0.m['t'] = t
    
    f = lh5py.file_name_in_dir(v0, savefolder + '/Volume'+ "/")
    lh5py.obj_in_h5py(v0, f)
    f.close()


m.add_measurement(v)
# save the measure of volume in a hdf5 file    
f = lh5py.file_name_in_dir(m, savefolder)
lh5py.obj_in_h5py(m, f)
f.close()

#stophere

stophere


###generate Piv3D object
piv3 = lpiv3d.Piv3D(d)
m.add_measurement(piv3)

# run the piv algorithm with multi processing
t1 = time.time()
overlap = 16
window_size = 32

cinefile_truncated = cinefile.rsplit(".",1)[0]
piv3 = piv3.analysis_multi_proc('', cinefile_truncated, cinefile_truncated, npy=None, fx='toto', dt_origin=None, frame_diff=None, crop_lims=None, maskers=None, window_size=window_size, overlap=overlap, search_area_size=window_size, save=False, s2n_thresh=1.2, bg_n_frames=None)
t2 = time.time()

#save the piv result in a hdf5 file
f = lh5py.file_name_in_dir(m, savefolder)
lh5py.obj_in_h5py(m, f)
f.close()

#go from 2d to 3d field, still some correction to make
piv3 = piv3.from2d_to3d()

#sauvegarde la mesure, après reconstitution des volumes
f = lh5py.file_name_in_dir(m, savefolder)
lh5py.obj_in_h5py(m,f)
f.close()

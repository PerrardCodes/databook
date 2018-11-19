# -*- coding: utf-8 -*-
import lea.data.Data as ldata
import lea.data.Param as lparam

import lea.mesure.Piv3D as lpiv3d
import lea.mesure.Mesure as lmesure
import lea.mesure.Volume as lvolume

import lea.hdf5.h5py_convert as h5pylea

import stephane.analysis.cdata as cdata

import os
import glob
import time

import numpy as np

import sys

def os_base():
    if sys.platform=='win32':
        base = 'F:'
    if sys.platform=='linux':    
        base = '/media/stephane/DATA'
    if sys.platform=='darwin':
        base = '/Volumes/Diderot/DATA_MSC_Jamin/'    
    return base

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
            
def get_param_right(s,unit):
    if len(unit)>0:
        s = s.rsplit(unit,1)[0]

    table = {'k':1000,'m':0.001,'c':0.01}    
    for key in table.keys():
        if key in s:
            return float(s.rsplit(key,1)[0])*table[key]
        else:
            return float(s)
            
def update_param(param):
    paramlist = {'fps':'','f':'Hz','fx':'','l_c':''}
    
    for key in paramlist.keys():
        s = getattr(param,key)
        val = get_param_right(s,unit=paramlist[key])
        setattr(param,key,val)
    return param


date = "20181106"
savefolder = '/Users/stephane/Documents/JRC_ENS/Data/Turbulence3d/'+date+'/'

base = os_base()
folder = base+'Turbulence3d/'+date+'/'
cinefile = ask(folder)
datafile = ask(folder,ext='/20*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')
paramfile = ask(folder,ext='*.txt')

print(datafile)
print(paramfile)

#cree un data à partir d'un fichier hdf5 existant
f = h5pylea.ouverture_fichier(datafile)
Data = h5pylea.h5py_in_Data(f)
f.close()

#recree un param à partir d'un fichier .txt (spécifié) et du nom du cinefile associé
param = lparam.Param(p=paramfile,spec=cinefile)
print(param.__dict__.keys())

param = update_param(param)

#update le fichier param du data
Data.param = param 

#update l'emplacement du cinefile
Data.fichier = cinefile


#sauvegarde le fichier Data
#f = h5pylea.file_name_in_dir(Data, savefolder)
#h5pylea.obj_in_h5py(Data,f)
#f.close()

# get the phase between images and volume scanning 
v = lvolume.Volume(Data)
v = v.volume(nb_im=100)

#print(v.m['instantV'][0])
#save the first volume position. Works for movies without time jump
setattr(Data.param,'startV',v.m['instantV'][0][0])
setattr(Data.param,'endV',v.m['instantV'][0][1])
setattr(Data.param,'tV',v.m['tV'][0])

#sauvegarde le fichier Data
f = h5pylea.file_name_in_dir(Data, savefolder)
h5pylea.obj_in_h5py(Data,f)
f.close()

print('Data object saved')

#cree un mesure à partir d'un fichier hdf5 existant
mesurefile = ask(folder,ext='/Mesure*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')

f = h5pylea.ouverture_fichier(mesurefile)
M = h5pylea.h5py_in_Mesure(f)
f.close()

print('Mesure object loaded')
if 'U' in M.PIV3D.m.keys():
    print('U format')

    print(M.PIV3D.m['U'].shape)
if 'np' in M.PIV3D.m.keys():
    print('np format')
    print(M.PIV3D.m['np'].shape)

#update le Data du Mesure
M.data = Data
M.PIV3D.data = Data
print(M.data.param.__dict__)

#update field name
if 'np' in M.PIV3D.m.keys():
    M.PIV3D.m['U'] = M.PIV3D.m['np']
    M.PIV3D.m.pop('np')

#sauvegarde le fichier Mesure
f = h5pylea.file_name_in_dir(M, savefolder,overwrite=True)
h5pylea.obj_in_h5py(M,f)
f.close()


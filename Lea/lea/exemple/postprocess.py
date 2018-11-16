# -*- coding: utf-8 -*-
import lea.data.Data as ldata
import lea.data.Param as lparam

import lea.mesure.Piv3D as lpiv3d
import lea.mesure.Mesure as lmesure
import lea.mesure.Volume as lvolume

import lea.hdf5.h5py_convert as h5pylea


import os
import glob
import time

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
### CHarge un fichier Data## .

date = "20181106"
savefolder = '/Users/stephane/Documents/JRC_ENS/Data/Turbulence3d/'+date+'/'

base = os_base()
folder = base+'Turbulence3d/'+date+'/'
cinefile = ask(folder)
datafile = ask(folder,ext='/20*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')
#paramfile = ask(folder,ext='*.txt')
mesurefile = ask(folder,ext='/Mesure*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')

print(datafile)
print(mesurefile)

#cree un data à partir d'un fichier hdf5 existant
f = h5pylea.ouverture_fichier(datafile)
Data = h5pylea.h5py_in_Data(f)
f.close()

#cree une mesure à partir d'un fichier hdf5 existant
f = h5pylea.ouverture_fichier(mesurefile)
M = h5pylea.h5py_in_Mesure(f)
f.close()#ouvrir un data à partir d'un hdf5 existant

#update le fichier data
M.data = Data

#sauvegarde la mesure
f = h5pylea.file_name_in_dir(M, savefolder)
h5pylea.obj_in_h5py(M,f)
f.close()

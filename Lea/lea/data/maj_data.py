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
#stophere
setattr(Data.param,'startV',v.m['instantV'][0][0])
setattr(Data.param,'endV',v.m['instantV'][0][1])
setattr(Data.param,'tV',v.m['tV'][0])

#sauvegarde le fichier Data
f = h5pylea.file_name_in_dir(Data, savefolder)
h5pylea.obj_in_h5py(Data,f)
f.close()
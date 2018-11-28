# -*- coding: utf-8 -*-
import lea.data.Data as data
import lea.mesure.Piv3D as piv
import lea.mesure.Mesure as m
import lea.hdf5.h5py_convert as h5py
import lea.hdf5.routine as routine

import os
import glob
import time

#basefolder = '/media/stephane/DATA/Experimental_data/Turbulence3d'
#adresse_s = basefolder
#routine.convert_arbo(basefolder, adresse_s)


###Création de la Data :###
##Depuis un fichier cine, jpg, dossier...
date = "20181126"
heure = "1000"

#base = "/media/stephane/"
#folder = 'DATA/Experimental_data/Turbulence3d/'+date+'/'

base = ""
folder = '/Volumes/Diderot/DATA_Princeton_November2018/20181126/'
adresse_s= '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/20181106/'


l =glob.glob(base+folder+'*.cine')
print("number of cinefiles : "+str(len(l)))

cinefile = l[0].rsplit(".",1)[0]

fichier = cinefile+'.cine'#"/media/stephane/OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_4pumpsOn.cine"
#cherche le fichier param associé
param =glob.glob(base+folder+'*.txt')[0] #si un seul fichier param présent
spec=fichier

d = data.Data(fichier, param, spec, date=date, heure=heure)
##Depuis un fichier hdf5
#data = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_frame.hdf5"))
###Création de Mesure et de ses sous-classes###
##Création de Mesure
mesure = m.Mesure(d)

##Création de Piv3D
piv3 = piv.Piv3D(d)
mesure.add_measurement(piv3)
t1 = time.time()
#print(d.param.fx)
#print(d.param.fps)
#print(d.param.f)
overlap = 16
window_size = 32

piv3 = piv3.analysis_multi_proc('', cinefile, cinefile, npy=None, fx='toto', dt_origin=None, frame_diff=None, crop_lims=None, maskers=None, window_size=window_size, overlap=overlap, search_area_size=window_size, save=False, s2n_thresh=1.2, bg_n_frames=None)
t2 = time.time()
###Mise des données dans un fichier HDF5###
##Si le fichier est déjà crée :
#f = ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/Mesure_0_20171109_1_frame.hdf5")
##Pour créer le fichier
f = h5py.file_name_in_dir(mesure, adresse_s)
h5py.obj_in_h5py(mesure, f)


print("temps : ")
print(t2-t1)

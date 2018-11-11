import lea.Data
import lea.Contour
import lea.Bulles
import lea.Piv3D
import lea.Mesure
import lea.h5py_convert
import lea.routine as routine

import os

basefolder = '/media/stephane/DATA/Experimental_data/Turbulence3d'
adresse_s = basefolder
routine.convert_arbo(basefolder, adresse_s)

stophere

###Création de la Data :###
##Depuis un fichier cine, jpg, dossier...
spec = []
date = "20181105"
heure = "1000"

base = "/media/stephane/"
folder = 'DATA/Experimental_data/Turbulence3d/'+date+'/'
l =glob.glob(base+folder+'*.cine')
print("number of cinefiles : "+str(len(l)))

cinefile = l[1].rsplit(".",1)[0]

fichier = cinefile+'.cine'#"/media/stephane/OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_4pumpsOn.cine"
#cherche le fichier param associé
param =glob.glob(base+folder+'*.txt')[0] #si un seul fichier param présent


data = Data(fichier, param, spec, date=date, heure=heure)
##Depuis un fichier hdf5
#data = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_frame.hdf5"))
###Création de Mesure et de ses sous-classes###
##Création de Mesure
mesure = Mesure(data)

##Création de Piv3D
piv = Piv3D(data)
mesure.add_measurement(piv)
piv = piv.analysis_multi_proc('', cinefile, cinefile, npy=None, fx=0.3457E-03, dt_origin=1./40000, frame_diff=40, crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32, save=False, s2n_thresh=1.2, bg_n_frames=None)
###Mise des données dans un fichier HDF5###
##Si le fichier est déjà crée :
#f = ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/Mesure_0_20171109_1_frame.hdf5")
##Pour créer le fichier
f = file_name_in_dir(mesure, os.path.dirname(cinefile))
obj_in_h5py(mesure, f)

import lea.data.Data as data
import lea.mesure.Contour as contour
import lea.mesure.Bulles as bulles
import lea.mesure.Piv3D as piv
import lea.mesure.Mesure as mesure
import lea.h5py.h5py_convert h5py

import os
import glob


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

#param = "/media/stephane/OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_param.txt"

#'/media/stephane/DATA/Experimental_data/Turbulence3d/20181010/test_flowfield.npy'
d = data.Data(fichier, param, spec, date=date, heure=heure)

##Depuis un fichier hdf5

#d = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_frame.hdf5"))

###Création de Mesure et de ses sous-classes###
##Création de Mesure
m = mesure.Mesure(d)

##Création de Contours
#c = contour.Contour(d)
#m.add_measurement(c)

##Création de Bulles
#b = Bulles(d)
#m.add_measurement(b)

##Création de Piv3D
p = piv.Piv3D(data)
m.add_measurement(p)


###Calcul des Mesures###
##Contour
##Mise des images dans la RAM avant de la calculer
#c = c.contour_RAM(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=40)
##Calcul des images une par une
#c = c.contour_instant(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=10)

#c = c.contour_multi_proc(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=10)
#mesurebase.add_measurem"/home/stephane/Documents/"ent(contour)

##Bulles
#f = h5py.file_name_in_dir(m, "/home/ldupuy/Documents/Stage_Python_(2018)/new")
#h5py.obj_in_h5py(m, f)
#b.bulle(f, adresse="/home/ldupuy/Documents/Stage_Python_(2018)/new", xmin=300, xmax=800, ymin=120, ymax=690, x0=460, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", p_im = 0, nb_im=10)

##Piv3D
#p = p.analysis("/media/stephane/", "OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_4pumpsOn", "DATA/Experimental_data/Turbulence3d/20181010/test", npy="", fx=0.3457E-03, dt_origin=1./40000, frame_diff=40, crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32, a_frames=np.arange(0,119960,1), save=True, s2n_thresh=1.2, bg_n_frames=None)


p = p.analysis_multi_proc('', cinefile, cinefile, npy=None, fx=0.3457E-03, dt_origin=1./40000, frame_diff=40, crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32, save=False, s2n_thresh=1.2, bg_n_frames=None)
###Mise des données dans un fichier HDF5###
##Si le fichier est déjà crée :
#f = ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/Mesure_0_20171109_1_frame.hdf5")
##Pour créer le fichier
f = h5py.file_name_in_dir(m, os.path.dirname(cinefile))
h5py.obj_in_h5py(m, f)

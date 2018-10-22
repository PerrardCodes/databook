from Data import *
from Contour import Contour
from Bulles import Bulles
from Piv3D import Piv3D
from Mesure import Mesure
from h5py_convert import *


###Création de la Data :###
##Depuis un fichier cine, jpg, dossier...
fichier = "/home/ldupuy/Documents/Stage_Python_(2018)/new/video_test/balloon_breakup_nopumps_fps10000_backlight_D800minch.cine"
param = "/home/ldupuy/Documents/Stage_Python_(2018)/new/video_test/Reference.txt"
spec = []
date = "20171109"
heure = "1808"

data = Data(fichier, param, spec, date=date, heure=heure)

##Depuis un fichier hdf5

data = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_frame.hdf5"))

###Création de Mesure et de ses sous-classes###
##Création de Mesure
mesure = Mesure(data)

##Création de Contours
contour = Contour(data)
mesure.add_measurement(contour)

##Création de Bulles
bulles = Bulles(data)
mesure.add_measurement(bulles)

##Création de Piv3D
piv = Piv3D(data)
mesure.add_measurement(piv)


###Calcul des Mesures###
##Contour
##Mise des images dans la RAM avant de la calculer
#contour = contour.contour_RAM(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=40)
##Calcul des images une par une
#contour = contour.contour_instant(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=10)

##Bulles
f = file_name_in_dir(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new")
obj_in_h5py(mesure, f)
bulles.bulle(f, adresse="/home/ldupuy/Documents/Stage_Python_(2018)/new", xmin=300, xmax=800, ymin=120, ymax=690, x0=460, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", p_im = 0, nb_im=10)

##Piv3D
#piv = piv.analysis("/media/stephane/", "OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_4pumpsOn", "DATA/Experimental_data/Turbulence3d/20181010/test", npy="", fx=0.3457E-03, dt_origin=1./40000, frame_diff=40, crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32, a_frames=np.arange(0,119960,1), save=True, s2n_thresh=1.2, bg_n_frames=None)


###Mise des données dans un fichier HDF5###
##Si le fichier est déjà crée :
#f = ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/Mesure_0_20171109_1_frame.hdf5")
##Pour créer le fichier
#f = file_name_in_dir(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new")
obj_in_h5py(mesure, f)

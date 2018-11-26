import lea.mesure.Mesure as mesure
import lea.mesure.Volume as volume
import lea.data.Data as data
import lea.hdf5.h5py_convert as lh5py

import glob
import time
import os

tab = {}
#20181106
#table to get the correspondance between fichier and parameter files

tab[0] = {"fichier":"/Volumes/Diderot/DATA_Princeton_November2018/20181126/PIV3d_scan_nikon105mm_fps20k_galvo1k_A800mV.cine", "param" : "/Volumes/Diderot/DATA_Princeton_November2018/20181126/PIV3d_scan_nikon105mm_param.txt"}
adresse_s= '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/20181106/Mesure/Volume/'

heure="0000"
for i in range(len(tab)):
    print(os.path.exists(tab[i]["fichier"]))
    print(os.path.exists(tab[i]["param"]))
    fichier = tab[i]["fichier"]
    param = tab[i]["param"]
    spec = fichier
    date = '20181126'#fichier.split("/")[6]
    print(os.path.dirname(fichier))
    d = data.Data(fichier, param, spec, date=date, heure=heure)
    m = mesure.Mesure(d)
    v = volume.Volume(d)
    v = v.volume(nb_im=200)
    m.add_measurement(v)
    
    f = lh5py.file_name_in_dir(m, adresse_s)
    lh5py.obj_in_h5py(m, f)
    f.close()
#    v.get_volume(os.path.dirname(fichier), os.path.dirname(fichier) + "/Mesure_Volume/Mesure_0_" + date + "_1_" + os.path.basename(fichier).rsplit(".", 1)[0] +".hdf5")

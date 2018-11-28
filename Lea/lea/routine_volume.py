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

tab[0] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3d_nikon50mm_64pumps_random16_fps40k_Pump30Hz_f1kHz_A1600mV_line5.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3dscan_nikon50mm_param.txt"}
tab[1] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3d_nikon50mm_64pumps_random16_fps40k_Pump30Hz_f1kHz_A1600mV_line5_z450mm.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3dscan_nikon50mm_param.txt"}
tab[2] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3d_nikon50mm_64pumps_random16_fps40k_Pump30Hz_f800Hz_A1600mV_line5_z400mm.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3dscan_nikon50mm_param.txt"}
tab[3] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3d_nikon50mm_64pumps_random16_fps40k_Pump30Hz_f800Hz_A1600mV_line5_z400mm_EXPT2.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/PIV3dscan_nikon50mm_param_EXPT2.txt"}
#20181112
tab[4] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181112/PIV2d_mikro50mm_fps1000_pump30Hz_jets16Random_line5.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181112/PIV3dscan_nikon50mm_param.txt"}
tab[5] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181112/PIV3dscan_mikro50mm_fps40000_pump30Hz_jets16Random_f1kHz_A1400mV_line5_flowfield.npy", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181112/PIV3dscan_nikon50mm_param.txt"}
#20181113
tab[6] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181113/PIV3dscan_mikro50mm_fps40000_pump30Hz_jets16Random_f1kHz_A1400mV_waittime100ms_duty3c_line5.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181113/PIV3dscan_nikon50mm_param.txt"}
#20181114
tab[7] = {"fichier":"/media/stephane/DATA/Experimental_data/Turbulence3d/20181114/PIV3dscan_mikro50mm_fps20000_pump30Hz_jets16Random_f500Hz_A3000mV.cine", "param" : "/media/stephane/DATA/Experimental_data/Turbulence3d/20181114/PIV3dscan_nikon50mm_param.txt"}

heure="0000"
for i in range(6, len(tab)) :
    print(os.path.exists(tab[i]["fichier"]))
    print(os.path.exists(tab[i]["param"]))
    fichier = tab[i]["fichier"]
    param = tab[i]["param"]
    spec = fichier
    date = fichier.split("/")[6]
    print(os.path.dirname(fichier))
    d = data.Data(fichier, param, spec, date=date, heure=heure)
    m = mesure.Mesure(d)
    v = volume.Volume(d)
    v = v.volume()
    m.add_measurement(v)
    f = lh5py.file_name_in_dir(m, os.path.dirname(fichier) + "/Mesure_Volume/")
    lh5py.obj_in_h5py(m, f)
    f.close()
    v.get_volume(os.path.dirname(fichier), os.path.dirname(fichier), os.path.dirname(fichier) + "/Mesure_Volume/Mesure_0_" + date + "_1_" + os.path.basename(fichier).rsplit(".", 1)[0] +".hdf5")

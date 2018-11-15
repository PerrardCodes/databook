import lea.mesure.Mesure as mesure
import lea.mesure.Volume as volume
import lea.data.Data as data
import lea.hdf5.h5py_convert as lh5py

import glob
import time
import os


spec = []
date = "20181106"
heure = "1000"

base = "/media/stephane/"
folder = 'DATA/Experimental_data/Turbulence3d/'+date+'/'
l =glob.glob(base+folder+'*.cine')
cinefile = l[0]
print(os.path.exists(cinefile))
param = glob.glob(base+folder+'*.txt')[0] #si un seul fichier param présent
spec = cinefile
#param = "/media/stephane/OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_param.txt"

#'/media/stephane/DATA/Experimental_data/Turbulence3d/20181010/test_flowfield.npy'
d = data.Data(cinefile, param, spec, date=date, heure=heure)

m = mesure.Mesure(d)
v = volume.Volume(d)
print(v.data.param.__dict__)
t1 = time.time()
#v = v.volume(nb_im=1000)
print(time.time()-t1)
#m.add_measurement(v)

#f = lh5py.file_name_in_dir(m, base + folder + "/Mesure_20181114/")
#lh5py.obj_in_h5py(m, f)
print(time.time()-t1)

v.get_volume(os.path.dirname(cinefile), '/media/stephane/DATA/Experimental_data/Turbulence3d/20181106/Mesure_20181114/Mesure_1_20181106_1_PIV3d_nikon50mm_64pumps_random16_fps40k_Pump30Hz_f1kHz_A1600mV_line5.hdf5')

import lea.mesure.Mesure as mesure
import lea.mesure.Volume as volume
import lea.data.Data as data
import lea.h5py.h5py_convert as h5py

import glob
import time
import os


spec = []
date = "20181106"
heure = "1000"

base = "/media/stephane/"
folder = 'DATA/Experimental_data/Turbulence3d/'+date+'/'
l =glob.glob(base+folder+'*.cine')
cinefile = l[3]
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
v = v.volume()
print(time.time()-t1)
m.add_measurement(v)

f = h5py.file_name_in_dir(m, folder)
h5py.obj_in_h5py(m, f)
print(time.time()-t1)

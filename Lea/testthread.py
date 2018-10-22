
import threading
import time
import psutil
from multiprocessing import Process, Pool
import os
import matplotlib.pyplot as plt
import numpy as np
from Data import *
from Contour import Contour
from Bulles import Bulles
from Piv3D import Piv3D
from Mesure import Mesure
from h5py_convert import *
from functools import partial


#data = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_frame.hdf5"))
data = h5py_in_Data(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/20171109_1_balloon_breakup_nopumps_fps10000_backlight_D800minch.hdf5"))

###Création de Mesure et de ses sous-classes###
##Création de Mesure
mesure = Mesure(data)

##Création de Contours
contour = Contour(data)
mesure.add_measurement(contour)

    ##Création de Contours
bulles = Bulles(data)
mesure.add_measurement(bulles)

###Calcul des Mesures###
##Contour
##Mise des images dans la RAM avant de la calculer
#contour = contour.contour_RAM(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", nb_im=40)
##Calcul des images une par une

def g(d, f):
    global contour
    print(d, f)
    contour.contour_instant(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", p_im=d, nb_im=f)
    #bulles.bulle(file, adresse="/home/ldupuy/Documents/Stage_Python_(2018)/new", xmin=300, xmax=800, ymin=120, ymax=690, x0=460, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", p_im=d,nb_im=f)
    print(contour.__dict__)

n = np.array([0,0,0,0], dtype=np.float64)
for i in range (1, os.cpu_count()+1):
    with Pool(processes=i) as pool:
        time1 = time.time()
        #func = partial(g, mesure, contour)
        ite = [(0,10), (11, 20)]
        print(contour)
        pool.starmap(g, ite)
        #print(c)
        #c = c[0].m.update(c[1].m)
        #contour.m = c
        print(contour.__dict__)
        stophere
        #pool.map(f, range(0, 1000000))
        f = file_name_in_dir(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new")
        obj_in_h5py(mesure, f)
        time2 = time.time()
        n[i-1] = time2 - time1
print(n)
plt.plot(n)
plt.show()
#p=Process(target=f)
#p.start()
#for i in range(0, 1000000) :
#    print(psutil.cpu_times_percent())
#    print("Time  = " + str(time.time()))
#time2 = time.time() - time1

#time1 = time.time()

#m = MonThread(1000, "A")
#m.start()

#m2 = MonThread(1000, "B")  # crée un second thread
#m2.start()                 # démarre le thread,

#for i in range(0, 90):
#    print("programme ", i)
#    time.sleep(0.1)

print("first : " + str(time2) + " second : " + str(time.time()-time1))


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
    print(d, f)
    global contour
    contour.contour_instant(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", im_save=200 ,p_im=d, nb_im=f)
    #bulles.bulle(file, adresse="/home/ldupuy/Documents/Stage_Python_(2018)/new", xmin=300, xmax=800, ymin=120, ymax=690, x0=460, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/Test", p_im=d,nb_im=f)
    print(contour.__dict__)
    return contour


test = 10
n = np.array([0,0,0,0], dtype=np.float64)
for i in range (4, os.cpu_count()+1):
    with Pool(processes=i) as pool:
        time1 = time.time()
        #func = partial(g, contour)
        #ite = [(0,50), (51, 100)]
        nb_im = 99
        nb = os.cpu_count()
        temp = nb_im/nb
        ite = []
        for j in range(0, nb):
            ite.append((int(temp*j), int(temp*(j+1))))
        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
        c = pool.starmap(g, ite)
        print(len(c[0].m['xf']))
        print(len(c[1].m['xf']))
        print(type(c[1].m['xf']))
        c = c[0].merge_all(c)
        print(len(c.m['xf']))
        print(c)
        mesure.add_measurement(c)
        #pool.map(f, range(0, 1000000))
        f = file_name_in_dir(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new")
        obj_in_h5py(mesure, f)
        time2 = time.time()
        n[i-1] = time2 - time1
print(test)
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



i = [916.97238469, 489.77731895,372.70821023, 281.52963066, 212.87292886, 197.02372265, 167.14954686, 158.26504779, 147.80870128, 116.03863764, 110.9878161, 108.33978558, 102.50973392,  89.39405251,  87.96847534,86.13772511, 85.49219942,  85.76712847,  85.4440124, 76.2437017, 68.6539669, 70.53214645, 70.90979028, 71.34067369, 70.23077369, 68.35903835, 70.37099814, 72.68370056, 69.88470888, 71.62808204, 70.74638915, 70.76199389, 71.19000721, 71.2631526, 71.63601542, 71.80244613, 70.47100425, 69.15406966, 69.32042265, 58.49300361]
plt.plot(i)
plt.show()

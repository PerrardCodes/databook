from Data import Data
from Traitement import *
from pre_traitement import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.interpolate as interp
import numpy as np
import os
import time
from PIL import Image
import PIL.ImageOps 
import cv2
import display.graphes as graphes

    

class Mesure:
    def __init__(self, data, m={}, historique={}):
        self.m=m
        self.data=data
        self.historique=historique

    def get_name(self):
    	return "Mesure"

#data = h5py_in_Data("/home/ldupuy/Documents/Stage_Python_(2018)/new/4_20171109_1808.hdf5")
#data = h5py_in_Data("/home/ldupuy/Documents/Stage_Python_(2018)/new/2_20171109_1437.hdf5")
#data = h5py_in_Data("/home/ldupuy/Documents/Stage_Python_(2018)/new/1_20180926_1217.hdf5")
#mesure = Mesure(data, m={})

#traitement_parameters(mesure)

#traitement_parameters(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new/balloon_breakup_nopumps_fps10000_backlight_D800minch.cine", xmin=200, xmax=950, ymin=120, ymax=690, x0=460, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/graph_balloon_2")

#traitement_parameters(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new/video_frame/balloon_breakup_nopumps_fps10000_backlight_D400minch.cine", xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/graph_balloon_171109")

#traitement_parameters(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new/balloon_breakup_nopumps_fps10000_backlight_D800minch.cine", xmin=200, xmax=950, ymin=120, ymax=690, x0=460, y0=305, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/graph_balloon", B=5)

#m = traitement_parameters(mesure, "/home/ldupuy/Documents/Stage_Python_(2018)/new/video_frame/frame", xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=295, adresse_s="/home/ldupuy/Documents/Stage_Python_(2018)/new/graph_balloon_171109", rmax=30, B=5)
#print(m.__dict__)

#load("/home/ldupuy/Documents/Stage_Python_(2018)/new/balloon_breakup_nopumps_fps10000_backlight_D800minch.cine")

#fig = plt.figure()
#ax = fig.add_subplot(111)
#D = param(load("/home/ldupuy/Documents/Stage_Python_(2018)/new/test3.png"), "")
#x = D['x']
#y = D['y']
#Z = D['im']
#c=plt.pcolormesh(x,y,Z)
#plt.draw()
#plt.savefig("test5.png")


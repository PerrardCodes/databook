# -*- coding: utf-8 -*-
import lea.data.Data
import lea.mesure.pre_traitement as preT
import lea.display.graphes as graphes

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.interpolate as interp
import numpy as np
import os
import time
from PIL import Image
import PIL.ImageOps
import cv2
#from pre_traitement import *



class Mesure:
	def __init__(self, data="", historique={}):
		self.data=data
		self.historique=historique

	def get_name(self):
		return "Mesure"

	#Ajoute un paramètre à Mesure, si c'est un objet il
	#ajoute l'attribut avec pour nom le nom de la classe
	#sinon il l'ajoute avec le name donné en paramètre
	def add_measurement(self, obj, name=None):
		try:
			name = obj.get_name()
		except NameError:
			pass
		setattr(self, name, obj)


	def get_im(self, object, i):
		if(object.data.extension in ['tif', 'png', 'jpg']):
			im = preT.get_im_files(object.data.fichier, i, self.data.extension)
		elif(object.data.extension in ['cine', 'avi']):
			im = preT.get_im_video(object.data.fichier, i)
		return im

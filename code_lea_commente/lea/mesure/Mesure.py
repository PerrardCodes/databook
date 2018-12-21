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
	"""
	:param data: Objet contenant les paramètres
	:type data: Data Object
	"""
	def __init__(self, data="", historique={}):
		self.data=data
		self.historique=historique

	def get_name(self):
		"""
        :return: Le nom de l'objet, ici "Mesure"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
		return "Mesure"

	#Ajoute un paramètre à Mesure, si c'est un objet il
	#ajoute l'attribut avec pour nom le nom de la classe
	#sinon il l'ajoute avec le name donné en paramètre
	def add_measurement(self, obj, name=None):
		"""
		Ajoute un paramètre à Mesure, si c'est un objet il ajoute l'attribut avec pour nom le nom de la classe qu'on a récupéré grâce à la méthode :func:`get_name()` sinon il l'ajoute avec le nom donné en paramètre
		"""
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

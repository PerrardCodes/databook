import os
import h5py
import numpy as np
import datetime
import time
import calendar
import lea.Param as p
import lea.Id as id
from PIL import Image
import PIL.ImageOps
import cv2
from os import listdir
import glob

class Data:
	def __init__(self, fichier, param, spec, **kwargs):
		#Fichier pointe vers le fichier type (video, ...)
		#Param pointe vers un fichier txt dans lequel
		#sont rentrés tous les paramètres
		if type(fichier)==dict :
			#Si fichier n'est pas un fichier alors c'est que c'est une liste
			#On utilise ce cas là lors de la création d'un objet Data
			#depuis un .hdf5
			for attr, value in fichier.items():
				setattr(self,attr,value)
		#Si fichier est un fichier, alors on crée tous les attributs qui ne
		# dépendent pas de l'extension du fichier
		elif(os.path.isfile(fichier)):
			self.fichier=fichier
			self.extension = get_extension(fichier)
			self.size = os.path.getsize(fichier)
			#Si le fichier est une video on utilise opencv2 pour récupérer
			#l'image de référence ainsi que la taille
			if(self.extension in ["cine", "avi"]):
				video = fichier
				vidcap = cv2.VideoCapture(video)
				success, image = vidcap.read()
				length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
				self.nb_im=length
				self.im_ref=np.asarray(image[...,0])
			#Si le fichier est une image alors on utilise le module PIL pour
			#récupérer l'image
			elif(self.extension in ["tif", "png", "jpeg"]):
				im = Image.open(fichier)
				self.im_ref = np.asarray(im)
				self.im_ref = np.asarray(self.im_ref[...,0])
				self.nb_im = 1
			else :
				print("extension : " + self.extension)
		elif(os.path.isdir(fichier)) :
			#Si le fichier est un dossier alors on utilise le module glob
			#pour récupérer les informations nécessaire
			self.fichier = fichier
			if len(glob.glob(fichier + "/*.png"))>0:
				self.extension = "png"
			elif len(glob.glob(fichier + "/*.tif"))>0:
				self.extension = "tif"
			elif len(glob.glob(fichier + "/*.jpeg"))>0:
				self.extension = "jpeg"
			if hasattr(self, "extension") :
				temp = glob.glob(fichier + "/*." + self.extension)
				self.im_ref = np.asarray(Image.open(temp[0]))
				self.shape = self.im_ref.shape
				self.im_ref = np.asarray(self.im_ref[...,0])
				self.nb_im = len(temp)



		#On crée ensuite les objets Param et Id
		self.param = p.Param(param, spec)
		self.id = id.Id(**kwargs)



	def redefinir(self, attr, value):
		if(hasattr(self, attr)):
			setattr(self, attr, value)
		elif hasattr(self.param, attr) :
			setattr(self.param, attr, value)
		elif hasattr(self.id, attr):
			setattr(self.id, attr, value)
		else :
			print("L'attribut n'existe pas dans Data, dans Param ou dans Id")

	def get_name(self):
		return "Data"

	def get_im_ref(self):#Renvoie une image PIL
		#Pour l'afficher : im.show()
		#Pour la sauvegarder : im.save(nom_image)
		im = Image.fromarray(self.im_ref)
		return im


def get_extension(fichier):
	if("." in fichier):
		temp = fichier.rsplit(".", 1)
		return temp[1]
	else :
		return ""

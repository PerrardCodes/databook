
from Mesure import Mesure
import pre_traitement as pre
import fluids2d.backlight as bl
import display.graphes as graphes

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import h5py
import psutil
import time

class Bulles(Mesure):
	def __init__(self, data, m={}):
		Mesure.__init__(self, data)
		self.m=m

	def get_name(self):
		return "Bulles"


#bulle sert à calculer les bulles (code présent dans fluids2d.backlight)
#puis il ajoute dynamiquement dans un fichier hdf5 qui est passé en paramètre
	def bulle(self, filename, adresse="", fx=0., fps=1., D=0, xmin=0, xmax=-1, ymin=0, ymax=-1, \
			x0=0, y0=0, im_save=50, adresse_s="", p_im=0,nb_im=0):
		mesure = self
		Dic = {}
		f = filename

		#Si le nombre d'image n'est pas défini il est automatiquement mis au
		#nombre d'image dans Data
		if(nb_im==0):
			nb_im=self.data.nb_im

		Dic.update(pre.get_data_param(Dic, mesure, fx, fps, D))

		Dic.update(pre.get_H_and_L(Dic, mesure))

		Dic.update(pre.set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax))

		self.m.update(Dic)

		im = super().get_im(self, p_im)
		im, D = pre.load_im(im, Dic)
		Dic.update(D)

		f = f['Mesure/Bulles']
		##Pour le premier cas, il est nécessaire de le faire à part pour
		## la création de la Dataset

		filled = bl.get_filled(im,125,filter_size=2)
		df = bl.filled2regionpropsdf(filled,frame=p_im)
		dset = []
		print(df)
		for i in range (0, len(df.columns)):
			#Convertion de toutes les données en float
			df[df.columns] = df[df.columns].astype(np.float64)
			#Insertion dans un tableau de Dataset
			#A chaque tour de boucle crée une nouvelle dataset avec comme paramètre
			#le nom de la colonne, la taille, le type, et si on peut modifier la taille
			if p_im==0:
				d = f.create_dataset(df.columns[i], (1, df.shape[0]), dtype=np.float64, chunks=True, maxshape=(df.shape[1],None))
			else :
				d = f[df.columns[i]]
				old_shape = d.shape[1]
				d.resize(old_shape + df[df.columns[i]].shape[0], axis=1)
			dset.insert(i, d)#f.create_dataset(df.columns[i], (1, df.shape[0]), dtype=np.float64, chunks=True, maxshape=(None, df.shape[1])))
			#Ajout des valeurs dans la dataset
			dset[i][:,p_im:] = df[df.columns[i]]

		#Remplissage de la dataset
		for i in range(p_im+1, nb_im):
			t1 = time.time()
			#update de l'image
			im = super().get_im(self, i)
			im, D = pre.load_im(im, Dic)
			Dic.update(D)

			#Calcul
			filled = bl.get_filled(im,125,filter_size=2)
			d = bl.filled2regionpropsdf(filled,frame=i)

			#Ajout dans le tableau de dataset en changeant la taille de la
			#dataset à chaque tour de boucle
			for i in range (0, len(d.columns)):
				old_shape = dset[i].shape[1]
				dset[i].resize(old_shape + d[d.columns[i]].shape[0], axis=1)
				d[d.columns] = d[d.columns].astype(np.float64)
				dset[i][:,old_shape:] = d[d.columns[i]]
			t2 = time.time()
			print(t2-t1)
			print(psutil.virtual_memory().used)

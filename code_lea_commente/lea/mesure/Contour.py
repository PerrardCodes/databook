##Code déjà existant##
import lea.display.graphes as graphes
import lea.mesure.Mesure as m
import lea.mesure.pre_traitement as preT
##Librairie

import numpy as np
import scipy.interpolate as interp
import pandas as pd
import math
import matplotlib.pyplot as plt
import h5py
from multiprocessing import Process, Pool
import os
import time
from functools import partial


class Contour(m.Mesure) :
	"""
	:param m: Contient toutes les informations obtenues lorsqu'on a lancé le traitement.
	:type m: dict

	Contient le même data que celui de sa classe mère Mesure, il est nécessaire d'avoir les informations en double notamment si on change des paramètres.

	"""
	def __init__(self, data, m={}):
		print(Mesure(data))
		Mesure.__init__(self, data)
		self.m=m

	def add_measurement(self, obj, name):
		"""
		Ajoute un paramètre à Contour, si c'est un objet il ajoute l'attribut avec pour nom le nom de la classe qu'on a récupéré grâce à la méthode :func:`get_name()` sinon il l'ajoute avec le nom donné en paramètre
		"""
		setattr(self, obj, name)

	def merge_all(self, tab):
		for i in range(1, len(tab)):
			self = self.merge(tab[i])
		return self

	def merge(self, obj):
		self.data = obj.data
		for n in self.m :
			if isinstance(self.m[n], np.ndarray) and (not(n=="x") or not(n=="y")):
				self.m[n] = np.concatenate((self.m[n], obj.m[n]))
		return self


#fx = spacial scale

#ft = (1/fps)*1000

#Diametre initial

#xmin, xmax contiennent les valeurs mins et max de l'axe x pour la ROI
#(Region Of Interest)
#ymin, ymax sont pareils que xmin,xmax mais pour l'axe  y

#x0, y0 sont les coordonnées du centre (par rapport à l'image de base)

#im_save est le numéro de la combientième image à sauvegarder
#aucune autre ne sera sauvegardé

#adresse_s est l'adresse ou doit être sauvegarder l'image

#N est le nombre de droite
#nr est le nombre de point par droite
#rmin et rmax : distance entre lesquels ont doit mettre les points
#les 4 sont fixés à l'aide du suivant :
#rmax-rmin est le nombre de pixel à considéré sur les droites
#nr = rmax-rmin *B
#On veut en effet qu'il y ait plus de points c'est B
#De même pour N
#N = pi * (rmin-rmax) *B

#nb_im est le nombre d'image qu'on veut traiter

	def contour_RAM(self, fx=0., fps=1., D=0, xmin=0, xmax=-1, ymin=0, ymax=-1, \
					x0=0, y0=0, im_save=50, adresse_s="", rmin=10, rmax=30, B=5, \
					thetamin=0.7, thetamax=0.15, nb_im=0):
		"""
		Cette fonction récupère les contours d'un ballon et grâce à la fonction :func: `contour`. Lors de son utilisation avec un film celui-ci est stocké entièrement dans la RAM (c'est à dire qu'il charge en premier toutes les images ou tout le film puis le traite en suite), il faut préférer utiliser :func:`contour_instant` ou :func:`contour_multi_proc` pour l'utilisation du multiprocessing python

		:param fx: spacial scale
		:type fx: float
		:param fps: Utilisé pour calculer le ft
		:type fps: float
		:param D: Diametre initial
		:type D: float
		:param xmin: Pour crop l'image, de base à 0
		:type xmin: int
		:param xmax: Pour crop l'image, de base à -1 et si non définit il prend le maximum de l'axe x
		:type xmax: int
		:param ymin: Pour crop l'image, de base à 0
		:type ymin: int
		:param ymax: Pour crop l'image, de base à -1 et si non définit il prend le maximum de l'axe y
		:type ymax: int
		:param x0: Le centre en x, il faut indiquer le centre avant que l'image ne soit crop.
		:type x0: int
		:param y0: Le centre en y, il faut indiquer le centre avant que l'image ne soit crop.
		:type y0: int
		:param im_save: Image à sauvegarder
		:type im_save: int
		:param adresse_s: Où sauvegarder l'image
		:type adresse_s: adresse du fichier
		:param rmin: rmin et rmax servent à savoir à quelle distance on doit mettre les points
		:type rmin: int
		:param rmax: rmin et rmax servent à savoir à quelle distance on doit mettre les points
		:type rmax: int
		:param N: N est le nombre de droite (N = pi* (rmin-rmax) *B)
		:type N: int
		:param nr: nr est le nombre de point par droite (nr = (rmax-rmin)*B)
		:type nr: int
		:param nb_im: Dernière image à traiter, si égale à 0 elle est mise au nombre maximum d'image
		:type nb_im: int
		:return: Objet Contour

		"""

		mesure = self

		if(nb_im==0):
			nb_im=self.data.nb_im

		#Dictionnaire qui stocke toutes les données nécessaire
		Dic = {}

		Dic.update(preT.get_data_param(Dic, mesure, fx, fps, D))

		Dic.update(preT.get_H_and_L(Dic, mesure))

		Dic.update(preT.set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax))

		#Chargement des fichiers
		if(self.data.extension in ['tif', 'png', 'jpg']):
			Na, D = preT.charge_image_ram(self.data.fichier, Dic, self.data.extension, nb_im=nb_im)
		elif(self.data.extension in ['cine', 'avi']):
			Na, D = preT.charge_video_ram(self.data.fichier, Dic, nb_im=nb_im)
		Dic.update(D)

			##Différents paramètres
		Dic.update(preT.in_dict(Dic, thetamin, thetamax, rmax, rmin, B))

		#yxf est actualisé à chaque tour de boucle avec la nouvelle valeur du centre
		#xcf ne bouge pas car on considère que le centre ne peut que bouger sur
		#l'axe des y
		Dic['ycf'] = 0
		Dic['xcf'] = 0

		#on prépare le tableau de données pour la fonction contour
		indices = range(0, Na.shape[0])


		for i,indice in enumerate(indices):
			display = (i==im_save)
			adresse = adresse_s + "/graph%d.png" %indice
			DF = contour(Na[indice], Dic, display=display, save=adresse)
			print("image = " + str(indice))
			for index, column in DF.iteritems():
				if not index in self.m.keys():
					#creation du tableau de donnée de sortie, pour tous les itérés contenu dans indices
					self.m[index] = np.zeros((len(indices),Dic['N']))
				self.m[index][i,:] = np.asarray(DF[index].values)
			Dic.update(preT.redefine_rmax(Dic, DF))
			Dic.update(preT.redefine_center(Dic, DF))

		##Mise des données dans mesure##
		self.m.update(Dic)

		return self

	def contour_instant(self, fx=0., fps=1., D=0, xmin=0, xmax=-1, ymin=0, ymax=-1, \
					x0=0, y0=0, im_save=50, adresse_s="", rmin=10, rmax=30, B=5, \
					thetamin=0.7, thetamax=0.15, p_im=0, nb_im=0):
		"""
		Cette fonction récupère les contours d'un ballon et grâce à la fonction :func: `contour`. Le film n'est pas stocké dans la RAM, c'est à dire qu'il récupère une image, la traite, puis passe à la suivante, pour plus d'efficacité utiliser la fonction :func:`contour_multi_proc` pour l'utilisation du multiprocessing python

		:param fx: spacial scale
		:type fx: float
		:param fps: Utilisé pour calculer le ft
		:type fps: float
		:param D: Diametre initial
		:type D: float
		:param xmin: Pour crop l'image, de base à 0
		:type xmin: int
		:param xmax: Pour crop l'image, de base à -1 et si non définit il prend le maximum de l'axe x
		:type xmax: int
		:param ymin: Pour crop l'image, de base à 0
		:type ymin: int
		:param ymax: Pour crop l'image, de base à -1 et si non définit il prend le maximum de l'axe y
		:type ymax: int
		:param x0: Le centre en x, il faut indiquer le centre avant que l'image ne soit crop.
		:type x0: int
		:param y0: Le centre en y, il faut indiquer le centre avant que l'image ne soit crop.
		:type y0: int
		:param im_save: Image à sauvegarder
		:type im_save: int
		:param adresse_s: Où sauvegarder l'image
		:type adresse_s: adresse du fichier
		:param rmin: rmin et rmax servent à savoir à quelle distance on doit mettre les points
		:type rmin: int
		:param rmax: rmin et rmax servent à savoir à quelle distance on doit mettre les points
		:type rmax: int
		:param N: N est le nombre de droite (N = pi* (rmin-rmax) *B)
		:type N: int
		:param nr: nr est le nombre de point par droite (nr = (rmax-rmin)*B)
		:type nr: int
		:param p_im: Première image à traiter, de base mise à 0
		:type nb_im: int
		:param nb_im: Dernière image à traiter, si égale à 0 elle est mise au nombre maximum d'image
		:type nb_im: int
		:return: Objet Contour
		"""

		mesure = self
		if(nb_im==0):
			nb_im=self.data.nb_im

		#Dic stocke toutes les données nécessaires à Contour

		Dic = {}

		Dic.update(preT.get_data_param(Dic, mesure, fx, fps, D))

		Dic.update(preT.get_H_and_L(Dic, mesure))

		Dic.update(preT.set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax))

		Dic.update(preT.in_dict(Dic, thetamin, thetamax, rmax, rmin, B))


		#yxf est actualisé à chaque tour de boucle avec la nouvelle valeur du centre
		#xcf ne bouge pas car on considère que le centre ne peut que bouger sur
		#l'axe des y
		Dic['ycf'] = 0
		Dic['xcf'] = 0

		Dic['p_im'] = p_im
		for i in range(p_im, nb_im):
			im = self.get_im(i)
			im, D = load_im(im, Dic)
			Dic.update(D)
			display = (i==i)#m_save)
			adresse = adresse_s + "/graph%d.png" %i
			#Calcul des points, mis dans un Dataframe DF
			DF = contour(im, Dic, display=display, save=adresse)
			print("i = " + str(i))
			#Mise des données dans l'objet Contour
			for index, column in DF.iteritems():
				#Création de l'index dans m s'il n'est pas créé
				if not index in mesure.m.keys():
					self.m[index] = np.zeros((nb_im-p_im, Dic['N']))
				if p_im!=0 :
				#	self.m[index] = np.resize(self.m[index],(nb_im,self.m[index].shape[1]))
					self.m[index][i-p_im,:] = np.asarray(DF[index].values)
				else :
					self.m[index][i,:] = np.asarray(DF[index].values)
				print("index = " + str(index))
			Dic.update(preT.redefine_rmax(Dic, DF))
			Dic.update(preT.redefine_center(Dic, DF))

		self.m.update(Dic)
		return self

	def get_im(self,i):
		return super().get_im(self,i)

	def get_name(self):
		"""
        :return: Le nom de l'objet, ici "Contour"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
		return "Contour"


	def contour_multi_proc(self, nb_im=0, fx=0., fps=1., D=0, xmin=0, xmax=-1, ymin=0, ymax=-1, \
					x0=0, y0=0, im_save=50, adresse_s="", rmin=10, rmax=30, B=5, \
					thetamin=0.7, thetamax=0.15):

		"""
		Utilise la fonction :func:`contour_instant` et l'optimise avec du multiprocessing
		"""
		if(nb_im==0):
			nb_im=self.data.nb_im
		with Pool(processes=os.cpu_count()) as pool:
			nb = os.cpu_count()
			temp = nb_im/nb
			ite = []
			for j in range(0, nb):
				ite.append((int(temp*j), int(temp*(j+1))))
	        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
			func = partial(self.contour_instant, fx, fps, D, xmin, xmax, ymin, ymax, x0, y0, im_save, adresse_s, rmin, rmax, B, thetamin, thetamax)
			c = pool.starmap(func, ite)
			self = c[0].merge_all(c)
		return self

	#Fonction de mesure

def contour(im, Dic, display=True, save="test.png"):
	"""
	Fonction de mesure
	"""
	x = Dic['x']
	y = Dic['y']
	xc = Dic['xcf']
	yc = Dic['ycf']
	nr = Dic['nr']
	N = Dic['N']
	rmin = Dic['rmin']
	rmax = Dic['rmax']
	X,Y = np.meshgrid(x,y)

	thetamin = Dic['thetamin']
	thetamax = Dic['thetamax']
	theta = np.concatenate((np.linspace(-thetamin,np.pi/2-thetamax, N/2),\
							np.linspace(np.pi/2+thetamax,np.pi+thetamin,N/2)))
	grad = np.sum(np.asarray(np.gradient(im))**2, axis=0)
	f = interp.interp2d(x,y,grad)

	r = np.linspace(rmin, rmax, nr)

	R0 = np.zeros(N)
	for i, t in enumerate(theta):
		xi = r*np.cos(t)+xc
		yi = r*np.sin(t)+yc
		p = [f(xx,yy) for xx, yy, in zip(xi,yi)]
		R0[i] = r[np.argmax(p)]

	D = {}
	D['xf'] = (R0*np.cos(theta)+xc)
	D['yf'] = (R0*np.sin(theta)+yc)
	DF = pd.DataFrame(data=D)
	DF = lissage(DF)
	len(DF['xf'])
	if display:
		graphes.color_plot(X, Y, im)
		graphes.graph([0],[0], label='rx')
		graphes.graph([xc], [yc], label='ro')
		graphes.graph(DF['xf'],DF['yf'], label='r.', fignum=1)
		graphes.graph(np.max(r)*np.cos(theta)+xc,np.max(r)*np.sin(theta)+yc,label='w--',fignum=1)
		graphes.graph(np.min(r)*np.cos(theta)+xc,np.min(r)*np.sin(theta)+yc,label='w--',fignum=1)
		plt.savefig(save)
		plt.close()
	return DF

def lissage(DF):
	"""
	Si jamais un point est beaucoup torp loin de ses deux voisins il est remis au bon endroit
	"""
	for i in range(1, len(DF['yf'])-1):
		d_prec = math.sqrt((DF['xf'][i-1]-DF['xf'][i])**2+ \
						   (DF['yf'][i-1]-DF['yf'][i])**2)
		d_suiv = math.sqrt((DF['xf'][i]-DF['xf'][i+1])**2+ \
						   (DF['yf'][i]-DF['yf'][i+1])**2)
		if(d_prec > 5*0.3 and d_suiv > 5*0.3):
			DF['xf'][i] = (DF['xf'][i-1]+DF['xf'][i+1])/2
			DF['yf'][i] = (DF['yf'][i-1]+DF['yf'][i+1])/2
	return DF

##Code déjà existant##
import display.graphes as graphes
from Mesure import Mesure
from pre_traitement import *
##Librairie

import numpy as np
import scipy.interpolate as interp
import pandas as pd
import math
import matplotlib.pyplot as plt
import h5py


class Contour(Mesure) :
	def __init__(self, data, m={}):
		print(Mesure(data))
		Mesure.__init__(self, data)
		self.m=m


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

		mesure = self

		if(nb_im==0):
			nb_im=self.data.nb_im

		#Dictionnaire qui stocke toutes les données nécessaire
		Dic = {}

		Dic.update(get_data_param(Dic, mesure, fx, fps, D))

		Dic.update(get_H_and_L(Dic, mesure))

		Dic.update(set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax))

		#Chargement des fichiers
		if(self.data.extension in ['tif', 'png', 'jpg']):
			Na, D = charge_image_ram(self.data.fichier, Dic, self.data.extension, nb_im=nb_im)
		elif(self.data.extension in ['cine', 'avi']):
			Na, D = charge_video_ram(self.data.fichier, Dic, nb_im=nb_im)
		Dic.update(D)

			##Différents paramètres
		Dic.update(in_dict(Dic, thetamin, thetamax, rmax, rmin, B))

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
			Dic.update(redefine_rmax(Dic, DF))
			Dic.update(redefine_center(Dic, DF))

		##Mise des données dans mesure##
		self.m.update(Dic)

		return self

	def contour_instant(self, fx=0., fps=1., D=0, xmin=0, xmax=-1, ymin=0, ymax=-1, \
					x0=0, y0=0, im_save=50, adresse_s="", rmin=10, rmax=30, B=5, \
					thetamin=0.7, thetamax=0.15, nb_im=0, p_im=0):
		mesure = self

		if(nb_im==0):
			nb_im=self.data.nb_im

		#Dic stocke toutes les données nécessaires à Contour

		Dic = {}

		Dic.update(get_data_param(Dic, mesure, fx, fps, D))

		Dic.update(get_H_and_L(Dic, mesure))

		Dic.update(set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax))

		Dic.update(in_dict(Dic, thetamin, thetamax, rmax, rmin, B))


		#yxf est actualisé à chaque tour de boucle avec la nouvelle valeur du centre
		#xcf ne bouge pas car on considère que le centre ne peut que bouger sur
		#l'axe des y
		Dic['ycf'] = 0
		Dic['xcf'] = 0


		for i in range(p_im, nb_im):
			im = self.get_im(i)
			im, D = load_im(im, Dic)
			Dic.update(D)
			display = (i==im_save)
			adresse = adresse_s + "/graph%d.png" %i
			#Calcul des points, mis dans un Dataframe DF
			DF = contour(im, Dic, display=display, save=adresse)
			print("i = " + str(i))
			#Mise des données dans l'objet Contour
			for index, column in DF.iteritems():
				#Création de l'index dans m s'il n'est pas créé
				if not index in mesure.m.keys():
					self.m[index] = np.zeros((nb_im, Dic['N']))
				if p_im!=0 :
					self.m[index] = np.resize(self.m[index],(nb_im,self.m[index].shape[1]))
				self.m[index][i,:] = np.asarray(DF[index].values)
				print("index = " + str(index))
			Dic.update(redefine_rmax(Dic, DF))
			Dic.update(redefine_center(Dic, DF))

		self.m.update(Dic)
		return self

	def get_im(self,i):
		return super().get_im(self,i)

	def get_name(self):
		return "Contour"


	#Fonction de mesure

def contour(im, Dic, display=True, save="test.png"):
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
	for i in range(1, len(DF['yf'])-1):
		d_prec = math.sqrt((DF['xf'][i-1]-DF['xf'][i])**2+ \
						   (DF['yf'][i-1]-DF['yf'][i])**2)
		d_suiv = math.sqrt((DF['xf'][i]-DF['xf'][i+1])**2+ \
						   (DF['yf'][i]-DF['yf'][i+1])**2)
		if(d_prec > 5*0.3 and d_suiv > 5*0.3):
			DF['xf'][i] = (DF['xf'][i-1]+DF['xf'][i+1])/2
			DF['yf'][i] = (DF['yf'][i-1]+DF['yf'][i+1])/2
	return DF

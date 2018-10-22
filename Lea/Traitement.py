import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.interpolate as interp
import numpy as np
import os
from PIL import Image
import cv2
import display.graphes as graphes
import math
from math import sqrt
import pandas as pd

#mesure est un objet de type mesure dans lequel on va stocker les informations
#mesurées dans ce fichier

#fichier est la vidéo où on doit faire le traitement d'image

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
def traitement_parameters(mesure, fichier, fx="", ft="", D="", \
						  xmin="", xmax="", ymin="", ymax="", \
						  x0="", y0="", im_save=50, adresse_s="",\
						  rmin=10, rmax=30, B=2):
	Dic = {}
	if(os.path.exists(fichier)):
		if(hasattr(mesure.data.param, "fx")):
			fx = float(mesure.data.param.fx)
		print(fx)
		print(type(fx))
		Dic['fx']=fx
		if(hasattr(mesure.data.param, "fps")):
			ft = float(mesure.data.param.fps)
		ft = (1/ft)*1000.0
		Dic['ft']=ft

		#Le diametre doit être rentré en mm
		#s'il est rentré en minch, le code s'occupe de la conversion
		if(hasattr(mesure.data.param, "D")):
			for i in range(0, len(mesure.data.param.D)):
				if(mesure.data.param.D[i].isalpha()):
					if(mesure.data.param.D[i:len(mesure.data.param.D)]=="minch"):
						Dic['D'] = float(mesure.data.param.D[:i]) * 25.4
					elif(mesure.data.param.D[i:len(mesure.data.param.D)]=="mm"):
						Dic['D'] = float(mesure.data.param.D[:i])
					else :
						break
		else :
			Dic['D']=D



		#Les coordonnées du centre sont données avant que l'image soit coupée
		y0 = y0-ymin
		x0 = x0-xmin

		## Stockage des données dans la RAM ##

		#Cas où c'est une ou plusieurs image.s
		print(mesure.data.extension)
		if(mesure.data.extension in ['tif', 'png', 'jpg']):
			if os.path.isdir(mesure.data.fichier):
				files = os.listdir(mesure.data.fichier)
				files = tri_insertion(files)
				H,L = Image.open(mesure.data.fichier + "/" + files[0]).size
			else:
				files = mesure.data.fichier
				adresse = mesure.data.fichier
				H,L = Image.open(adresse).size
			temp = {}
			Dic['im'] = {}
			Dic['H'] = {}
			Dic['L'] = {}
			NaT = np.empty([len(files),H,L])
			Na = np.empty([len(files), (xmax-xmin), (ymax-ymin)])
			for i in range(0, 1):#len(files)):
				if os.path.isdir(mesure.data.fichier):
					adresse = mesure.data.fichier + "/" + files[i]
				im = Image.open(adresse)
				Dic['im'][i] = {}
				temp = load_im(im)
				Dic['H'][i] = temp['H']
				Dic['L'][i] = temp['L']
				Dic['im'][i]['H'] = temp['H']
				Dic['im'][i]['L'] = temp['L']
				Dic['im'][i]['im'] = temp['im']
				NaT[i] = temp['im']
				temp1, temp2 = (param(Dic['H'][i], Dic['L'][i], NaT[i], fx, xmin, xmax, \
									  ymin, ymax, x0, y0))
				Na[i] = temp1
				Dic.update(temp2)
				print(i)
		#Cas où c'est une vidéo
		if(mesure.data.extension=='cine'):
			temp1, temp2 = charge_video(mesure.data.fichier, Dic['fx'], \
										xmin, xmax, ymin, ymax, x0, y0, max=50)
			Na = temp1
			Dic.update(temp2)
			
		## Différents paramètres ##
		nr = (rmax-rmin) * B
		#Au cas où N est impair il ajoute 1
		N0 = int(np.pi * (rmax-rmin) *B)
		N = N0 + np.mod(N0,2)

		##Mise des données dans mesure##
		mesure.m['x'] = Dic['x']
		mesure.m['y'] = Dic['y']
		mesure.m['xf'] = {}
		mesure.m['yf'] = {}
		
		print(Na.shape[0])
		#Génération des données
		yf = 0
		for i in range(0, 1): #Na.shape[0]):
			display = (im_save==im_save)
			adresse = adresse_s + "/graph%d.png" %i
			DF = interface(Na[i], Dic, 0, yf, \
							   N, nr, rmin, rmax,display = display, \
							   save = adresse)
			for index, column in DF.iteritems():
				print("index = " + str(index))
				print("i = " +  str(i))
				mesure.m[index][i] = {}
				mesure.m[index][i].update(DF[index])
			rmax = func_rmax(yf, DF, rmax)
			yf = min_std_dist(DF, rmax)

		return mesure

def charge_video(fichier, fx, xmin, xmax, ymin, ymax, x0, y0, max=250):
	video = fichier
	vidcap = cv2.VideoCapture(video)
	success,image = vidcap.read()
	count = 0
	D = {}
	D['im'] = {}
	D['H'] = {}
	D['L'] = {}
	temp = {}
	H, L = Image.fromarray(image).size
	taille = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
	NaT = np.empty([max, H, L])
	Na = np.empty([max, (xmax-xmin), (ymax-ymin)])
	while success and count<max :
		#D['im'][count] = {}
		success, image = vidcap.read()
		temp = load_im(Image.fromarray(image))
		D['H'][count] = temp['H']
		D['L'][count] = temp['L']
		#D['im'][count]['H'] = temp['H']
		#D['im'][count]['L'] = temp['L']
		#D['im'][count]['im'] = temp['im']
		NaT[count] = temp['im']
		temp1, temp2 = (param(D['H'][count], D['L'][count], NaT[count],fx, xmin, xmax, ymin, ymax, x0, y0))
		Na[count] = temp1
		D.update(temp2)
		print(count)
		count +=1
	return Na, D

def func_rmax(yf, DF, rmax):
	for i in range(len(DF['yf'])):
		if rmax-math.sqrt((DF['xf'][i]**2)+(DF['yf'][i] + yf)**2)<0 :
			rmax +=1
			return rmax
	return rmax

def min_std_dist(DF, rmax):
	r = []
	std = []
	for j in range(0, rmax):
		for i in range(0, len(DF['yf'])):
			r.insert(i,math.sqrt((DF['xf'][i]**2) +\
								 (DF['yf'][i] + j)**2))
		std.insert(j, np.std(r))
	print(np.amin(std))
	return np.amin(std)			
	
def load_im(image):
	im = image
	data = []
	pix = im.load()
	H,L = im.size
	data = np.asarray([[pix[i,j] for j in range(L)] for i in range(H)])
	D = {}
	D['im']=np.asarray(data[...,0]) #les images sont noir et blancs ! on garde le permier canal rgb uniquement
	D['H']=H
	D['L']=L
	
	return D

def param(H, L, im, fx, xmin, xmax, ymin, ymax, x0, y0):
	if(L>H):
		im = np.transpose(im)
		
	#definition of a ROI (Region Of Interest)
	im = im[xmin:xmax,ymin:ymax]
	(ny,nx)=im.shape

	D = {}
	D['x']=(np.arange(0,nx)-x0)*fx
	D['y']=(np.arange(ny,0,-1)-y0)*fx
	
	return im, D
	

def interface(im, D, xc, yc, N, nr, rmin, rmax, display=True, save="test.png"):
	im0 = im
	x = D['x']
	y = D['y']
	X,Y = np.meshgrid(x,y)

	thetamin = 0.7
	thetamax = 0.15
	theta = np.concatenate((np.linspace(-thetamin,np.pi/2-thetamax,N/2),\
							np.linspace(np.pi/2+thetamax,np.pi+thetamin,N/2)))

	grad = np.sum(np.asarray(np.gradient(im0))**2,axis=0)
	f = interp.interp2d(x,y,grad)

	r= np.linspace(rmin,rmax,nr)
	
	R0 = np.zeros(N)
	for i,t in enumerate(theta):
		xi = r*np.cos(t)+xc
		yi = r*np.sin(t)+yc
		p = [f(xx,yy) for xx,yy in zip(xi,yi)]

		#if (i>N/4) and (i<N/4+2):
		#	plt.figure(2)
		#	plt.cla()
		#	plt.plot(r,p,'ko-')
		#	plt.show()
			
		R0[i] = r[np.argmax(p)]

	D = {}
	D['xf'] = (R0*np.cos(theta)+xc)
	D['yf'] = (R0*np.sin(theta)+yc)
	DF = pd.DataFrame(data=D)
	DF = lissage(DF)
	xf =DF['xf']
	yf =DF['yf']
	if display:
		graphes.color_plot(X,Y,im0)
		graphes.graph([xc],[yc],label='ro')
		graphes.graph(xf,yf,label='r.',fignum=1)
		graphes.graph(np.max(r)*np.cos(theta)+xc,np.max(r)*np.sin(theta)+yc,label='w--',fignum=1)
		graphes.graph(np.min(r)*np.cos(theta)+xc,np.min(r)*np.sin(theta)+yc,label='w--',fignum=1)
		plt.savefig(save)
		plt.close()
		#plt.colorbar()
		#graphes.legende('x (pix)','y (pix)','')
	return DF


def lissage(DF):
	for i in range(1, len(DF['yf'])-1):
		d_prec = math.sqrt((DF['xf'][i-1]-DF['xf'][i])**2+ \
						   (DF['yf'][i-1]-DF['yf'][i])**2)
		d_suiv = math.sqrt((DF['xf'][i]-DF['xf'][i+1])**2+ \
						   (DF['yf'][i]-DF['yf'][i+1])**2)
		if(d_prec > 5*0.5 and d_suiv > 5*0.5):
			print("i lissage : " + str(i))
			DF['xf'][i] = (DF['xf'][i-1]+DF['xf'][i+1])/2
			DF['yf'][i] = (DF['yf'][i-1]+DF['yf'][i+1])/2
			print("x = " + str(DF['xf'][i]))
			print(DF['yf'][i])
	return DF



def tri_insertion(liste):
	for i in range(1, len(liste)):
		x = liste[i]
		j = i
		while j>0 and plus_petit(liste[j-1], x) :
			liste[j] = liste[j-1]
			j = j-1
		liste[j] = x
	return liste

def plus_petit(file1, file2):
	temp = 0
	for i in range(0, len(file1)):
		if file1[i].isdigit() and temp==0:
			temp = i
		if not(file1[i].isdigit()) and temp>0:
			int1 = int(file1[temp:i])
			break
	temp = 0
	for i in range(0, len(file2)):
		if file2[i].isdigit() and temp==0:
			temp = i
		if not(file2[i].isdigit()) and temp>0:
			int2 = int(file2[temp:i])
			break
	return int1>int2
#load("/home/ldupuy/Documents/Stage_Python_(2018)/new/balloon_breakup_nopumps_fps10000_backlight_D800minch.cine")

#load("/home/ldupuy/Documents/Stage_Python_(2018)/new/test3.png")

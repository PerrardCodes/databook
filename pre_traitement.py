##Code déjà existant##
import display.graphes as graphes
##Librairie##
from PIL import Image
import os
import cv2
import numpy as np
import scipy.interpolate as interp
import pandas as pd
import math
import matplotlib.pyplot as plt
import glob


			##CHARGE LES VIDEOS/IMAGES DANS LA RAM##
	##A NE PAS UTILISER SUR DES FILMS/IMAGE TROP LOURDES##
#Charge la video dans la ram et envoie chaque image à image_to_array
#à crop, à define_axes_center
def charge_video_ram(fichier, Dic, nb_im=20):
	video = fichier
	vidcap = cv2.VideoCapture(video)
	count = 0
	success, image = vidcap.read()
	Na = np.empty([nb_im, (Dic['xmax']-Dic['xmin']), (Dic['ymax']-Dic['ymin'])])
	while(success and count<nb_im):
		success, image = vidcap.read()
		im_temp = image_to_array(Dic, Image.fromarray(image))
		Na[count] = crop(Dic, im_temp)
		Dic.update(define_axes_center(Dic, Na[count]))
		print("count : " + str(count))
		count+=1
	return Na, Dic

#Charge l.es image.s dans la ram et envoie chaque image à image_to_array
#à crop, à define_axes_center
def charge_image_ram(fichier, Dic, extension, nb_im=20):
	if os.path.isdir(fichier):
		files = glob.glob(fichier + "/*." + extension)
		files = tri_insertion(files)
	else :
		files = fichier
		adresse = fichier
	Na = np.empty([nb_im,(Dic['xmax']-Dic['xmin']),(Dic['ymax']-Dic['ymin'])])
	for i in range(0, nb_im):
		#if os.path.isdir(fichier):
		adresse = files[i]
		im = Image.open(adresse)
		im_temp = image_to_array(Dic, im)
		Na[i] = crop(Dic, im_temp)
		Dic.update(define_axes_center(Dic, Na[i]))
		print(i)
	return Na, Dic


			##CHARGE PUIS TRAITE LES IMAGES/VIDEOS##
			##Ne sauvegarde pas les images dans la RAM##

#Récupère une image et lance : image_to_array, crop et define_axes_center
def load_im(im, Dic):
	im_temp = image_to_array(Dic, im)
	im_temp = crop(Dic, im_temp)
	Dic.update(define_axes_center(Dic, im_temp))
	return im_temp, Dic

#return l'image numéro num dans une video
def get_im_video(video, num):
	vidcap = cv2.VideoCapture(video)
	success, image = vidcap.read()
	count = 0
	while success and count<num :
		success, image = vidcap.read()
		count+=1
	return Image.fromarray(image)

def get_im_files(fichier, num, extension) :
	if os.path.isdir(fichier):
		files = glob.glob(fichier + "/*." + extension)
		files = tri_insertion(files)
		file = files[num]
	else :
		file = fichier
	return Image.open(file)



##Différentes fonctions pour définir/refefinir les paramètres.##

##Récupère fx,ft et D depuis Data s'ils existent sinon ceux passer en paramètre##
#Le D doit être en mm, il est donc convertit si nécessaire
def get_data_param(Dic, mesure, fx, fps, D):
	param = mesure.data.param
	if(hasattr(param, "fx")):
		fx = float(param.fx)
	Dic['fx']=fx
	if(hasattr(param, "fps")):
		fps = float(param.fps)
	ft = (1/fps)*1000.0
	Dic['ft']=ft

	if(hasattr(param, "D")):
		for i in range(0, len(param.D)):
			if(param.D[i].isalpha()):
				if(param.D[i:len(param.D)]=="minch"):
					Dic['D'] = float(param.D[:i])* 25.4/1000
					break
				if(param.D[i:len(param.D)]=="inch"):
					Dic['D'] = float(param.D[:i])* 25.4
					break
				elif(param.D[i:len(param.D)]=="mm"):
					Dic['D'] = float(param.D[:i])
					break
				else :
					break
	else :
		Dic['D']=D
	return Dic

def get_H_and_L(Dic, mesure):
	if(mesure.data.extension in ['tif', 'png', 'jpg']):
		if(os.path.isdir(mesure.data.fichier)):
			ffile = os.listdir(mesure.data.fichier)[0]
			im = Image.open(mesure.data.fichier + "/" + ffile)
		else :
			im = Image.open(mesure.data.fichier)
		H,L=im.size
	elif (mesure.data.extension in ['cine', 'avi']):
		video = mesure.data.fichier
		vidcap = cv2.VideoCapture(video)
		L = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		H = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
	Dic['H'] = H
	Dic['L'] = L
	return Dic

##Paramètres des axes##
def set_axes(Dic, x0, y0, xmin, xmax, ymin, ymax):
	#Les coordonnées du centre sont données avant que l'image soit coupée
	Dic['x0']=x0-xmin
	Dic['y0']=y0-ymin
	#Si xmax et/ou ymax est à -1 on leur affecte la valeur maximal
	#Sinon on les stocke juste dans Dic
	if(xmax==-1):
		Dic['xmax']=Dic['H']
	else :
		Dic['xmax']=xmax
	Dic['xmin']=xmin
	if(ymax==-1):
		Dic['ymax']=Dic['L']
	else :
		Dic['ymax']=ymax
	Dic['ymin']=ymin
	return Dic

def crop(Dic, im):
	if(Dic['H']<Dic['L']):
		im = np.transpose(im)
	im = im[Dic['xmin']:Dic['xmax'],Dic['ymin']:Dic['ymax']]
	return im

def define_axes_center(Dic, im):
	(ny, nx)=im.shape
	Dic['x']=(np.arange(0,nx)-Dic['x0'])*Dic['fx']
	Dic['y']=(np.arange(ny,0,-1)-Dic['y0'])*Dic['fx']
	return Dic

def image_to_array(Dic, im):
	pix = im.load()
	data = np.asarray([[pix[i,j] for j in range(Dic['L'])] for i in range(Dic['H'])])
	im = np.asarray(data[...,0])#Les images sont en noir et blanc ! on garde le premier canal rgb uniquement
	return im

def in_dict(Dic, thetamin, thetamax, rmax, rmin, B):
		##Différents paramètres##
	Dic['thetamin']=thetamin
	Dic['thetamax']=thetamax
	Dic['rmax']=rmax
	Dic['rmin']=rmin
	Dic['nr'] = (rmax-rmin) * B
	#Au cas où N est impaire on ajoute 1
	N0 = int(np.pi * (rmax-rmin) *B)
	Dic['N'] = N0 + np.mod(N0,2)
	return Dic

def redefine_rmax(Dic, DF):
	for i in range(0, len(DF['yf'])):
		if Dic['rmax']-math.sqrt((DF['xf'][i]**2)+(DF['yf'][i]+Dic['ycf'])**2)<0:
			Dic['rmax'] +=1
			return Dic
	return Dic

def redefine_center(Dic, DF):
	r = []
	std = []
	for j in range(0, Dic['rmax']):
		for i in range(0, len(DF['yf'])):
			r.insert(i, math.sqrt((DF['xf'][i]**2) + \
									(DF['yf'][i] + j)**2))
		std.insert(j, np.std(r))
	Dic['ycf'] = np.amin(std)
	print("center = " + str(Dic['ycf']))
	return Dic







#Fonctions génériques de tri
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
	file1 = file1.rsplit("/", 1)[1]
	file2 = file2.rsplit("/", 1)[1]
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

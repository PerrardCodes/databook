# -*- coding: utf-8 -*-
import lea.data.Data as data
import lea.hdf5.h5py_convert as lh5py

import os
import time
from PIL import Image
import glob



#Ref -> adresse du dossier parent
#name_dir -> nom du dossier courant
#adresse -> ref + "/" + name_dir
#list_fichier -> liste des fichiers contenus dans name_dir
#adresse_s -> adresse où on sauvegarde les fichiers hdf5



def convert_arbo(ref, adresse_s):
	list_ref = os.listdir(ref)
	#On arrive dans le dossier et on convertit tous les .cine
	#sauf si c'est des .tiff dans ce cas on convertit le dossier entier
	if not(os.path.exists(adresse_s)):
		os.makedirs(adresse_s)
	if tiff(ref) :
		convert_dir(ref, adresse_s)
		#convert_files(ref, adresse_s)
	else :
		convert_files(ref, adresse_s)
	for dir in list_ref:
		#Si dans le dossier courant il y a d'autre dossier on
		#rappelle la fonction dessus
		if(os.path.isdir(ref + "/" + dir)):
			convert_arbo(ref + "/" + dir, adresse_s + "/" + dir)



def convert_files(adresse, adresse_s):
	name_dir = adresse.rsplit('/', 1)[1]
	liste_fichier= os.listdir(adresse)
	liste_fichier = tri_insertion(liste_fichier, adresse)
	cine = is_cine(liste_fichier, adresse)
	p = glob.glob(adresse + "/*.txt")[0]
	index = 1
	#Maintenant on s'occupe à tous les fichiers présents dans le dossier
	for file in liste_fichier:
		#spec est une liste propre à chaque fichier
		spec = []
		#sont les paramètres propre à chaque fichier
		#auxquels on ajoute ceux commun au dossier
		#regarde si le fichier est un .cine
		#ou s'il n'y a pas de .cine il prend les .avi
		if(get_extention(file)=="cine" or (get_extention(file)=="avi" and not(cine))):
			#On veut récupérer l'heure et la date
			#Si le fichier n'a pas la date de son dossier il la prend
			#Si le fichier n'a pas de date en titre il met alors date du fichier
			try :
				dir = int(name_dir)
			except :
				date = time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(adresse + "/" + file)))
				heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse+ "/" + file)))
				print("Le nom du dossier doit être une date")
			else :
				if time.strftime("%y%m%d" , time.localtime(os.path.getmtime(adresse + "/" + file)))==dir:
					heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse+ "/" + file)))
				else :
					heure = "0000"
				if(len(name_dir)==6):
					date = "20" + str(dir)
				else :
					date = str(dir)
			#On a tous ce qui est nécessaire à la création de Data
			d = data.Data(adresse + "/" + file, p, spec, index=index, date=date, heure=heure)
			lh5py.obj_in_h5py(d, lh5py.file_name_in_dir(d, adresse_s))
			index +=1
		elif(get_extention(file) in ["tif", "jpeg", "png"]):
			date = time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(adresse + "/" + file)))
			heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse+ "/" + file)))
			d = data.Data(adresse + "/" + file, p, spec, index=index,date=date, heure=heure)
			lh5py.obj_in_h5py(d, lh5py.file_name_in_dir(d, adresse_s))
			index+=1


def convert_dir(adresse, adresse_s):
	param = get_param(adresse)
	spec = []
	date = time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(adresse)))
	heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse)))
	d = data.Data(adresse, param, spec, index=1, date=date, heure=heure)
	print(d.fichier)
	lh5py.obj_in_h5py(d, lh5py.file_name_in_dir(d, adresse_s))

def tiff(adresse):
	if not os.listdir(adresse) :
		return False
	else :
		return len(glob.glob(adresse + "/*.tif"))>1 or len(glob.glob(adresse + "/*.png"))>1


def extract_param(str):
	p= {}
	for i in range(0, len(str)):
		if(str[i].isdigit()):
			p[str[0:i]] = str[i:len(str)]
			return p
	return {}


def get_param(adresse):
	reference = adresse + "/Reference.txt"
	param = {}
	if(os.path.exists(reference)):
		with open(reference, "r") as file:
			for lines in file.readlines():
				data = lines.strip().split('\t')
				if len(data)==2:
					param[data[0]] = data[1]
	return param

	#s'occupe du tri insertion
def tri_insertion(liste, adresse):
	for i in range(1, len(liste)):
		x = liste[i]
		j = i
		while j>0 and plus_petit(liste[j-1], x, adresse) :
			liste[j] = liste[j-1]
			j = j-1
		liste[j] = x
	return liste
	#return true si file 1 > file 2
def plus_petit(file1, file2, adresse):
	return time.mktime(time.localtime(os.path.getmtime(adresse + "/" +file1))) > time.mktime(time.localtime(os.path.getmtime(adresse + "/" +file2)))

# return true s'il y a un fichier .cine à l'adresse
def is_cine(liste, adresse):
	cine = False
	for file in liste:
		if(os.path.isfile(adresse + "/" +file) and get_extention(file)=="cine"):
		   cine =True
	return cine
#recupère l'extention du fichier, renvoie "" si c'est un dossier
def get_extention(fichier):
	if("." in fichier):
		temp = fichier.rsplit(".", 1)
		return temp[1]
	else :
		return ""

#Lors de la création des fichiers hdf5 on crée des dossiers vides
#avec cette fonction on les supprime
def errase_dir(ref):
	#On arrive dans le dossier et on regarde s'il est vide
	list_ref = os.listdir(ref)
	for dir in list_ref:
		#Si dans le dossier courant il y a d'autre dossier on
		#rappelle la fonction dessus
		if(os.path.isdir(ref + "/" + dir)):
			errase_dir(ref + "/" + dir)
	if not os.listdir(ref) :
		os.rmdir(ref)



#convert_arbo("/home/ldupuy/Documents/Stage_Python_(2018)/new/courage", "/home/ldupuy/Documents/Stage_Python_(2018)/new")
#convert_arbo("/media/ldupuy/Chicago2/Experiments_Princeton", "/home/ldupuy/Documents/Stage_Python_(2018)/new/Experiments_Princeton_hdf5/")
#errase_dir("/home/ldupuy/Documents/Stage_Python_(2018)/new/Experiments_Princeton_hdf5")
if __name__ == '__main__':
	#ref = '/home/dini/Documents/Stage_Stephane_2018'
	#adresse_s = '/home/dini/Documents/Stage_Stephane_2018'
	ref = '/Volumes/Diderot/DATA_Princeton_November2018/20181126'
	adresse_s= '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/20181106'

	#ref = "/media/stephane/OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010"
	#adresse_s = '/media/stephane/DATA/Experimental_data/Turbulence3d/20181010'
	convert_arbo(ref, adresse_s)

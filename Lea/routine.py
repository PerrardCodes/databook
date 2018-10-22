import os
import Data
from Data import Data
from h5py_convert import *
import time
from PIL import Image
import glob



#Ref -> adresse de mon dossier parent
#name_dir -> nom de mon dossier courant
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
		convert_files(ref, adresse_s)
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
	#Récupère les paramètres présents dans le fichier /Reference.txt
	#Si le fichier n'existe pas initialise param à {}
	#Les paramètres dans /Reference.txt sont communs au dossier
	param = get_param(adresse)
	index = 1
	#Maintenant on s'occupe à tous les fichiers présents dans le dossier
	for file in liste_fichier:
		#spec est une liste propre à chaque fichier
		spec = []
		#sont les paramètres propre à chaque fichier
		p = {}
		#auxquels on ajoute ceux commun au dossier
		p.update(param)
		#regarde si le fichier est un .cine
		#ou s'il n'y a pas de .cine il prend les .avi
		if(get_extention(file)=="cine" or (get_extention(file)=="avi" and not(cine))):
			#Enlève le .cine pour ne garder que les infos importantes
			name = file.rsplit(".", 1)
			#parse le nom avec les _ pour récupérer les infos importantes
			name = name[0].split('_')
			#J'ai maintenant un tableau de string
			for strg in name :
				#str peut aller dans param si :
				#str ne contient pas que des nombres
				# str ne contient pas que des lettres
				# et si str ne commence pas par une lettre
				if(not(strg=="") and not(strg.isdigit()) and not(strg.isalpha()) and not(strg[0].isdigit())):
					#Récupére les paramètres sous forme de Dictionnaire
					#puis les update dans p
					p.update(extract_param(strg))
				#si ça ne peut aller dans param ça va dans spec
				else :
					spec.append(strg)
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
			d = Data(adresse + "/" + file, p, spec, index=index, date=date, heure=heure)
			obj_in_h5py(d, file_name_in_dir(d, adresse_s))
			index +=1
		elif(get_extention(file) in ["tif", "jpeg", "png"]):
			date = time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(adresse + "/" + file)))
			heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse+ "/" + file)))
			d = Data(adresse + "/" + file, p, spec, index=index,date=date, heure=heure)
			obj_in_h5py(d, file_name_in_dir(d, adresse_s))
			index+=1


def convert_dir(adresse, adresse_s):
	param = get_param(adresse)
	spec = []
	date = time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(adresse)))
	heure = time.strftime("%H%M" , time.localtime(os.path.getmtime(adresse)))
	d = Data(adresse, param, spec, index=1, date=date, heure=heure)
	obj_in_h5py(d, file_name_in_dir(d, adresse_s))

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

ref = "/media/stephane/DATA2/Experiments_Princeton/Balloon/Backlight"
adresse_s = "/media/stephane/DATA2/Experiments_Princeton/Balloon/Backlight"
convert_arbo(ref, adresse_s)
# -*- coding: utf-8 -*-
import lea.data.Data as data


import numpy as np
import h5py
import os
import time
import pandas as pd
import glob


def obj_in_h5py(object, file, group=None, point='', attr=''):
	try :
		dic = object.__dict__
	except AttributeError :
		pass
		#print(object)
	else :
		if group is None:
			group = object.get_name()
		else :
			group = group.name + '/' + object.get_name()
		if group not in file:
			group = file.create_group(group)
		else :
			group = file[group]
		for key, attr in dic.items():
			obj_in_h5py(dic[key], file, group=group, point=key, attr=attr)
	if type(object) in [dict]:
		for key, attr in object.items():
			obj_in_h5py(object[key], file, group=group, point=key, attr=attr)
	if type(object) in [list,tuple]:
		object = np.asarray(object)
		#for i in range (0, len(attr)):
		#	attr[i] = attr[i]#.encode("utf-8")
	if type(object) in [np.ndarray]:
		dataname = group.name+'/'+point
		if dataname not in file :
			dset = file.create_dataset(dataname, data=attr, chunks=True)
		else :
			file[dataname][...] = attr
	if type(object) in [bool, int, float, np.int64, np.float64]:
		group.attrs[point] = attr
	elif type(object) in [str]:
		group.attrs[point] = attr.encode('utf-8') #encode it to avoid error due to special characters


#Crée et ouvre le fichier à une certaine adresse et grace à un objet
#Si l'adresse n'existe pas il crée la crée.
def file_name_in_dir(object, adresse):
	if not(os.path.exists(adresse)):
		os.makedirs(adresse)
	if(object.get_name()=="Data"):
		name = cstr(object.id.date) + '_' + cstr(object.id.index) + '_' +  cstr(object.fichier.rsplit("/", 1)[1].split(".")[0]) + ".hdf5"
	else:
		name = cstr(object.data.id.date) + '_' + cstr(object.data.id.index) + '_' +  cstr(object.data.fichier.rsplit("/", 1)[1].split(".")[0]) + ".hdf5"
		count = len(glob.glob(adresse + "/Mesure_*" +name))
		name = "Mesure_" + str(count) + "_" + name
	#Crée le fichier avec w, si le fichier existe le supprime
	f = h5py.File(adresse + "/" + name, "w")
	#r+ sert à lire/écrire si le fichier existe
	#f = h5py.File(adresse + "/" + name, "r+")
	return f

def cstr(s):
	if(type(s) in[str]):
		return s
	elif (type(s) in[int, np.int64, np.float64]):
		return str(s)
	else :
		return str(s.decode('utf-8'))

#Ouvre le fichier
def ouverture_fichier(name, mode="r"):
	#print(type(h5py))
	f = h5py.File(name, mode)
	return f


#récupère un fichier hdf5 et en crée un data
def h5py_in_Data(f) :
	from lea.data.Param import define_type as dt
	group = f['Data']
	d={}
	for attr in group:
		is_dataset = isinstance(group[attr], h5py.Dataset)
		if(is_dataset):
			d[attr] = []
			for i in range(0, len(group[attr])):
				d[attr].append(group[attr][i])
	for attr in group.attrs:
		if(type(group.attrs[attr]) in[int, np.int64, np.float64]):
			d[attr] = group.attrs[attr]
		else :
			d[attr] = dt(group.attrs[attr].decode('utf-8'))

	group = f['Data/Param']
	p = {}
	for attr in group.attrs :
		if(type(group.attrs[attr]) in[int, np.int64, np.float64]):
			p[attr] = group.attrs[attr]
		else :
			p[attr] = dt(group.attrs[attr].decode('utf-8'))

	s = group.get("spec")
	spec = []
	if(s!=None):
		for t in s:
			spec.append(t.decode('utf-8'))

	group = f['Data/Id']
	i = {}
	for attr in group.attrs :
		i[attr] = group.attrs[attr]

	return data.Data(d, p, spec, **i)

#récupère un fichier hdf5 et crée un objet mesure
def h5py_in_Mesure(f):
	import lea.mesure.Mesure as mesure
	group = f['Mesure']
	m_dico = {}
	bulles = None
	contour = None
	for attr in group:
		is_dataset = isinstance(group[attr], h5py.Dataset)
		if(is_dataset):
			m_dico[attr] = []
			for i in range(0, len(group[attr])):
				m_dico[attr].append(group[attr][i])
	f = f['Mesure']
	data = h5py_in_Data(f)
	m = mesure.Mesure(data)
	if(f.__contains__("Contour")) :
		c = h5py_in_Contour(f, data)
		m.add_measurement(c)
	if(f.__contains__("Bulles")) :
		b = h5py_in_Bulles(f, data)
		m.add_measurement(b)
	if(f.__contains__("PIV3D")) :
		p = h5py_in_piv3d(f, data)
		m.add_measurement(p)
	if(f.__contains__("Volume")) :
		p = h5py_in_Volume(f, data)
		m.add_measurement(p)

	return m

#récupère un file hdf5, un data et crée un objet Bulles
def key(f):
    return [key for key in f.keys()]

def h5py_in_obj(f,data=None):
    keys = key(f)
    if 'Volume' in keys:
        return h5py_in_Volume(f)


def h5py_in_Bulles(f,data=None):
	import lea.mesure.Bulles as bulles
	group_b = f['Bulles']
	m={}
	temp={}
	for attr in group_b :
		if(isinstance(group_b[attr], h5py.Dataset)) :
			for i in range (0, len(group_b[attr])):
				temp[attr] = group_b[attr][i]
	for attr in group_b.attrs:
		m[attr] = group_b.attrs[attr]
	df = pd.DataFrame(data=temp)
	m["DF"] = df
	b = bulles.Bulles(data, m=m)
	return b

def h5py_in_Volume(f, data=None):
	import lea.mesure.Volume_SP as volume
	group_v = f['Volume']
	m={}
	for attr in group_v :
		if(isinstance(group_v[attr], h5py.Dataset)) :
			m[attr] = group_v[attr][()]
	for attr in group_v.attrs:
		m[attr] = group_v.attrs[attr]
	#df = pd.DataFrame(data=temp)
	#m["DF"] = df
	f = f['Volume']
	if data == None:
	       data = h5py_in_Data(f)

	v = volume.Volume(data, m=m)
	return v

#récupére un file hdf5, un data et crée un objet Contour
def h5py_in_Contour(f, data):
	import lea.mesure.Contour as contour
	group = f['Contour']
	c = {}
	df = pd.DataFrame()
	m = {}
	for attr in group :
		if isinstance(group[attr], h5py.Dataset):
			m[attr] = pd.DataFrame(data=group[attr].value)
	for attr in group.attrs :
		m[attr] = group.attrs[attr]
	return contour.Contour(data, m=m)


#récupère un file hdf5, un data et crée un objet PIV3D
def h5py_in_piv3d(f, data):
	import lea.mesure.Piv3D as piv
	group_p = f['PIV3D']
	m={}
	#temp={}
	for attr in group_p :
	   is_dataset = isinstance(group_p[attr], h5py.Dataset)
	   if(is_dataset):
	       m[attr] = group_p[attr][()]

	for attr in group_p.attrs:
	   m[attr] = group_p.attrs[attr]
	#df = pd.DataFrame(data=temp)
	#m["DF"] = df
	b = piv.Piv3D(data, m=m)
	return b


def creation_utilisateur():
	print("Création de l'objet Data")
	print("Veuillez entrer l'adresse du fichier (video, image...)")
	fichier = input()
	if not(os.path.exists(fichier)):
		raise Exception('L\'adresse entrée ne convient pas')
	print("Veuillez entrer l'adresse du fichier des paramètres.")
	param = input()
	if not(os.path.exists(param)):
		raise Exception('L\'adresse entrée ne convient pas')
	print("Veuillez entrer l'index de la manip :")
	index = input()
	try :
		index = int(index)
	except :
		raise Exception("Veuillez entrer un nombre entier")
	print("Veuillez entrer le type de la manip")
	typ = input()
	if(typ==""):
		typ="Non spécifié"
	print("Veuillez entrer la personne ayant réalisé la manip")
	who = input()
	if(who==""):
		who ="SPerrard"
	date =time.strftime("%Y%m%d" , time.localtime(os.path.getmtime(fichier)))
	heure =time.strftime("%H%M" , time.localtime(os.path.getmtime(fichier)))
	spec = {}
	d = data.Data(fichier, param, spec, index=index, typ=typ, who=who, date=date, heure=heure)
	return d

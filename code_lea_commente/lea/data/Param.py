import numpy as np
import os

class Param:
    """
    :param p: Sert à mettre les paramètres en attribut
    :type p: dict or adresse
    :param spec: Sert à donner les informations supplémentaire dans une liste
    :type spec: list or adresse
    """
    def __init__(self, p, spec):
        print(p)
        if(type(p)==dict):
            self.from_dict(p)
        elif(os.path.exists(p)) :
            self.from_file(p)
        else :
            raise Exception('Param n\'a pas pu être créé (param)')
        if (type(spec)==list):
            self.spec = spec
        elif (os.path.exists(spec)):
            self.spec_file(spec)
        else :
            raise Exception('Param n\'a pas pu être crée (spec)')

    def from_dict(self, dic):
        """
        :param dic: Dictionnaire récupéré de l'__init__
        :type dic: dict
        :return: Rien mais met tout les attributs avec les valeurs présente dans le dictionnaire passé en paramètre.
        """
        for key, attr in dic.items():
            setattr(self, key, attr)

    def from_file(self, fichier):
        """
        :param fichier: Adresse récupéré de l'__init__
        :type fichier: fichier
        :return: Rien mais met tout les attributs avec les valeurs présentes dans le fichier passé en paramètre

        .. warning:: Le nom du paramètre et sa valeur doivent être séparé d'une tabulation

        """
        #Ouvre le fichier avec les droits de lecture uniquement
        with open(fichier, "r") as f:
            for lines in f.readlines():
                data = lines.strip().split('\t')
                if len(data)==2: #En cas de saut de ligne vide
                    setattr(self, data[0], define_type(data[1]))

    def spec_file(self, fichier):
        """
        :param fichier: Adresse récupéré de l'__init__ (spec)
        :type fichier: fichier
        :return: Rien mais met les attributs présent dans le titre du fichier passé en paramètre

        .. warning:: Dans le titre tout les attributs doivent être séparé d'un underscore ("_")

        .. note:: Pour qu'une information soit mise en tant que paramètre elle ne doit pas contenir que des nombres ni ne contenir que des lettres et ne commence pas par une lettre
        """
        p = {}
        spec = []
        name = fichier.rsplit(".", 1)
        name = name[0].rsplit("/", 1)
		#parse le nom avec les _ pour récupérer les infos importantes
        name = name[1].split('_')
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
        for key, attr in p.items():
            setattr(self, key, attr)


    def get_name(self):
        """
        :return: Le nom de l'objet, ici "Param"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
        return "Param"

def extract_param(str):
	p= {}
	for i in range(0, len(str)):
		if(str[i].isdigit()):
			p[str[0:i]] = define_type(str[i:len(str)])
			return p
	return {}

def define_type(strg):
    """
    :return: La valeur une fois convertit

    Convertit les valeurs qui sont récupéré depuis le fichier texte.
    Essaie de la convertir en int, sinon en float.
    Si jamais c'est un string la fonction essaie de convertir les valeurs (k, minch, inch, mV)

    """
    if(type(strg)==str):
        try:
            strg = int(strg)
        except ValueError:
            pass
        else :
            return strg
        try:
            strg = float(strg)
        except ValueError:
            pass
        else :
            return strg
        if(strg[len(strg)-2:len(strg)]=="mV"):
            return str(float(strg[0:len(strg)-2])/1000)+"V"
        if(strg[0].isdigit()):
            for i in range(0, len(strg)):
                if(strg[i].isalpha() and strg[i]=="k"):
                    return str(float(strg[0:i])*1000) + strg[i+1:len(strg)]
        if(strg[len(strg)-5:len(strg)]=="minch"):
            return str(float(strg[:len(strg)-5])* 25.4/1000)+"mm"
        if(strg[len(strg)-4:len(strg)]=="inch"):
            return str(float(strg[:len(strg)-4])* 25.4)+"mm"
        return strg

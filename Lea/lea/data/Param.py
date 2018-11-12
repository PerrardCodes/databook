import numpy as np
import os

class Param:

    def __init__(self, p, spec):
        print(p)
        if(type(p)==dict):
            self.from_dict(p)
        elif(os.path.exists(p)) :
            self.from_file(p)
        else :
            raise Exception('Param n\'a pas pu être créé')
        self.spec = spec

    def from_dict(self, dic):
        for key, attr in dic.items():
            setattr(self, key, attr)


    def from_file(self, fichier):
        #Ouvre le fichier avec les droits de lecture uniquement
        with open(fichier, "r") as f:
            for lines in f.readlines():
                data = lines.strip().split('\t')
                if len(data)==2: #En cas de saut de ligne vide
                    setattr(self, data[0], data[1])


    def get_name(self):
        return "Param"

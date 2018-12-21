#!/usr/bin/python
# -*- coding: utf8 -*-
import lea.mesure.Mesure as mesure
import lea.mesure.pre_traitement as preT
import lea.danjruth.piv as piv
import stephane.cine.cine as cine

import lea.hdf5.h5py_convert as lh5py

import matplotlib.pyplot as plt
import glob
import numpy as np
import sys
import h5py
from functools import partial
from multiprocessing import Process,Pool
import os
import cv2
from ast import literal_eval as make_tuple


class Volume(mesure.Mesure):
    """
    :param m: Contient toutes les informations obtenues lorsqu'on a lancé le traitement.
    :type m: dict

    Contient le même data que celui de sa classe mère Mesure, il est nécessaire d'avoir les informations en double notamment si on change des paramètres.

    """
    def __init__(self, data, m={}):
        mesure.Mesure.__init__(self, data)
        if m == {}:
            print('Create object with no measurement file')
        else:
            print('Are you sure you want to generate a volume object with an already existing m field ?')
        self.m=m

    def get_name(self):
        """
        :return: Le nom de l'objet, ici "Volume"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
        return "Volume"


    def volume(self, nb_im=None, nmin=5, dtmax=10, instant=None):
        """
        :returns: Objet Volume avec dans le dictionnaire m, "instantV", "tV", "CV"
        """

        Dic = {}
        cinefile = self.data.fichier
        c = cine.Cine(cinefile)
        if(type(self.data.param.fps) in [int, float]):
            Dic['fps'] = int(self.data.param.fps)
        elif(self.data.param.fps[len(self.data.param.fps)-1]=="k"):
            Dic['fps'] = (int(self.data.param.fps.rsplit("k",1)[0])*1000)

        #detecte les débuts et fin de Volumes
        #ft = 1./40000 #should be given directly by Data.param.ft
        Dic['dtmin'] = nmin*Dic['fps']#we look for jumps at least 10 times Dt
        Dic['dtmax'] = dtmax #value in second
        if(nb_im==None):
            Dic['N']=len(c)
        else :
            Dic['N'] = nb_im
        if instant==None :
            instant = self.find_timejumps(c, Dic)

        Dic['f'] = int(self.data.param.flaser)
        Dic['Nz'] = Dic['fps']//Dic['f']
        #we should find the number of images using framerate/f, see data.param, need lea's package

        #(instantV,tV) = find_positionlaser(c,instant,Nz=Nz)
        (instantV,tV,CV) = self.analysis_multi_proc(cinefile, instant, Dic, Nz=Dic['Nz'])
        self.m['instantV']=instantV
        self.m['tV'] = tV
        self.m['CV'] = CV
        return self

    def volume_2d(self, nb_im=None, nmin=5, dtmax=10):
        """
        :returns: Objet Volume contenant dans le dictionnaire m, un "instant"
        """
        Dic = {}
        cinefile = self.data.fichier
        c=cine.Cine(cinefile)
        Dic['fps'] = int(self.data.param.fps)

        Dic['dtmin'] = nmin * Dic['fps']
        Dic['dtmax'] = dtmax
        if(nb_im==None):
            Dic['N']=len(c)
        else :
            Dic['N'] = nb_im

        instant = self.find_timejumps(c, Dic)
        self.m['instant'] = instant
        self.m.update(Dic)
        return self

    def find_timejumps(self, c, Dic):
        N = Dic['N']
        dtmin = Dic['dtmin']
        dtmax = Dic['dtmax']

        t =   np.asarray([c.get_time(i) for i in range(N)])
        jumps = np.logical_and(np.diff(t)>dtmin,np.diff(t)<dtmax)
        indices = np.where(jumps)[0]
        if len(indices)>2:
            waittime = np.diff(t[indices])
            print('Maximum difference between waiting times : '+str(np.max(waittime)-np.min(waittime)))

            instant = []
            for i,ind in enumerate(indices[1:-1]):
                start = indices[i]+1
                end = indices[i+1]-1
            #plt.plot(np.diff(timages[start:end]))
                instant.append((start,end))
        else:
            instant = [(0,N)]

        return instant


    def analysis_multi_proc(self, c, instant, Dic, Nz=20):
        N = Dic['N']
        #cut_function
        Ncpu = os.cpu_count()
        ite = []#np.zeros(Ncpu)
        #instant = np.asarray(instant)

        with Pool(processes=Ncpu) as pool:
    	        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
                func = partial(self.find_positionlaser, c, Nz)
                f = pool.starmap(func, instant)

                instantV = []
                tV = []
                CV = []
                print(len(instant))
                print(len(instant[0]))

                for i in range(min(Ncpu,len(instant))):
                    instantV = instantV + f[i][0]
                    tV = tV + f[i][1]
                    CV = CV + f[i][2]


        return (instantV,tV,CV)

    def find_positionlaser(self, c, Nz, start=0, end=1):#, a=5, Nz=None):
        instantV = []
        tV = []
        print(start,end)
        a=5
        c = cine.Cine(c)

    #    for (start,end) in instant:
        if(True):
            C = []
            print(start)
            for j in range(start,end-1):
                print("image : " + str(j))
                im = c.get_frame(j)
                im1 = c.get_frame(j+1)
                mean1 = np.mean(im,axis=(0,1))
                mean2 = np.mean(im1,axis=(0,1))
                std1 = np.std(im,axis=(0,1))
                std2 = np.std(im1,axis=(0,1))

                C.append(np.mean((im-mean1)*(im1-mean2),axis=(0,1))/(std1*std2))

            maximum=[]
            minimum=[]
            for i in range(a,len(C)-a):
                print("deuxième partie : " + str(i))
                window = slice(i-a,i+a+1)
                if np.argmax(C[window])==a+1:
                    maximum.append(i+1)
                    #plt.plot(i+1-maximum[0],C[i+1],'rx')
                    if len(maximum)>1 and len(minimum)>0:
                        # get which way we are scanning
                        if (minimum[-1]-maximum[-2])<=Nz/2:
                            startV = maximum[-2]+start
                            endV = maximum[-1]+start
                        else:
                            startV = maximum[-1]+start
                            endV = maximum[-2]+start
                        instantV.append((startV,endV))
                        tV.append(c.get_time((startV+endV)//2))

                if np.argmin(C[window])==a+1:
                    if len(maximum)>0:
                        minimum.append(i+1)
                        #if (minimum[-1]-maximum[-1])<=Nz/2:
                        #    plt.plot(i+1-maximum[0],C[i+1],'bo')
                        #else:
                        #    plt.plot(i+1-maximum[0],C[i+1],'k*')
                            #do a mirror symetry

            #plt.plot(C[maximum[0]:maximum[-1]])
            #plt.axis([0,150,0.65,1])
        return (instantV,tV,C)

    def get_im(self,i):
    	return super().get_im(self,i)

    def save_volume(self, savefolder, start=None, end=None):
        """
        Une fois qu'on a la liste des volumes on souhaite créer un fichier HDF5 pour chaque volume
        """
        d = self.data
        Nt = len(self.m['tV'])

        for i in range(Nt):
            v0 = Volume(d,m={})

            Vol,instant,t = self.get_volume(i, start, end)#Vol,instant,t

            v0.m['volume'] = Vol
            v0.m['instant'] = instant
            v0.m['t'] = t

            f = lh5py.file_name_in_dir(v0, savefolder)
            lh5py.obj_in_h5py(v0, f)
            f.close()



    def get_volume(self, i, start=None, end=None):#adresse, adresse_s):
        c = cine.Cine(self.data.fichier)

        L,H = c.get_frame(0).shape
        if start==None and end==None :
            start,end = (self.m['instantV'][i][0],self.m['instantV'][i][1])

        tV = self.m['tV'][i]

        Nz = np.abs(start-end)+1
        Vol = np.zeros((Nz,L,H))

        print(start,end)
        frames = np.arange(start,end+1,np.sign(end-start))

        for j,frame in enumerate(frames):
            Vol[j,...] = c.get_frame(frame)

        return Vol,(start,end),tV

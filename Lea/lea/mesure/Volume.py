#!/usr/bin/python
# -*- coding: utf8 -*-
import lea.mesure.Mesure as mesure
import lea.mesure.pre_traitement as preT
import fluids2d.piv as piv
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
    def __init__(self, data, m={}):
        mesure.Mesure.__init__(self, data)
        self.m=m

    def get_name(self):
        return "Volume"

    def get_volume(self, adresse, hdf5):
        f = lh5py.ouverture_fichier(hdf5)
        f = f["Mesure/Volume"]
        d = lh5py.h5py_in_Data(f)
        c = cine.Cine(d.fichier)
        vidcap = cv2.VideoCapture(d.fichier)
        L = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        H = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        group = f
        temp = {}
        temp['instantV'] = {}
        temp['tV'] = {}
        for n in range(0, len(group['instantV'])) :
            temp["instantV"][n] = group['instantV'][n].decode('UTF-8')
        for n in range(0, len(group['tV'])) :
            temp["tV"][n] = group['tV'][n].decode('UTF-8')
        for i in range(0, len(temp['instantV'])):
            un = make_tuple(temp['instantV'][i])[0]
            deux = make_tuple(temp['instantV'][i])[1]
            nump = np.zeros((abs(un-deux)+1,L,H))
            for j in range(min(un, deux), max(un, deux)+1):
                print(j)
                nump[j-min(un,deux),...]=c.get_frame(j)
            self.m['volume']=nump
            self.m['t']=temp['tV'][i]
            self.m['instant']=temp['instantV'][i]
            file = lh5py.file_name_in_dir(self, adresse + "/Volume/")
            lh5py.obj_in_h5py(self, file)
            print(nump.shape)

        #temp['instantV'] = group['instantV'][()]
        #print(temp)

    def volume(self, nb_im=None, nmin=5, dtmax=10):
        Dic = {}
        cinefile = self.data.fichier
        c = cine.Cine(cinefile)
        if(self.data.param.fps[len(self.data.param.fps)-1]=="k"):
            Dic['fps'] = (int(self.data.param.fps.rsplit("k",1)[0])*1000)
        else :
            Dic['fps'] = int(self.data.param.fps)
        #detecte les débuts et fin de Volumes
        #ft = 1./40000 #should be given directly by Data.param.ft
        Dic['dtmin'] = nmin*Dic['fps']#we look for jumps at least 10 times Dt
        Dic['dtmax'] = dtmax #value in second
        if(nb_im==None):
            Dic['N']=len(c)
        else :
            Dic['N'] = nb_im
        instant = self.find_timejumps(c, Dic)

        Dic['Nz'] = 20
        #we should find the number of images using framerate/f, see data.param, need lea's package

        #(instantV,tV) = find_positionlaser(c,instant,Nz=Nz)
        (instantV,tV) = self.analysis_multi_proc(cinefile, instant, Dic, Nz=Dic['Nz'])
        self.m['instantV']=instantV
        self.m['tV'] = tV
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
                print(len(instant))
                print(len(instant[0]))

                for i in range(min(Ncpu,len(instant))):
                    instantV = instantV + f[i][0]
                    tV = tV + f[i][1]

        return (instantV,tV)

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
            for j in range(start,end):
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
        return (instantV,tV)

    def get_im(self,i):
    	return super().get_im(self,i)
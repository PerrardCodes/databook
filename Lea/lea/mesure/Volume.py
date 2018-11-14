#!/usr/bin/python
# -*- coding: utf8 -*-
import lea.mesure.Mesure as mesure
import lea.mesure.pre_traitement as preT
import fluids2d.piv as piv
import stephane.cine.cine as cine

import matplotlib.pyplot as plt
import glob
import numpy as np
import sys
from functools import partial
from multiprocessing import Process,Pool
import os


class Volume(mesure.Mesure):
    def __init__(self, data, m={}):
        mesure.Mesure.__init__(self, data)
        self.m=m

    def get_name(self):
        return "Volume"

    def volume(self):
        Dic = {}
        cinefile = self.data.fichier
        c = cine.Cine(cinefile)
        if(self.data.param.fps[len(self.data.param.fps)-1]=="k"):
            Dic['fps'] = 1./(int(self.data.param.fps.rsplit("k",1)[0])*1000)
        else :
            Dic['fps'] = 1./self.data.param.fps
        #detecte les débuts et fin de Volumes
        #ft = 1./40000 #should be given directly by Data.param.ft
        Dic['dtmin'] = 10*Dic['fps']#we look for jumps at least 10 times Dt
        Dic['dtmax'] = 10 #value in second
        Dic['N'] = 1000#len(c)
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

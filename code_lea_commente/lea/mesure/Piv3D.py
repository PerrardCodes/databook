# -*- coding: utf-8 -*-
import lea.mesure.Mesure as mesure
import lea.mesure.pre_traitement as pre
import lea.danjruth.piv as p

import lea.danjruth.piv_volume as p3d

import stephane.analysis.cdata as cdata


from functools import partial
from multiprocessing import Process, Pool
import os
import numpy as np

class Piv3D(mesure.Mesure):
    """
    :param m: Contient toutes les informations obtenues lorsqu'on a lancé le traitement.
    :type m: dict

    Contient le même data que celui de sa classe mère Mesure, il est nécessaire d'avoir les informations en double notamment si on change des paramètres.

    """
    def __init__(self, data, m={}):
        mesure.Mesure.__init__(self, data)
        self.m=m

    def load_piv_parameters(self):
        """
        Load les paramètres suivant dans un dictionnaire :

        * fx
        * f
        * fps
        * frame_diff
        * dt_origin

        """
        param = self.data.param
        Dic = {}
        if(hasattr(param, "fx")):
            Dic["fx"] = float(param.fx)
        if(hasattr(param, "galvo")):
            Dic["f"] = int(param.galvo)
        if(hasattr(param, "fps")):
            Dic["fps"] = int(param.fps)
        if(hasattr(param, "frame_diff")):
            Dic["frame_diff"]=param.frame_diff
        else :
            Dic["frame_diff"] = int(Dic["fps"]/Dic["f"])
        Dic["dt_origin"] = 1./Dic["frame_diff"]
        return Dic


    def analysis(self, parent_folder, cine_name, adresse_s, npy=None, fx=1., dt_origin="", \
                frame_diff="", crop_lims=None, maskers=None,\
                window_size=32, overlap=16, search_area_size=32,\
                save=True, s2n_thresh=1.2, bg_n_frames=None, a_frames=""):
        """
        Lance et stocke dans un objet le code présent dans danjruth.piv
        """
        param = self.data.param
        Dic = self.load_piv_parameters()
        frame_diff = Dic["frame_diff"]
        #Crée un objet processing présent dans : danjruth.piv
        processing = p.PIVDataProcessing(parent_folder, cine_name, name_for_save=adresse_s, dx=fx, dt_orig=dt_origin,\
                                        frame_diff=frame_diff, crop_lims=crop_lims, maskers=maskers,\
                                        window_size=window_size, overlap=16, search_area_size=search_area_size)
        #ajoute à m ce qu'il a dans l'objet processing
        self.m.update(processing.__dict__)
        #Si npy n'est pas donné en paramètre il lance l'analyse sur l'objet
        if(npy==None):
            flowfield = processing.run_analysis(a_frames=a_frames, save=save, s2n_thresh=s2n_thresh, bg_n_frames=bg_n_frames)
        #Sinon il load juste le npy dans m
        else :
            self.m['U'] = np.load(npy)

        return flowfield


    def load(self, npy):
        self.m['U'] = np.load(npy)

    def analysis_multi_proc(self, parent_folder, cine_name, adresse_s, npy=None, fx=1., dt_origin="", frame_diff="", crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32,save=True, s2n_thresh=1.2, bg_n_frames=None):
        #frame_diff = self.frame_diff
        #fx = self.fx
        #dt_origin = self.dt_origin

        """
        Lance la fonction :func:`analysis` en multiprocessing
        """
        Dic = self.load_piv_parameters()

        frame_diff = int(Dic["frame_diff"])
        self.data.nb_im = int(self.data.nb_im)

        print(frame_diff)
        Ncpu = os.cpu_count()
        print(Ncpu)
        print(frame_diff/Ncpu)
        print(Ncpu/frame_diff)
        if Ncpu>frame_diff and Ncpu%frame_diff>0:
            Ncpu = Ncpu-Ncpu%frame_diff
        with Pool(processes=Ncpu) as pool:
            ite = []
            if frame_diff==1:
                for i in range(Ncpu):
                    ite.append(np.arange(i*2,self.data.nb_im-frame_diff, Ncpu*2))
                for i in range(Ncpu):
                    ite.append(np.arange(i*2+1,self.data.nb_im-frame_diff, Ncpu*2))
            elif Ncpu<=frame_diff:
                if frame_diff%Ncpu==0:
                    print('Algorithm optimal')
                for i in range(frame_diff):
                    ite.append(np.arange(i,self.data.nb_im-frame_diff,frame_diff))
            else: # each cpu will work twice : one time on indices [0,2*Ncpu, ...] one time on indices [frame_diff,frame_diff+2*Ncpu]
                for i in range(Ncpu//frame_diff):
                    for j in range(frame_diff):
                        ite.append(np.arange(i*2*frame_diff+j,self.data.nb_im-frame_diff,2*Ncpu))
                for i in range(Ncpu//frame_diff):
                    for j in range(frame_diff):
                        ite.append(np.arange(i*2*frame_diff+j+frame_diff,self.data.nb_im-frame_diff,2*Ncpu))


	        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
            func = partial(self.analysis, parent_folder, cine_name, adresse_s, npy, Dic["fx"], Dic["dt_origin"],frame_diff, crop_lims, maskers, window_size, overlap, search_area_size, save, s2n_thresh, bg_n_frames)
            f = pool.map(func, ite)

            print(len(f))
#            stophere
            #get the image shape and the number of images processed by cpu from the output
            N=0
            for i in range(frame_diff):
                dim = f[i].shape
                N += dim[0]
            dimensions = (N,)+dim[1:] #assume all the images have the same shape
            flowfield = np.zeros(dimensions)

            for i in range(frame_diff):
                flowfield[i:N:frame_diff,...]=f[i]
            np.save(parent_folder+adresse_s+'_flowfield.npy',flowfield)
        self.m['U'] = flowfield
        return self

    def space_axis(self):
        ff = self.m['U']
        dx = self.m['dx']
        dz = self.m['dz']
                #generate space axis
        (Nz,Nx,Ny,Nc) = ff[0,...].shape
#mean_flow = np.transpose(mean_flow,(1,2,0,3))
        x = np.arange(-(Nx-1)/2,(Nx-1)/2+1)*dx
        y = np.arange(-(Ny-1)/2,(Ny-1)/2+1)*dx
        z = np.arange(-Nz/2,Nz/2)*dz-2
        [X,Z,Y] = np.meshgrid(x,z,y)

        self.m['x'] = x
        self.m['y'] = y
        self.m['z'] = z

    def from2d_to3d(self):
    #make sure the name is correct
        if 'np' in self.m.keys():
            print('np format')
            print(self.m['np'].shape)

            # rename the field
            self.m['U']=M.PIV3D.m['np']
            self.m.pop('np')

        #create a shortcut for the velocity field
        ff = self.m['U']

        self.load_piv_parameters()
        print(self.fx)

        #convert 2d to 3d data
        (Nt,Nx,Ny,Nc) = ff.shape
        frame_diff = self.frame_diff#int(M.data.param.fps // M.data.param.f)
        print(frame_diff)

        start = self.data.param.startV[0]#int(M.data.param.startV)
        Nt = (Nt-start)//frame_diff
        Nz = frame_diff
        end = start+Nz//2#int(M.data.param.endV)

#ff=ff[:,9:25,...]
#(start,end) = v.m['instantV'][0]
#ff=ff[:,start:end,...]
        ff = np.reshape(ff[start:Nt*Nz+start,...],(Nt,Nz,Nx,Ny,Nc))
        ff[...,1] = -ff[...,1] #reverse sign of horizontal component
        ff = ff[:,:Nz//2,...]
        print(ff.shape)


        # generate time axis
        dz = float(self.data.param.l_c)/frame_diff*2
        print(dz)

        self.m['overlap'] = 16
        dx = float(self.data.param.fx*self.m['overlap'])
        print(dx)

        self.m['dz'] = dz
        self.m['dx'] = dx
        self.space_axis()

        #generate time axis
        ft = frame_diff/self.fps
        print(ft)
        self.m['ft'] =  ft
        self.m['t'] = np.arange(0,Nt*ft,ft)


        # remove nan from the edges
        print(cdata.nancount(ff))
        ff = ff[...,1:-1,1:-1,:]
        print(cdata.nancount(ff))

        ff = cdata.remove_nan_3d(ff)
        print(cdata.nancount(ff))

        self.m['U'] = ff
        self.compute_mean_flow()

    def compute_mean_flow(self):
#compute mean_flow
        ff = self.m['U']
        mean_flow = np.nanmean(ff,axis=0)
        mean_flow_speed = np.linalg.norm(mean_flow,axis=2)
        mean_speed = np.nanmean( np.sqrt(ff[...,0]**2 + ff[...,1]**2 ), axis=0)
        fluc = ff - mean_flow
        u_rms = np.sqrt(np.nanmean(fluc[...,0]**2+fluc[...,1]**2 ,axis=0) )

        self.m['mean_flow'] = mean_flow
#piv.m['fluc'] = fluc
        self.m['u_rms'] = u_rms
        self.m['U'] = ff

    def add_measurement(self, obj, name):
        """
        Ajoute un paramètre à Piv3D, si c'est un objet il ajoute l'attribut avec pour nom le nom de la classe qu'on a récupéré grâce à la méthode :func:`get_name()` sinon il l'ajoute avec le nom donné en paramètre
        """
        setattr(self, name, obj)

    def get_name(self):
        """
        :return: Le nom de l'objet, ici "PIV3D"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
        return "PIV3D"

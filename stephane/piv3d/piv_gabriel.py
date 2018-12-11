import matplotlib.pyplot as plt
import glob
import numpy as np
from functools import partial
from multiprocessing import Process,Pool
import os

#!/usr/bin/python
# -*- coding: utf8 -*-

#from danjruth.piv import *
import openpiv.process as process
import openpiv.validation as validation
import cv2 #for loading images

class PIVDataProcessing:
    
    def __init__(self,folder,window_size=32,overlap=16,search_area_size=32,frame_diff=1,name_for_save=None,maskers=None,crop_lims=None,dx=1,dt_orig=1):
        
         # Metadata
        self.folder=folder
        #self.num_frames_orig = len(pims.open(self.cine_filepath))
        self.maskers=maskers
        self.crop_lims = crop_lims
        self.cine_frame_shape=None

        # PIV Parameters
        self.window_size=window_size
        self.overlap=overlap
        self.search_area_size=search_area_size
        self.frame_diff = frame_diff # pairs of frames separated by how many frames

        # Scaling, for reference -- results are still stored in [pixels / frame] !
        self.dx=dx
        self.dt_orig=dt_orig # "original" dt - between frames in the cine
        self.origin_pos=None

        self.dt_ab = self.dt_orig*self.frame_diff # dt between frames a and b

        # For saving the results
        self.flow_field_res_filepath = None # will store a path to the numpy array with the flow field results
        if name_for_save is None:
            self.name_for_save = self.cine_name
        else:
            self.name_for_save = name_for_save
                
    
    def analysis_multi_proc(self, adresse_s, fx=1., dt=1, crop_lims=None, maskers=None, window_size=32, overlap=16, search_area_size=32,save=True, s2n_thresh=1.2, bg_n_frames=None):
        
        frames = glob.glob(self.folder+'*.tiff')
        N = len(frames)-dt
        Ncpu = os.cpu_count()
        with Pool(processes=Ncpu) as pool:
            ite = []
            for i in range(Ncpu):
                indices = range(i,N,Ncpu*2)
                ite.append(frames(indices))
   	        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
   	        
            func = partial(self.analysis, dt, window_size, overlap, search_area_size, save, s2n_thresh, bg_n_frames)
            f = pool.map(func, ite)
    
                #get the image shape and the number of images processed by cpu from the output
            N=0
            for i in range(Ncpu):
                dim = f[i].shape
                N += dim[0]
            dimensions = (N,)+dim[1:] #assume all the images have the same shape
            flowfield = np.zeros(dimensions)
    
            for i in range(Ncpu):
                flowfield[i:N:Ncpu*2,...]=f[i]
                
            #savefolder = folder.rsplit("/", 1)[-1]+'/savedata'
            np.save(adresse_s+'_flowfield.npy',flowfield)
        self.m['U'] = flowfield
        return self
    
    def analysis(self,frames,dt , window_size, overlap, search_area_size, save, s2n_thresh, bg_n_frames):

        frame_a = self.load_image(frames[0])
        frame_b = self.load_image(frames[0]+dt)
        u,v = self.process_frame(frame_a,frame_b)
        dimensions = u.shape
        
        N = len(frames)-1
        U = np.zeros((N,)+dimensions+(2,))
            
        for i,ind in enumerate(frames):
            frame_a = self.load_image(ind)
            frame_b = self.load_image(ind+dt)
            
            u,v = self.process_frame(frame_a,frame_b)
            U[i,...,0]=u
            U[i,...,1]=v
        return U

    def load_image(self,filename):
        return "your favorite image loader"
    
    def process_frame(self,frame_a,frame_b,s2n_thresh=1.3):
        frame_a = frame_a.astype(np.int32)
        frame_b = frame_b.astype(np.int32)
    
        u,v,sig2noise = process.extended_search_area_piv( frame_a, frame_b, window_size=self.window_size, overlap=self.overlap, dt=1, search_area_size=self.search_area_size,sig2noise_method='peak2peak' )
        #u, v, mask = validation.sig2noise_val( u, v, sig2noise, threshold = s2n_thresh )
    
        return u,v
        
folder = ''
p = PIVDataProcessing(folder)
adresse_s = ''
p.analysis_multi_proc(adresse_s)

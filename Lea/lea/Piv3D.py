import lea.Mesure as m
import lea.pre_traitement as pre
import lea.danjruth.piv as p


from functools import partial
from multiprocessing import Process, Pool
import os
import numpy as np

class Piv3D(m.Mesure):
    def __init__(self, data, m={}):
        Mesure.__init__(self, data)
        self.m=m

    def analysis(self, parent_folder, cine_name, adresse_s, npy=None, fx=1., dt_origin="", \
                frame_diff="", crop_lims=None, maskers=None,\
                window_size=32, overlap=16, search_area_size=32,\
                save=True, s2n_thresh=1.2, bg_n_frames=None, a_frames=""):

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
        Ncpu = os.cpu_count()
        with Pool(processes=Ncpu) as pool:
            ite = []
            for i in range(frame_diff):
                ite.append(np.arange(i, self.data.nb_im-frame_diff, frame_diff))
	        #ite = [(0,25), (26, 50), (51, 75), (76, 100)]
            func = partial(self.analysis, parent_folder, cine_name, adresse_s, npy, fx, dt_origin,frame_diff, crop_lims, maskers, window_size, overlap, search_area_size, save, s2n_thresh, bg_n_frames)
            f = pool.map(func, ite)

            #get the image shape and the number of images processed by cpu from the output
            N=0
            for i in range(Ncpu):
                dim = f[i].shape
                N += dim[0]
            dimensions = (N,)+dim[1:] #assume all the images have the same shape
            flowfield = np.zeros(dimensions)

            for i in range(Ncpu):
                flowfield[i:N:Ncpu,...]=f[i]
            np.save(parent_folder+adresse_s+'_flowfield.npy',flowfield)
        self.m['U'] = flowfield
        return self


    def add_measurement(self, obj, name):
        setattr(self, obj, name)

    def get_name(self):
        return "PIV3D"

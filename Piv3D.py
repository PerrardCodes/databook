from Mesure import Mesure
import pre_traitement as pre
from danjruth.piv import *
import numpy as np

class Piv3D(Mesure):
    def __init__(self, data, m={}):
        Mesure.__init__(self, data)
        self.m=m

    def analysis(self, parent_folder, cine_name, adresse_s, npy=None, fx=1., dt_origin="", \
                frame_diff="", crop_lims=None, maskers=None,\
                window_size=32, overlap=16, search_area_size=32,\
                a_frames="", save=True, s2n_thresh=1.2, bg_n_frames=None):

        #Crée un objet processing présent dans : danjruth.piv
        processing = PIVDataProcessing(parent_folder, cine_name, name_for_save=adresse_s, dx=fx, dt_orig=dt_origin,\
                                        frame_diff=frame_diff, crop_lims=crop_lims, maskers=maskers,\
                                        window_size=window_size, overlap=16, search_area_size=search_area_size)
        #ajoute à m ce qu'il a dans l'objet processing
        self.m.update(processing.__dict__)
        #Si npy n'est pas donné en paramètre il lance l'analyse sur l'objet
        if(npy==None):
            processing.run_analysis(a_frames=a_frames, save=save, s2n_thresh=s2n_thresh, bg_n_frames=bg_n_frames)
            self.m['np'] = np.load(self.m["parent_folder"] + self.m["adresse_s"] + "_flowfield.npy")
        #Sinon il load juste le npy dans m
        else :
            self.m['np'] = np.load(npy)

    def load(self, npy):
        self.m['np'] = np.load(npy)

    def get_name(self):
        return "PIV3D"

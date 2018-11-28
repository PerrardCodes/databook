import lea.h5py_convert
import lea.Piv3D

def genere_manual(piv):
    parent_folder = '/media/stephane/'
    date = '20181018'

    cine_name = 'OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_rotator'

    #cine_name = 'OS/Documents and Settings/Stephane/Documents/Data_buffer/20181010/PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_4pumpsOn'

    #parent_folder = r'\\Mae-deike-lab3\c\Users\Luc Deike\data_comp3_C\180726\\'
    #parent_folder = r'F:\from_comp3_D\171203\\'
    #parent_folder = comps.cf('comp3d')+r'180803\\'


    data_folder = 'DATA/Experimental_data/Turbulence3d/'+date+'/raw'
    save_folder = data_folder+ '/Fluctuations/'

    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)

    # dx and dt for the cine file
    #dx = 3.3240951317E-05 # viewA
    #dx = 8.4191870904E-05 # viewB
    dx =  0.35E-03#7.3469357156E-05
    dt_orig = 1./31000

    crop_lims=None
    pre_constructed_masker = None
    t0 = 21
    a_frames = np.arange(t0,93000+t0,1)
    frame_diff = 31

    window_size = 32
    overlap = 16

    datafile = '/media/stephane/DATA/Experimental_data/Turbulence3d/20181018/raw_flowfield.npy'

    piv.analysis(parent_folder,cine_name, save_folder, npy=datafile, fx=dx, dt_origin=dt_orig, frame_diff=frame_diff, crop_lims=None, maskers=None, \
    window_size=window_size, overlap=overlap, search_area_size=window_size, a_frames=a_frames, save=True, s2n_thresh=1.2, bg_n_frames=None)

    return piv


#data = h5py_in_Data(ouverture_fichier("/media/stephane/DATA/Experimental_data/Turbulence3d/20181010/20181010_3_PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_rotator.hdf5"))

#mesure = Mesure(data)

#piv = Piv3D(data)
#print(piv.__dict__)


#piv = genere_manual(piv)
#print(piv.__dict__)

#mesure.add_measurement(piv)

#f = file_name_in_dir(mesure, "/media/stephane/DATA/Experimental_data/Turbulence3d/20181018")
#obj_in_h5py(mesure, f)
mesure = h5py_in_Mesure(ouverture_fichier("/home/ldupuy/Documents/Stage_Python_(2018)/new/Mesure_0_20181010_3_PIV3dscan_nikon50mm_f1kHz_A800mV_offsetm2800mV_rotator.hdf5"))
print(mesure.__dict__)
print(mesure.PIV3D.m['np'].shape)

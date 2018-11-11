import lea.h5py_convert

import glob

ref = "/media/stephane/DATA2/Experiments_Princeton/Balloon/Backlight/170808"
hdf = glob.glob(ref + "/*.hdf5")
for file in hdf :
    f = ouverture_fichier(file)
    data = h5py_in_Data(f)
    mesure = Mesure(data)
    c = Contour(data)
    contour = contour.contour_instant(xmin=200, xmax=950, ymin=120, ymax=690, x0=490, y0=285, adresse_s=ref, nb_im=250)
    mesure.add_measurement(c)
    f = file_name_in_dir(mesure, ref)
    obj_in_h5py(mesure, f)

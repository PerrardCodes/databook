"""
Creation de Mesure
-------------------
Création d'un objet Mesure ::

    import lea.data.Data as ldata
    import lea.mesure.Mesure as lmesure

    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    m = lmesure.Mesure(d)

Création d'un objet Bulles et lancement de la fonction :func:`lea.mesure.Bulles.bulle` ::

    import lea.data.Data as ldata
    import lea.mesure.Mesure as lmesure
    import lea.mesure.Bulles as lBulle
    import lea.hdf5.h5py_convert as lh5py

    folder = "/home/ldupuy/Documents/"
    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    m = lmesure.Mesure(d)
    b = lBulle.Bulle(d)
    m.add_measurement(b)

    f = lh5py.file_name_in_dir(m, folder)
    lh5py.obj_in_h5py(m, f)
    b.bulle(f, xmin=0, xmax=0, ymin=0, ymax=0, x0=0, y0=0, p_im = 0, nb_im=10)

Création d'un objet Contour, lancement d'une fonction de calcul et sauvegarde en HDF5 ::

    import lea.data.Data as ldata
    import lea.mesure.Mesure as lmesure
    import lea.mesure.Contour as lContour
    import lea.hdf5.h5py_convert as lh5py

    folder = "/home/ldupuy/Documents/"
    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    m = lmesure.Mesure(d)
    c = lContour.Contour(d)

    c.contour_instant(fx=0.0, fps=1.0, xmin=0, xmax=-1, ymin=0, ymax=-1, x0=0, y0=0, im_save=50, adresse_s=folder)

    m.add_measurement(c)

    f = lh5py.file_name_in_dir(m, folder)
    lh5py.obj_in_h5py(m, f)
    f.close()

Création d'un objet Piv3D, lancement d'une fonction de calcul et sauvegarde en HDF5 ::


    import lea.data.Data as ldata
    import lea.mesure.Mesure as lmesure
    import lea.mesure.Piv3D as lpiv
    import lea.hdf5.h5py_convert as lh5py

    folder = "/home/ldupuy/Documents/"
    cinename = "test1.cine"
    adresse_s = folder
    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    m = lmesure.Mesure(d)
    p = lpiv(d)

    p.analysis_multi_proc(folder, cinename, adresse_s)

    m.add_measurement(p)

    f = lh5py.file_name_in_dir(m, folder)
    lh5py.obj_in_h5py(m, f)
    f.close()


Création d'un Volume, lancement d'une fonction de calcul et sauvegarde en HDF5 ::

    import lea.data.Data as ldata
    import lea.mesure.Mesure as lmesure
    import lea.mesure.Volume as lvolume
    import lea.hdf5.h5py_convert as lh5py

    folder = "/home/ldupuy/Documents/"
    cinename = "test1.cine"
    adresse_s = folder
    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    m = lmesure.Mesure(d)
    v = lvolume.Volume(v)

    v = v.volume()
    v.save_volume(folder + "Volume/")

    m.add_measurement(v)

    f = lh5py.file_name_in_dir(m, folder)
    lh5py.obj_in_h5py(m, f)
    f.close()



"""

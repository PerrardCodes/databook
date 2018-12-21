"""
Creation des fichiers HDF5 Data recursivement
---------------------------------------------
Créer les fichiers HDF5 des fichiers cine/png/jpg ::

    import lea.hdf5.routine as routine

    datafolder = "/home/ldupuy/Documents/"
    savefolder = datafolder
    routine.convert_arbo(datafolder, savefolder)


Sauvegarde des données depuis un objet
---------------------------------------
Créer un fichier HDF5 depuis un objet ::

    #Je prend ici l'exemple d'un objet Data, mais cela marche aussi avec un objet Mesure ou un objet de votre création
    import lea.hdf5.h5py_convert as lh5py
    import lea.data.Data as ldata

    adresse = "/home/ldupuy/Documents/"
    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

    f = lh5py.file_name_in_dir(d, adresse)
    lh5py.obj_in_h5py(d, f)
    f.close()

Créer un fichier HDF5 depuis un sous-objet de Mesure ::

    import lea.hdf5.h5py_convert as lh5py
    import lea.mesure.Mesure as lmesure
    import lea.mesure.Volume as lvolume
    import lea.data.Data as ldata

    adresse = "/home/ldupuy/Documents/"

    d = ldata.Data(fichier, param, spec, date=date, heure, heure)
    m = lmesure.Mesure(d)
    v = lvolume.Volume(d)
    #Faire les actions qu'on veut sur les volumes.#
    m.add_measurement(v)
    f = lh5py.file_name_in_dir(m, adresse)
    lh5py.obj_in_h5py(m, f)
    f.close()

.. warning:: Mieux vaut sauvegarder le sous-objet de Mesure dans Mesure pour le hdf5

Récupération des données depuis un fichier HDF5
-----------------------------------------------
Récupération d'un objet Data depuis le HDF5 ::

    import lea.hdf5.h5py_convert as lh5py

    datafile="/home/ldupuy/Documents/20181220_1_test1.hdf5"
    f = lh5py.ouverture_fichier(datafile)
    d = lh5py.h5py_in_Data(f)
    f.close()

    #Pour tester si cela a bien marché

    print(d.__dict__)
    print(d.param.__dict__)

Récupération d'un objet Mesure depuis le HDF5 ::

    import lea.hdf5.h5py_convert as lh5py

    datafile="/home/ldupuy/Documents/Mesure_0_20181220_1_test1.hdf5"
    f = lh5py.ouverture_fichier(datafile)
    m = lh5py.h5py_in_Mesure(f)
    f.close()

    #Pour tester si cela a bien marché

    print(m.__dict__)
    print(m.d.__dict__)

Récupération d'un sous-objet de Mesure depuis le HDF5 ::

    import lea.hdf5.h5py_convert as lh5py

    datafile="/home/ldupuy/Documents/20181220_1_test1.hdf5"
    f = lh5py.ouverture_fichier(datafile)
    m = lh5py.h5py_in_Mesure(f)
    f.close()
    v = m.Volume

    #Pour tester si cela a bien marché

    print(m.__dict__)
    print(v.__dict__)



"""

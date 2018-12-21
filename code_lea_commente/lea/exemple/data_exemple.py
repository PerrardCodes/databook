"""
Creation de Data
-----------------
How to create a data object ::

    import lea.data.Data as ldata

    #Create a data object from a cinefile
    fichier = "/home/ldupuy/Documents/test1.cine"
    param = "/home/ldupuy/Documents/test1_param.txt"
    #On met spec à param pour avoir les informations dans le titre
    spec = param
    date = "20181220"
    heure = "0000"

    d = ldata.Data(fichier, param, spec, date=date, heure=heure)

Import de Data
---------------
How to import a data object from an hdf5 files::

    import lea.data.Data as ldata
    import lea.hdf5.h5py_convert as lh5py

    datafile = "/home/ldupuy/Documents/20181220_1_test1.hdf5"
    f = lh5py.ouverture_fichier(datafile)
    d = lh5py.h5py_in_Data(f)
"""

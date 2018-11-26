# -*- coding: utf-8 -*-
import lea.data.Data as ldata
import lea.data.Param as lparam

import lea.mesure.Piv3D as lpiv3d
import lea.mesure.Mesure as lmesure
import lea.mesure.Volume as lvolume

import lea.hdf5.h5py_convert as h5pylea

import stephane.analysis.cdata as cdata
import numpy as np

import os
import glob
import time

import sys

def os_base():
    if sys.platform=='win32':
        base = 'F:'
    if sys.platform=='linux':    
        base = '/media/stephane/DATA'
    if sys.platform=='darwin':
        base = '/Volumes/Diderot/DATA_MSC_Jamin/'    
        base = '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/'#'/Volumes/Diderot/DATA_Princeton_November2018/'
    return base

def ask(folder,ext='*.cine'):
    l=glob.glob(folder+ext)
    if len(l)>1:
        for i,name in enumerate(l):
            print(str(i)+' : '+os.path.basename(name))
    
        s = input()
        try:
            i = int(s)
        except:
            print("cannot be converted to an integer")
        return l[i]
    else:
        if len(l)==1:
            return l[0]
        else:
            print('no file found in '+folder)
            return None
            
    
def nancount(data):
    print(data.shape)
    Nnan = np.sum(np.ndarray.flatten(np.isnan(data)))
    N = np.prod(data.shape)
    print('Ratio nan :' +str(Nnan/N))
    print('nan number :'+str(Nnan))
### CHarge un fichier Data## .
### CHarge un fichier Data## .

date = "20181126"
savefolder = '/Users/stephane/Documents/Postdoc_Princeton/Piv3d/'+date

base = os_base()
folder = base+date+'/'
cinefile = ask(folder)
#cinefile = None
if cinefile is not None:
    datafile = ask(folder,ext='/20*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')
else:
    datafile = ask(folder,ext='20*'+'.hdf5')

#paramfile = ask(folder,ext='*.txt')
if cinefile is not None:
    mesurefile = ask(folder,ext='/Mesure*'+os.path.basename(cinefile).rsplit(".",1)[0]+'.hdf5')
else:
    mesurefile = ask(folder,ext='Mesure*'+'.hdf5')
    
print(datafile)
print(mesurefile)

#cree un data à partir d'un fichier hdf5 existant
f = h5pylea.ouverture_fichier(datafile)
Data = h5pylea.h5py_in_Data(f)
f.close()

#cree une mesure à partir d'un fichier hdf5 existant
f = h5pylea.ouverture_fichier(mesurefile)
M = h5pylea.h5py_in_Mesure(f)
f.close()#ouvrir un data à partir d'un hdf5 existant

##update le fichier data
#M.data = Data
if 'U' in M.PIV3D.m.keys():
    print('U format')

    print(M.PIV3D.m['U'].shape)
if 'np' in M.PIV3D.m.keys():
    print('np format')
    print(M.PIV3D.m['np'].shape)
    
    # rename the field
    M.PIV3D.m['U']=M.PIV3D.m['np']
    M.PIV3D.m.pop('np')

# update the data file
#M.data = Data
M.PIV3D.data = M.data

#stophere
#M.PIV3d.m['np']

#sauvegarde la mesure
f = h5pylea.file_name_in_dir(M, savefolder)
h5pylea.obj_in_h5py(M,f)
f.close()


# create a shortcut
piv = M.PIV3D
ff = piv.m['U']

M.data.param.f = int(M.data.param.galvo[:-1])*1000
M.data.param.fps = int(M.data.param.fps[:-1])*1000
M.data.param.fx = float(M.data.param.fx)
print(M.data.param.fx)

#convert 2d to 3d data
(Nt,Nx,Ny,Nc) = ff.shape
frame_diff = int(M.data.param.fps // M.data.param.f)
print(frame_diff)

start = 4#int(M.data.param.startV)
Nt = (Nt-start)//frame_diff
Nz = frame_diff
end = 4+Nz//2#int(M.data.param.endV)

#ff=ff[:,9:25,...]
#(start,end) = v.m['instantV'][0]
#ff=ff[:,start:end,...]
ff = np.reshape(ff[start:Nt*Nz+start,...],(Nt,Nz,Nx,Ny,Nc))
ff[...,1] = -ff[...,1] #reverse sign of horizontal component
ff = ff[:,:Nz//2,...]

print(ff.shape)


# generate time axis
dz = float(piv.data.param.l_c)/frame_diff*2
print(dz)

piv.m['overlap'] = 16
dx = float(M.data.param.fx*piv.m['overlap'])
print(dx)

#generate axis
(Nz,Nx,Ny,Nc) = ff[0,...].shape
#mean_flow = np.transpose(mean_flow,(1,2,0,3))

print(dx)
print(Nx)

x = np.arange(-(Nx-1)/2,(Nx-1)/2+1)*dx
y = np.arange(-(Ny-1)/2,(Ny-1)/2+1)*dx
z = np.arange(-Nz/2,Nz/2)*dz-2

#invariance by rotation in the plane (x,z)
[X,Z,Y] = np.meshgrid(x,z,y)

#generate space axis
piv.m['x'] = x
piv.m['y'] = y
piv.m['z'] = z

#generate time axis
ft = frame_diff/piv.data.param.fps
print(ft)
piv.m['ft'] =  ft
piv.m['t'] = np.arange(0,Nt*ft,ft)


# remove nan from the edges
print(nancount(ff))
ff = ff[...,1:-1,1:-1,:]
print(nancount(ff))

# remove nan in the bulk (only few of them should be present)
Nt = ff.shape[0]
for i in range(Nt):
    for j in range(2):
        data = np.squeeze(ff[i,...,j])
        indices = np.where(np.isnan(data))
        (t0,t1,t2) = indices
        for tup in zip(t0,t1,t2):
            data = cdata.replace_nan(data,tup)
        ff[i,...,j]=data
print(nancount(ff))


#compute mean_flow
mean_flow = np.nanmean(ff,axis=0)
mean_flow_speed = np.linalg.norm(mean_flow,axis=2)
mean_speed = np.nanmean( np.sqrt(ff[...,0]**2 + ff[...,1]**2 ), axis=0)
fluc = ff - mean_flow    
u_rms = np.sqrt(np.nanmean(fluc[...,0]**2+fluc[...,1]**2 ,axis=0) )

piv.m['mean_flow'] = mean_flow
#piv.m['fluc'] = fluc
piv.m['u_rms'] = u_rms
piv.m['U'] = ff

#sauvegarde la mesure, après reconstitution des volumes
f = h5pylea.file_name_in_dir(M, savefolder)
h5pylea.obj_in_h5py(M,f)
f.close()

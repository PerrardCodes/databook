##Code déjà existant##
import display.graphes as graphes
##Librairie

import Mesure
import  numpy as np
import scipy.interpolate as interp
import pandas as pd
import math
import matplotlib.pyplot as plt


class Contour(Mesure) :
	def __init__(self, data):
		super().__init__(self, data)


	#Fonction de mesure
def contour(im, Dic, display=True, save="test.png"):
	x = Dic['x']
	y = Dic['y']
	xc = Dic['xcf']
	yc = Dic['ycf']
	nr = Dic['nr']
	N = Dic['N']
	rmin = Dic['rmin']
	rmax = Dic['rmax']
	X,Y = np.meshgrid(x,y)

	thetamin = Dic['thetamin']
	thetamax = Dic['thetamax']
	theta = np.concatenate((np.linspace(-thetamin,np.pi/2-thetamax, N/2),\
							np.linspace(np.pi/2+thetamax,np.pi+thetamin,N/2)))
	grad = np.sum(np.asarray(np.gradient(im))**2, axis=0)
	f = interp.interp2d(x,y,grad)

	r = np.linspace(rmin, rmax, nr)

	R0 = np.zeros(N)
	for i, t in enumerate(theta):
		xi = r*np.cos(t)+xc
		yi = r*np.sin(t)+yc
		p = [f(xx,yy) for xx, yy, in zip(xi,yi)]
		R0[i] = r[np.argmax(p)]

	D = {}
	D['xf'] = (R0*np.cos(theta)+xc)
	D['yf'] = (R0*np.sin(theta)+yc)
	DF = pd.DataFrame(data=D)
	DF = lissage(DF)
	len(DF['xf'])
	if display:
		graphes.color_plot(X, Y, im)
		graphes.graph([0],[0], label='rx')
		graphes.graph([xc], [yc], label='ro')
		graphes.graph(DF['xf'],DF['yf'], label='r.', fignum=1)
		graphes.graph(np.max(r)*np.cos(theta)+xc,np.max(r)*np.sin(theta)+yc,label='w--',fignum=1)
		graphes.graph(np.min(r)*np.cos(theta)+xc,np.min(r)*np.sin(theta)+yc,label='w--',fignum=1)
		plt.savefig(save)
		plt.close()
	return DF

def lissage(DF):
	for i in range(1, len(DF['yf'])-1):
		d_prec = math.sqrt((DF['xf'][i-1]-DF['xf'][i])**2+ \
						   (DF['yf'][i-1]-DF['yf'][i])**2)
		d_suiv = math.sqrt((DF['xf'][i]-DF['xf'][i+1])**2+ \
						   (DF['yf'][i]-DF['yf'][i+1])**2)
		if(d_prec > 5*0.3 and d_suiv > 5*0.3):
			DF['xf'][i] = (DF['xf'][i-1]+DF['xf'][i+1])/2
			DF['yf'][i] = (DF['yf'][i-1]+DF['yf'][i+1])/2
	return DF


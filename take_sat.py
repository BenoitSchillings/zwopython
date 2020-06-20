import zmq
import numpy as np
import time
import cv2
import astropy
from astropy.io import fits
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB
import os
import skyx
import datetime
from coo import *


context = zmq.Context()
app = QtGui.QApplication([])

#--------------------------------------------------------

def pool_get(socket):
	while(True):
		count = socket.poll(timeout=50)
		app.processEvents()
		if (count != 0):
			obj = socket.recv_pyobj()
			return obj


#--------------------------------------------------------


def get(socket, params):
	socket.send_pyobj(params)

	obj = pool_get(socket)
	return obj

#--------------------------------------------------------

zwocam = context.socket(zmq.REQ)
zwocam.connect("tcp://localhost:5555")

#--------------------------------------------------------

def status(pos, image, legend, value):
	pos = 20 + pos * 25
    
	cv2.rectangle(image, (20, pos), (20+200, pos + 20), (0.0, 0.0, 0.0), -1)
	cv2.rectangle(image, (20, pos), (20+200, pos + 20), (1.0, 1.0, 1.0), 1)

	cv2.putText(image, legend, (30, pos + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1.0, 1.0, 1.0)) 
	size = cv2.getTextSize(value, fontScale = 0.5, fontFace = cv2.FONT_HERSHEY_SIMPLEX, thickness=1)
	
	cv2.putText(image, value, (200  - size[0][0], pos + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1.0, 1.0, 1.0)) 

#--------------------------------------------------------
import argparse
#--------------------------------------------------------

def bin(a):
	return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

#--------------------------------------------------------

def crop_center(img,crop):
    y,x = img.shape
    startx = x//2 - crop//2
    starty = y//2 - crop//2    
    return img[starty:starty+crop, startx:startx+crop]

#--------------------------------------------------------


frame = 0

def mainloop(args):

	sky = skyx.sky6RASCOMTele()
	sky.Connect()


	p0 = sky.GetRaDec()


	print(args)
	frame = 0
	viewer = pg.image(np.zeros((10,10)))
	center_viewer = pg.image(np.zeros((10,10)))
	filename = args.filename + str(int(time.time()))
	dirname = args.filename


	flat = fits.getdata("flat_100_50.fits", ext=0)
	bias = fits.getdata("bias.fits", ext=0)
	dark = fits.getdata("dark.fits", ext=0)

	#flat = flat - bias
	flat = flat / flat.mean()


	if (not os.path.isdir(dirname)):
		os.mkdir(dirname)

	img_number = 0

	while(img_number < args.count):
		img_number = img_number + 1

		now = datetime.datetime.now(datetime.timezone.utc)
		img = get(zwocam, {'exposure': args.exp, 'gain':args.gain, 'bin':args.bin})
		img = img - dark
		img = img / flat

		img = img / 2.0

		if (args.filename != ''):
			hdr = fits.header.Header()
			ra_string = cvt_ra(float(p0[0]))
			dec_string = cvt_dec(float(p0[1]))

			hdr['RA'] = ra_string 
			hdr['DEC'] = dec_string

			file_str = dirname + "/" + filename + "_" + str(frame) + ".fits"
			fits.writeto(file_str, img.astype(np.uint16), hdr, overwrite=True)
			fits.setval(file_str,'DATE',value=str(now.astimezone().isoformat())[:-7] )
			fits.setval(file_str,'DATE-OBS',value=str(now.astimezone().isoformat())[:-7] )
			fits.setval(file_str,'EXPTIME',value=args.exp)

		frame = frame + 1
		vmin = np.min(img)
		vmax = np.max(img)


		viewer.setImage(np.swapaxes(bin(img.astype(float)), 0, 1))
		center_viewer.setImage(crop_center(np.swapaxes(img, 0, 1), 768))



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--filename", type=str, default = '', help="generic file name")
	parser.add_argument("-exp", type=float, default = 1.0, help="exposure in seconds (default 1.0)")
	parser.add_argument("-gain", "--gain", type=int, default = 200, help="camera gain (default 200)")
	parser.add_argument("-bin", "--bin", type=int, default = 1, help="camera binning (default 1-6)")
	parser.add_argument("-guide", "--guide", type=int, default = 0, help="frame per guide cycle (0 to disable)")
	parser.add_argument("-count", "--count", type=int, default = 100, help="number of frames to capture")
	args = parser.parse_args()

	mainloop(args)



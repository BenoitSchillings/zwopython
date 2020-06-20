import zmq
import numpy as np
import time
import cv2
import astropy
from astropy.io import fits
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB



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

def bin(arr, new_shape):
	return arr

#--------------------------------------------------------


frame = 0

def mainloop(args):
	print(args)
	frame = 0
	viewer = pg.image(np.zeros((10,10)))

	while(frame < args.count):
		img = get(zwocam, {'exposure': args.exp, 'gain':args.gain, 'bin':args.bin})

		vmean = np.mean(img)
		vmax = np.max(img)
		if (vmean != vmax):
			viewer.setImage(bin(np.swapaxes(img, 0, 1), 3))

		print(vmean)
		if (vmean < 24000):
			frame = frame + 1
			if (frame == 1):
				flat_sum = img * 1.0
			else:
				flat_sum = flat_sum + img

	flat_sum = flat_sum / (frame*1.0)
	if (args.filename != ''):
		hdr = fits.header.Header()
		fits.writeto(args.filename + str(frame) + ".fits", flat_sum.astype(np.float32), hdr, overwrite=True)
		


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--filename", type=str, default = 'bias_c4_', help="generic file name")
	parser.add_argument("-exp", "--exp", type=float, default = 0.00001, help="exposure in seconds (default 1.0)")
	parser.add_argument("-gain", "--gain", type=int, default = 350, help="camera gain (default 200)")
	parser.add_argument("-bin", "--bin", type=int, default = 1, help="camera binning (default 1-6)")
	parser.add_argument("-guide", "--guide", type=int, default = 0, help="frame per guide cycle (0 to disable)")
	parser.add_argument("-count", "--count", type=int, default = 550, help="number of frames to capture")
	args = parser.parse_args()

	mainloop(args)



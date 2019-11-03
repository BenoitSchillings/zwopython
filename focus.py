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

def bin(a, bin_factor):
	shape = a.shape
	s0 = a.shape[0] // bin_factor
	s1 = a.shape[1] // bin_factor
	sh = s0,a.shape[0]//s0,s1,a.shape[1]//s1
	return a.reshape(sh).sum(-1).sum(1)



#--------------------------------------------------------


frame = 0

def mainloop(args):
	print(args)
	frame = 0
	center_viewer = pg.image(np.zeros((10,10)))

	while(True):
		img = get(zwocam, {'exposure': args.exp, 'gain':args.gain, 'bin':1, 'crop':args.crop})
		frame = frame + 1
		vmin = np.min(img)
		vmax = np.max(img)
		print("max ", vmax)


		center_viewer.setImage(np.swapaxes(img, 0, 1))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-exp", "--exp", type=float, default = 1.0, help="exposure in seconds (default 1.0)")
	parser.add_argument("-gain", "--gain", type=int, default = 200, help="camera gain (default 200)")
	parser.add_argument("-count", "--count", type=int, default = 1000, help="number of frames to capture")
	parser.add_argument("-crop", "--crop", type=float, default = 0.25, help="number of frames to capture")
	args = parser.parse_args()

	mainloop(args)



import zmq
import numpy as np
import time
import cv2
import astropy
from astropy.io import fits
import argparse


context = zmq.Context()

#--------------------------------------------------------

def pool_get(socket):
	while(True):
		count = socket.poll(timeout=300)
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
def bin(a):
	return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

frame = 0

parser = argparse.ArgumentParser()

parser.add_argument("-exp", "--exp", type=float, default = 0.1, help="exposure in seconds (default 0.1)")
parser.add_argument("-gain", "--gain", type=int, default = 300, help="camera gain (default 300)")
parser.add_argument("-bin", "--bin", type=int, default = 4, help="binning (default 4)")

args = parser.parse_args()



while(True):
	img = get(zwocam, {'exposure':args.exp, 'gain':args.gain, 'bin':args.bin})
	frame = frame + 1

	bg = np.percentile(img, 0)
	print(np.mean(img))
	
	img = img / 65535.0
	img = bin(img)
	img = img - np.percentile(img, 1)
	max = np.percentile(img, 90) * 2.0
	img = img / max


	cv2.imshow("image", img)
	key = cv2.waitKey(1)
	print(key)
	if (key == 27):
		camera.close()
		sys.exit(0)



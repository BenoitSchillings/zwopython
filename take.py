import zmq
import numpy as np
import time
import cv2
import astropy
from astropy.io import fits



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

frame = 0
while(True):
	img = get(zwocam, {'exposure':15.0, 'gain':200, 'bin':1})
	hdr = fits.header.Header()
	fits.writeto("data" + str(frame) + ".fits", img, hdr, overwrite=True)
	frame = frame + 1

	print(img)
	img = img / 65535.0
	img = img - np.percentile(img, 0)
	max = np.percentile(img, 90) * 2.0
	img = img / max


	cv2.imshow("image", img)
	key = cv2.waitKey(1)
	print(key)
	if (key == 27):
		camera.close()
		sys.exit(0)



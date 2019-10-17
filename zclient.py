import zmq
import numpy as np
import time
import cv2

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
# for an image of input size (x,y)
# return a corner/center view


def crop_collimation_boxes(image):
	size_x = image.shape[1]
	size_y = image.shape[0]
	print(size_x, size_y)

	box_x = size_x // 8
	box_y = size_y // 8

	out = np.ones((box_y * 3, box_x * 3), dtype=float)

#x and y center minus half box

	cx = size_x // 2 - (box_x//2)
	cy = size_y // 2 - (box_y//2)

	out[box_y*0:box_y*1, 0:box_x] = image[0:box_y, 0: box_x]									#topleft
	out[box_y*1:box_y*2, 0:box_x] = image[box_y*1:box_y*2, 0: box_x]							#midleft
	out[box_y*2:box_y*3, 0:box_x] = image[box_y*2:box_y*3, 0: box_x]							#botleft

	out[box_y*0:box_y*1, box_x:box_x*2] = image[0:box_y, cx: cx + box_x]						#topmid
	out[box_y*1:box_y*2, box_x:box_x*2] = image[cy:cy+box_y, cx: cx + box_x]					#midmid
	out[box_y*2:box_y*3, box_x:box_x*2] = image[size_y-box_y:size_y, cx: cx + box_x]			#bottom-mid

	out[box_y*0:box_y*1, box_x*2:box_x*3] = image[0:box_y, size_x - box_x: size_x]				#topright
	out[box_y*1:box_y*2, box_x*2:box_x*3] = image[cy:cy+box_y, size_x - box_x: size_x]			#midright
	out[box_y*2:box_y*3, box_x*2:box_x*3] = image[size_y-box_y:size_y, size_x - box_x: size_x]	#bottom-right

	out[box_y:(box_y) + 1, :] = 1.0
	out[box_y*2:(box_y*2) + 1, :] = 1.0
	out[:, box_x:box_x+1] = 1.0
	out[:, box_x*2:(box_x*2)+1] = 1.0

	return out

#--------------------------------------------------------


zwocam = context.socket(zmq.REQ)
zwocam.connect("tcp://localhost:5555")

#--------------------------------------------------------

while(True):
	img = get(zwocam, {'exposure':0.001, 'gain':10, 'bin':4})
	img = img / 65535.0
	img = img - np.percentile(img, 0)
	max = np.percentile(img, 90)
	img = img / max

	img_crop = crop_collimation_boxes(img)


	cv2.imshow("image", img_crop)
	key = cv2.waitKey(1)
	print(key)
	if (key == 27):
		camera.close()
		sys.exit(0)



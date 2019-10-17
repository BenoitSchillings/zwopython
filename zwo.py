import argparse
import os
import sys
import time
import zwoasi as asi
import cv2
import numpy as np
import math

#----------------------------------------------------------------------

def init_cam():
	asi.init(".\\ASICamera2.dll")

	num_cameras = asi.get_num_cameras()
	if num_cameras == 0:
		print('No cameras found')
		sys.exit(0)

	cameras_found = asi.list_cameras()  # Models names of the connected cameras
	camera_id = 0

	camera = asi.Camera(camera_id)


	camera.disable_dark_subtract()
	camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, 60)

	camera.set_control_value(asi.ASI_GAIN, 20)
	camera.set_control_value(asi.ASI_EXPOSURE, int(0.00001*1000000))
	camera.set_control_value(asi.ASI_GAMMA, 50)
	camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_TARGET_TEMP, -10)
	camera.set_control_value(asi.ASI_COOLER_ON, 1)
	camera.set_control_value(asi.ASI_HARDWARE_BIN, 1)
	camera.set_roi(bins=2)
	return camera

#----------------------------------------------------------------------

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

	out[box_y*0:box_y*1, 0:box_x] = image[0:box_y, 0: box_x]					#topleft
	out[box_y*1:box_y*2, 0:box_x] = image[box_y*1:box_y*2, 0: box_x]				#midleft
	out[box_y*2:box_y*3, 0:box_x] = image[box_y*2:box_y*3, 0: box_x]				#botleft

	out[box_y*0:box_y*1, box_x:box_x*2] = image[0:box_y, cx: cx + box_x]				#topmid
	out[box_y*1:box_y*2, box_x:box_x*2] = image[cy:cy+box_y, cx: cx + box_x]			#midmid
	out[box_y*2:box_y*3, box_x:box_x*2] = image[size_y-box_y:size_y, cx: cx + box_x]		#bottom-mid

	out[box_y*0:box_y*1, box_x*2:box_x*3] = image[0:box_y, size_x - box_x: size_x]			#topright
	out[box_y*1:box_y*2, box_x*2:box_x*3] = image[cy:cy+box_y, size_x - box_x: size_x]		#midright
	out[box_y*2:box_y*3, box_x*2:box_x*3] = image[size_y-box_y:size_y, size_x - box_x: size_x]	#bottom-right

	out[box_y:(box_y) + 1, :] = 1.0
	out[box_y*2:(box_y*2) + 1, :] = 1.0
	out[:, box_x:box_x+1] = 1.0
	out[:, box_x*2:(box_x*2)+1] = 1.0
	return out


camera = init_cam()

camera.set_image_type(asi.ASI_IMG_RAW16)

for i in range(100000):
	print(camera.get_control_value(asi.ASI_TEMPERATURE))
	time.sleep(0.1)
	img = camera.capture()
	#print(img)
	#img = np.fromfunction(lambda i, j: np.sin(i/20.0) + np.cos(j/18.0), img.shape, dtype=float)
	img = img / 65535.0
	img = img - np.percentile(img, 1)
	max = np.percentile(img, 90)
	img = img / max

	img_crop = crop_collimation_boxes(img)
	#img_crop = img

	cv2.imshow("image", img_crop)
	key = cv2.waitKey(1)
	print(key)
	if (key == 27):
		camera.close()
		sys.exit(0)







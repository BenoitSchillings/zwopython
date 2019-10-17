import argparse
import os
import sys
import time
import zwoasi as asi
import cv2
import numpy as np


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

	camera.set_control_value(asi.ASI_GAIN, 150)
	camera.set_control_value(asi.ASI_EXPOSURE, int(0.1*1000000))
	camera.set_control_value(asi.ASI_GAMMA, 50)
	camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_TARGET_TEMP, -10)
	camera.set_control_value(asi.ASI_COOLER_ON, 1)
	camera.set_control_value(asi.ASI_HARDWARE_BIN, 1)
	camera.set_roi(bins=4)
	return camera

#----------------------------------------------------------------------


camera = init_cam()

camera.set_image_type(asi.ASI_IMG_RAW16)

for i in range(100):
	print(camera.get_control_value(asi.ASI_TEMPERATURE))
	time.sleep(1)
	img = camera.capture()
	img = img / 65535.0
	print(img)
	img = img - np.percentile(img, 1)
	max = np.percentile(img, 80)

	cv2.imshow("image", img/max)
	cv2.waitKey(1)






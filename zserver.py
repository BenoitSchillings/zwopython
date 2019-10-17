import time
import zmq
import numpy as np
import zwoasi as asi


#-------------------------------------------------------


def pool_status():
	global acamera

	print("running")


#-------------------------------------------------------

def pool_get(socket):
	while(True):
		count = socket.poll(timeout=300)
		if (count != 0):
			obj = socket.recv_pyobj()
			return obj

		pool_status()

#-------------------------------------------------------


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
	camera.set_image_type(asi.ASI_IMG_RAW16)

	return camera

#-------------------------------------------------------

def set_params(camera, params):
	for param in params:
		value = params[param]
		param = param.upper()

		if (param == 'EXPOSURE'):
			camera.set_control_value(asi.ASI_EXPOSURE, int(value*1000000))
		if (param == 'GAIN'):
			camera.set_control_value(asi.ASI_GAIN, int(value))
		if (param == 'BIN'):
			camera.set_roi(bins=int(value))
		

#-------------------------------------------------------

def server(socket, camera):
	while True:
		obj = pool_get(socket)
		print("Received object", obj)
		set_params(camera, obj)
		img = camera.capture()
		socket.send_pyobj(img)


#-------------------------------------------------------

acamera = init_cam()
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
server(socket, acamera)


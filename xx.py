import time
import zmq
import numpy as np
import zwoasi as asi


#-------------------------------------------------------


def pool_status():
	global acamera

	#print("running")


#-------------------------------------------------------

def pool_get(socket):
	while(True):
		count = socket.poll(timeout=100)
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
	print("found camera")

	camera.disable_dark_subtract()
	camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, 40)

	camera.set_control_value(asi.ASI_GAIN, 20)
	camera.set_control_value(asi.ASI_EXPOSURE, int(0.00001*1000000))
	camera.set_control_value(asi.ASI_GAMMA, 50)
	camera.set_control_value(asi.ASI_BRIGHTNESS, 85)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_FLIP, 0)
	camera.set_control_value(asi.ASI_HIGH_SPEED_MODE, 0)
	camera.set_control_value(asi.ASI_HARDWARE_BIN, 1)
	camera.set_roi(bins=3)
	camera.set_image_type(asi.ASI_IMG_RAW16)
	print("ready")
	return camera

#-------------------------------------------------------

def set_params(camera, params):
	def clip8(value):
		value = value - (value % 8)
		return value


	for param in params:
		value = params[param]
		param = param.upper()

		if (param == 'EXPOSURE'):
			camera.set_control_value(asi.ASI_EXPOSURE, int(value*1000000))
		if (param == 'GAIN'):
			camera.set_control_value(asi.ASI_GAIN, int(value))
		if (param == 'BIN'):
			print("bin", value)
			camera.set_roi(bins=int(value))
		if (param == 'CROP'):
			vsize = 6388#3520
			hsize = 9576#4656
			vsize = 1520
			hsize = 1656
			dv = int(vsize * value)
			dh = int(hsize * value)
			dv = dv // 2
			dh = dh // 2
			camera.set_roi(start_x=clip8(hsize//2 - dh), start_y=clip8(vsize//2 - dv), width=clip8(dh*2), height=clip8(dv*2))
		

#-------------------------------------------------------

def server(socket, camera):
	while True:
		obj = pool_get(socket)
		print("Received object", obj)
		set_params(camera, obj)

		has_pic = False
		print("temp ", camera.get_control_value(asi.ASI_TEMPERATURE)[0]/10.0)

		while(not has_pic):
			try:
				img = camera.capture()
				has_pic = True
			except:
				print("failed capture")
				has_pic = False
	

		socket.send_pyobj(img)


#-------------------------------------------------------

print("server")
acamera = init_cam()
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
server(socket, acamera)


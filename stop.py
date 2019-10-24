import skyx
import time

sky = skyx.sky6RASCOMTele()
sky.Connect()

for i in range(11000):
	print(i, sky.GetRaDec())
	time.sleep(1)
	
sky.stop()

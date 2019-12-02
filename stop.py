import skyx
import time

sky = skyx.sky6RASCOMTele()
sky.Connect()

sky.stop()

import skyx
import time
import argparse
import random



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-ra", type=float, default = 1.0, help="ra rate")
	parser.add_argument("-dec", type=float, default = 1.0, help="dec rate")
	args = parser.parse_args()
	print(args)

	sky = skyx.sky6RASCOMTele()
	sky.Connect()

	sky.rate(args.ra, args.dec)

	p0 = sky.GetRaDec()
	count = 0.0
	for i in range(14000):
		time.sleep(1)
		p1 = sky.GetRaDec()
		count = count + 1.0
		if (i % 10 == 0):
			print( (float(p0[0]) - float(p1[0])) / (count/15.0), (float(p0[1]) - float(p1[1])) / count)
			print( 15.0*3600.0*(float(p0[0]) - float(p1[0])), 3600.0*(float(p0[1]) - float(p1[1])))
		if (i % 1000 == 0 and i >= 1000):
			print("goto ")
			dx = random.random() - 0.5
			dy = random.random() - 0.5
			sky.bump(self, dx/4.0, dy/4.0)
   
			#sky.goto(float(p0[0]) + dx, float(p0[1]) + dy)


	sky.stop()


import skyx
import time
import argparse




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
	while(1):
		time.sleep(3)
		p1 = sky.GetRaDec()
		count = count + 1.0
		print( (float(p0[0]) - float(p1[0])) / count, (float(p0[1]) - float(p1[1])) / count)


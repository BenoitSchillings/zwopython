import numpy as np
import math

def cvt_dec(value):
	v0 = value
	value = np.abs(value)
	deg = int(value)
	
	value = value - deg
	value = value * 60.0

	min = int(value)

	value = value - min

	value = value * 60.0

	sec = value

	if (v0 > 0):
		dec_str = '+'
	else:
		dec_str = '-'

	dec_str = dec_str + str(deg) + ":" + str(min) + ":" + str(round(sec,3))

	return dec_str



def cvt_ra(value):
	hours = int(value)
	
	value = value - hours
	value = value * 60.0

	min = int(value)

	value = value - min

	value = value * 60.0

	sec = value



	ra_str = str(hours) + ":" + str(min) + ":" + str(round(sec,3))

	return ra_str







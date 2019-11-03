import numpy as np
import time
import cv2
import astropy
import sys
from astropy.io import fits
import image_registration
from glob import glob

#--------------------------------------------------------

def crop_center(img,crop):
    y,x = img.shape
    startx = x//2 - crop//2
    starty = y//2 - crop//2    
    return img[starty:starty+crop, startx:startx+crop]


#--------------------------------------------------------

def sharpness(img):
	v1 = np.sum(np.diff(img, axis=0)**2)
	v2 = np.sum(np.diff(img, axis=1)**2)

	return(v1+v2)


#--------------------------------------------------------

file = sys.argv[1]

def fn(idx):
	return file + str(idx) + ".fits" 



frame = 0


for frame in range(0,400, 3):
	img1 = fits.getdata(fn(frame), ext=0)
	img2 = fits.getdata(fn(frame+1), ext=0)
	img3 = fits.getdata(fn(frame+2), ext=0)
	#img = img - dark
	#img = img / flat

	yoff,xoff = image_registration.cross_correlation_shifts(crop_center(img2, 1024), crop_center(img1, 1024))
	s2 = np.roll(np.roll(img2,int(yoff),1),int(xoff),0)
	yoff,xoff = image_registration.cross_correlation_shifts(crop_center(img3, 1024), crop_center(img1, 1024))
	s3 = np.roll(np.roll(img3,int(yoff),1),int(xoff),0)

	output = np.median([img1, s2, s3], axis=0)
	hdr = fits.header.Header()
	fits.writeto("out" + str(frame//3) + ".fits", output.astype(np.float32), hdr, overwrite=True)
	print(frame//3, yoff, xoff)
	#print(frame ," of " ,len(files), yoff,xoff)
	output = output / 65535.0
	output = output - np.percentile(output, 3)
	max = np.percentile(output, 90) * 2.0
	output = output / max

	cv2.imshow("image", crop_center(output, 1024))
	key = cv2.waitKey(1)

cv2.waitKey(0)


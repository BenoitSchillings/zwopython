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

files = glob(sys.argv[1])

def fn(idx):
	return files[idx]


frame = 0
img0 = fits.getdata(fn(0), ext=0)
sum = np.empty_like(img0, dtype=float)


for frame in range(0,len(files)):
	img = fits.getdata(fn(frame), ext=0)
	frame = frame + 1
	yoff,xoff = image_registration.cross_correlation_shifts(crop_center(img, 1024), crop_center(img0, 1024))
	#shifted = image_registration.fft_tools.shift.shiftnd(img, (xoff,yoff))
	shifted = np.roll(np.roll(img,int(yoff),1),int(xoff),0)
	sum +=  shifted
	print(yoff,xoff)
	img = sum / 65535.0
	img = img - np.percentile(img, 3)
	max = np.percentile(img, 90) * 2.0
	img = img / max


	cv2.imshow("image", crop_center(img, 1024))
	key = cv2.waitKey(1)


hdr = fits.header.Header()
fits.writeto("stack.fits", img.astype(np.float32), hdr, overwrite=True)



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

def bin(a):
	return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

#--------------------------------------------------------

files = glob(sys.argv[1])

def fn(idx):
	return files[idx]


frame = 0
img0 = fits.getdata(fn(20), ext=0) * 2.0
sum = np.empty_like(img0, dtype=float)

flat = fits.getdata("flat.fits", ext=0)
bias = fits.getdata("bias.fits", ext=0)
dark = fits.getdata("dark.fits", ext=0)

print("dark ", np.mean(dark))
print("bias ", np.mean(bias))
print("flat ", np.mean(flat))

flat = flat - bias

flat = flat / np.mean(flat)

img0 = img0 - dark
#img0 = img0 / flat
sum = img0

ref_norm = np.percentile(img0, 20)

for frame in range(0,len(files)):
	img = fits.getdata(fn(frame), ext=0) * 2.0
	
	img = img - dark
	#img = img / flat
	norm = np.percentile(img, 20)
	img = img * (ref_norm/norm)
	
	frame = frame + 1

	sum =  np.minimum(img, sum)

	print(frame ," of " ,len(files))
	img = sum / 65535.0
	img = img -  np.percentile(img, 1)
	max = np.max(img)
	img = img / max


	cv2.imshow("image", 0.09 + 0.3 * bin(bin(img)))
	key = cv2.waitKey(1)

hdr = fits.header.Header()
fits.writeto("result" + str(time.time()) + ".fits", sum.astype(np.float32), hdr, overwrite=True)



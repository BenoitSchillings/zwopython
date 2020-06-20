import numpy as np
import time
import cv2
import astropy
import sys
from astropy.io import fits
import image_registration
from glob import glob
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter

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

files = glob(sys.argv[1]) + glob(sys.argv[2]) + glob(sys.argv[3])
np.random.shuffle(files)
np.random.shuffle(files)
print(files)

def fn(idx):
	return files[idx]


frame = 0
img0 = fits.getdata(fn(0), ext=0) * 2.0
sum = np.empty_like(img0, dtype=float)

flat = fits.getdata("flat.fits", ext=0)
bias = fits.getdata("bias.fits", ext=0)
dark = fits.getdata("dark.fits", ext=0)

flat = flat - bias

flat = flat / np.mean(flat)

img0 = img0 - dark
img0 = img0 / flat

sum = img0

iref = np.percentile(img0, 20)
for frame in range(0,len(files)-4, 4):
	img1 = fits.getdata(fn(frame), ext=0) * 2.0
	img1 = img1 - dark
	img1 = img1 / flat
	img2 = fits.getdata(fn(frame+1), ext=0) * 2.0
	img2 = img2 - dark
	img2 = img2 / flat
	img3 = fits.getdata(fn(frame+2), ext=0) * 2.0
	img3 = img3 - dark
	img3 = img3 / flat
	img4 = fits.getdata(fn(frame+3), ext=0) * 2.0
	img4 = img4 - dark
	img4 = img4 / flat

	
	i1 = np.percentile(img1, 20)
	i2 = np.percentile(img2, 20)
	i3 = np.percentile(img3, 20)
	i4 = np.percentile(img4, 20)
	
	i1 = i1 / iref
	i2 = i2 / iref
	i3 = i3 / iref
	i4 = i4 / iref
	
	img1 = img1 / i1
	img2 = img2 / i2
	img3 = img3 / i3
	img4 = img4 / i4

	print("mean ", img3.mean(),img2.mean(),img1.mean())

	i0 = np.minimum(img1, img2)
	i0 = np.minimum(i0, img3)
	i0 = np.minimum(i0, img4)
	frame = frame + 1

	#sum +=  i0
	sum = np.minimum(sum, i0)
	
	img = sum / 65535.0
	img = img -  np.percentile(img, 1)
	max = np.max(img)/2.0
	img = img / max
	print(max)

	cv2.imshow("sfimage", 0.09 + bin(bin(img)))
	key = cv2.waitKey(1)

hdr = fits.header.Header()
frame = 1.0
fits.writeto("result" + str(time.time()) + ".fits", sum.astype(np.float32)/frame, hdr, overwrite=True)

cv2.waitKey(0)


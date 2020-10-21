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

def crop_a(img,crop):
    y,x = img.shape
    startx = x//4 - crop//2
    starty = y//4 - crop//2    
    return img[starty:starty+crop, startx:startx+crop]


#--------------------------------------------------------

def sharpness(img):
	v1 = np.sum(np.diff(img, axis=0)**2)
	v2 = np.sum(np.diff(img, axis=1)**2)

	return(v1+v2)

def bin(a):
	return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

#--------------------------------------------------------
import random

files = glob(sys.argv[1])
#random.shuffle(files)
print(files)

def fn(idx):
	return files[idx]


frame = 0
img0 = fits.getdata(fn(0), ext=0) * 2.0
sum = np.empty_like(img0, dtype=float)

flat = fits.getdata("flat.fits", ext=0)
bias = fits.getdata("bias.fits", ext=0)
dark = fits.getdata("bias.fits", ext=0)

flat = flat - bias

print("bias", dark.mean())

flat = flat / np.mean(flat)

img0 = img0 - dark
img0 = img0 / flat
ref_level = np.percentile(img0, 20)


img_prop = [('idx', int), ('dx', float), ('dy', float), ('delta', float), ('name', str)]
images_prop = np.array([], dtype=img_prop) 


for frame in range(0, len(files)):
	img = fits.getdata(fn(frame), ext=0) * 2.0
	
	img = img - dark
	img = img / flat
	ref_level1 = np.percentile(img, 20)

	print("mean ", img.mean())
	yoff,xoff = image_registration.cross_correlation_shifts(crop_center(img, 2048), crop_center(img0, 2048))
	#yoff1,xoff1 = image_registration.cross_correlation_shifts(crop_a(img, 2048), crop_a(img0, 2048))
	#print(yoff,xoff,yoff1,xoff1)
	
	shifted = np.roll(np.roll(img,int(round(yoff)),1),int(round(xoff)),0)

	#delta = sharpness(crop_center(shifted, 1024))
	delta = -np.mean(shifted - img0)
	print(delta)
	
	element = [(frame, xoff, yoff, -delta, fn(frame))]
	images_prop = np.append(images_prop, np.array(element, dtype=img_prop))

	frame = frame + 1

	sum +=  shifted
	print(frame ," of " ,len(files), yoff,xoff)
	img = sum / 65535.0
	img = img -  np.percentile(img, 1)
	max = np.max(img)/4.0
	img = img / max
	print(max)

	cv2.imshow("image", 0.03 + bin(bin(img)))
	key = cv2.waitKey(1)

hdr = fits.header.Header()
fits.writeto("result" + str(time.time()) + ".fits", sum.astype(np.float32), hdr, overwrite=True)

#stack 90 % of frames
sum = np.empty_like(img0, dtype=float)
images_prop = np.sort(images_prop, order='delta')
print(images_prop)




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

files = glob(sys.argv[1])

def fn(idx):
	return files[idx]


frame = 0
img0 = fits.getdata(fn(11), ext=0)
sum = np.empty_like(img0, dtype=float)

flat = fits.getdata("flat_100_50.fits", ext=0)
bias = fits.getdata("bias.fits", ext=0)
dark = fits.getdata("dark.fits", ext=0)

flat = flat - bias
#img0 = img0 - dark
#img0 = img0 / flat


img_prop = [('idx', int), ('dx', float), ('dy', float), ('delta', float), ('name', str)]
images_prop = np.array([], dtype=img_prop) 


for frame in range(0,len(files)):
	img = fits.getdata(fn(frame), ext=0)
	#img = img - dark
	#img = img / flat

	yoff,xoff = image_registration.cross_correlation_shifts(crop_center(img, 2048), crop_center(img0, 2048))
	shifted = np.roll(np.roll(img,int(yoff),1),int(xoff),0)

	#delta = sharpness(crop_center(shifted, 1024))
	delta = -np.mean(shifted - img0)
	print(delta)
	
	element = [(frame, xoff, yoff, -delta, fn(frame))]
	images_prop = np.append(images_prop, np.array(element, dtype=img_prop))

	frame = frame + 1

	sum +=  shifted
	print(frame ," of " ,len(files), yoff,xoff)
	img = sum / 65535.0
	img = img - np.percentile(img, 3)
	max = np.percentile(img, 90) * 2.0
	img = img / max


	cv2.imshow("image", crop_center(img, 1024))
	key = cv2.waitKey(1)


#stack 90 % of frames
sum = np.empty_like(img0, dtype=float)
images_prop = np.sort(images_prop, order='delta')
print(images_prop)



for frame in range(0,int(len(files)*0.9)):
	print(frame, " of ", len(files)*0.9)
	img = fits.getdata(fn(images_prop[frame][0]), ext=0)
	#img = img - dark
	#img = img / flat

	shifted = np.roll(np.roll(img,int(round(images_prop[frame][2])),1),int(round(images_prop[frame][1])),0)

	frame = frame + 1

	sum +=  shifted
	img = sum / 65535.0
	img = img - np.percentile(img, 3)
	max = np.percentile(img, 90) * 2.0
	img = img / max


	cv2.imshow("image", crop_center(img, 1024))
	key = cv2.waitKey(1)




hdr = fits.header.Header()
fits.writeto("result" + str(time.time()) + ".fits", img.astype(np.float32), hdr, overwrite=True)
cv2.waitKey(0)


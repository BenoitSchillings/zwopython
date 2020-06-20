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






for frame in range(0,int(len(files))):
	print(frame, " of ", len(files)*1.0)
	img = fits.getdata(fn(frame), ext=0)
	frame = frame + 1

	sum +=  img * 1.0
	cv2.imshow("image", crop_center(img, 1024))
	key = cv2.waitKey(1)

sum = sum / (len(files)*1.0)

print(sum)
hdr = fits.header.Header()
fits.writeto("result" + str(time.time()) + ".fits", sum.astype(np.float32), hdr, overwrite=True)
cv2.waitKey(0)


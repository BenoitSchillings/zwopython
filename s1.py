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

files = glob(sys.argv[1])
print(files)

def fn(idx):
    return files[idx]


frame = 0
img0 = fits.getdata(fn(0), ext=0) * 2.0
vmin = np.empty_like(img0, dtype=float)
vmin = vmin + 1000000.0

flat = fits.getdata("flat.fits", ext=0)
bias = fits.getdata("bias.fits", ext=0) * 2.0
dark = fits.getdata("bias.fits", ext=0)
flat = flat - bias

print("bias", dark.mean())

flat = flat / np.mean(flat)
flat = flat + 0.0001

#img0 = img0 - dark
ref_level = np.percentile(img0, 20)



for frame in range(0, len(files)):
    img = fits.getdata(fn(frame), ext=0) * 2.0
    
    img = img - dark
    ref_level1 = np.percentile(img, 20)
    img = img / (flat)

    print("mean ", img.mean())
    
    frame = frame + 1

    vmin = np.minimum(vmin, img)
    

    img = vmin / 65535.0
    img = img -  np.percentile(img, 1)
    max = np.max(img)/4.0
    img = img / max
    print(max)

    cv2.imshow("image", 0.03 + (bin(img)))
    key = cv2.waitKey(1)

hdr = fits.header.Header()
fits.writeto("result" + str(time.time()) + ".fits", vmin.astype(np.float32), hdr, overwrite=True)



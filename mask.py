from astropy.stats import SigmaClip
from photutils import Background2D, MedianBackground, MMMBackground, SExtractorBackground
import sys
from glob import glob
from astropy.io import fits
import numpy as np
from scipy import ndimage, misc
from scipy.ndimage.filters import gaussian_filter

def bin(a):
	a = a - np.min(a)
	return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

def clip(a):
	return a
	result = ndimage.minimum_filter(gaussian_filter(a, 2), size=40)
	#bg = np.percentile(a, 45)
	#print(bg)
	#return(np.clip(a, -1e9, bg))
	return result

file = glob(sys.argv[1])[0]

image = fits.getdata(file, ext=0)
#image = bin(image)

clipped = clip(image)

sigma_clip = SigmaClip(sigma=3.)
bkg_estimator = SExtractorBackground(sigma_clip)
bkg = Background2D(clipped, (64, 64), filter_size=(5, 5), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
image = image - bkg.background
hdr = fits.header.Header()
fits.writeto("out.fits", image.astype(np.float32), hdr, overwrite=True)
fits.writeto("mask.fits", clipped.astype(np.float32), hdr, overwrite=True)



import okWangluoPydicom as tz

import matplotlib.pyplot as plt
import pydicom
import numpy as np
import pylab
filename="mr15.dcm"
dcm = pydicom.dcmread(filename)
img,wight,hight=tz.get_pixeldata(dcm)
im=np.reshape(img,(-1,1))

hist=plt.hist(im,bins=662)
a=hist[0][20:]
b=hist[1][21:]
plt.plot(b,a)
plt.show()
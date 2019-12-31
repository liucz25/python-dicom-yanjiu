import okWangluoPydicom as tz

import matplotlib.pyplot as plt
import pydicom
import numpy as np
filename="Image15.dcm"
dcm = pydicom.dcmread(filename)
img,wight,hight=tz.get_pixeldata(dcm)
img_low=tz.setDicomWinWidthWinCenter(img,80,40,wight,hight)

imgg=np.reshape(img_low,(-1,1))


hist2=plt.hist(imgg,bins=256)

plt.show()

b=hist2[1][1:-2]
a=hist2[0][1:-1]
plt.plot(b,a)
plt.show()
plt.scatter(b,a)
plt.show()
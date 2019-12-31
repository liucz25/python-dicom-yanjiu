
import okWangluoPydicom as tz

import matplotlib.pyplot as plt
import pydicom
import numpy as np
filename="ctp15.dcm"
dcm = pydicom.dcmread(filename)
img,wight,hight=tz.get_pixeldata(dcm)
plt.imageshow(img)
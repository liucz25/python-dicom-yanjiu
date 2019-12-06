import okWangluoPydicom as tz
import matplotlib.pyplot as plt
import pydicom
import pydicom.uid
import sys
import PIL.Image as Image
from PyQt5 import QtGui
import os
import numpy as np
filename="Image15.dcm"
dcm = pydicom.dcmread(filename)
img,wight,hight=tz.get_pixeldata(dcm)

img_low=tz.setDicomWinWidthWinCenter(img,1000,-600,wight,hight)/255*360
data_low=Image.fromarray(img_low)
data_low = data_low.convert('L')
#data_low.show()
h=np.ones((wight,hight))
dh=Image.fromarray(h)
dh=dh.convert('L')

s=np.ones((wight,hight))*255
ds=Image.fromarray(s)
ds=ds.convert('L')

v=np.ones((wight,hight))*255
dv=Image.fromarray(v)
dv=dv.convert('L')

data5=[data_low,ds,dv]
imm=Image.merge("HSV",data5)
print(imm.mode)

imm.show()
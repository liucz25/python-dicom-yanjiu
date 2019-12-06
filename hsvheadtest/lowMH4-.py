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

img_low=tz.setDicomWinWidthWinCenter(img,1000,-600,wight,hight)/2
data_low=Image.fromarray(img_low)
data_low = data_low.convert('L')
# data_low.show()

s=np.ones((wight,hight))
ds=Image.fromarray(s)
ds=ds.convert('L')

v=np.ones((wight,hight))
dv=Image.fromarray(v)
dv=dv.convert('L')

data5=[data_low,ds,dv]
imm=Image.merge("HSV",data5)
print(imm.mode)

imm.show()
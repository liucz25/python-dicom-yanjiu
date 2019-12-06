import okWangluoPydicom as tz
import matplotlib.pyplot as plt
import pydicom
import pydicom.uid
import sys
import PIL.Image as Image
from PyQt5 import QtGui
import os
import numpy
filename="Image15.dcm"
dcm = pydicom.dcmread(filename)
img,wight,hight=tz.get_pixeldata(dcm)

img_low=tz.setDicomWinWidthWinCenter(img,1000,-600,wight,hight)
data_low=Image.fromarray(img_low)
data_low = data_low.convert('L')
# data_low.show()
img_mid=tz.setDicomWinWidthWinCenter(img,300,50,wight,hight)
data_mid=Image.fromarray(img_mid)
data_mid = data_mid.convert('L')
# data_mid.show()
img_h=tz.setDicomWinWidthWinCenter(img,1600,1000,wight,hight)
data_h=Image.fromarray(img_h)
data_h = data_h.convert('L')

im=[img_low,img_mid,img_h]
data=[data_low,data_mid,data_h]
data2=[data_mid,data_low,data_h]
data3=[data_h,data_low,data_mid]
data4=[data_mid,data_h,data_low]
data5=[data_low,data_h,data_mid]
imm=Image.merge("RGB",data5)
print(imm.mode)

imm.show()
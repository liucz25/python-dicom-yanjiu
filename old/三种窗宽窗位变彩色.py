import numpy as np
import pydicom
import matplotlib.pyplot as plt

def setWW(pix,ww,wc):
    img=pix
    rows=len(img)
    cols=len(img[0])
    min=(2.0*wc-ww)/2.0 
    max=(2.0*wc+ww)/2.0
    print(ww,wc,min,max)
    img_t=np.zeros([rows,cols])
    dFactor=255.0/(max-min)
    for i in np.arange(rows):
        for j in np.arange(cols):
            img_t[i,j]=np.int8((pix[i,j]-min)*dFactor)
    min_index=img_t<0
    img_t[min_index]=0
    max_index=img_t>255
    img_t[max_index]=255
    return img_t

if __name__=="__main__":

    ds=pydicom.dcmread("Image15.dcm")
    ##dp=ds.pixel_array
    dp=setWW(ds.pixel_array,1500,500)
    ##dp=setWW(ds.pixel_array,350,200)
    dp1=setWW(ds.pixel_array,1500,-500)
    dp2=setWW(ds.pixel_array,2000,800)
    dp3=setWW(ds.pixel_array,350,200)
    dp4=setWW(ds.pixel_array,80,40)
    ##dpdp=[][][]
    dpdp=np.array([dp1,dp2,dp3])
    ##dpdp+=dp2
    ##dpdp+=dp3

    dpt=dpdp.transpose(1,2,0)
    print (dpt)

    ##plt.gray()
    plt.imshow(dpt)
    plt.show()
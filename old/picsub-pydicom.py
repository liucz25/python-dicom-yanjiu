# -*- coding=utf-8 -*-
import matplotlib.pyplot as plt
import pydicom
import pydicom.uid
import sys
import PIL.Image as Image
from PyQt5 import QtGui
import os

have_numpy = True

try:
    import numpy
except ImportError:
    have_numpy = False
    raise
sys_is_little_endian = (sys.byteorder == 'little')
NumpySupportedTransferSyntaxes = [
    pydicom.uid.ExplicitVRLittleEndian,
    pydicom.uid.ImplicitVRLittleEndian,
    pydicom.uid.DeflatedExplicitVRLittleEndian,
    pydicom.uid.ExplicitVRBigEndian,
]

# 支持的传输语法
def supports_transfer_syntax(dicom_dataset):
    """
    Returns
    -------
    bool
        True if this pixel data handler might support this transfer syntax.
        False to prevent any attempt to try to use this handler
        to decode the given transfer syntax
    """
    return (dicom_dataset.file_meta.TransferSyntaxUID in
            NumpySupportedTransferSyntaxes)


def needs_to_convert_to_RGB(dicom_dataset):
    return False


def should_change_PhotometricInterpretation_to_RGB(dicom_dataset):
    return False


# 加载Dicom图像数据
def get_pixeldata(dicom_dataset):
    """If NumPy is available, return an ndarray of the Pixel Data.
    Raises
    ------
    TypeError
        If there is no Pixel Data or not a supported data type.
    ImportError
        If NumPy isn't found
    NotImplementedError
        if the transfer syntax is not supported
    AttributeError
        if the decoded amount of data does not match the expected amount
    Returns
    -------
    numpy.ndarray
       The contents of the Pixel Data element (7FE0,0010) as an ndarray.
    """
    if (dicom_dataset.file_meta.TransferSyntaxUID not in
            NumpySupportedTransferSyntaxes):
        raise NotImplementedError("Pixel Data is compressed in a "
                                  "format pydicom does not yet handle. "
                                  "Cannot return array. Pydicom might "
                                  "be able to convert the pixel data "
                                  "using GDCM if it is installed.")

    # 设置窗宽窗位
    #dicom_dataset.

    if not have_numpy:
        msg = ("The Numpy package is required to use pixel_array, and "
               "numpy could not be imported.")
        raise ImportError(msg)
    if 'PixelData' not in dicom_dataset:
        raise TypeError("No pixel data found in this dataset.")

    # Make NumPy format code, e.g. "uint16", "int32" etc
    # from two pieces of info:
    # dicom_dataset.PixelRepresentation -- 0 for unsigned, 1 for signed;
    # dicom_dataset.BitsAllocated -- 8, 16, or 32
    if dicom_dataset.BitsAllocated == 1:
        # single bits are used for representation of binary data
        format_str = 'uint8'
    elif dicom_dataset.PixelRepresentation == 0:
        format_str = 'uint{}'.format(dicom_dataset.BitsAllocated)
    elif dicom_dataset.PixelRepresentation == 1:
        format_str = 'int{}'.format(dicom_dataset.BitsAllocated)
    else:
        format_str = 'bad_pixel_representation'
    try:
        numpy_dtype = numpy.dtype(format_str)
    except TypeError:
        msg = ("Data type not understood by NumPy: "
               "format='{}', PixelRepresentation={}, "
               "BitsAllocated={}".format(
                   format_str,
                   dicom_dataset.PixelRepresentation,
                   dicom_dataset.BitsAllocated))
        raise TypeError(msg)

    if dicom_dataset.is_little_endian != sys_is_little_endian:
        numpy_dtype = numpy_dtype.newbyteorder('S')

    pixel_bytearray = dicom_dataset.PixelData

    if dicom_dataset.BitsAllocated == 1:
        # if single bits are used for binary representation, a uint8 array
        # has to be converted to a binary-valued array (that is 8 times bigger)
        try:
            pixel_array = numpy.unpackbits(
                numpy.frombuffer(pixel_bytearray, dtype='uint8'))
        except NotImplementedError:
            # PyPy2 does not implement numpy.unpackbits
            raise NotImplementedError(
                'Cannot handle BitsAllocated == 1 on this platform')
    else:
        pixel_array = numpy.frombuffer(pixel_bytearray, dtype=numpy_dtype)
    length_of_pixel_array = pixel_array.nbytes
    expected_length = dicom_dataset.Rows * dicom_dataset.Columns
    if ('NumberOfFrames' in dicom_dataset and
            dicom_dataset.NumberOfFrames > 1):
        expected_length *= dicom_dataset.NumberOfFrames
    if ('SamplesPerPixel' in dicom_dataset and
            dicom_dataset.SamplesPerPixel > 1):
        expected_length *= dicom_dataset.SamplesPerPixel
    if dicom_dataset.BitsAllocated > 8:
        expected_length *= (dicom_dataset.BitsAllocated // 8)
    padded_length = expected_length
    if expected_length & 1:
        padded_length += 1
    if length_of_pixel_array != padded_length:
        raise AttributeError(
            "Amount of pixel data %d does not "
            "match the expected data %d" %
            (length_of_pixel_array, padded_length))
    if expected_length != padded_length:
        pixel_array = pixel_array[:expected_length]
    if should_change_PhotometricInterpretation_to_RGB(dicom_dataset):
        dicom_dataset.PhotometricInterpretation = "RGB"
    if dicom_dataset.Modality.lower().find('ct') >= 0:  # CT图像需要得到其CT值图像
        pixel_array = pixel_array * dicom_dataset.RescaleSlope + dicom_dataset.RescaleIntercept  # 获得图像的CT值
    pixel_array = pixel_array.reshape(dicom_dataset.Rows, dicom_dataset.Columns*dicom_dataset.SamplesPerPixel)
    return pixel_array, dicom_dataset.Rows, dicom_dataset.Columns
# 调整CT图像的窗宽窗位
def setDicomWinWidthWinCenter(img_data, winwidth, wincenter, rows, cols):
    img_temp = numpy.zeros((rows,cols),dtype=numpy.int16)
    img_temp.flags.writeable = True
    min = (2 * wincenter - winwidth) / 2.0 + 0.5
    max = (2 * wincenter + winwidth) / 2.0 + 0.5
    dFactor = 255.0 / (max - min)

    for i in numpy.arange(rows):
        for j in numpy.arange(cols):
            img_temp[i, j] = int((img_data[i, j]-min)*dFactor)

    min_index = img_temp < 0
    img_temp[min_index] = 0
    max_index = img_temp > 255
    img_temp[max_index] = 255

    return img_temp
# 加载Dicom图片中的Tag信息
def loadFileInformation(filename):
    information = {}
    ds = pydicom.read_file(filename)
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] = ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    print(dir(ds))
    print(type(information))
    return information

if __name__=="__main__":
    filename1="Image22.dcm"
    filename2="Image23.dcm"
    dcm1 = pydicom.dcmread(filename1)  # 加载Dicom数据
    # infr=loadFileInformation(filename)
    img1,wight1,hight1=get_pixeldata(dcm1)
    dcm2 = pydicom.dcmread(filename2)  # 加载Dicom数据
    # infr=loadFileInformation(filename)
    img2,wight2,hight2=get_pixeldata(dcm2)

    img_1=setDicomWinWidthWinCenter(img1,1500,-500,wight1,hight1)
    data_1=Image.fromarray(img_1)
    data_1 = data_1.convert('L')
    data_1.show()
    img_2=setDicomWinWidthWinCenter(img2,1500,-500,wight2,hight2)
    data_2=Image.fromarray(img_2)
    data_2 = data_2.convert('L')
    data_2.show()
    img_sub=img_1-img_2
    data_3=Image.fromarray(img_sub)
    data_3 = data_3.convert('L')
    data_3.show()
    plt.imshow(data_3)
    plt.show()

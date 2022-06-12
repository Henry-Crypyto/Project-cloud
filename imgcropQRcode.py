import cv2
import sys  # opencv
from PIL import Image # Python Imaging Library
from pyzbar.pyzbar import decode # python zbarcode
image = cv2.imread('test7.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (7,7), 0)
thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,3)

cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
for c in cnts:
    x,y,w,h = cv2.boundingRect(c)
    ROI = image[y:y+h, x:x+w]
    break

cv2.imwrite('ROI.png', ROI)
x = 70
y = 500

# 裁切區域的長度與寬度
w = 300
h = 500

# 裁切圖片
img = cv2.imread('ROI.png')
crop_img = img[y:y+h, x:x+w]
cv2.imwrite('QR.png', crop_img)
data = decode(Image.open('QR.png'))  # QR code decoder
str_data=str(data[0])
data1=str_data.split(',')
data2=str(data1)
print(data2[17:27])

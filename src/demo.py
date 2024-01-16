# coding=gbk
import cv2 
import numpy as np

src = cv2.imread("qrcode.jpg")
src=cv2.resize(src,(0,0),fx=0.25,fy=0.25)
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
# cv2.imshow("result",gray)
# cv2.waitKey(0)

_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

qrcoder = cv2.QRCodeDetector()

codeinfo, points, straight_qrcode = qrcoder.detectAndDecode(gray)
# cv2.imshow("binary",binary)
# cv2.waitKey()
print(points)
result = np.copy(src)
cv2.drawContours(result, [np.int32(points)], 0, (0, 255, 255), 2)
#print("qrcode information is : \n%s"% codeinfo)
cv2.imshow("result", result)
cv2.waitKey(0)

cv2.destroyAllWindows()
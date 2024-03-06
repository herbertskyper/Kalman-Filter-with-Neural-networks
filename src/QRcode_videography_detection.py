# -*- coding: gbk -*-
'''
��ȡ��Ƶ��̽���ά��ģ��
ͨ��opencv��������ͷ����ȡͼ�񣬼���ά�룬���һ֡һ֡��ʱ�Ķ�ά��λ����Ϣ��pnp.py
'''
import cv2
import numpy as np
# cap = cv2.VideoCapture(0)      
class point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
class QRcode:
    def __init__(self,camera_id=0):
        self.camera=cv2.VideoCapture(camera_id)
        self.Data=0
        self.Point=[]
    def detectcode(self):
        ret , qrcode_input = self.camera.read()
        if qrcode_input is None:
            return None,ret
        qrcode_1 = cv2.cvtColor(qrcode_input, cv2.COLOR_BGR2GRAY)
        _, qrcode_2 = cv2.threshold(qrcode_1, 127, 255, cv2.THRESH_BINARY)
        qrcode = cv2.QRCodeDetector()
        data, points, _ = qrcode.detectAndDecode(qrcode_2)
        self.Data=data
        self.Point=points
        return data,qrcode_input
    
    def get_corners(self):
        if self.Data:
            corners=[]
            for ip in self.Point[0]:
                corners.append(point(ip[0],ip[1]))
            #cv2.drawContours(qrcode_input, [np.int32(self.Point)], 0, (0, 0, 255), 2)
            return corners
    
    def release(self):
        self.camera.release()

    def draw(self,img):
        cv2.drawContours(img, [np.int32(self.Point)], 0, (0, 0, 255), 2)
        return img
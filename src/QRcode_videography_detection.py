# -*- coding: gbk -*-
'''
??????????????????
???opencv???????????????????????????????????????λ???????pnp.py
'''
import cv2
import numpy as np
import copy
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
    
    def get_points(self):
        if self.Data:
            corners=[]
            points=[]
            for ip in self.Point[0]:
                corners.append(point(ip[0],ip[1]))
            #cv2.drawContours(qrcode_input, [np.int32(self.Point)], 0, (0, 0, 255), 2)
            center_x,center_y=QRcode.calculate_center(corners)
            points=copy.deepcopy(corners)
            points.insert(0,point(center_x,center_y))
            return points
    
    def release(self):
        self.camera.release()

    def draw(self,img):
        cv2.drawContours(img, [np.int32(self.Point)], 0, (0, 0, 255), 2)
        return img
    
    @staticmethod
    def calculate_center(corners):
        x_coords = [corner.x for corner in corners]
        y_coords = [corner.y for corner in corners]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return center_x, center_y
    
    @staticmethod
    def show_originPoints(points):
        print("originPoints:")
        for i in range(5):
            print("x{}:{:.2f},y{}:{:.2f}".format(i, points[i].x, i, points[i].y))

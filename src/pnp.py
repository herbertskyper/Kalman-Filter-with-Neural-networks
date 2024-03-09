'''
Pnp解算模块
接收video.py探测到的二维码位置信息，通过solve()输出给KF.py(卡尔曼滤波)
'''

import cv2
import numpy as np 
from typing import Tuple # 对pnp.solve()返回值做类型标注，返回含6个float的tuple

class Pnp:
    @staticmethod
    def convertCornerToImagePoints(corners):
        return np.array([[corners[i].x, corners[i].y] for i in range(4)], dtype=np.float32)

    def setObjectPoints(self, halfLength:float):
        self.obj_points = np.array([
            [-halfLength, -halfLength, 0],
            [halfLength, -halfLength, 0],
            [halfLength, halfLength, 0],
            [-halfLength, halfLength, 0]
        ], dtype=np.float32)

    def __init__(self, halfLength, camera_matrix, dist_coeffs = np.zeros((4, 1))) -> None:
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.setObjectPoints(halfLength)
        
    def solve(self, imagePoints:np.array, objectPoints:np.array):
        '''
        pnp解算，输入一帧图像，输出解算得到的坐标等
        输入：image（通过video.py读取）
        输出：x,y,z,r,p,y
        '''
        success, rvec, tvec = cv2.solvePnP(objectPoints, imagePoints, self.camera_matrix, self.dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE) 
        if success == False:
            raise ValueError("solvePnP failed")
        self.__getTransformedPoints(rvec, tvec)
        return rvec, tvec
    
    def __showTransformedPoints(self):
        for i in range(4):
            print(self.transformedPoints[:, i])

    def __getTransformedPoints(self, rvec, tvec):
        rotMat = cv2.Rodrigues(rvec)[0] # rotMat: 3*3
        # self.obj_points.T: 3*4(each column is a point vector)
        self.transformedPoints = rotMat @ self.obj_points.T + tvec

        self.__showTransformedPoints()
        return self.transformedPoints


        # cv2.solvePnP(self.obj_points,self.img_points,self.camera_matrix,self.dist_coeffs,self.rvec,self.tvec, ...)
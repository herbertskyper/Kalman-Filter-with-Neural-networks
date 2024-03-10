'''
Pnp解算模块
接收video.py探测到的二维码位置信息，通过solve()输出给KF.py(卡尔曼滤波)
'''

import cv2
import numpy as np 
from typing import Tuple # 对pnp.solve()返回值做类型标注，返回含6个float的tuple

class Pnp:
    @staticmethod
    def convertCornerToImagePoints(points):
        return np.array([[points[i].x, points[i].y] for i in range(5)], dtype=np.float32)

    #必须传入二维码的一半长度
    def setObjectPoints(self, halfLength:float):
        self.obj_points = np.array([
            [0          ,0          ,0],
            [-halfLength, -halfLength, 0],
            [halfLength, -halfLength, 0],
            [halfLength, halfLength, 0],
            [-halfLength, halfLength, 0]
        ], dtype=np.float32)

    def __init__(self, halfLength, camera_matrix, dist_coeffs = np.zeros((4, 1))) -> None:
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.setObjectPoints(halfLength)
        
    def solve(self, imagePoints:np.array, objectPoints:np.array) -> Tuple[np.array, np.array]:
        '''
        pnp解算，输入一帧图像，输出解算得到的坐标等
        输入：image（通过QRcode_videography_detection.py读取）
        输出：x,y,z,r,p,y
        '''
        success, rvec, tvec = cv2.solvePnP(objectPoints, imagePoints, self.camera_matrix, self.dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE) 
        if success == False:
            raise ValueError("solvePnP failed")
        self.__getTransformedPoints(rvec, tvec)
        return rvec, tvec
    
    def __showTransformedPoints(self):
        print('transformedPoints:')
        np.set_printoptions(precision=2)  # 设置打印选项，使得每个元素都保留两位小数
        for i in range(5):
            print(f'point{i}: {self.transformedPoints[:, i]}')

    def __getTransformedPoints(self, rvec, tvec):
        #将旋转向量 rvec 转换为旋转矩阵 rotMat
        rotMat = cv2.Rodrigues(rvec)[0] # rotMat: 3*3
        # self.obj_points.T: 3*4(each column is a point vector)
        self.transformedPoints = rotMat @ self.obj_points.T + tvec

        self.__showTransformedPoints()
        return self.transformedPoints


        # cv2.solvePnP(self.obj_points,self.img_points,self.camera_matrix,self.dist_coeffs,self.rvec,self.tvec, ...)
'''
Pnp解算模块
接收video.py探测到的二维码位置信息，通过solve()输出给KF.py(卡尔曼滤波)
'''

import cv2
from typing import Tuple # 对pnp.solve()返回值做类型标注，返回含6个float的tuple
import video # video.py

class PnpSolver:
    def __init__(self) -> None:
        pass
    def solve(self, image) -> Tuple[float,float,float,float,float,float]:
        '''
        pnp解算，输入一帧图像，输出解算得到的坐标等
        输入：image（通过video.py读取）
        输出：x,y,z,r,p,y
        '''
        # cv2.solvePnP(self.obj_points,self.img_points,self.camera_matrix,self.dist_coeffs,self.rvec,self.tvec, ...)
        pass
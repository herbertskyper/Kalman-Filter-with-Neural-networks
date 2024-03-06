# -*- coding: utf-8 -*-
'''
卡尔曼滤波模块

接收pnp.solve输出的x,y,z,r,p,y,
在内部更新坐标，供输出目标跟踪的结果

使用：
kf = KF()
kf.update(x,y,z,r,p,y)
...
'''

import numpy.matlib
import numpy.linalg
import numpy as np

class KF(object):
    '''卡尔曼滤波

    观测量z：x,y,z

    状态量Xe：x,Vx,ax, y,Vy,ay, z,Vz,az

    属性（见__init__）：
        n：状态量维数
        m：观测量维数
        Xe：状态量
        Pe：先验估计协方差
        R：测量噪声协方差
        sigma2：滤波器内部确定的参数，和Q矩阵的计算有关
    '''
    def __init__(self) -> None:
        self.n = 9 # 状态量维数
        self.m = 3 # 观测量维数

        self.Xe:np.matrix = np.matrix([1,2,1,0,0,1,0,0,1], dtype=float).transpose() # 状态量
        self.Pe:np.matrix = numpy.matlib.eye(self.n) # TODO 待定
        self.Pe:np.matrix = self.Pe * 0.01 # 先默认为0.01
        self.R:np.matrix = numpy.matlib.eye(self.m) # TODO 待定
        self.R:np.matrix = self.R * 0.01 # 先默认为0.01

        # self.Q:np.matrix = numpy.matlib.empty((self.n,self.n)) # 状态转移协方差矩阵，在update中根据每次观测的时间间隔t计算
        # Q矩阵也可在init中设置定值，根据效果调整

        self.sigma2 = float(50) # TODO 待定

    def update(self, x:float, y:float, z:float, roll:float, pitch:float, yaw:float, dT) -> None:
        # 外部调用卡尔曼滤波的接口，可以考虑删去，直接调用_calc 
        z = np.matrix([x,y,z])
        Z=self._calc(z, dT)
        return Z

    def _calc(self, Z:np.matrix, dT:float):
        # TODO 没有测试，可能有 numpy.ndarray 和 numpy.matrix 两种类型转换和运算的问题
        # 或者改为全用 ndarray 会不会好一些？
        F:np.matrix = np.matrix([[1,dT,0,0,0,0,0,0,0,],
                                 [0,1,dT,0,0,0,0,0,0,],
                                 [0,0,1,0,0,0,0,0,0],
                                 [0,0,0,1,dT,0,0,0,0,],
                                 [0,0,0,0,1,dT,0,0,0,],
                                 [0,0,0,0,0,1,0,0,0,],
                                 [0,0,0,0,0,0,1,dT,0,],
                                 [0,0,0,0,0,0,0,1,dT,],
                                 [0,0,0,0,0,0,0,0,1,]])
        
        H:np.matrix = np.matrix([[1,0,0,0,0,0,0,0,0,],
                                 [0,0,0,1,0,0,0,0,0,],
                                 [0,0,0,0,0,0,1,0,0,]])
        
        # 引用下面链接：Q矩阵是由不确定的噪声引起的，确定Q的各元素大小是不容易的.
        # 使用时都是具体问题具体分析，比方说针对只有x，y，z，Vx，Vy，Vz的状态，误差来源是移动中的打滑等
        # 最底层的是由于力的变化导致的加速度的变化，因此我们找到了加速度方差，就可以推导出Q矩阵，假设加速度方差是D(a)。
        # https://blog.csdn.net/u011362822/article/details/95905113
        # TODO 这里如果假设Q是由加速度对时间的导数引起的可以写出一个dT相关的矩阵，脑子傻了，之后写
        Q:np.matrix = numpy.matlib.eye(self.n)*0.000 # TODO 待定
        
        print(Q.shape)
        
        Q[0,1] = Q[1,0] = Q[2,1] = Q[1,2] = Q[4,3] = Q[3,4] = Q[5,4] = Q[4,5] = Q[7,6] = Q[6,7] = Q[8,7] = Q[7,8] = 0
        
        
        print(Q)

        X_pri = F @ self.Xe
        self.Pe = F @ self.Pe @ F.transpose() + Q
        print(H @ self.Pe @ H.transpose() + self.R)
        K = self.Pe @ H.transpose() @ numpy.linalg.inv(H @ self.Pe @ H.transpose() + self.R)
        Zp = H @ X_pri
        self.Xe = X_pri + K @ (Z - Zp)
        self.Pe = (numpy.matlib.eye(self.n) - K @ H) @ self.Pe
        return self.Xe

if __name__ == '__main__':
    kf_instance = KF()
    kf_instance.update(1,2,3,4,5,6,0.01)

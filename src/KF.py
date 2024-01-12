'''
卡尔曼滤波
接收pnp.solve输出的x,y,z,r,p,y
更新
'''

import numpy as np
class KF:
    def __init__(self) -> None:
        pass
    def update(self, x:float, y:float, z:float, roll:float, pitch:float, yaw:float) -> None:
        pass
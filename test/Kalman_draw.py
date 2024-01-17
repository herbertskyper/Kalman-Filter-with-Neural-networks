# -*- coding: gbk -*-
from src import KF as filter
import numpy as np

def calc_stead_acceleration(x,vx,ax,y,vy,ay,z,vz,az,dt) -> list:
    '''计算匀加速运动的位移'''
    # e=np.random.normal(0,0.1)
    # x = x + vx*dt + 0.5*ax*dt**2
    # vx = vx + ax*dt
    # ax = ax
    # y = y + vy*dt + 0.5*ay*dt**2
    # vy = vy + ay*dt
    # ay = ay
    # z = z + vz*dt + 0.5*az*dt**2
    # vz = vz + az*dt
    # az = az
    # return [x,vx,ax,y,vy,ay,z,vz,az]
    return [x+vx*dt+0.5*ax*dt**2+np.random.normal(0,0.1), vx+ax*dt+np.random.normal(0,0.1), ax, 
            y+vy*dt+0.5*ay*dt**2+np.random.normal(0,0.1), vy+ay*dt+np.random.normal(0,0.1), ay, 
            z+vz*dt+0.5*az*dt**2+np.random.normal(0,0.1), vz+az*dt+np.random.normal(0,0.1), az]

def draw_sport(data:np.ndarray) -> None:
    '''绘制运动轨迹'''
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot(data[:,0],data[:,3],data[:,6])
    plt.show() 
    
def draw_predict(data_origin:np.ndarray,data_predict:np.ndarray) -> None:
    '''绘制运动轨迹'''
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot(data_origin[:,0],data_origin[:,3],data_origin[:,6],color='red')
    ax.plot(data_predict[:,0],data_predict[:,1],data_predict[:,2],color='blue')
    plt.show() 
    
    # 二维图
    plt.plot(data_origin[:,0], data_origin[:,3], color='red')
    plt.plot(data_predict[:,0], data_predict[:,1], color='blue')

    plt.show()
    

def generate_data():
    '''生成测试数据'''
    kf=filter.KF()
    [ax,ay,az,dt] = [1,1,1,0.05]
    origin_data:np.ndarray = np.empty((100,9))
    predict_data:np.ndarray = np.empty((100,3))
    origin_data[0]=[0,0,1,0,0,1,0,0,1]  #x,vx,ax,y,vy,ay,z,vz,az
    for i in range(1,100):
        origin_data[i]=calc_stead_acceleration(*origin_data[0],dt*i)
    #draw_sport(data)
    for i in range(100):
        predict_data[i]=kf.update(origin_data[i][0],origin_data[i][3],origin_data[i][6],0,0,0,dt).tolist()[0]
    draw_predict(origin_data,predict_data)
# -*- coding: gbk -*-
from test import Kalman_draw as draw
import cv2
import numpy as np
import time
from src.QRcode_videography_detection import QRcode
from src.pnp import Pnp
from src.KF import KF
from src.yaml_loader import load_config

if __name__ == '__main__':
      # draw.generate_data() for test
      detector = QRcode()
      filter=KF()
      pnp = Pnp(0.02, *load_config("tzh_cam.yaml")) # TODO
      flag_first = True
      while True:
            dataresult,inputresult=detector.detectcode()
            if dataresult:
                  if flag_first:
                        time_prev = time.time()
                        flag_first = False
                  points=detector.get_points()
                  detector.show_originPoints(points)#打印二维码中心点和四个角点在画面坐标系下的坐标(二维)
                  
                  imagePoints:np.array = Pnp.convertCornerToImagePoints(points)
                  pnp.solve(imagePoints, pnp.obj_points)#打印二维码中心点和四个角点在相机坐标系下的坐标(三维)
                  
                  dT=time.time()-time_prev
                  time_prev = time.time()
                  #dT = 0.02
                  predict_points_3D=filter.update(*pnp.transformedPoints[:,0],0,0,0,dT).tolist()[0]
                  print("predict:")
                  print(predict_points_3D)
                  cv2.circle(inputresult,(int(imagePoints[0][0]),int(imagePoints[0][1])),5,(0,0,255),-1)
                  
                  predict_points_3D = np.array(predict_points_3D).reshape(-1, 1, 3)
                  predict_points_2D, _ = cv2.projectPoints(predict_points_3D, pnp.rvec, pnp.tvec, pnp.camera_matrix, pnp.dist_coeffs)
                  #predict_points_2D形状为(1,1,2)
                  cv2.circle(inputresult,(int(predict_points_2D[0][0][0]),int(predict_points_2D[0][0][1])),5,(0,255,0),-1)
                  input_dealed=detector.draw(inputresult)
                  cv2.imshow("camera",input_dealed)
            else:
                  cv2.imshow("camera",inputresult)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                  break
      detector.release()
      cv2.destroyAllWindows()

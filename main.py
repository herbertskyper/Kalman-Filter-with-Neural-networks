# -*- coding: gbk -*-
from test import Kalman_draw as draw
import cv2
import numpy as np
import time
from src.QRcode_videography_detection import QRcode
from src.pnp import Pnp
from src.KF import KF

if __name__ == '__main__':
      # draw.generate_data() for test
      detector = QRcode()
      #����ڲΣ���δ�궨 TODO
      pnp = Pnp(0.5, np.array([[3666.666504, 0, 1920 / 2], [0, 3666.666504, 1080 / 2], [0, 0, 1]], dtype=np.double))

      while True:
            dataresult,inputresult=detector.detectcode()
            if dataresult:
                  points=detector.get_points()
                  detector.show_originPoints(points)#��ӡ��ά�����ĵ���ĸ��ǵ��ڻ�������ϵ�µ�����(��ά)
                  
                  imagePoints:np.array = Pnp.convertCornerToImagePoints(points)
                  pnp.solve(imagePoints, pnp.obj_points)#��ӡ��ά�����ĵ���ĸ��ǵ����������ϵ�µ�����(��ά)

                  input_dealed=detector.draw(inputresult)
                  cv2.imshow("camera",input_dealed)
            else:
                  cv2.imshow("camera",inputresult)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                  break
      detector.release()
      cv2.destroyAllWindows()

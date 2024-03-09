# -*- coding: gbk -*-
from test import Kalman_draw as draw
import cv2
import numpy as np
import time
from src.QRcode_videography_detection import QRcode
from src.pnp import Pnp

if __name__ == '__main__':
      # draw.generate_data() for test
      detector = QRcode()
      pnp = Pnp(0.5, np.array([[3666.666504, 0, 1920 / 2], [0, 3666.666504, 1080 / 2], [0, 0, 1]], dtype=np.double)) # TODO

      while True:
            dataresult,inputresult=detector.detectcode()
            if dataresult:
                  corners=detector.get_corners()
                  for i in range(4):
                        print("x{}:{},y{}:{}".format(i, corners[i].x, i, corners[i].y))

                        imagePoints:np.array = Pnp.convertCornerToImagePoints(corners)
                        pnp.solve(imagePoints, pnp.obj_points)

                  input_dealed=detector.draw(inputresult)
                  cv2.imshow("camera",input_dealed)
            else:
                  cv2.imshow("camera",inputresult)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                  break
      detector.release()
      cv2.destroyAllWindows()

# -*- coding: gbk -*-
from test import Kalman_draw as draw
import cv2
import numpy as np
import time
from src.QRcode_videography_detection import QRcode

if __name__ == '__main__':
      # draw.generate_data() for test
      detector = QRcode()
      while True:
            dataresult,inputresult=detector.detectcode()
            if dataresult:
                  corners=detector.get_corners()
                  for i in range(4):
                        print("x{}:{},y{}:{}".format(i, corners[i].x, i, corners[i].y))
                  input_dealed=detector.draw(inputresult)
                  cv2.imshow("camera",input_dealed)
            else:
                  cv2.imshow("camera",inputresult)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                  break
      detector.release()
      cv2.destroyAllWindows()

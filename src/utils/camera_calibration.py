import cv2
import numpy as np
import glob

# 设置棋盘格的尺寸
chessboard_size = (9, 6)
square_size = 1.0  # 每个方格的实际尺寸（单位可以是米、厘米等）

# 准备棋盘格的3D点坐标
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# 存储所有图像的3D点和2D点
objpoints = []
imgpoints = []

# 读取所有标定图像
images = glob.glob('calibration_images/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 查找棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # 绘制并显示角点
        cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# 标定相机
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 打印标定结果
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs)
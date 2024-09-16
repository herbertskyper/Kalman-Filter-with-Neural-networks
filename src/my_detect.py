# 导入必要的库
import cv2
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.torch_utils import select_device, time_synchronized
import torch

# 初始化
device = select_device('')
half = device.type != 'cpu'  # 半精度仅在CUDA上支持

# 加载模型
model = attempt_load('yolov5s.pt', map_location=device)  # 加载FP32模型
imgsz = 640
imgsz = check_img_size(imgsz, s=model.stride.max())  # 检查img_size
if half:
    model.half()  # to FP16

# 设置数据源
source = '0'  # 例如，0为webcam
dataset = LoadStreams(source, img_size=imgsz, stride=model.stride.max())

# 检测
for path, img, im0s, vid_cap in dataset:
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 图像归一化
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # 推理
    pred = model(img, augment=False)[0]

    # 应用NMS
    pred = non_max_suppression(pred, 0.4, 0.5, classes=None, agnostic=False)

    # 处理检测结果
    for i, det in enumerate(pred):  # 检测每个图像
        if len(det):
            # 将坐标转换为原始图像的坐标
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s[i].shape).round()

            # 打印结果
            for *xyxy, conf, cls in det:
                print(f'坐标: {xyxy} 类别: {cls} 置信度: {conf}')
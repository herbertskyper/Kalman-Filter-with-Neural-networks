import os

class YoloResult:
    '''
    存储yolo的探测结果/处理yolo的结果文件，将结果文件中的位置信息提取出来
    '''
    
    def __init__(self, if_file=False ,folder_path=''):
        self.h=480  #图像高度
        self.w=640  #图像宽度
        self.position_data = []
        self.central_position_data = []
        # self.position4_data=[]  #4个角点坐标（按照左上，右上，左下，右下的顺序）以及时间，元组形式，
        
        if if_file:
            self.process_data(folder_path)

        
    def process_data(self, file_path):
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip().split(" ")
                self.position_data.append({
                    "x": float(line[1]),
                    "y": float(line[2]),
                    "w": float(line[3]),
                    "h": float(line[4])
                })
        
    def process_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                self.process_file(file_path)
        
    def process_file(self, file_path):
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip().split(" ")
                self.position_data.append({
                    "x": float(line[1]),
                    "y": float(line[2]),
                    "w": float(line[3]),
                    "h": float(line[4]),
                    "confidence": float(line[5])
                })
        
        




if __name__ == "__main__":
    yolo_result = YoloResult("yolov5/runs/detect/exp47/labels")
    print(yolo_result.position_data)
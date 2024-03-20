from typing import Any,Tuple
import face_recognition
import cv2
import serial
import serial.tools.list_ports
import time
import numpy as np

def mytime(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        t1 = time.time()
        print(f"Time: {t1 - t0}")
        return result
    return wrapper

def face_location(frame: np.array, frame_center: Tuple[int, int]) -> Tuple[int, int, Any]:
    # return the location of the first face found
    # if not detected, return the center of the frame
    face_locations: list[Tuple[int, Any, Any, int]] = face_recognition.face_locations(frame)
    face_landmarks_list:list[dict[str, list[tuple]]] = face_recognition.face_landmarks(frame)
    if len(face_locations) > 0:
        y0, x0, y1, x1 = face_locations[0]
        face_x = int((x0 + x1) / 2)
        face_y = int((y0 + y1) / 2)
        return face_x, face_y, face_landmarks_list
    return (frame_center[0], frame_center[1], face_landmarks_list)

class PID:
    def __init__(self, kP=1, kI=0, kD=0):
        # initialize gains
        self.kP = kP
        self.kI = kI
        self.kD = kD

    def initialize(self):
        # intialize the current and previous time
        self.currTime = time.time()
        self.prevTime = self.currTime

        # initialize the previous error
        self.prevError = 0

        # initialize the term result variables
        self.cP = 0
        self.cI = 0
        self.cD = 0

    def update(self, error:float, sleep:float=0.2) -> int:
        # pause for a bit
        time.sleep(sleep)

        # grab the current time and calculate delta time
        self.currTime = time.time()
        deltaTime = self.currTime - self.prevTime

        # delta error
        deltaError = error - self.prevError

        # proportional term
        self.cP = error

        # integral term
        self.cI += error * deltaTime

        # derivative term and prevent divide by zero
        self.cD = (deltaError / deltaTime) if deltaTime > 0 else 0

        # save previous time and error for the next update
        self.prevTime = self.currTime
        self.prevError = error

        # sum the terms and return
        return int(sum([
            self.kP * self.cP,
            self.kI * self.cI,
            self.kD * self.cD]))
    
def list_ports():
    ports_list = list(serial.tools.list_ports.comports())
    if len(ports_list) <= 0:
        print("无串口设备。")
    else:
        print("可用的串口设备如下：")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])

class Head:
    def __init__(self):
        self.center_x = 0
        self.center_y = 0
        self.obj_x = 0
        self.obj_y = 0
        
# def get_face_center(frame):

#     process_this_frame = 0
#     while True:
#         time.sleep(0.01)
#         if not QUEUE_IMG.empty():
#             frame = QUEUE_IMG.get()
#         else:
#             continue

#         (h, w) = frame.shape[:2]
#         HEAD.center_x = w // 2
#         HEAD.center_y = h // 2

#         if process_this_frame > 8:
#             HEAD.obj_x, HEAD.obj_y = face_location(frame, (HEAD.center_x, HEAD.center_y))
#             print(HEAD.obj_x, HEAD.obj_y)
#             process_this_frame = 0
#         process_this_frame += 1
def draw(frame, face_landmarks_list) -> None:
    for face_landmarks in face_landmarks_list:
    # Loop over each facial feature (eye, nose, mouth, etc)
        for _, list_of_points in face_landmarks.items():
            # Print the location of each facial feature in this image
            for point in list_of_points:
                cv2.circle(frame, point, 2, (255, 0, 0), -1)
    cv2.imshow("Face Detection", frame)

def pid_init() -> Tuple[PID, PID]:
    pan:PID = PID(0.08, 0, 0)
    tilt:PID = PID(0.08, 0, 0)
    pan.initialize()
    tilt.initialize()
    return pan, tilt

def pid_update(frame: np.array, pan:PID, tilt:PID) -> Tuple[int, int]:
    head:Head = Head()
    head.center_x = frame.shape[1] // 2
    head.center_y = frame.shape[0] // 2
    head.obj_x, head.obj_y, face_landmarks_list = face_location(frame, (head.center_x, head.center_y))

    draw(frame, face_landmarks_list)
    
    error_x = head.center_x - head.obj_x
    error_y = head.center_y - head.obj_y

    BLOCK_SIZE = 20
    if abs(error_x) < BLOCK_SIZE and abs(error_y) < BLOCK_SIZE:
        delta_x = 0
        delta_y = 0
    else:
        delta_x = pan.update(error_x)
        delta_y = tilt.update(error_y)

    pan_angle = delta_x + 90
    tilt_angle = delta_y + 90
    print('[pan_angle, tlt_angle] = ', pan_angle, tilt_angle)
    
    return delta_x, delta_y

def set_servos(ser:serial.Serial, delta_x:int, delta_y:int) -> None:
    pan_angle = delta_x + 90
    tilt_angle = delta_y + 90
    print('[pan_angle, tlt_angle] = ', pan_angle, tilt_angle)
    ser.write(str(pan_angle).encode('ascii'))
    ser.write(str(tilt_angle).encode('ascii')) # FIXME: check if this is the correct way to send data to the arduino
  
def main(path: str = ''):
    cap:cv2.VideoCapture = cv2.VideoCapture(0)
    ser = serial.Serial(path, 9600, timeout=0.5)
    pan, tilt = pid_init()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Error: Couldn't read frame.")
        

        # cv2.imshow('Before pid_update', frame)
        delta_x, delta_y = pid_update(frame, pan, tilt)
        set_servos(ser, delta_x, delta_y)

        # cv2.imshow('After pid_update', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ser.close()
    cap.release()
    cv2.destroyAllWindows()

main("/dev/ttyUSB0")
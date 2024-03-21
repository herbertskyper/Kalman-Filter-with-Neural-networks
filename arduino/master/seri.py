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

def face_location_visual(frame: np.array, frame_center: Tuple[int, int]) -> Tuple[int, int, Any]:
    face_locations: list[Tuple[int, Any, Any, int]] = face_recognition.face_locations(frame)
    face_landmarks_list:list[dict[str, list[tuple]]] = face_recognition.face_landmarks(frame) # TODO: whether or not delete this line
    if len(face_locations) > 0:
        y0, x0, y1, x1 = face_locations[0]
        face_x = int((x0 + x1) / 2)
        face_y = int((y0 + y1) / 2)
        return face_x, face_y, face_landmarks_list
    return (-1, -1, face_landmarks_list)

def face_location(frame: np.array, frame_center: Tuple[int, int]) -> Tuple[int, int, Any]:
    face_locations: list[Tuple[int, Any, Any, int]] = face_recognition.face_locations(frame)
    if len(face_locations) > 0:
        y0, x0, y1, x1 = face_locations[0]
        face_x = int((x0 + x1) / 2)
        face_y = int((y0 + y1) / 2)
        return face_x, face_y
    return (-1, -1)

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
        print("[INFO] 无串口设备。")
    else:
        print("[INFO] 可用的串口设备如下：")
        for comport in ports_list:
            print(list(comport)[0], list(comport)[1])

class Head:
    def __init__(self):
        self.center_x = 0
        self.center_y = 0
        self.obj_x = 0
        self.obj_y = 0
        
def draw(frame:np.array, face_landmarks_list) -> None:
    for face_landmarks in face_landmarks_list:
    # Loop over each facial feature (eye, nose, mouth, etc)
        for _, list_of_points in face_landmarks.items():
            # Print the location of each facial feature in this image
            for point in list_of_points:
                cv2.circle(frame, point, 2, (255, 0, 0), -1)
    cv2.imshow("Face Detection", frame)

def pid_init() -> Tuple[PID, PID]:
    pan:PID = PID(0.06, 0, 0) # TODO: change these values
    tilt:PID = PID(-0.06, 0, 0)
    pan.initialize()
    tilt.initialize()
    return pan, tilt

def pid_update(frame: np.array, pan:PID, tilt:PID) -> Tuple[int, int]:
    """detect face and update the pan and tilt angles

    Args:
        frame (np.array): image captured by OpenCV
        pan (PID): PID object
        tilt (PID): PID object

    Returns:
        Tuple[int, int]: Delta angles for pan and tilt
    """    
    head:Head = Head()
    head.center_x = frame.shape[1] // 2
    head.center_y = frame.shape[0] // 2
    # head.obj_x, head.obj_y, face_landmarks_list = face_location(frame, (head.center_x, head.center_y))
    head.obj_x, head.obj_y = face_location(frame, (head.center_x, head.center_y))

    if head.obj_x == -1 and head.obj_y == -1:
        error_x = 0
        error_y = 0

    # draw(frame, face_landmarks_list)
    
    error_x = head.center_x - head.obj_x
    error_y = head.center_y - head.obj_y

    BLOCK_SIZE = 0 # TODO: change this value
    if abs(error_x) < BLOCK_SIZE and abs(error_y) < BLOCK_SIZE:
        delta_x = 0
        delta_y = 0
    else:
        delta_pan = pan.update(error_x)
        delta_tilt = tilt.update(error_y)
    
    return delta_pan, delta_tilt

def int_to_str(num:int) -> str:
    num_str = str(num)

    return '0' * (3 - len(num_str)) + num_str


def set_servos(ser:serial.Serial, delta_pan:int, delta_tilt:int) -> None:
    pan_angle = delta_pan + 90
    tilt_angle = delta_tilt + 90
    print('[pan_angle, tlt_angle] = ', pan_angle, tilt_angle)

    pan_str = int_to_str(pan_angle)
    tilt_str = int_to_str(tilt_angle)
    
    ser.write(tilt_str.encode('ascii')) # FIXME: check if the order is correct
    ser.write(pan_str.encode('ascii'))
  
def main(path: str = '', cam_id: int = 0):
    list_ports()
    cap:cv2.VideoCapture = cv2.VideoCapture(cam_id)
    ser = serial.Serial(path, 9600, timeout=0.5)
    pan, tilt = pid_init()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Error: Couldn't read frame.")
        
        # cv2.imshow('Before pid_update', frame)
        delta_pan, delta_tilt = pid_update(frame, pan, tilt)
        set_servos(ser, delta_pan, delta_tilt)

        # cv2.imshow('After pid_update', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ser.close()
    cap.release()
    cv2.destroyAllWindows()

main("/dev/ttyUSB0", 0)
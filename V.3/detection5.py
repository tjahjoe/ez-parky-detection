import torch
import cv2
from time import time, sleep
from requests import get, post
import numpy as np
from ultralytics.utils.plotting import Annotator

def view(annotator,box_parking, boxes, clss, confs, condition,frame, space, valid_parking_indices):
    cv2.putText(frame, f"kosong : {space}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    for box, cls, cnf in zip(boxes, clss, confs):
        annotator.box_label(box, f"{cls} {float(cnf):.2}") 

    for i in range(len(box_parking)):
        x1, y1, x2, y2 = box_parking[i]
        if condition[i] or i in valid_parking_indices:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  
        else:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2) 
    
    cv2.imshow("frame", frame)

    
def get_condition(condition, last_get_time):
    if time() - last_get_time >= 5:
        url = "http://172.20.10.3:5000/getParking"

        try:
            data = get(url=url, timeout=1).json()
            condition = np.array(data)
        except:
                pass

        last_get_time = time()

    return [condition, last_get_time]

def post_amount(space, last_send_time):
    if time() - last_send_time >= 5:
        url = "http://172.20.10.3:5000/postAmount"
        data = {"amount" : space}
        try:
            post(url=url, json=data, timeout=1)
        except:
            pass

        last_send_time = time()
    
    return last_send_time

def detection(box_parking, condition, frame, last_get_time, last_send_time, model):
    results = model(frame)
    annotator = Annotator(frame)

    datas = results.pandas().xyxy[0].to_numpy()

    boxes = datas[:, :4] 
    confs = datas[:, 4]
    clss = datas[:, 6] 

    x1_boxes, y1_boxes, x2_boxes, y2_boxes = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    x_mid = (box_parking[:, 0] + box_parking[:, 2])/2
    y_mid = (box_parking[:, 1] + box_parking[:, 3])/2

    condition_x1 = x1_boxes[:, None] <= x_mid
    condition_y1 = y1_boxes[:, None] <= y_mid
    condition_x2 = x2_boxes[:, None] > x_mid
    condition_y2 = y2_boxes[:, None] > y_mid

    condition_cls = clss[:, None] == 'car'

    valid_condition = condition_x1 & condition_y1 & condition_x2 & condition_y2 & condition_cls
    condition, last_get_time = get_condition(condition, last_get_time)

    valid_parking_indices = np.where(valid_condition.any(axis=0))[0]
    condition_indices = np.where(condition)[0]

    index_filled = np.unique(np.sort(np.hstack((valid_parking_indices, condition_indices))))

    space =len(box_parking) - len(index_filled)

    view(annotator,box_parking, boxes, clss, confs, condition,frame, space, valid_parking_indices)

    last_send_time = post_amount(space, last_send_time)

    return condition, last_get_time, last_send_time


def open_cam(box_parking, condition, last_get_time, last_send_time, model):
    
    while True:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            break
        sleep(10)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA)

        condition, last_get_time, last_send_time =  detection(box_parking, condition, frame, last_get_time, last_send_time, model)

        if cv2.waitKey(1) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    

def load_model_and_prepare():
    model = torch.hub.load('ultralytics/yolov5', "custom", path="visdrone.pt")

    box_parking = np.array(
                        [[540, 313, 807, 450], 
                        [516, 469, 792, 611],
                        [494, 630, 770, 789],
                        [459, 808, 755, 992],
                        [1135, 347, 1453, 484],
                        [1146, 499, 1481, 646],
                        [1166, 663, 1505, 823],
                        [1196, 838, 1534, 1039]]
                        )
    
    condition = np.array([False for _ in range(len(box_parking))])

    last_get_time = 0
    last_send_time = 0

    open_cam(box_parking, condition, last_get_time, last_send_time, model)
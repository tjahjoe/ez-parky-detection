from ultralytics.utils.plotting import Annotator
from copy import deepcopy
from time import sleep, time
from requests import post
from threading import Thread
import pathlib
import cv2
import torch
pathlib.PosixPath = pathlib.WindowsPath

stop = False

def space_perky(rect, row, space, stop_loop_parky):
    for idx, (p1, p2) in enumerate(zip(rect[0], rect[1])):
        dot = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
        if row['xmin'] < dot[0] < row['xmax'] and row['ymin'] < dot[1] < row['ymax']:
            space[idx] = True
            stop_loop_parky += 1
            break
    return space, stop_loop_parky

def plotting(results, annotator, frame,rect):
    space = [False] * len(rect[0])
    stop_loop_parky = 0

    for _, row in results.pandas().xyxy[0].iterrows():
        if row['name'] == 'person':
            box = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
            annotator.box_label(box, f"{row['name']} {float(row['confidence']):.2}")
            if stop_loop_parky < len(rect[0]):
                space, stop_loop_parky = space_perky(rect, row, space, stop_loop_parky)

    free_space = 0
    for p1, p2, is_occupied in zip(rect[0], rect[1], space):
        color = (255, 0, 0) if is_occupied else (0, 255, 0)
        cv2.rectangle(frame, p1, p2, color, 2)
        if not is_occupied:
            free_space += 1
    return free_space

def detection():
    global stop
    while True:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            break
        sleep(10)
    model = torch.hub.load('ultralytics/yolov5', "custom", path="yolov5s.pt")
    rect = [[[400, 260], [400, 450], [400, 623], [400, 815], [1200, 260], [1200, 450], [1200, 623], [1200, 815]], 
            [[700, 425], [700, 610], [700, 800], [700, 995], [1500, 425], [1500, 610], [1500, 800], [1500, 995]]]
    
    last_send_time = 0
    cv2.namedWindow('ezparky', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('ezparky', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA)
        
        results = model(frame)
        annotator = Annotator(frame)

        free_space = plotting(results, annotator, frame, rect)

        cv2.putText(frame, f"kosong: {free_space}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("ezparky", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

detection()
from ultralytics.utils.plotting import Annotator
from copy import deepcopy
from time import sleep, time
from requests import post
import cv2
import torch

stop = False
def detection():
    global stop
    while True:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            break
        sleep(10)
    model = torch.hub.load('ultralytics/yolov5', "custom", path="visdrone.pt")
    rect = [[[540, 313], [516, 469], [494, 630], [459, 808], [1135, 347], [1146, 499], [1166, 663], [1196, 838]], 
            [[807, 450], [792, 611], [770, 789], [755, 992], [1453, 484], [1481, 646], [1505, 823], [1534, 1039]]]
    
    last_send_time = 0
    cv2.namedWindow('ezparky', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('ezparky', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            stop = True
            break
        temporary_rect = deepcopy(rect)
        copy_rect =[[[0 for _ in range(2)] for _ in range(len(rect[0]))] for _ in range(2)]
        #frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_AREA)
        results = model(frame)
        annotator = Annotator(frame)
        i = 0
        for _,row in results.pandas().xyxy[0].iterrows():
            if row['name'] == 'car':
                box = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                annotator.box_label(box, f"{row['name']} {float(row['confidence']):.2}")
                index = 0
                for p1, p2 in zip(temporary_rect[0], temporary_rect[1]):
                    dot = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2]
                    if(row['xmin'] < dot[0] and row['ymin'] < dot[1] and row['xmax'] > dot[0] and row['ymax'] > dot[1] ) :
                        copy_rect[0][i] = p1
                        copy_rect[1][i] = p2
                        temporary_rect[0].pop(index)
                        temporary_rect[1].pop(index)
                        break
                    index += 1
                if(i < len(rect[0]) - 1):
                    i += 1

        space = [False for _ in range(len(rect[0]))]
        for i in range(len(rect[0])) :
            for j in range(len(copy_rect[0])) :
                if rect[0][i][0] == copy_rect[0][j][0] and rect[0][i][1] == copy_rect[0][j][1] and rect[1][i][0] == copy_rect[1][j][0] and rect[1][i][1] == copy_rect[1][j][1] :
                    space[i] = True
                    copy_rect[0].pop(j)
                    copy_rect[1].pop(j)
                    break
        
        free_space = 0
        for p1, p2, sp in zip(rect[0], rect[1], space) :
            if sp :
                cv2.rectangle(frame, p1, p2, (255, 0, 0), 2)
            else :
                cv2.rectangle(frame, p1, p2, (0, 255, 0), 2)
                free_space += 1
        
        cv2.putText(frame, f"kosong : {free_space}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("ezparky", frame)

#         if time() - last_send_time >= 5:
#             url = "http://192.168.53.201:5000/postData"
#             data = {"data" : space}
#             try:
#                 post(url=url, json=data, timeout=1)
#             except:
#                 pass
#             last_send_time = time()

        if cv2.waitKey(1) == ord('q'):
            stop = True
            break

    cap.release()
    cv2.destroyAllWindows()
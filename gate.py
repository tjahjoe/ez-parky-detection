from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep, time
from requests import get

def get_condition(url):
    open_gate = False
    try:
        open_gate = get(url=url, timeout=1).json()['data']#disesuaikan nanti
    except:
        open_gate = False
    return open_gate

def servo_actived(url, time_gate, servo, condition, min_deg, max_deg):
    if get_condition(url) == "True":
        if condition != "up":
            print('up')
            servo.angle = max_deg
        condition = "up"
        time_gate = time()
        return [condition, time_gate]
    
    if time() - time_gate >= 10:
        if condition != "down":
            print('down')
            servo.angle = min_deg
        condition = "down"
    return [condition, time_gate]
    
def gate():
    factory = PiGPIOFactory()
    min_angle = 0
    max_angle = 360
    min_pw = 0.0005
    max_pw = 0.0025
    servo_one = AngularServo(27, pin_factory=factory, min_angle=min_angle, max_angle=max_angle, min_pulse_width=min_pw, max_pulse_width=max_pw) #17 keluar
    servo_two = AngularServo(17, pin_factory=factory, min_angle=min_angle, max_angle=max_angle, min_pulse_width=min_pw, max_pulse_width=max_pw) #27 masuk
    
    condition_one = ""
    condition_two = ""
    
    time_gate_one = 0
    time_gate_two = 0
    
    url_gate_one = 'http://172.20.10.3:5000/gate'
    url_gate_two = 'http://172.20.10.3:5000/gate'
    
    servo_one.angle = 100
    servo_two.angle = 190
    
    while True:
        from detection import stop
        condition_one, time_gate_one = servo_actived(url_gate_one, time_gate_one, servo_one, condition_one, 100, 270)
        condition_two, time_gate_two = servo_actived(url_gate_two, time_gate_two, servo_two, condition_two, 190, 360)
        if stop:
            break
        sleep(1)

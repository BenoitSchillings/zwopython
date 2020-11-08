import keyboard
import skyx
import time
import threading
from ui import UI

import subprocess
import yaml
import time

 
def ticcmd(*args):
    return subprocess.check_output(['ticcmd'] + list(args))
  
  
def mcmd(motor, *args):
    if (motor == 0):
        m = '00277048'

    return ticcmd(*args, '-d', m)

def get_position(motor):
    status = yaml.safe_load(mcmd(motor, '-s', '--full'))
    #print(status)
    position = status['Current position']
    print("pos", position)
    return position

def init_motor(motor):
    mcmd(motor, '--exit-safe-start', '--deenergize')
    #mcmd(motor, '--step-mode 8')

def close(motor):
    mcmd(motor,  '--deenergize')

def disable(motor):
    mcmd(motor,  '--deenergize')

def set_pos(motor, pos):
    mcmd(motor, '--exit-safe-start', '--energize')
    mcmd(motor, '--position', str(pos))

def wait_for_motor(motor, pos):
    max = 100
    while(max > 0):
        max = max - 1
        p = get_position(motor)
        print(p, pos)
        ggui.set("Focus_pos", str(p)[0:8])
        if ((abs(p - pos))<2):
            break;
        
        time.sleep(0.03)
        

def move_focus(dv):
    pos = get_position(0)
    set_pos(0, pos + dv*32)
    wait_for_motor(0, pos + dv*32)
    
    #time.sleep(0.01)
    disable(0)

rate_x = 0.0
rate_y = 0.0
focus_pos = 0
running = True
ggui = 0

def bla(rx, ry):
    print(rx, ry)
    radec = sky.GetRaDec()
    print(radec)
    ggui.set("RA", radec[0][0:8])
    ggui.set("DEC", radec[1][0:8])
    ggui.set("Rate_RA", str(rx)[0:8])
    ggui.set("Rate_DEC", str(ry)[0:8])
    sky.rate(rx, ry)
    
    
sky = skyx.sky6RASCOMTele()
sky.Connect()


def worker(inputs):
    global rate_x
    global rate_y
    global focus_pos
    global running
    
    rx1 = rate_x
    ry1 = rate_y
    fpos1 = focus_pos
    
    init_motor(0)
    move_focus(0)
    bla(0,0)
    
    count = 0
    
    while running:
        count = count + 1
        time.sleep(0.05)
   
        if (rate_x != rx1) or (rate_y != ry1):
            rx1 = rate_x
            ry1 = rate_y
            print("change rate to ", rate_x, rate_y)
            bla(rate_x, rate_y)
            
        if (focus_pos != fpos1):
            delta = focus_pos - fpos1
            fpos1 = focus_pos
            print("change focus by ", delta)
            move_focus(delta)
            print(get_position(0))

def callback(e):
    global rate_x
    global rate_y
    global focus_pos
    global running
    global ggui
    
    if (e.event_type == 'up'):
        if (e.scan_code == 72):              #up
            rate_x = 0
           
        if (e.scan_code == 80):              #down
            rate_x = 0
           
        if (e.scan_code == 77):              #right
            rate_y = 0
            
        if (e.scan_code == 75):              #left
            rate_y = 0
            

    if (e.event_type != 'down'):
        return
        
    print(e.event_type)
    print(e.scan_code)
    if (e.scan_code == 16):
        running = False
        ggui.exit = True
    
    if (e.scan_code == 0x49):            #page up
        focus_pos = focus_pos - 2
    if (e.scan_code == 0x51):            #page down
        focus_pos = focus_pos + 2
        
        
    drate =32 
    
    if (e.scan_code == 72):              #up
        rate_x = -drate
        
    if (e.scan_code == 80):              #down
        rate_x = drate
        
    if (e.scan_code == 77):              #right
        rate_y = drate
        
    if (e.scan_code == 75):              #left
        rate_y = -drate
        
    
    
ggui = UI()  
running = True

x = threading.Thread(target=worker, args=(0,), daemon=True)
x.start()


keyboard.hook(callback)
keyboard.wait()

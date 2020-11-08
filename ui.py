import PySimpleGUI as sg
import time
from threading import Thread
import sys
import signal
import os

gui = 0

def signal_handler(signal, frame):
    gui.exit = True



def ui_thread(args):
        global gui

        while(gui.exit == False):
            gui.idle()
            time.sleep(0.1)

        print("exit ui thread")
        gui.window.close()
        os.kill(os.getpid(),signal.SIGINT)


class UI:
    def __init__(self):
        global gui
        self.exit = False
        signal.signal(signal.SIGINT, signal_handler)

        self.values = {}

        self.dirty = True 
        self.values['RA'] = '00:00:00.0'
        self.values['DEC'] = '00:00:00.0'
        self.values['Rate_RA'] = '0'
        self.values['Rate_DEC'] = '0'
        self.values['Focus_pos'] = '0'
        #self.values['Last'] = ''

        gui = self

        sg.change_look_and_feel("Dark Red")

        layout = [
        [sg.Text('RA', pad=((11, 0), 0), font='Any 15', key='outputz1', size=(14,0)),
        sg.Text(self.values['RA'], pad=((21, 0), 0), font='Any 15', key='RA', relief = sg.RELIEF_RIDGE,size=(12,0), justification='right')],

        [sg.Text('DEC', pad=((11, 0), 0), font='Any 15', key='outputz2', size=(14,0)),
        sg.Text('+89:32:41', pad=((21, 0), 0), font='Any 15', key='DEC', relief = sg.RELIEF_RIDGE, size=(12,0), justification='right')],

        [sg.VerticalSeparator(pad=(0,15))],

        [sg.Text('Rate_RA', pad=((11, 0), 0), font='Any 15', key='outputz3', size=(14,0)),
        sg.Text('+890', pad=((21, 0), 0), font='Any 15', key='Rate_RA', relief = sg.RELIEF_RIDGE, size=(12,0), justification='right')],

        [sg.Text('Rate_DEC', pad=((11, 0), 0), font='Any 15', key='outputz4', size=(14,0)),
        sg.Text('+121', pad=((21, 0), 0), font='Any 15', key='Rate_DEC', relief = sg.RELIEF_RIDGE, size=(12,0), justification='right')],

        [sg.VerticalSeparator(pad=(0,15))],

        [sg.Text('Focus_pos', pad=((11, 0), 0), font='Any 15', key='outputz5', size=(14,0)),
        sg.Text('1', pad=((21, 0), 0), font='Any 15', key='Focus_pos', relief = sg.RELIEF_RIDGE, size=(12,0), justification='right')],
        ]

    
        self.window = sg.Window('ctrl', layout,
                                grab_anywhere=True,
                                keep_on_top=True,
                                #background_color='white',
                                no_titlebar=True)
        gwindow = self.window
        
                                
        thread = Thread(target=ui_thread, args=(None,))
        thread.start()
        
        
    def idle(self):

        if (self.dirty == True):
            for val in self.values:
                self.window[val].update(self.values[val])
            self.dirty = False


        event, values = self.window.read(timeout=0)
        #print(event, values) 


        #self.window['output'].update(1)
 
    def set(self, name, value):
        self.dirty = True 
        self.values[name] = value          
   
#ggui = UI() 

#while(True):
#    time.sleep(0.1)
            
            

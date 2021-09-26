from fastapi import FastAPI
from pydantic import BaseModel
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BEDINFO = {'bed1n2':{'pin':19,'is_open':False},
           'bed3n4':{'pin':20,'is_open':False},
           'spikes':{'pin':21,'is_open':False}}
MIN, MAX = 0, 10

class Valve(BaseModel):
    bedinfo: dict = BEDINFO

    def init(self):
        for key in self.bedinfo:
            pin = self.bedinfo[key]['pin']
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH) # Frivolous startup blink
            GPIO.output(pin, GPIO.LOW)  # -""-
        return self

    def open(self, bed:str):
        try:
            pin = self.bedinfo[bed]['pin']
            GPIO.output(pin, GPIO.HIGH)
            self.bedinfo[bed]['is_open'] = True
        except KeyError:
            pass

    def close(self, bed:str):
        try:
            pin = self.bedinfo[bed]['pin']
            GPIO.output(pin, GPIO.LOW)
            self.bedinfo[bed]['is_open'] = False
        except KeyError:
            pass

    def timeOne(self, bed:str, sec:int):
        if sec > 0:
            self.open(bed)
            time.sleep(sec)
            self.close(bed)
    
    def timeAll(self, *args):
        lst = []
        for sec in args:
            lst.append(self._checktime(sec))
        lst.reverse()
        for key in self.bedinfo:
            sec = lst.pop()
            self.timeOne(key, sec)
    
    @staticmethod
    def _checktime(sec:int):
        if   sec > MAX: return MAX
        elif sec < MIN: return MIN
        return sec

valve = Valve().init()
valve_app = FastAPI()

#@valve_app.on_event("shutdown")
#def close_valves():
#    valve.close(19)
#    valve.close(20)
#    valve.close(21)

@valve_app.get("/valves/open", response_model=Valve)
def open_valve(id:str):
    valve.open(id)
    return valve

@valve_app.get("/valves/close", response_model=Valve)
def close_valve(id:str):
    valve.close(id)
    return valve

@valve_app.get("/valves/timeOne", response_model=Valve)
def timeOne(id:str, sec:int):
    valve.timeOne(id, sec)
    return valve

@valve_app.get("/valves/timeAll", response_model=Valve)
def timeAll(bed1n2:int, bed3n4:int, spikes:int):
    valve.timeAll(bed1n2, bed3n4, spikes)
    return valve

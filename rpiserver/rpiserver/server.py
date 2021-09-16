from fastapi import FastAPI
from pydantic import BaseModel
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BEDINFO = {'bed1n2':{'pin':19,'is_open':False},
           'bed3n4':{'pin':20,'is_open':False},
           'spikes':{'pin':21,'is_open':False}}

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

    def timer(self, bed:str, sec:int):
        self.open(bed)
        time.sleep(sec)
        self.close(bed)

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

@valve_app.get("/valves/timer", response_model=Valve)
def close_valve(id:str, sec:int):
    valve.timer(id, sec)
    return valve

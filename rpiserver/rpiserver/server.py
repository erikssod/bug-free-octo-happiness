from fastapi import FastAPI
from pydantic import BaseModel
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Valve(BaseModel):
    gpio: list
    is_open: bool = False

    def init(self):
        for gpio in self.gpio:
            GPIO.setup(gpio, GPIO.OUT)
            GPIO.output(gpio, GPIO.HIGH) # Frivolous startup blink
            GPIO.output(gpio, GPIO.LOW)  # -""-
        return self

    def open(self, gpio):
            GPIO.output(gpio, GPIO.HIGH)
            self.is_open = True

    def close(self, gpio):
            GPIO.output(gpio, GPIO.LOW)
            self.is_open = False

valve = Valve(gpio=[19,20,21]).init()

valve_app = FastAPI()

@valve_app.on_event("shutdown")
def close_valves():
    valve.close(19)
    valve.close(20)
    valve.close(21)

@valve_app.get("/valves/open", response_model=Valve)
def open_valve(id:int):
    valve.open(id)
    return valve

@valve_app.get("/valves/close", response_model=Valve)
def close_valve(id:int):
    valve.close(id)
    return valve


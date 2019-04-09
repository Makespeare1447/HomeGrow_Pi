########################################################### IMPORTS ###############################################################################

import time
from time import sleep
import os
import matplotlib.pyplot as plt
#import pandas as pd
import numpy as np
import gpiozero as io
from gpiozero.tones import Tone 
from smbus2 import SMBusWrapper, i2c_msg               #for i2c devices
import Adafruit_DHT
import Adafruit_Python_SSD1306   




########################################################### FUNCTIONS ###############################################################################

def device_on(device):
    device.on()
    return 0

def device_off(device):
    device.off()
    return 0

def gethours():
    hours = time.strftime("%H")
    return hours

def DHT_read(sensor, pin):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return (round(humidity, 1), round(temperature, 1))
    
def beep(buzzer):
    buzzer.play(Tone(500.0)) # Hz
    sleep(0.15)
    buzzer.stop()
    sleep(0.15)
    buzzer.play(Tone(500.0)) # Hz
    sleep(0.15)
    buzzer.stop()

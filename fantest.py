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
import Adafruit_Python_SSD1306                                #oled




fan = io.PWMLED(21)


for i in range(10):
    speed = i*0.1
    fan.value(speed)
    sleep(3)


fan.value()
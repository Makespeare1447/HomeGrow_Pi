#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################

########################################################### IMPORTS #################################################################################

import time
from time import sleep
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import gpiozero as io 
from smbus2 import SMBusWrapper, i2c_msg               #for i2c devices
import Adafruit_DHT
import Adafruit_SSD1306                                #oled





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

def DHT_read(sensor=Adafruit_DHT.DHT22, pin=dht_pin):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    return [round(humidity, 1), round(temperature, 1)]


    
##########################################################   SETUP  #################################################################################

lamp = io.LED(pin=17, active_high=False)
dht_pin = 4




print('Success! - you reached the end of the Program!')
########################################################### IMPORTS ###############################################################################
import matplotlib
matplotlib.use('Agg')
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
#import Adafruit_Python_SSD1306   #oled if necessary
import telegram
from configuration import *




########################################################### FUNCTIONS ###############################################################################

def gettimestamp():
        timestamp = time.strftime("%H:%M:%S")
        return timestamp

def gethours():
    hours = time.strftime("%H")
    return int(hours)

def getminutes():
    minutes = time.strftime("%M")
    return int(minutes)

def DHT_read(sensor, pin, bot, chat_id):
    sleep(3)
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    sleep(3)
    if humidity==None or temperature==None:     #2nd try
        sleep(60)
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        sleep(60)
    if humidity==None or temperature==None:             #if not okay after 2nd try then reboot
        print('rebooting because of DHT error...')
        bot.send_message(chat_id, text='rebooting because of DHT error...')
        os.system("sudo shutdown -r now")
    return (humidity, temperature)
    
def beep(buzzer):
    buzzer.play(Tone(500.0)) # Hz
    sleep(0.15)
    buzzer.stop()
    sleep(0.15)
    buzzer.play(Tone(500.0)) # Hz
    sleep(0.15)
    buzzer.stop()

def emergency(lamp, pump, fan1, fan2, buzzer, humidity, temperature, co2, tvoc, bot, chat_id, cycles, wateringcycles, lampstate):
    lamp.off()
    pump.off()
    fan1.off()
    fan2.off()
    for minutes in range (60):
        print("Emergency Shutdown - last measurements: ")
        print('Humidity: {}'.format(humidity))
        print('Temperature: {}'.format(temperature))
        print('Co2: {}'.format(co2))
        print('TVOC: {}'.format(tvoc))
        bot.send_message(chat_id, text='Emergency Shutdown! - last measurements: \n')
        report_per_telegram(bot, chat_id, temperature, humidity, co2, tvoc, cycles, wateringcycles, lampstate)
        beep(buzzer)
        print('Time til reboot: {}'.format(60-minutes))
        bot.send_message(chat_id, text='time til reboot: {} minutes'.format(60-minutes))
        sleep(60)
    print('rebooting...')
    bot.send_message(chat_id, text='rebooting now...')
    os.system("sudo shutdown -r now")
        
def watering(pump, pumptime):
        print('watering plants...\n')
        pump.on()
        sleep(pumptime)
        pump.off()

def vent_moisture(fan1, fan2):
        print('venting moist air...\n')
        fan1.on()
        fan2.on()
        sleep(60)
        fan1.off()
        fan2.off()

def inhouseventilation(fan2):
        print('moving air around...\n')
        fan2.on()
        sleep(10)
        fan2.off()

def set_starttime():
        start_time = time.time()
        return start_time

def time_since_start(start_time):
        return((time.time() - start_time))

def i2c_iAq_read(address):
    """
     Read 9 bits from iAq (default adress 90)
     returns CO2, R, TVOC
    """
    with SMBusWrapper(1) as bus:
        # Read 64 bytes from address 80
        msg = i2c_msg.read(address, 9)
        bus.i2c_rdwr(msg)
    byte = []

    for value in msg:
        byte.append(value)

    CO2 = byte[0] * 2 ** 8 + byte[1]
    R = byte[4] * 2 ** 16 + byte[5] * 2 ** 8 + byte[6]
    TVOC = byte[7] * 2 ** 8 + byte[8]

    return (CO2, TVOC)

def report_per_telegram(bot, chat_id, temperature, humidity, co2, tvoc, cycles, wateringcycles, lampstate):
        if lampstate==True:
                bot.send_message(chat_id=chat_id, text='Humdity: {0} %\nTemperature: {1} deg\nCo2: {2} ppm\nTVOC: {3} ppb\nCycles: {4}\nWateringcycles: {5}\nlamp on '.format(humidity, temperature,
                co2, tvoc, cycles, wateringcycles))
        else:
                bot.send_message(chat_id=chat_id, text='Humdity: {0} %\nTemperature: {1} deg\nCo2: {2} ppm\nTVOC: {3} ppb\nCycles: {4}\nWateringcycles: {5}\nlamp off '.format(humidity, temperature,
                co2, tvoc, cycles, wateringcycles))
                

def plot_figure(timestamp_list ,bot, chat_id, temperature_list, humidity_list, co2_list, tvoc_list, seconds_since_start_list, temp_min, temp_max, humidity_min, humidity_max, co2_min, co2_max, tvoc_min, tvoc_max):
        print('generating plot...')
        bot.send_message(chat_id=chat_id, text='generating plot...')
        sleep(2)
        fig = plt.figure(figsize=(14,9))

        tempplot = fig.add_subplot(221)
        humidplot = fig.add_subplot(222)
        co2plot = fig.add_subplot(223)
        tvocplot = fig.add_subplot(224)

        tempplot.plot(seconds_since_start_list, temperature_list, color='#C04CFD', label='Temperature', linewidth=3)
        humidplot.plot(seconds_since_start_list, humidity_list, color='#FC6DAB', label='Humidity', linewidth=3)
        co2plot.plot(seconds_since_start_list, co2_list, color='#1f6600', label='Co2', linewidth=3)
        tvocplot.plot(seconds_since_start_list, tvoc_list, color='#153B50', label='TVOC', linewidth=3)

        tempplot.axhline(y=temp_min, color='red', linewidth=0.8)
        tempplot.axhline(y=temp_max, color='red', linewidth=0.8)
        humidplot.axhline(y=humidity_min, color='red', linewidth=0.8)
        humidplot.axhline(y=humidity_max, color='red', linewidth=0.8)
        co2plot.axhline(y=co2_min, color='red', linewidth=0.8)
        co2plot.axhline(y=co2_max, color='red', linewidth=0.8)
        tvocplot.axhline(y=tvoc_min, color='red', linewidth=0.8)
        tvocplot.axhline(y=tvoc_max, color='red', linewidth=0.8)

        tempplot.set_xlabel('Time [s]', fontsize=12.5)
        humidplot.set_xlabel('Time [s]', fontsize=12.5)
        co2plot.set_xlabel('Time [s]', fontsize=12.5)
        tvocplot.set_xlabel('Time [s]', fontsize=12.5)
        tempplot.set_ylabel('Temperature [°C]', fontsize=12.5)
        humidplot.set_ylabel('Humidity [%]', fontsize=12.5)
        co2plot.set_ylabel('Co2 [ppm]', fontsize=12.5)
        tvocplot.set_ylabel('TVOC [ppb]', fontsize=12.5)

        tempplot.set_facecolor("#fefcdb")
        humidplot.set_facecolor("#fefcdb")
        co2plot.set_facecolor("#fefcdb")
        tvocplot.set_facecolor("#fefcdb")
        fig.set_facecolor("#b0f4e6")
        fig.set_edgecolor("black")

        tempplot.grid()
        humidplot.grid()
        co2plot.grid()
        tvocplot.grid()

        tempplot.legend()
        humidplot.legend()
        co2plot.legend()
        tvocplot.legend()

        #plt.setp(tempplot.spines.values(), linewidth=2)
        #plt.setp(humidplot.spines.values(), linewidth=2)
        #plt.setp(co2plot.spines.values(), linewidth=2)
        #plt.setp(tvocplot.spines.values(), linewidth=2)


        plt.tight_layout()

        print('saving plot...')
        bot.send_message(chat_id=chat_id, text='saving plot...')
        sleep(2)
        plt.savefig('\home\Veggie_Pi\plot.png',  facecolor=fig.get_facecolor(), edgecolor=fig.get_edgecolor())
        sleep(2)

def send_plot_per_telegram(bot, chat_id):
        print('sending plot per telegram...')
        bot.send_message(chat_id=chat_id, text='sending plot per telegram...')
        sleep(3)
        bot.send_photo(chat_id=chat_id, photo=open('\home\Veggie_Pi\plot.png', mode='rb'))
        sleep(3)
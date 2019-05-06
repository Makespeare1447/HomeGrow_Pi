
from functions_and_modules import *


lamp_pin = 17
pump_pin = 27
fan1_pin = 14 
dht1_pin = 4
buzzer_pin = 22

lamp = io.LED(pin=lamp_pin, active_high=False)
pump = io.LED(pin=pump_pin, active_high=False)
dht1 = Adafruit_DHT.DHT22
buzzer = io.TonalBuzzer(buzzer_pin)
fan1 = io.PWMLED(fan1_pin)

#variable initialisation:
temperature = 0
humidity = 0
gas = 0

##########################################################   MAIN LOOP  #################################################################################

while(True):
    #Measurements:
    (humidity, temperature) = DHT_read(dht1, dht1_pin)
    print(humidity)
    print(temperature)
    print('\n')
    sleep(5) 
    
       
    




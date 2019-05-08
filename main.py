#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################



########################################################### IMPORTS #################################################################################
from functions_and_modules import *

##########################################################   SETUP  #################################################################################
#setup is executed once at startup
#pin declaration:
#lamp and pump are connected to the double relais module
#fan1: humidity regulation, fan2: inhouse ventilation (air movement)
lamp_pin = 17
pump_pin = 27
fan1_pin = 21 
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
hours = 0
hours_old = 0
emergency = False
daytime_interval = (8,20)  #time interval for lights on
pumptime = 10              #seconds for plantwatering per wateringcycle
main_delay = 2
cycles = 0


#set device states (setup)
lamp.off()
pump.off()
fan1.off()

beep(buzzer)      #initial startup beep


##########################################################   MAIN LOOP  #################################################################################

while(True):
    #get actual time:
    hours = gethours()

    #Measurements:
    (humidity, temperature) = DHT_read(dht1, dht1_pin)
    
    #check for emergency state:
    if((humidity<5 or humidity>95) and (temperature<12 or temperature>40)):
        emergency = True
        emergency()             #trigger emergency routine

    #check if daytime:
    if(hours>daytime_interval[0] and hours<daytime_interval[1]):
        daytime = True
    else:
        daytime = False
    
    #light control:
    if(daytime==True and humidity>5 and humidity<85 and temperature <=37 and temperature >=12):
        lamp.on()
    else:
        lamp.off()

    #fan control:
    if(humidity>70 or temperature>32):
        fan1.on()
    else:
        fan1.off()

    oldhours = hours
    cycles = cycles + 1         #increment cycles for debugging

    print('Humidity: {}'.format(humidity))
    print('Temperature: {}'.format(temperature))
    print('Cycles: {}\n'.format(cycles))

    sleep(main_delay)  #main delay

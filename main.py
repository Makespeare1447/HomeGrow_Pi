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
minutes = 0
minutes_old = 0
cycles = 0                 #cyclenumber for debugging
emergencystate = False

#parameter declaration:
daytime_interval = (8,20)  #time interval for lights on
pumptime = 10              #seconds for plantwatering per wateringcycle
main_delay = 2             #delay in seconds for main loop


#set device states (setup)
lamp.off()
pump.off()
fan1.off()

beep(buzzer)      #initial startup beep
start_time = set_starttime()


##########################################################   MAIN LOOP  #################################################################################

while(True):
    #get actual time:
    hours = gethours()
    minutes = getminutes()

    #check if daytime:
    if(hours>=daytime_interval[0] and hours<daytime_interval[1]):
        daytime = True
    else:
        daytime = False

    #Measurements:
    (humidity, temperature) = DHT_read(dht1, dht1_pin)
    if (type(humidity) != float or type(temperature) != float):         #check if DHT works
        emergencystate = True
        emergency(lamp, pump, fan1, buzzer)
    humidity = round(humidity, 2)
    temperature = round(temperature, 2)


    #check for emergency state:
    if((humidity<5 or humidity>98) and (temperature<5 or temperature>38)):
        emergencystate = True
        emergency(lamp, pump, fan1, buzzer)             #trigger emergency routine

    #check for venting:
    if((humidity>60 and hours == 7 and minutes == 55 and emergencystate == False)):
        vent_moisture(fan1)

    
    #light control:
    if(daytime==True and humidity>5 and humidity<85 and temperature<=37 and temperature>=12):
        lamp.on()
    else:
        lamp.off()

    #fan control:
    if(cycles%5 == 0):                                                   #check every 5 cycles if fan is necessary (hysteresis)
        if((humidity>=80 or temperature>=32) and daytime==True):
            fan1.on()
        else:
            fan1.off()
    else:
        pass


    oldhours = hours
    cycles = cycles + 1         #increment cycles for debugging

    print('Humidity: {}'.format(humidity))
    print('Temperature: {}'.format(temperature))
    print('Cycles: {}'.format(cycles))
    print('Seconds since program start: {}\n'.format(time_since_start(start_time)))

    sleep(main_delay)  #main delay

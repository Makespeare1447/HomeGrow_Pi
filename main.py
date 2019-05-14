#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################
#information
#iAQ Sensor Range:  co2: (450-2000) ppm,      tvoc: (125-600) ppb


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
fan2_pin = 20
dht1_pin = 4
buzzer_pin = 22
iaq_address = 90

lamp = io.LED(pin=lamp_pin, active_high=False)
pump = io.LED(pin=pump_pin, active_high=False)
dht1 = Adafruit_DHT.DHT22
buzzer = io.TonalBuzzer(buzzer_pin)
fan1 = io.PWMLED(fan1_pin)
fan2 = io.PWMLED(fan2_pin)

#variable initialisation:
temperature = 0
humidity = 0
tvoc = 0
co2 = 0
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
start_time = round(set_starttime(), 1)


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
        emergency(lamp, pump, fan1, fan2, buzzer, humidity, temperature, co2, tvoc)
    humidity = round(humidity, 2)
    temperature = round(temperature, 2)
    (co2, tvoc) = i2c_iAq_read(iaq_address)



    #check for emergency state:
    if(humidity<5 or humidity>98 or temperature<5 or temperature>38 or tvoc<125 or co2<450 or tvoc>450 or co2>1500):
        emergencystate = True
        emergency(lamp, pump, fan1, fan2, buzzer, humidity, temperature, co2, tvoc)             #trigger emergency routine

    #check for venting:
    if((humidity>60 and (hours==7 or hours==19) and minutes==55 and emergencystate==False)):
        vent_moisture(fan1, fan2)

    #check for inhouse ventilation:
    if(daytime==True and cycles%200==0):
        inhouseventilation(fan2)

    #light control:
    if(daytime==True and humidity>5 and humidity<85 and temperature<=37 and temperature>=12 and tvoc<450 and co2<1500):
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


    #printing out information in command line:
    print('Humidity: {}'.format(humidity))
    print('Temperature: {}'.format(temperature))
    print('Co2: {}'.format(co2))
    print('TVOC: {}'.format(tvoc))
    print('Cycles: {}'.format(cycles))
    print('Seconds since program start: {}\n'.format(round(time_since_start(start_time), 1)))

    


    

    sleep(main_delay)  #main delay

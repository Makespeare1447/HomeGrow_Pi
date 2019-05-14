#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################
#information
#iAQ Sensor Range:  co2: (450-2000) ppm,      tvoc: (125-600) ppb

print('setting parameters and importing libraries...')

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
#absolute maximum values:
co2_min = 450
co2_max = 1550
tvoc_min = 125
tvoc_max = 450
temp_min = 5
temp_max = 36
humidity_min = 15
humidity_max = 98

#set device states (setup)
lamp.off()
pump.off()
fan1.off()

beep(buzzer)      #initial startup beep
start_time = round(set_starttime(), 1)
print('starting up...\n')

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
    if(humidity<humidity_min or humidity>humidity_max or temperature<temp_min or temperature>temp_max or tvoc<tvoc_min
     or co2<co2_min or tvoc>tvoc_max or co2>co2_max):
        emergencystate = True
        emergency(lamp, pump, fan1, fan2, buzzer, humidity, temperature, co2, tvoc)             #trigger emergency routine

    #venting moist air in the morning and in the evening
    if((humidity>60 and (hours==7 or hours==19) and minutes==55 and emergencystate==False)):
        vent_moisture(fan1, fan2)

    #check for inhouse ventilation:
    if(daytime==True and cycles%100==0 and emergencystate==False):
        inhouseventilation(fan2)

    #light control:
    if(daytime==True and emergencystate==False and humidity>humidity_min and humidity<humidity_max and temperature<=temp_max 
    and temperature>=temp_min and tvoc<tvoc_max and co2<co2_max):
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
    cycles = cycles + 1         


    #printing out information in command line:
    print('Humidity: {}'.format(humidity))
    print('Temperature: {}'.format(temperature))
    print('Co2: {}'.format(co2))
    print('TVOC: {}'.format(tvoc))
    print('Cycles: {}'.format(cycles))
    print('Seconds since program start: {}\n'.format(int(round(time_since_start(start_time), 0)))

    
    sleep(main_delay)  #main delay

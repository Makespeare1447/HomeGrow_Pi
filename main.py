#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################
#information
#iAQ Sensor Range:  co2: (450-2000) ppm,      tvoc: (125-600) ppb

print('setting parameters and importing libraries...')

########################################################### IMPORTS #################################################################################
from functions_and_modules import *
#me = SingleInstance() #from tendo - prevents multiple script instances
##########################################################   SETUP  #################################################################################
#setup is executed once at startup
#setting permissions (necessary for sending image)
print('setting permissions...')
os.system('sudo chmod -R 777 .')

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
bot = telegram.Bot(token=token) #token comes from your configuration.py file


#variable initialisation:
errorcounter = 0
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
wateringcycles = 0
emergencystate = False
lampstate = False
humidity_list = []
temperature_list = []
timestamp_list = []
seconds_since_start_list = []
co2_list = []
tvoc_list = []

#parameter declaration:
maxerrors = 5
daytime_interval = (10,18)  #time interval for lights on
pumptime = 8              #seconds for plantwatering per wateringcycle
main_delay = 1             #delay in seconds for main loop
#chat_id = set your telegram chat id here (or from configuration file)

#absolute maximum values:
co2_min = 450
co2_max = 3500
tvoc_min = 125
tvoc_max = 599
temp_min = 5
temp_max = 36
humidity_min = 15
humidity_max = 98
humidity_target = 70
temp_target = 32

#set device states (setup)
lamp.off()
pump.off()
fan1.off()

beep(buzzer)      #initial startup beep

start_time = round(set_starttime(), 1)

print('starting up...\n')
bot.send_message(chat_id=chat_id, text='Hello Sir, i am starting up now...\n')

print('venting air on startup...')
bot.send_message(chat_id=chat_id, text='venting air on startup...\n')
fan1.on()
fan2.on()
sleep(15)
fan1.off()
fan2.off()

hours = gethours()
minutes = getminutes()
oldhours = hours
oldminutes = minutes
##########################################################   MAIN LOOP  #################################################################################

while(True):
    try:
        #get actual time:
        hours = gethours()
        minutes = getminutes()
        timestamp = gettimestamp()

        #reboot in the morning :
        if((hours==9 and hours!=oldhours)):
            print('good morning! - rebooting...')
            bot.send_message(chat_id, text='good morning! - rebooting...')
            os.system("sudo shutdown -r now")


        #check if daytime:
        if(hours>=daytime_interval[0] and hours<daytime_interval[1]):
            daytime = True
        else:
            daytime = False

        #Measurements every 2 cycles:
        if cycles%2==0:
            (humidity, temperature) = DHT_read(dht1, dht1_pin, bot, chat_id)
            humidity = round(humidity, 2)
            temperature = round(temperature, 2)
            (co2, tvoc) = i2c_iAq_read(iaq_address)


        #check for emergency state:
        if(humidity<humidity_min or humidity>humidity_max or temperature<temp_min or temperature>temp_max or co2>co2_max or
        co2==None or tvoc==None or humidity==None or temperature==None):
            emergencystate = True
            emergency(lamp, pump, fan1, fan2, buzzer, humidity, temperature, co2, tvoc, bot, chat_id, cycles, wateringcycles, lampstate)             #trigger emergency routine

        #venting moist air in the morning and in the evening
        if((humidity>60 and (hours==9 or hours==18) and minutes==56 and emergencystate==False)):
            vent_moisture(fan1, fan2)

        #check for inhouse ventilation:
        if(daytime==True and minutes%8==0 and minutes!=oldminutes and emergencystate==False and cycles!=0):
            inhouseventilation(fan2)

        #light control:
        if(daytime==True and emergencystate==False and humidity>humidity_min and humidity<85 and temperature<=temp_max 
        and temperature>=temp_min):
            lamp.on()
            lampstate = True
        else:
            lamp.off()
            lampstate = False

        #fan control:
        if(cycles%2 == 0):     #check every 2 cycles if fan is necessary (hysteresis)
            if((humidity>=humidity_target or temperature>=temp_target) and emergencystate==False and daytime==True):
                fan1.on() 
            else:
                fan1.off()
            


        #watering
        if(((hours==8 or hours==10 or hours==14 or hours==19) and hours!=oldhours and emergencystate==False)):
            watering(pump, pumptime)
            wateringcycles = wateringcycles + 1

        #deleting first element of lists if length exceeds 50k
        if len(seconds_since_start_list)>50000:
            humidity_list = humidity_list[1:]
            temperature_list = temperature_list[1:]
            timestamp_list = timestamp_list[1:]
            seconds_since_start_list = seconds_since_start_list[1:]
            co2_list = co2_list[1:]
            tvoc_list = tvoc_list[1:]


        #logging data
        if (cycles%2==0):
            humidity_list.append(humidity)
            temperature_list.append(temperature)
            timestamp_list.append(timestamp)
            seconds_since_start_list.append(int(round(time_since_start(start_time), 0)))
            co2_list.append(co2)
            tvoc_list.append(tvoc)

            

        #printing out information
        print('Humidity: {}'.format(humidity) + ' %')
        print('Temperature: {}'.format(temperature) + ' deg')
        print('Co2: {}'.format(co2) + ' ppm')
        print('TVOC: {}'.format(tvoc) + ' ppb')
        print('Cycles: {}'.format(cycles))
        print('Wateringcycles: {}'.format(wateringcycles))
        print('Seconds since program start: {}'.format(int(round(time_since_start(start_time), 0))))
        if lampstate==True:
            print('light is on\n')
        else:
            print('light is off\n')

        
        if (minutes%5==0 and minutes!=oldminutes):                #reporting to telegram every 5 minutes
            report_per_telegram(bot, chat_id, temperature, humidity, co2, tvoc, cycles, wateringcycles, lampstate)

            
        #plotting and send plot per telegram
        if (minutes%30==0 and minutes!=oldminutes):
            plot_figure(timestamp_list, bot, chat_id, temperature_list, humidity_list, co2_list, tvoc_list, seconds_since_start_list,
            temp_min, temp_max, humidity_min, humidity_max, co2_min, co2_max, tvoc_min, tvoc_max, humidity_target, temp_target)
            send_plot_per_telegram(bot, chat_id)
            
            



        oldhours = hours
        oldminutes = minutes
        cycles = cycles + 1   
        sleep(main_delay)  #main delay


    except:
        errorcounter = errorcounter + 1
        print('Error occured! - errorcounter = {}'.format(errorcounter))
        bot.send_message(chat_id, text='Error occured! - errorcounter = {}'.format(errorcounter))
        if errorcounter>=maxerrors:
            print('5 errors occured - terminating program now...')
            bot.send_message(chat_id, text='5 errors occured - terminating program...')
            raise ValueError('A very specific bad thing happened')

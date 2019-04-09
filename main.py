#####################################################################################################################################################
########################                                    HEADER                              #####################################################
#####################################################################################################################################################


########################################################### IMPORTS #################################################################################
from functions import *






##########################################################   SETUP  #################################################################################
#setup is executed once at startup
#pin declaration:
#lamp and pump are connected to the double relais module
#fan1: humidity regulation, fan2: inhouse ventilation (air movement)
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



beep(buzzer) #final beep
print('Success! - you reached the end of the Program!')
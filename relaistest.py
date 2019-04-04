import gpiozero as io
from time import sleep

relais_1 = io.LED(pin=17, active_high=False)
relais_2 = io.LED(pin=27, active_high=False)

sleep(2)
relais_1.on()
relais_2.on()
sleep (3)
relais_1.on()
relais_2.off()
sleep(2)
relais_1.off()
relais_2.on()
sleep(2)
relais_1.on()
relais_2.on()
sleep(2)
relais_1.off()
relais_2.off()
sleep(2)
relais_1.on()
relais_2.on()



print('Success! - you reached the end of the Program!')
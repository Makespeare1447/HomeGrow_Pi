import gpiozero as io
from time import sleep

relais_1 = io.LED(pin=17, active_high=False)
relais_2 = io.LED(pin=27, active_high=False)

sleep(2)
relais_2.on()
sleep(300)
relais_2.off()



print('Success! - you reached the end of the Program!')
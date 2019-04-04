import gpiozero as io
from time import sleep

relais = io.LED(pin=17, active_high=False)

relais.on()
sleep(10)
relais.off()
sleep(10)
relais.on()
sleep(10)
relais.off()



print('Success! - you reached the end of the Program!')
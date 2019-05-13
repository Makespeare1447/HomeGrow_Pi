from functions_and_modules import *

    
#iaq prototyping:
address = 'ax50'
co2 = i2c_iAq_read(address)[0]
print('co2: {}'.format(co2))
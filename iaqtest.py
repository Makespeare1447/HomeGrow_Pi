    from functions_and_modules import *

    
    #iaq prototyping:
    adress = 'ax50'
    co2 = i2c_iAq_read(adress)[0]
    print('co2: {}'.format(co2))
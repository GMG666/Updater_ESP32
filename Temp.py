from time import sleep_ms
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
# the device is on GPIO12

dat = Pin(14)
RELPIN1WARM = Pin(32, Pin.OUT)
RELPIN2KALT = Pin(33, Pin.OUT)

# create the onewire object
ds = DS18X20(OneWire(dat))
print('Vers 1.0')
# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# loop 10 times and print all temperatures
#for i in range(10):
while True:
    #print('messe Temperatur:', end=' ') # end=' ' no crlf
    ds.convert_temp()
    sleep_ms(750)
    for rom in roms:
        temp = ds.read_temp(rom)
        if temp <= 19.0:
           print('messe Temperatur:', end=' ') # end=' ' no crlf
           print(temp, end=' ')
           print("stelle waermer")
           RELPIN2KALT.value(0)
           RELPIN1WARM.value(1)
           
        elif temp <= 21.0:
           print('messe Temperatur:', end=' ') # end=' ' no crlf
           print(temp, end=' ')
           print("Temperatur erreicht")
           RELPIN2KALT.value(0)
           RELPIN1WARM.value(0)
           
        elif temp <= 21.1:
           print('messe Temperatur:', end=' ') # end=' ' no crlf
           print(temp, end=' ')
           print("stelle kaelter")
           RELPIN1WARM.value(0)
           RELPIN2KALT.value(1)
        else:
           print('messe Temperatur:', end=' ') # end=' ' no crlf
           print(temp, end=' ')
           
        
           
       
    #print()


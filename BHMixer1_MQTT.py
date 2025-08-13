from time import sleep_ms
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

# Tempsection 1 Wire

dat = Pin(18) #ex 14 Tempsensor Nr1

REL1 = Pin(32, Pin.OUT) # EHeat
REL2 = Pin(33, Pin.OUT) # Pumpe
REL3 = Pin(25, Pin.OUT) # Mischer kaelter
REL4 = Pin(26, Pin.OUT) # Mischer waermer

# create the onewire object
ds = DS18X20(OneWire(dat))
print('ESP_BHMixer1\Main\BHMixer1_Mqtt by GMG 2025')
Vers = 'Vers 2.0'
print(Vers)
# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# MQTT Section
ssid = 'GMG_ON_AIR'
password = 'gmggmggmg'
mqtt_server = '192.168.8.200'
mqtt_user = 'mqtt_user'
mqtt_pass = 'mqtt_gmg'

#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
#Cannel 1 empfänt rel todo und sendet den status des rel

Command = b'Rel_command' #topic_sub
Status = b'Rel_status'
infotxt = b'Bh-Telex'
Statustxt=""

SVorL=20
SVorLmin=SVorL - 4# 24°C
SVorLmax=SVorL + 0.1# 28.1 Abschalten

#channel 2 sendet den tempwert des Boilers
Puffer_topic = b'Bh_Puffer_Temp'# so heisst der Name des empfangen Topics
Vorlauf_topic = b'Bh_Vorlauf_Temp'# so heisst der Name des empfangen Topics

Puffertemperatur=0
Vorlauftemperatur=0

last_message = 0
message_interval = 5#ex5
counter = 0

#bei neustart alle rel aus
REL1.value(0)
REL2.value(0)
REL3.value(0)
REL4.value(0)



station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:  
    pass

print('Verbindung steht')
print(station.ifconfig())


# Complete project details at https://RandomNerdTutorials.com/micropython-programming-with-esp32-and-esp8266/

def sub_cb(topic, msg):
      global SVorL #= int(sux)
      global SVorLmin #= int(sux) - Zusatz
      global SVorLmax #= int(sux) + ET
      print((topic, msg))
   
      if topic == b'Rel_command' and msg == b'OFF1':# EHeat
          print('schalte EHeat aus')
          REL1.value(0)
          msg = b'OFF1'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'ON1':
          print('schalte EHeat ein')
          REL1.value(1)
          msg = b'ON1'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'OFF2':# Pumpe
          print('schalte Pumpe aus')
          REL2.value(0)
          msg = b'OFF2'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'ON2':
          print('schalte Pumpe ein')
          REL2.value(1)
          msg = b'ON2'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'OFF3':# Mischer kaelter
          print('schalte Mischer kaelter aus')
          REL3.value(0)
          msg = b'OFF3'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'ON3':
          print('schalte Mischer kaelter ein')
          REL3.value(1)
          msg = b'ON3'
          client.publish(Status, msg)
          REL4.value(0)
          msg = b'OFF4'
          client.publish(Status, msg)   
        
      if topic == b'Rel_command' and msg == b'OFF4':# Mischer waermer
          print('schalte Mischer waermer aus')
          REL4.value(0)
          msg = b'OFF4'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'ON4':
          print('schalte Mischer waermer ein')
          REL4.value(1)
          msg = b'ON4'
          client.publish(Status, msg)
          REL3.value(0)
          msg = b'OFF3'
          client.publish(Status, msg)
        
      if topic == b'Rel_command' and msg == b'ON5':
          print('mache Reset')
          msg = b'ON5'
          client.publish(Status, msg)
          sleep_ms(1000)
          machine.reset()

      if msg[0:4] == b'OFF5':  
          sux=msg[6:8] # 2 zeichen auslesen
          Zusatz = 4
          ET = 0.1
          SVorL = int(sux)
          SVorLmin = int(sux) - Zusatz
          SVorLmax = int(sux) + ET
          #print("Ergebnis=",SVorL, " ; Type is:", type(SVorL) )
          #print("Ergebnis=",SVorLmin, " ; Type is:", type(SVorLmin) )
          #print("Ergebnis=",SVorLmax, " ; Type is:", type(SVorLmax) )
          
def connect_and_subscribe(): 
    global client_id, mqtt_server, Command
    client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(Command)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, Command))
    msg = b'OFF1'
    client.publish(Status, msg)
    msg = b'OFF2'
    client.publish(Status, msg)
    msg = b'OFF3'
    client.publish(Status, msg)
    msg = b'OFF4'
    client.publish(Status, msg)
    msg = b'OFF5'
    client.publish(Status, msg)
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()
try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()

while True:    
    ds.convert_temp()
    sleep_ms(750)#750
    i=0
    for rom in roms:
        i=i+1
        temp = ds.read_temp(rom)
        if i == 1 :        
            Puffertemperatur=temp
        if i == 2 :
            Vorlauftemperatur=temp
  # ende der for schleife                 
    if Puffertemperatur >= 50.1:
        REL1.value(0) # sonst aus
        msg = b'OFF1'
        client.publish(Status, msg)
          
    if Vorlauftemperatur <= SVorLmin: #-4°C von SVorL
        Statustxt="stelle waermer"              
        REL3.value(0)      
        msg = b'OFF3'
        client.publish(Status, msg)
        REL4.value(1)
        msg = b'ON4'
        client.publish(Status, msg)
                        
    elif Vorlauftemperatur <= SVorL:
        Statustxt="Temperatur erreicht"
        REL3.value(0)     
        msg = b'OFF3'
        client.publish(Status, msg)
        REL4.value(0)
        msg = b'OFF4'
        client.publish(Status, msg)      
           
    elif Vorlauftemperatur >= SVorLmax:
        Statustxt="stelle kaelter"
        REL4.value(0)
        REL3.value(1)
        msg = b'OFF4'
        client.publish(Status, msg)
        msg = b'ON3'
        client.publish(Status, msg)
              
    try:
       client.check_msg()
       if (time.time() - last_message) > message_interval:       
           msg = (b'{0:3.1f}'.format(Puffertemperatur)) #Formatierung für 1 Nachkomma stelle
           client.publish(Puffer_topic, msg)
           msg = (b'{0:3.1f}'.format(Vorlauftemperatur)) #Formatierung für 1 Nachkomma stelle
           client.publish(Vorlauf_topic, msg)
           client.publish(infotxt, Statustxt)   
    except OSError as e:
        restart_and_reconnect()

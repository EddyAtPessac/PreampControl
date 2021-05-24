# Complete project details at https://RandomNerdTutorials.com
# Pour charger le code, utiliser et activer l'extension VSC pymakr

import machine, neopixel
from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C
from time import sleep
from ledDrive import *
from Encoder import *
from LogicPotentiometer import *
from ir_rx import IR_RX

from ir_rx.nec import NEC_8, NEC_16
from ir_rx.sony import SONY_12, SONY_15, SONY_20
from ir_rx.philips import RC5_IR
from ir_rx.test import test


led = Pin(25, Pin.OUT)
led.value(1)

def toggleLed():
    led.value(not led.value())

def IR_Callback(data, addr, ctrl):
    if data < 0:  # NEC protocol sends repeat codes.
        print('Repeat code.')
    else:
        print('Data {:02x} Addr {:04x}'.format(data, addr))
        pBt.encoderChange = pBt.ENCODER_PUSH
    if data == 0x99:
        pBt.level += 2
    if data == 0x9a:
        pBt.level -= 2


# test(0)



i2c = SoftI2C(scl=Pin(15), sda=Pin(4))

oleRz = Pin(16,Pin.OUT)
oleRz.value(0)
sleep(0.05)
oleRz.value(1)
oled_with = 128
oled_hight = 64
oled = SSD1306_I2C(oled_with, oled_hight, i2c)
lin_hight = 9
col_with = 8
def text_write(text, lin, col):
    oled.text(text, col*col_with, lin*lin_hight)

oled.fill(0)
oled.text("MicroPython", 20, 0)
oled.show()

led = Pin(25, Pin.OUT)

# initPinEncoder()
print("\nStarting...")

nbLedRing = 20
ring = neopixel.NeoPixel(machine.Pin(22), nbLedRing)


rotate_button = Encoder(36, 37, 38)
pot_Vol = LogicPotentiometer(rotate_button, name="Vol")
pot_Bal = LogicPotentiometer(rotate_button, name="Bal")
pot_Bss = LogicPotentiometer(rotate_button, name="Bas")
pot_Tre = LogicPotentiometer(rotate_button, name="Tre")

# Link ir reception with the LogicPententiometer class callback
ir = NEC_16(Pin(39, Pin.IN), LogicPotentiometer.ir_callback)

pot_Vol.attach_IR_Code(0x99,0x9a)

while True:
    sleep(0.5)


# global encoderChange
""" lvl = [22,22,22,22,22]
lvl[1] = 20
lvl[4] = 22
lvl[2] = 22
lvl[3] = 20
while True:
    #print("encoderChange: {}".format(encoderChange))
    #print("getEncoderChange: {}".format(getEncoderChange()))
    if pBt.encoderChange != pBt.ENCODER_NONE:
        ledNum = pBt.pushSel +1
        print(pBt.encoderChange)
        if pBt.encoderChange == pBt.ENCODER_PUSH:
            print ("main Push: {}".format(pBt.pushSel))
            pBt.level = lvl[ledNum]
        else:
            lvl[ledNum] = pBt.level
            ring[ledNum] = (lvl[ledNum],lvl[ledNum],lvl[ledNum])
        ring.write()
        print(lvl)
        print ("Count: {} PushSel: {}".format(pBt.level, pBt.pushSel))
        pBt.encoderChange = pBt.ENCODER_NONE
    sleep(0.2)
 """
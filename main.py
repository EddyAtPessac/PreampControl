# Complete project details at https://RandomNerdTutorials.com
# Pour charger le code, utiliser et activer l'extension VSC pymakr

# Note: Tentative de disable os.stdout impossible because en Rom

import machine, neopixel
from machine import Pin, SoftI2C
import sys, os # For enable and disable print
from PinsDefinition import *

from ssd1306 import SSD1306_I2C
from time import sleep
from ledDrive import *
from Encoder import *
from LogicPotentiometer import *
from ir_rx import IR_RX

from ir_rx.nec import NEC_8, NEC_16
# from ir_rx.sony import SONY_12, SONY_15, SONY_20
# from ir_rx.philips import RC5_IR
# from ir_rx.test import test


# led = Pin(25, Pin.OUT)
# led.value(1)

# def toggleLed():
#     led.value(not led.value())

# def IR_Callback(data, addr, ctrl):
#     if data < 0:  # NEC protocol sends repeat codes.
#         print('Repeat code.')
#     else:
#         print('Data {:02x} Addr {:04x}'.format(data, addr))
#     if data == 0x99:
#         pass
#     if data == 0x9a:
#         pass


# test(0)

# class NullWriter:
#     def write(self, arg):
#         pass

# def disable_print():
#     print (sys.stdout)
#     #sys.stdout = open(os.devnull, 'w')
#     sys.stdout = NullWriter
#     print (sys.stdout)

# def enable_print():
#     sys.stdout = sys.__stdout__


# Disabled to avoid problem with encoder 
# i2c = SoftI2C(scl=Pin(15), sda=Pin(4))

# oleRz = Pin(16,Pin.OUT)
# oleRz.value(0)
# sleep(0.05)
# oleRz.value(1)
# oled_with = 128
# oled_hight = 64
# oled = SSD1306_I2C(oled_with, oled_hight, i2c)
# lin_hight = 9
# col_with = 8
# def text_write(text, lin, col):
#     oled.text(text, col*col_with, lin*lin_hight)

# oled.fill(0)
# oled.text("MicroPython", 20, 0)
# oled.show()

led = Pin(25, Pin.OUT)

print("\nStarting...")


rotate_button = Encoder(PIN_ENCODER_A, PIN_ENCODER_B, PIN_ENCODER_PUSH)

# Utilisation de l'ESP32 V1
pot_Vol = LogicPotentiometer(rotate_button, Pin(PIN_PWM_VOL), name="Vol")
pot_Bal = LogicPotentiometer(rotate_button, Pin(PIN_PWM_BAL), name="Bal")
pot_Bss = LogicPotentiometer(rotate_button, Pin(PIN_PWM_BAS), name="Bas")
pot_Tre = LogicPotentiometer(rotate_button, Pin(PIN_PWM_TRE), name="Tre")

# Link ir reception with the LogicPententiometer class callback
ir = NEC_16(Pin(PIN_IR_RECEVER, Pin.IN), LogicPotentiometer.ir_callback)
#ir = NEC_16(Pin(39, Pin.IN), IR_Callback)
pot_Vol.attach_IR_Code(0x10, 0x14)
pot_Bal.attach_IR_Code(0x11, 0x16)
pot_Bss.attach_IR_Code(0x08, 0x0C)
pot_Tre.attach_IR_Code(0x0A, 0x0E)

pot_Vol.attachRingMode(RING_MODE_ONE_POINT, LED_COLOR_RED)
pot_Bal.attachRingMode(RING_MODE_ONE_POINT, (199>>1, 21>>1, 133>>1))
pot_Bss.attachRingMode(RING_MODE_ONE_POINT, LED_COLOR_BLUE)
pot_Tre.attachRingMode(RING_MODE_ONE_POINT, LED_COLOR_GREEN)

pot_list = (pot_Vol, pot_Bal, pot_Bss, pot_Tre)

# disable_print()

# All actions works with interrupt : IR or Encoder
while True:
    # We chose only the selected potentiometer
    sel_pot = LogicPotentiometer.sel_instance
    if  sel_pot is not None:
        sel_pot.update_ring()
    sleep(0.2)

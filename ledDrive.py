import machine, neopixel
from math import *

nbLedRing = 20
ring = neopixel.NeoPixel(machine.Pin(22), nbLedRing)
lum = 1

def rvbLum(r, v, b):
    return (int(lum*r), int(lum*v), int(lum*b))



def computeLedLevel( nb_dsp_led, led_num, dsp_level, tol ):
  led_val = 0.0  # Nominal value of the computed led num
  vt = 0.0       # Value of the tolerance (between led_val)
  dt_vt = 0.0    # Diference between led_val and dsp_level
  outputLevel = 0

  led_step = round(255 / nb_dsp_led)
  led_val =  led_step * led_num  # Nominal value
  vt =  round( led_step * tol)   # Tolerance value between led_val: => led_val +/- vt
  dt_vt = ( led_val - dsp_level)
  dt_vt = abs (dt_vt) # abs of the differance (we ignore the sign)
  dt_vt = vt -dt_vt   # Substract the value of the tolerance
  if (dt_vt > 0):
    outputLevel = dt_vt /vt; 
  return (outputLevel)


def setRing(level):
    for led in range(0, nbLedRing):
        val = computeLedLevel(nbLedRing, led, level, 2.0) * 255
        ring[led] = rvbLum(val, val, val)
    ring.write()

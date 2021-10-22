import machine, neopixel
from math import *
from PinsDefinition import *
#from functools import *

""" Neopixel library: 
    The ring is a array of tuple (r,v,b) from 0 to nbLedRing-1
"""




def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value


# Ring display mode
RING_MODE_ONE_POINT = 1   # Display one led 
RING_MODE_ONE_BAR = 2     # Display level from 0 to the actual level
RING_MODE_BALANCE = 3     # Display 2 level: one bar from 0 to 128 the otherbar for 128 to 255

# Ring colors
LED_COLOR_RED = (255, 0, 0)
LED_COLOR_BLACK = (0,0,0)
LED_COLOR_BLUE =(0,0,255)
LED_COLOR_GREEN = (0,255,0)
nb_led_ring = 24  # Not used, for information
# The content of the last display. Used to check if there is a change on the ring
last_ring = None    # The empty text assume that the 1st compare is False
#ring = neopixel.NeoPixel(machine.Pin(22), nb_led_ring)
ring = neopixel.NeoPixel(machine.Pin(PIN_NEOLED_OUT), nb_led_ring)


lum = 1

def rvbLum(r, v, b):
    return (int(lum*r), int(lum*v), int(lum*b))


def isRingChange(new_ring):
  """ Permet de comparer la liste new_ring avec last_ring """
  """ La comparaison des tuples est supporté nativement
  par contre, pour comparer 2 à 2 les éléments de chaque liste
  on utilise map avec une fonction de comparaison lambda des éléments,
  puis reduce qui va concaténer avec la fonction AND chaque résultat
  obtenu entre eux pour produire un seul resultat
  """
  global last_ring  # Do not create a local attribute, affect the global 
  try:  # At the initialisation last_ring is None an provoque a TypeError exeption
    # Compare 2 a 2 chaque tuple et renvoie une liste avec False/True pour chaque comparaison  
    compare_list = list(map (lambda tuple1, tuple2 :  
                        tuple1 == tuple2, last_ring, new_ring))
    #print(last_ring, new_ring, compare_list, sep='\n')
    if reduce(lambda a, b : a and b,    # Applique un AND entre chaque element de la liste 
                compare_list, True):    # Si tout les AND entre éléments aboutissent à True
      return False    # No change return False and do nothing else
  except TypeError:
    pass

  # The string new_ring is changed: note the new value
  last_ring = new_ring.copy()  # Make a copy of the new string (do not copy it's reference)
  # print ('Change', last_ring, new_ring, sep='\n')
  return True       # The ring is changed 


def setRingOnePointMode(level, color):
  """ Build a logic display in the led_display string next, copy the result 
  in led ring with the requested color 
  """
  low_color = tuple (map(lambda c : c>>5 , color))  # Get lower britenest
  new_ring = []
  led_display = "..[..................].."
  idx_min = led_display.find('[') + 1
  idx_max = led_display.find(']') 
  led_val = 0
  led_step = 1 / (idx_max - idx_min)
  l_led_display = list(led_display)   # list equivalent to the string (string are immuable)
  for idx in range(idx_min, idx_max):
    led_val += led_step
    if level < led_val:
      l_led_display[idx]='*'
      led_display = "".join(l_led_display) # Change list to string
      break
  # Coping the logic display in the led ring
  idx = 0
  for c in led_display:
    new_ring.append(LED_COLOR_BLACK if c=='.' else color if c=='*' else low_color)
    # print(new_ring)
    ring[idx] = new_ring[idx]   # Update the ring object with the Led color
    idx += 1
  if isRingChange(new_ring):
    print(led_display)
    ring.write()

def setRing(level, mode = RING_MODE_ONE_POINT, color = LED_COLOR_RED ):
  """ Display the level in function of the mode and the color.
  level must be between 0 and 1 
  """
  if mode == RING_MODE_ONE_POINT:
    setRingOnePointMode(level, color)



""" Unused """
"""
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
"""
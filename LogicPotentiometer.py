# Logic potentiometer class
# This class manage the level of one potentiometer (sutch as volume, or balance)
# It using the Encoder and IRdecoder class to manage the output level 
# Each object is a new potentiometer and could be activated in rolling mode with the encoder push

#from _typeshed import Self
from Encoder import *
from ledDrive import *
from machine import Pin, Timer

"""
Class LogicPotentiometer: This class manage potentiometer object. Each object have a 
name, a level, that can be modified by a encoder, or by a IR remote
We must give the encoder Class for the potentiometer so, the encoder could call
the change_level() method when the encoder is rotated
New design on 10 / 19th / 2021: The cursor is represented by a float between 0 and 1
The POT_MAX_LEVEL is the maximum physical value that could be send to the CAD. 
This value drive the increment used to change the potentiometer position
"""
POT_PHYSIQUE_MAX_LEVEL = 1024

class LogicPotentiometer():

    base_increment = 4 * 1.0 / POT_PHYSIQUE_MAX_LEVEL
    _nb_instance = 0
    _sel_instance = 0   # The instance that is selected at this time
    _instances_IR_datas = list() # List of tuple (callback, up_code, down_code)
    _IR_repeat_nb = 0
    _last_Cbk = None
    _default_change_level_callbak = None # This is used to select the default potentiometer 
    _direction = 0
    _increment = base_increment
    _fast_increment = _increment * 5
    _timer = Timer(0)


    def __init__(self, encoder, initial_level = 0.5, name=""):
        #global _nb_instance
        self.__class__._nb_instance += 1
        self.pot_pos = self._nb_instance        # Pot Number in the list of LogicPpotentiometer object
        self.pot_name = str(self.pot_pos) if name == "" else name
        self.level = initial_level
        self.color = LED_COLOR_RED
        self.ring_mode = RING_MODE_ONE_POINT
        encoder.register_callback(self.change_level)
        print("create potentiometer instance:{} initial_level:{} name:{}".format(
                self._nb_instance, initial_level, name))
        # We note the change_level callback of the default potentiometer
        if LogicPotentiometer._nb_instance == 1:    # When the 1st Potentiometer is defined, select it
            LogicPotentiometer._default_change_level_callbak = self.change_level
            LogicPotentiometer.return_to_default_selection(None)    # None replace the timer object

    @classmethod
    def reinit_timer(cls, _time=5000):  
        # Reload timer 
        cls._timer.init(period=_time, mode=Timer.ONE_SHOT, callback=cls.return_to_default_selection)

    @classmethod
    def return_to_default_selection(cls, timer_object):
        """ This function return the default selected potentiometer to the 1st.
        It is used to display Volume after a time without Encoder action, 
        or, at the initialisation when the 1st potentiometer is defined 
        The timer_object argument is provided when the timer call this function
        """
        if cls._default_change_level_callbak is not None:
            cls._default_change_level_callbak(0)


    @classmethod
    def register_instance(cls, instance_cbk, ir_up, ir_down):
        """ Append callback of the instance and the corresponding ir code """
        ir_tuple = instance_cbk, ir_up, ir_down
        cls._instances_IR_datas.append(ir_tuple) 


    @classmethod
    def ir_callback(cls, data, addr, ctrl):
        """   
        This method is a class method because only one IR receiver have to be shared
        with all the potentiometers. Here, we compare the receved code with the 
        data IR of each instances    
        """
        print("Receive {:02X}".format(data))
        IR_REPEAT_TRIG1 = 10
        if data < 0 and cls._direction != 0:  # Is a repeat code ?
            # every IR_REPEAT_TRIG1 we add _fast_increment to the increment (fast up/down)
            if cls._IR_repeat_nb>1 and (cls._IR_repeat_nb % IR_REPEAT_TRIG1) == 0:
                print("increment up at repeat {} ".format(cls._IR_repeat_nb))
                cls._increment += cls._fast_increment
            cls._IR_repeat_nb += 1      # count how many repeat receved
            cls._last_Cbk(cls._increment * cls._direction)    # send to the last callback the new increment
        else:
            print("search for {:02X}".format(data))
            cls._IR_repeat_nb = 0       # End of repeat. Reset the counter 
            cls._increment = cls.base_increment
            print("increment raz")

            # Search in list if the received code is up or down of one of the registered code
            cls._direction = 0      # if this value remain to 0, we dont find the touch code, so we dont increment anything when receving repeat code
            for instance_cbk, up, down in cls._instances_IR_datas:
                if data == up:
                    cls._direction = 1
                    instance_cbk(cls._increment )
                    cls._last_Cbk = instance_cbk
                if data == down:
                    cls._direction = -1
                    instance_cbk(-cls._increment)
                    cls._last_Cbk = instance_cbk


    def attach_IR_Code(self, up, down):
        """ Add up/down code and link them to this instance """
        LogicPotentiometer.register_instance( self.instance_ir_callback, up, down)
        pass
    
    def instance_ir_callback(self, increment):
        """ This method is called by the ir_callback class method 
        when the IR code corresponding to this instance is received 
        """
        print("Ir add {} to pot {}".format(increment, self.pot_name))
        #self.change_level(self, increment)   
        self.change_level(increment)   
        pass

    def attachRingMode(self, mode, color):
        """ Set a ring mode and color for this instance of potentiometer """
        self.color = color
        self.ring_mode = mode


    def change_level(self, increment):
        """ Add increment to potentiometer and check the bounds of level 
        set this instance of potentiometer as the selected one
        update led ring with the color of the selected potentiometer
        """
        print( "Rotation of {} for pot {} ".format(increment, self.pot_pos))
        #  Set the selected potentiometer to this instance
        LogicPotentiometer._sel_instance = self.pot_pos
        if self.pot_pos != 1:   # We return to pot 1 with a delay
            LogicPotentiometer.reinit_timer()   # Restart default selection timer

        self.level += increment
        if self.level > 1.0:
            self.level = 1.0
        if self.level < 0:
            self.level = 0
        self.update_level()

    def update_level(self):
        print("Pot '{:1d}' level:{:0.03f} ({})".format(self.pot_pos, self.level, self.pot_name))
        setRing(self.level, self.ring_mode, self.color )

# ----------UNUSED---------------

#    def is_selected(cls, self):
#        """ return True if this instance of potentiometer is selected """
#        return cls._sel_instance == self.self.pot_pos

def static_vars(**kwargs):
    """ Define a decorator to create static variables
    It look them that it doesnt works with class method
    """
    def decorate(func):

        print("Decorate of {}".format(func))
        for k in kwargs:
            print("Decorate add attr {} = {} to function  {}".format(k, kwargs[k], func))
            setattr(func, k, kwargs[k])
        return func
    return decorate



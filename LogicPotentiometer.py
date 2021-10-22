# Logic potentiometer class
# This class manage the level of one potentiometer (sutch as volume, or balance)
# It using the Encoder and IRdecoder class to manage the output level 
# Each object is a new potentiometer and could be activated in rolling mode with the encoder push

#from _typeshed import Self
from Encoder import *
from ledDrive import *
from machine import Pin, Timer, PWM

"""
Class LogicPotentiometer: This class manage potentiometer object. Each object have a 
name, a level, that can be modified by a encoder, or by a IR remote
We must give the encoder Class for the potentiometer so, the encoder could call
the change_level() method when the encoder is rotated
New design on 10 / 19th / 2021: The cursor is represented by a float between 0 and 1
The POT_MAX_LEVEL is the maximum physical value that could be send to the CAD (PWM). 
This value is used to define the increment used to change the potentiometer position
The PWM frequency on ESP32 is 5Khz for 13bits resolution (8192 step). 
In this audio application, we use 20Khz and 11 bits resoution to avoid PWM listening
"""
POT_PHYSIQUE_MAX_LEVEL = 1024 # Maximum PWM duty resolution at 40Khz
PWM_FREQUENCY = 40000
TIME_TO_DEFAULT = 10000 # Time to return to Volume display 

debug_print = True

def dbg_print(*arg):
    if debug_print == True:
        pass
        print(*arg)


class LogicPotentiometer():

    base_increment = 4 * 1.0 / POT_PHYSIQUE_MAX_LEVEL
    sel_instance_indx = 0   # The instance that is selected at this time from 1 to N
    #_nb_instance = 0
    instances = []  #List of the potentiometer instances 
    sel_instance = None
    _instances_IR_datas = list() # List of tuple (callback, up_code, down_code)
    _IR_repeat_nb = 0
    _last_Cbk = None
    _default_change_level_callbak = None # This is used to select the default potentiometer 
    _direction = 0
    _increment = base_increment
    _fast_increment = _increment * 5
    _timer = Timer(0)


    def __init__(self, encoder, out_pin, initial_level = 0.5, name=""):
        #global _nb_instance
        #self.__class__._nb_instance += 1
        #self.pot_pos = self.__class__._nb_instance        # Pot Number in the list of LogicPpotentiometer object
        LogicPotentiometer.instances.append(self)
        self.pot_pos = len(LogicPotentiometer.instances)
        self.pot_name = str(self.pot_pos) if name == "" else name
        dbg_print("create potentiometer instance:{} initial_level:{} name:{}".format(
                self.pot_pos, initial_level, name))
 
        dbg_print("Set PWM output on {}".format(out_pin))
        self.pwm = PWM(out_pin, freq=PWM_FREQUENCY)
        self.level = initial_level
        self.pwm.duty(int(self.level*POT_PHYSIQUE_MAX_LEVEL))
        dbg_print ('PWM: f={}, duty={}'.format(self.pwm.freq(),self.pwm.duty()))

        self.color = LED_COLOR_RED
        self.ring_mode = RING_MODE_ONE_POINT
        encoder.register_callback(self.change_level)
        # We note the change_level callback of the default potentiometer
        if self.pot_pos == 1:    # When the 1st Potentiometer is defined, select it
            dbg_print("Register callback as default potentiometer")
            LogicPotentiometer._default_change_level_callbak = self.change_level
            LogicPotentiometer.return_to_default_selection(None)    # None replace the timer object

    @classmethod
    def reinit_timer(cls, _time=TIME_TO_DEFAULT):  
        # Reload timer 
        cls._timer.init(period=_time, mode=Timer.ONE_SHOT, callback=cls.return_to_default_selection)

    @classmethod
    def return_to_default_selection(cls, timer_object):
        """ This function return the default selected potentiometer to the 1st.
        It is used to display Volume after a time without Encoder action, 
        or, at the initialisation when the 1st potentiometer is defined 
        The timer_object argument is provided when the timer call this function
        """
        cls.sel_instance_indx = 0
        if len(cls.instances)>0:
            cls.sel_instance =  cls.instances[cls.sel_instance_indx]

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
        dbg_print("Receive {:02X}".format(data))
        IR_REPEAT_TRIG1 = 10
        if data < 0 and cls._direction != 0:  # Is a repeat code ?
            # every IR_REPEAT_TRIG1 we add _fast_increment to the increment (fast up/down)
            if cls._IR_repeat_nb>1 and (cls._IR_repeat_nb % IR_REPEAT_TRIG1) == 0:
                dbg_print("increment up at repeat {} ".format(cls._IR_repeat_nb))
                cls._increment += cls._fast_increment
            cls._IR_repeat_nb += 1      # count how many repeat receved
            cls._last_Cbk(cls._increment * cls._direction)    # send to the last callback the new increment
        else:
            dbg_print("search for {:02X}".format(data))
            cls._IR_repeat_nb = 0       # End of repeat. Reset the counter 
            cls._increment = cls.base_increment
            dbg_print("increment raz")

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
        dbg_print("Ir add {} to pot {}".format(increment, self.pot_name))
        #self.change_level(self, increment)   
        self.change_level(increment)   
        pass

    def attachRingMode(self, mode, color):
        """ Set a ring mode and color for this instance of potentiometer """
        self.color = color
        self.ring_mode = mode


    @classmethod
    def select_next(cls):
        """ Called from Encoder Push interrupt, select the next instance of LogicPotentiometer """
        cls.sel_instance_indx += 1
        if cls.sel_instance_indx >= len(cls.instances):
            cls.sel_instance_indx = 0
        cls.sel_instance =  cls.instances[cls.sel_instance_indx]
        print("Select potentiometer N° {}, Name: {}".format(
                    cls.sel_instance_indx+1, cls.sel_instance.pot_name))

    @classmethod
    def change_pot_level(cls, increment):
        """ Called from Encoder rotation interrupt, increment the level of the selected potentiometer"""
        pot_instance = cls.sel_instance
        dbg_print("Change level for pot {} inc: {} ".format(pot_instance.pot_name, increment))
        cls.sel_instance.change_level(increment)


    def select_me(self):
        """ Make this instance as the selected. IE: if IR code select a instance, 
        it will be the new  selected instance 
        """
        LogicPotentiometer.sel_instance_indx = self.pot_pos-1
        LogicPotentiometer.sel_instance = LogicPotentiometer.instances[LogicPotentiometer.sel_instance_indx]



    def change_level(self, increment):
        """ Add increment to potentiometer and check the bounds of level 
        set this instance of potentiometer as the selected one
        update led ring with the color of the selected potentiometer
        """
        dbg_print( "Rotation of {:0.03} for pot {} ".format(increment, self.pot_name))
        self.select_me() #  Set the selected potentiometer to this instance
        if self.pot_pos != 1:   # We return to pot 1 with a delay
            LogicPotentiometer.reinit_timer()   # Restart default selection timer

        self.level += increment
        if self.level > 1.0:
            self.level = 1.0
        if self.level < 0:
            self.level = 0
        self.update_level()

    def update_level(self):
        duty = int (self.level*POT_PHYSIQUE_MAX_LEVEL)
        duty = duty if duty <= 1023 else 1023   # Duty above 1023 issue Pin output to gnd level
        dbg_print("Pot '{:1d}' level:{:0.03f} duty:{:0.1f} ({}) ".format(self.pot_pos, self.level, duty, self.pot_name))
        self.pwm.duty(duty)
        # setRing use List allocation and cost a lot of time. With that, the encoder have problem. 
        # It is necessary to manage the ring in the main loop.
        #setRing(self.level, self.ring_mode, self.color )

    def update_ring(self):
        """ This function take a lot of time, it is provided for calling from main """

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

        dbg_print("Decorate of {}".format(func))
        for k in kwargs:
            dbg_print("Decorate add attr {} = {} to function  {}".format(k, kwargs[k], func))
            setattr(func, k, kwargs[k])
        return func
    return decorate



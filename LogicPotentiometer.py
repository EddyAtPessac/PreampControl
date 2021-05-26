# Logic potentiometer class
# This class manage the level of one potentiometer (sutch as volume, or balance)
# It using the Encoder and IRdecoder class to manage the output level 
# Each object is a new potentiometer and could be activated in rolling mode with the encoder push

from Encoder import *

#  Define a decorator to create static variables
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate



class LogicPotentiometer():

    _nb_instance = 0
    _instances_datas = list()
    _IR_repeat = (0,0)

    @classmethod
    @static_vars(_ir_repeat=0)
    @static_vars(_last_cbk=-1)
    def ir_callback(cls, data, addr, ctrl):
        IR_REPEAT_TRIG1 = 10
        INC_TRIG_1 = 5
        print("search for {:02X}".format(data))
        increment = 1
        if data < 0 :  # Is a repeat code ?
            if cls._IR_repeat_nb > IR_REPEAT_TRIG1:
                if increment == 1:
                    print("increment up")
            increment = INC_TRIG_1

            ir_callback._ir_repeat += 1      # count how many repeat receved
            ir_callback._last_cbk(increment)  # send to the last callback the new increment
        else:
            ir_callback._ir_repeat = 0       # End of repeat. Reset the counter 
            print("increment raz")

        for instance_cbk, up, down in cls._instances_datas:
            if data == up:
                instance_cbk(+increment)
                ir_callback._last_cbk = instance_cbk
            if data == down:
                instance_cbk(-increment)
                ir_callback._last_cbk = instance_cbk

    @classmethod
    def register_instance(cls, instance_cbk, ir_up, ir_down):
        # Append callback of the instance and the corresponding ir code 
        ir_tuple = instance_cbk, ir_up, ir_down
        cls._instances_datas.append(ir_tuple) 

    def __init__(self, encoder, initial_level = 125, max_level = 255, name=""):
        global _nb_instance
        self.__class__._nb_instance += 1
        self.pot_pos = self._nb_instance
        self.pot_name = str(self.pot_pos) if name == "" else name
        self.max_level = max_level
        self.level = initial_level
        encoder.register_callback(self.encoder_rotation)
        print("create potentiometer instance:{} initial_level:{} max_level:{} name:{}".format(
                self._nb_instance, initial_level, max_level, name))

    # Add up/down code and link them to this instance
    def attach_IR_Code(self, up, down):
        LogicPotentiometer.register_instance( self.instance_ir_callback, up, down)
        pass
    
    def instance_ir_callback(self, increment):
        print("Ir add {} to pot {}".format(increment, self.pot_name))
        pass

    def encoder_rotation(self, increment, sel_pot):
        # print( "Rotation of {} for pot {} ".format(increment, sel_pot))
        self.level += increment
        if self.level > self.max_level:
            self.level = self.max_level
        if self.level < 0:
            self.level = 0
        self.update_level()

    def update_level(self):
        print("Pot '{:1d}' level:{:3d} ({})".format(self.pot_pos, self.level, self.pot_name))



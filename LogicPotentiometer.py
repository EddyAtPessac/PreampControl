# Logic potentiometer class
# This class manage the level of one potentiometer (sutch as volume, or balance)
# It using the Encoder and IRdecoder class to manage the output level 
# Each object is a new potentiometer and could be activated in rolling mode with the encoder push

from Encoder import *

class LogicPotentiometer():

    _nb_instance = 0
    _instances_datas = list()

    @classmethod
    def ir_callback(cls, data, addr, ctrl):
        print("search for {:02X}".format(data))
        for instance_cbk, up, down in cls._instances_datas:
            if data == up:
                instance_cbk(+1)
            if data == down:
                instance_cbk(-1)

    @classmethod
    def register_instance(cls, instance_cbk, ir_up, ir_down):
        # Append callback of the instance and the corresponding ir code 
        cls._instances_datas.append(instance_cbk, ir_up, ir_down) 

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



from machine import Pin
from time import ticks_ms
from utime import ticks_us
from LogicPotentiometer import LogicPotentiometer # To get base_increment

class Encoder():
    """ Gestion d'un encodeur rotatif """

    # Constants used in ms
    pushWait = 0
    push_debound_time = 2
    long_push = 50
    speedFast_1 = 10
    speedFast_2 = 40

    # Class variables: these variables depend from only one hard equipment
    pushTime = 0  # Measure from the last event of the push buton
    rotTime = 0   #   Measure from the last event of the rotating buton
    lastAState = 0   # Last state of pin A from the encoder
    
    # Last action memorised
    ENCODER_NONE = 0
    ENCODER_RIGHT = 1
    ENCODER_LEFT = 2
    ENCODER_PUSH = 3

    DEFAULT_PINA = 36
    DEFAULT_PINB = 37
    DEFAULT_PINBP = 38


    def __init__(self, pin_A = DEFAULT_PINA, pin_B = DEFAULT_PINB, pin_BP = DEFAULT_PINBP):
        print("Create Encoder {}  pin_A: {}, pin_BP: {}".format(self, pin_A, pin_BP))
        #self.pushSel = 0    # Decide which potentiometer is selected, and then, called to update_level()
        #self.cli_count = 0   # Number of registered client
        #self.cli_callback = []  # Callback for each client
        self.base_increment = LogicPotentiometer.base_increment
        self.pin_A = pin_A
        self.pin_B = pin_B
        self.pin_BP = pin_BP
        self.encoderChange = self.ENCODER_NONE
        self.lastAState = 0
        self.inA = Pin(pin_A, Pin.IN, Pin.PULL_UP)
        self.inB = Pin(pin_B, Pin.IN, Pin.PULL_UP)
        self.inBp = Pin(pin_BP, Pin.IN, Pin.PULL_UP)
        self.pushTime =  ticks_ms()
        self.inA.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = self.interruptHdl)
        self.inBp.irq(trigger =  Pin.IRQ_FALLING, handler = self.interruptHdl)


    def register_callback(self, callback):
        """ This function is called by the potentiometer to register this change_level() handler """
        pass
        #self.cli_callback.append(callback) 
        #print("register {} adress {}  list len: '{}'".format(callback.__name__, hex(id(callback)), len(self.cli_callback)))


    #Interrupt handler for all Pins
    def interruptHdl(self, pin):

        if pin == Pin(self.pin_A):
            #print("Pin A")
            self.manageEncoderRotation()
        elif pin == Pin(self.pin_BP): 
            #print("Pin Push")
            self.manageEncoderPush()
        # print('ISR EncoderChange:{}'.format(pin))


    def manageEncoderPush(self):
        dtime = ticks_ms() - self.pushTime
        self.pushTime = ticks_ms() + self.pushWait # Do not accept next push until wait time
        if dtime < self.push_debound_time:
            print ('push rebound')
            return
        # if dtime > self.long_push:
        #     print("long push")
        #     return

        LogicPotentiometer.select_next()    # Select the next one

        #old design 
        # self.pushSel += 1
        # if self.pushSel >= len(self.cli_callback):
        #     self.pushSel = 0
        # print( "PushSel:{}".format(self.pushSel))
        # # self.pushTime = ticks_ms() + self.pushWait # Do not accept next push until wait time
        # self.encoderChange = self.ENCODER_PUSH
        # if (len(self.cli_callback) > 0):    # If at least one potentiometer is registered 
        #     print("Call callback changeLevel(0) {}".format(self.pushSel))
        #     self.cli_callback[self.pushSel](0)  # Call  LogicPotentiometer.changeLevel()



    def manageEncoderRotation(self):
        inc = 1
        
        # Check time between to 2 interuption 
        dtime = ticks_ms() - self.rotTime
        if dtime < self.push_debound_time:
            return
        if dtime < self.speedFast_1:
            inc = 10 
        elif dtime < self.speedFast_2:
            inc = 5 

        bState =  self.inB.value()
        aState =  self.inA.value()
        # print("lastA:{}  B:{}".format(self.lastAState, bState))
        if bState != self.lastAState:
            self.encoderChange = self.ENCODER_LEFT
            inc *= -1
        else:
            self.encoderChange = self.ENCODER_RIGHT
        print("time: {}, Increment:{}".format(dtime, inc))
        inc *= self.base_increment
        self.rotTime = ticks_ms()
        self.lastAState = aState
        LogicPotentiometer.change_pot_level(inc)
        #if (True and len(self.cli_callback) > 0):    # If at least one potentiometer is registered 
        #    self.cli_callback[self.pushSel](inc)  # Call  LogicPotentiometer.changeLevel()
        
    """
    Ancienne tentative pour faire un heritage. Au final, on laisse tomber, c'est a l'utilisateur
    de créer l'objet encodeur, et d'utiliser cet objet pour la gestion des Potentiometer
 
    _Pin_A_dict = {} 
    _Callback_list =[]
    _Register_count = 0

    # The __new__ () is called just before __init__() when we try to instanciate a new object
    # If this class is used with the same PinA that is already used, we return the same instance
    # with the same pin. This is done to avoid to create multiple interupt for the same Pin
    # 

    Ici, ce new provoque une erreur sur le nom des arguments 
    other_params permet d'accepter les arguments nommes destines a LogicPotentiometer 
 
    def __new__(cls, callback, pin_A = DEFAULT_PINA, **other_params ):  
        #pin_A = other_params[pin_A]
        if pin_A in cls._Pin_A_dict:  # Is this Pin already used in another instance ?
            cls._Register_count +=1
            cls._Callback_list[cls._Register_count] = callback
            print ("New Encoder keep the instance {} with pin {} add callback #{} : {}".format(cls._Pin_A_dict[pin_A], pin_A, cls._Register_count, callback))
            return cls._Pin_A_dict[pin_A] # return the instance with this PinA definition
        #self = super(Encoder, cls).__new__(cls)  # Else create a new instance
        #cls._Pin_A_dict[pin_A] = self   
        self = object.__new__(cls)
        self.pin_A = pin_A
        cls._Pin_A_dict[pin_A] = self
        print ("New Encoder create the instance {} with pin {}".format(cls._Pin_A_dict[pin_A], pin_A))
        return self

    def __del__(self):
        del Encoder._Pin_A_dict[self.pin_A]

"""



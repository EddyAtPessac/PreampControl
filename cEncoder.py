from machine import Pin
from time import ticks_ms

# Pin used 
pinA = 36
pinB = 37 
pinBp = 38


class cEncoder:
    """ Gestion d'un encodeur rotatif """

    # Constants used
    pushWait = 0
    deboundTime = 2
    speedFast_1 = 5
    speedFast_2 = 20

    # Class variables: these variables depend from only one hard equipment
    pushTime = 0  # Measure from the last event of the push buton
    rotTime = 0   #   Measure from the last event of the rotating buton
    lastAState = 0   # Last state of pin A from the encoder
    
    # Last action memorised
    ENCODER_NONE = 0
    ENCODER_RIGHT = 1
    ENCODER_LEFT = 2
    ENCODER_PUSH = 3

    def __init__(self, _level = 127, _pushMax = 3):
        self.level = _level
        self.pushMax = _pushMax
        self.pushSel = 0
        self.encoderChange = self.ENCODER_NONE
        self.lastAState = 0
        self.inA = Pin(pinA, Pin.IN)
        self.inB = Pin(pinB, Pin.IN)
        self.inBp = Pin(pinBp, Pin.IN)
        self.pushTime =  ticks_ms()
        self.inA.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = self.interruptHdl)
        self.inBp.irq(trigger =  Pin.IRQ_FALLING, handler = self.interruptHdl)


    #Interrupt handler for all Pins
    def interruptHdl(self, pin):

        if pin == Pin(pinA):
            #print("Pin A")
            self.manageEncoderRotation()
        elif pin == Pin(pinBp): 
            #print("Pin Push")
            self.manageEncoderPush()
        # print('ISR EncoderChange:{}'.format(pin))


    def manageEncoderPush(self):
        dtime = ticks_ms() - self.pushTime
        if dtime < self.deboundTime:
            print ('to fast')
            return
        self.pushSel += 1
        print( "PushSel:{}".format(self.pushSel))
        if self.pushSel > self.pushMax:
            self.pushSel = 0
        self.pushTime = ticks_ms() + self.pushWait # Do not accept next push until wait time
        self.encoderChange = self.ENCODER_PUSH


    def manageEncoderRotation(self):
        inc = 1
        
        # Check time between to 2 interuption 
        dtime = ticks_ms() - self.rotTime
        if dtime < self.deboundTime:
            return
        if dtime < self.speedFast_1:
            inc = 10
        elif dtime < self.speedFast_2:
            inc = 5

        bState =  self.inB.value()
        aState =  self.inA.value()
        #print("lastA:{}  B:{}".format(lastAState, bState))
        if bState != self.lastAState:
            self.encoderChange = self.ENCODER_LEFT
            inc *= -1
        else:
            self.encoderChange = self.ENCODER_RIGHT

        #print("time: {}, Increment:{}".format(dtime, inc))
        self.level += inc
        if  self.level < 0: 
             self.level = 0
        if  self.level > 255:
             self.level = 255

        self.rotTime = ticks_ms()
        self.lastAState = aState


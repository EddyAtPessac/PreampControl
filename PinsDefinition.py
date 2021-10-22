# 
print ("Chargement PinDefinition")

# Pins 6, 7, 8, 11, 16, and 17 are used for connecting the embedded flash, and are not recommended for other uses
# Pins 34-39 are input only, and also do not have internal pull-up resistors

hardware = "ESP_V2_1"
if hardware == "ESP_V2_1":
    print("Hardware pin:", hardware)
    PIN_ENCODER_A = 36
    PIN_ENCODER_B = 37
    PIN_ENCODER_PUSH = 38
    PIN_IR_RECEVER = 39
    # Note: PWM on pin 19 doesnt  work, we use pin 17 instead
    PIN_PWM_VOL = 17
    PIN_PWM_BAL = 23
    PIN_PWM_BAS = 18
    PIN_PWM_TRE = 5
    PIN_NEOLED_OUT = 22
# Module meca assemblé avec ESP V1
if hardware == "ESP_V1":
    print("Hardware pin:", hardware)
    PIN_ENCODER_A = 36
    PIN_ENCODER_B = 37
    PIN_ENCODER_PUSH = 38
    PIN_IR_RECEVER = 39
    PIN_PWM_VOL = 25
    PIN_PWM_BAL = 26
    PIN_PWM_BAS = 27
    PIN_PWM_TRE = 14
    PIN_NEOLED_OUT = 12

# Module meca assemblé avec ESP_V2
if hardware == "ESP_V2_2":
    print("Hardware pin:", hardware)
    # La PIN 17 est occupée (peut-être par U2 TXD)
    PIN_ENCODER_A = 36
    PIN_ENCODER_B = 37
    PIN_ENCODER_PUSH = 38
    PIN_IR_RECEVER = 39
    PIN_PWM_VOL = 17
    PIN_PWM_BAL = 5
    PIN_PWM_BAS = 18
    PIN_PWM_TRE = 23
    PIN_NEOLED_OUT = 22




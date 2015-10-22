import webiopi
import datetime

GPIO = webiopi.GPIO

now = datetime.datetime.now()
KOTEL = 17 # GPIO pin using BCM numbering
#NOFROZEN = 12 # No Frozen Temperature
REQTEMP = 21 # Required temperature
HYSTER = 0.2  # Hysteresis
EKONOM = 1.2   # hysteresis for Temperature >16

# setup function is automatically called at WebIOPi startup
def setup():


    # set the GPIO used by the light to output
    GPIO.setFunction(KOTEL, GPIO.OUT)

    # retrieve current datetime
    global now
    now = datetime.datetime.now()


    GPIO.digitalWrite(KOTEL, GPIO.HIGH)

# loop function is repeatedly called by WebIOPi
def loop():

    tmpLR = webiopi.deviceInstance("Living_room")
    celsLR = tmpLR.getCelsius()

    if (REQTEMP>16):
        correct = HYSTER
    else:
        correct = EKONOM

    if (celsLR>(REQTEMP+correct)):
        GPIO.digitalWrite(KOTEL, GPIO.LOW)

    if (celsLR<(REQTEMP-correct)):
        GPIO.digitalWrite(KOTEL, GPIO.HIGH)

    # toggle light ON all days at the correct time
    #if (now.minute != datetime.datetime.now().minute ):
    #    if (GPIO.digitalRead(KOTEL) == GPIO.LOW):
    #        GPIO.digitalWrite(KOTEL, GPIO.HIGH)

    #    else:
    #        (GPIO.digitalRead(KOTEL) == GPIO.HIGH)
    #        GPIO.digitalWrite(KOTEL, GPIO.LOW)

    #    global now
    #    now = datetime.datetime.now()

    # gives CPU some time before looping again
    webiopi.sleep(3)

# destroy function is called at WebIOPi shutdown

def destroy():
    GPIO.digitalWrite(KOTEL, GPIO.LOW)

@webiopi.macro
def getReqTemp():
    return REQTEMP

# State of Gase heater, ON or OF
@webiopi.macro
def ignition():
    if (GPIO.digitalRead(KOTEL)==GPIO.HIGH):
        return 1
    else:
        return 0
@webiopi.macro
def plusReqTemp():
    global REQTEMP
    if (REQTEMP>=30):  return getReqTemp()
    REQTEMP=REQTEMP+0.5
    return getReqTemp()

@webiopi.macro
def minusReqTemp():
    global REQTEMP
    if (REQTEMP<=5):  return getReqTemp()
    REQTEMP=REQTEMP-0.5
    return getReqTemp()

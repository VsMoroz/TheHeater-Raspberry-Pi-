import webiopi
import datetime

GPIO = webiopi.GPIO

now = datetime.datetime.now()
KOTEL = 17 # GPIO pin using BCM numbering
#NOFROZEN = 12 # No Frozen Temperature
REQTEMP = 15 # Required temperature
HYSTER = 0.2  # Hysteresis
EKONOM = 0.2   # hysteresis for Temperature >16
statClass = None

# setup function is automatically called at WebIOPi startup
def setup():


    # set the GPIO used by the light to output
    GPIO.setFunction(KOTEL, GPIO.OUT)

    # retrieve current datetime
    global now
    now = datetime.datetime.now()
    GPIO.digitalWrite(KOTEL, GPIO.HIGH)

    global statClass
    statClass = Statistics()



# loop function is repeatedly called by WebIOPi
def loop():

    tmpLR = webiopi.deviceInstance("Living_room")
    celsLR = tmpLR.getCelsius()
    tmpCoolant = webiopi.deviceInstance("Coolant")
    celsCoolant = tmpCoolant.getCelsius()

    global statClass
    statClass.saveTemp(celsLR,celsCoolant)

    if (REQTEMP>=16):
        correct = HYSTER
    else:
        correct = EKONOM

    if (celsLR>(REQTEMP+correct)):
        GPIO.digitalWrite(KOTEL, GPIO.LOW) # off Heater

    if (celsLR<(REQTEMP-correct) and (ignition()==0) ):
        GPIO.digitalWrite(KOTEL, GPIO.HIGH) # on Heater
        statClass.timeON = datetime.datetime.now()

    #qw =  (datetime.datetime.now()- statClass.timeON).seconds


    if (ignition()==1 and (datetime.datetime.now()- statClass.timeON).seconds>60):
        statClass.addOnMinute()
        statClass.timeON =datetime.datetime.now()

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

class Statistics:
      rqTemp = REQTEMP
      currMax=0
      currMin=0
      coolMax=0
      coolMin=0
      onMinutes = 0
      currTemp = 0
      coolTemp = 0
      gasState = 0
      tmstamp = datetime.datetime.now()
      timeON = datetime.datetime.now()

      def __init__(self):
         #tmstamp = datetime.datetime.now()
         tmpLR = webiopi.deviceInstance("Living_room")
         celsLR = tmpLR.getCelsius()

         tmpCoolant = webiopi.deviceInstance("Coolant")
         celsCoolant = tmpCoolant.getCelsius()

         self.currMax=celsLR
         self.currMin=celsLR
         self.coolMax=celsCoolant
         self.coolMin=celsCoolant
         self.currTemp = celsLR
         self.coolTemp = celsCoolant
         tmstamp = datetime.datetime.now()
         timeON = datetime.datetime.now()

      def saveTemp(self,curr,cool):
           if (curr>self.currMax):
               self.currMax=curr
           if (curr<self.currMin):
               self.currMin=curr
           if (cool>self.coolMax):
               self.coolMax=cool
           if (cool<self.coolMin):
               self.coolMin=cool
           self.currTemp=curr
           if (cool>self.coolTemp and GPIO.digitalRead(KOTEL)==GPIO.HIGH):
               self.gasState=1
           else:
               self.gasState=0

           self.coolTemp =cool

      def passedDays(self):
           return (datetime.datetime.now()-self.tmstamp).days

      def getMinOnHeater(self):
           return self.onMinutes

      def addOnMinute(self):
          self.onMinutes=self.onMinutes+1


@webiopi.macro
def getReqTemp():
    return REQTEMP

# State of the water pump, ON or OFF
@webiopi.macro
def wp():
    if (GPIO.digitalRead(KOTEL)==GPIO.HIGH):
        return 1
    else:
        return 0

# State of the Gase heater, ON or OFF
@webiopi.macro
def ignition():
     global statClass
     return statClass.gasState

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

@webiopi.macro
def getCurrTempMax():
    global statClass
    return statClass.currMax

@webiopi.macro
def getCurrTempMin():
    global statClass
    return statClass.currMin

@webiopi.macro
def getCoolTempMax():
    global statClass
    return statClass.coolMax

@webiopi.macro
def getCoolTempMin():
    global statClass
    return statClass.coolMin

@webiopi.macro
def statReset():
    global statClass
    statClass = Statistics()

@webiopi.macro  # How many days ago was reseted statistic class
def passedD():
    global statClass
    return statClass.passedDays()

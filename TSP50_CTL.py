import RPi.GPIO as GPIO
import time
import sys


class TSP_CTL:
    def __init__(self):
        self.DetectorGPIOs = [2, 3, 4, 17, 27, 22, 10]
        self.GPIO_BCM_channels = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,
			21,20,16,12,7,8,25,24,23,18,15,14]
        self.LED_MAPPING = {2:2, 3:3, 4:4, 5:17, 6:27, 7:22, 8:10}
        self.GREET_MAPPING = {'A':20, 'B':21}
        self.configTSP50()
        self.lastInt = -1
        self.GREETS = {}
        self.GREETS['A'] = GPIO.PWM(self.GREET_MAPPING['A'], 400) #200 Hz frequency to turn on GREET LED
        self.GREETS['B'] = GPIO.PWM(self.GREET_MAPPING['B'], 400) 
    
    def DETECTOR_ON_ALL(self):
            GPIO.output(self.DetectorGPIOs, False)

    def DETECTOR_OFF_ALL(self):
            GPIO.output(self.DetectorGPIOs, True)

    def configTSP50(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.GPIO_BCM_channels, GPIO.OUT)
        self.DETECTOR_OFF_ALL()

    def intToBinArr(self, n): #convert an int (8 bit int) to bits array
        b = bin(255-n)[2:] #complement exp. '0b0000110' => '0b1111001', there are total 8 LEDs 8 bits
        while (len(b) < 8):
            b = '0'+b
        arr = list(map(int, list(b)))
        arr = arr[::-1]
        return arr
    
    def update(self, n): #n is the int value represent 8 bits
        if n < 256 and n >= 0 and n != self.lastInt:
            print('signal updated to ' + str(n))
            self.lastInt = n
            self.LED_flags = self.intToBinArr(n)
            for i in range(1, 8):
                if i+1 in self.LED_MAPPING:
                    GPIO.output(self.LED_MAPPING[i+1], self.LED_flags[i]) # 0 is on

    def GREET_ON(self, c): # c is the char name to define the GREET LED name
        if c in self.GREETS:
            self.GREETS[c].start(1)

    def GREET_OFF(self, c): # c is the char name to define the GREET LED name
        if c in self.GREETS:
            self.GREETS[c].stop()
        
        

    def reset(self):
        self.DETECTOR_OFF_ALL()
        GPIO.cleanup()
        configTSP50()



        
def main():
    ctl_model = TSP_CTL()
    ctl_model.update(9)
    ctl_model.GREET_ON('A')
    

# test
if __name__ == '__main__':
    main()
        


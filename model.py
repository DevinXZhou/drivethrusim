import sys
import random
import time
import datetime
import numpy as np
import csv
from DataStruct import Car, QType, Queue
from TSP50_CTL import TSP_CTL

#alt 3 to comment lines alt 4 to uncomment

## MENU1 = BCM 2 = Detector 2
## MENU2 = BCM 3 = Detector 3
## CASH1 = BCM 4 = Detector 4
## CASH2 = BCM 17 = Detector 5
## PRESENT1 = BCM 27 = Detector 6
## PRESENT2 = BCM 22 = Detector 7

#QType_Param is a dictionary to specify queue properties
            #[LED index, wait average time, wait deviation, max queue size]
QType_Param = {'MENU0':[1, 30, 10, 5], 'MENU1':[2, 30, 12, 5], 'CASH0':[3, 15, 5, 4], 'CASH1':[4, 20, 5, 4],
             'PRESENT0':[5, 15, 7, 2], 'PRESENT1':[6, 20, 8, 2], 'TRANSIT':[-1, 5, 1, 2]}

    
class Model:
    def __init__(self, arch):
        
        # arch means architecture of the lane model
        # exp. if arch = [2, 1, 1] each number means the number of windows... two menu, one casher, one present, if no such item put 0 
        # then the sequence is converted to [[1, 1], [2], [3]]
        # this means two menu (1) queues joined to one casher(2) queue,
        # then goes to present(3) queue

        # architect is the actual architecture of the model, translated from "arch"
        # exp. if architect = [[1, 1], [2, 2], [3]], 
        # two menu m1, m2, two casher c1, c2 and one present, 1 means type 1 which is menu, 2 means cash, 3 means present
        # there are also [0] between them, 0 is the transition queue. architect = [[1, 1], [0, 0], [2, 2], [0], [3]]
        # m1 goes to c1 only, m2 goes to c2 only
        assert arch != []

        self.timer = 0 # in virtually seconds
        self.record = {}
        
        self.architect = []
        self.outInt = -1 #used to track if output intger is changed
        self.outBits = [] #output bits converted from output intger, 8 bits
        
        for i, n in enumerate(arch): #translate arch into architect, add transition queues between each queue
            if n != 0:
                self.architect.append([i+1]*n)
                if i < len(arch)-1:
                    self.architect.append([0]*n) #adding transition queues between other queues

        
        self.queues = [] #store each constructed queue in here
        
        self.construct() #construct queues from translated "architect"
        self.link() #link one queue tail to another queue's head
            
        
    def construct(self): #build queue based on types, mean random wait time of the window (menu or casher)
                         #add transition queue between two queues
        i = 0 # skip transit
        for k, lanes in enumerate(self.architect):
            arr = []
            for j, qtype in enumerate(lanes):
                if qtype == 0:
                    name = 'TRANSIT'
                    arr.append(Queue(QType(qtype), QType_Param[name][1],
                                     QType_Param[name][2], QType_Param[name][3], j))
                else:
                    name = str(QType(qtype))[6:] + str(j)
                    arr.append(Queue(QType(qtype),  QType_Param[name][1],
                                     QType_Param[name][2], QType_Param[name][3], j))
            self.queues.append(arr)
            if k%2 == 1:
                i += 1
                
    def push(self, car): # push in model will automatically decide which next queue the car will go, use the number of cars from each of next queue as score
        if self.queues and self.queues[0]:
            score = sys.maxsize
            idx = 0
            for i, q in enumerate(self.queues[0]):
                if q.score < score:
                    score = q.score
                    idx = i
        self.queues[0][idx].push(car)
                

    def link(self): #exp, link the menu queue tail to casher queue head
        n = len(self.queues)
        print ("total queues: " + str(n))

        #link all the queques exp. menu queue link to a transition queue, transition queue link to casher queue
        if n >= 2:
            for i in range(0, n-1):
                if len(self.queues[i]) == len(self.queues[i+1]):
                    for j in range(0, len(self.queues[i])):
                        self.queues[i][j].nextqs.append(self.queues[i+1][j])
                else:
                    for j in range(0, len(self.queues[i])):
                        self.queues[i][j].nextqs = self.queues[i+1]
    
        
                        
    def timing(self): #model queues wait time count down
        for arr in self.queues:
            for q in arr:
                q.count_down() #wait time count down for each first car in each queue
                q.wait_time_count()

    def minToSeconds(time):#input is a time string such as 06:00 means 6 minutes
        arr = list(map(int, time.split(':')))
        seconds = 0
        power = 1
        for n in arr:
            seconds += n*(60**power)
            power -= 1
        return seconds
    
    
    def status(self): #call queue status
        print('processing vitual time: ' + str(self.timer) + ' s')
        for arr in self.queues:
            for q in arr:
                q.status()
        s = ''.join(list(map(str, self.outBits)))
        s = s[::-1]
        print('bits: ' + s) 
        print ('======================================================================================================')

    def getbits(self):
        bits = [0]
        for i, arr in enumerate(self.queues):
            if i%2 == 0:
                for q in arr:
                    bits.append(q.detect())
        while(len(bits) < 8):
            bits.append(0)
          
        return bits[::-1]

    def getint(self): #convert LED binary flags to an int
        s = ''.join(list(map(str, self.outBits)))
        s = '0b' + s
        return int(s, 2)

    def update(self, report_status = False):
        self.outBits = self.getbits()
        self.outInt = self.getint()
        if report_status:
            self.status()
        
        

    def writeCSV(self, filename = 'data/data_', timestamp = 'None'):
        filename = filename + timestamp + '.csv'
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in sorted(self.record.items()):
               writer.writerow([key, value])

    def readCSV(self, filename = 'timeline.csv'):
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            self.record = dict(reader)


           

class Scheduler:

    def __init__(self, carPerHr = 50, start_time = "06:00", end_time = "22:00"): #st is the store day starting time, et is the day ending time
        
        self.carPerHr = carPerHr
        self.totalCars = 0
        self.lastInt = -1
    
        self.st = start_time
        self.et = end_time
        self.car_queue_t = []
        self.sim_t = self.hrToSeconds(self.et) - self.hrToSeconds(self.st) #simulation time in seconds
        self.time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        
        
    def hrToSeconds(self, time):#input is a time string such as 06:00 means 6 am in the morning
                            # 06:00:00 is the same, return an int as number of seconds
        arr = list(map(int, time.split(':')))
        seconds = 0
        power = 2
        for n in arr:
            seconds += n*(60**power)
            power -= 1
        return seconds


    def car_seq_generator(self, time): # generate cars in a time manner in seconds, time is a priod in seconds
        n = int(time/3600*self.carPerHr)
        #sorted(np.random.randint(time, size=n))
        arr = np.int_(sorted(np.random.uniform(1,time,n)))
        arr = list(np.unique(arr))
        
        return arr
        

    def simulate(self, model, TSP_CTL, speedup = 1, display = False): # speedup = 1 means realtime
                                                                      # speedup = 0 means simulating the traffic and record the data into a csv immediately
        tic = 0
        toc = self.sim_t
        print ('total simulation time will be ' + str(self.sim_t) + ' seconds')
        print ('total simulation time will be approximate of ' + str(int(self.sim_t/60)) + ' minutes')
        tmp = int(self.sim_t/60/60)
        if tmp > 0:
            print ('total simulation time will be approximate of ' + str(tmp) + ' hours')
        self.car_queue_t = self.car_seq_generator(toc)
        self.totalCars = len(self.car_queue_t)
        idx = 0
        print ('generated ' + str(len(self.car_queue_t)) + ' cars in simulation queue')
        print ('Simulation start time at '+ self.st + ' and will end at '+self.et)
        if speedup == 1:
            print ('Simulation is in real time, will start in 5 seconds')
            time.sleep(5)
        elif speedup == 0:
            print ('Generating simulation data')
        else:
            print ('Simulation is speeded up by ' +speedup + 'times, and will start in 5 seconds')
            time.sleep(5)

        if ~display:
            print ('Drive through traffic queue display are hidden')

        if speedup == 0:
            print ('Simulating...........')
            
        while (tic < toc):
            if speedup != 0:
                start_time_ms = int(round(time.time())*1000) #timer on computer, to track program execution time
            
            if idx < self.totalCars and tic == self.car_queue_t[idx]:
                if display:
                    print('one car in, now generated total of |' + str(idx+1) + '| cars')
                model.push(Car(idx))
                idx += 1
            model.timer = tic

            model.update(report_status = display)
            model.timing()
        
            n = model.outInt
            
            if n != self.lastInt:
                self.lastInt = n
                model.record[tic] = n
                               
            if speedup != 0:
                past_time_ms = int(round(time.time())*1000) - start_time_ms
                sleep_time = 1000 - past_time_ms
                if sleep_time >= 0: #BUG running on raspberry pi2, timer chip is bad
                    TSP_CTL.update(n)
                    time.sleep(sleep_time/1000/speedup)
            tic += 1

        
        print ("generated "+ str(len(model.record)) + " time variables")

        model.writeCSV(timestamp = self.time_stamp)
        
                
            
def main():
    
    st = "06:00"
    et = "22:00"
    
    model = Model([2, 1, 1])
    #print (m1.architect)
    scheduler = Scheduler(90, st, et)
    TSP_Controller = TSP_CTL()

    scheduler.simulate(model, TSP_Controller, speedup = 1, display = False)
    


# test
if __name__ == '__main__':
    main()
    


























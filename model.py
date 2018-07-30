import sys
import random
import time
import datetime
import numpy as np
import csv
import json
from DataStruct import Car, QType, Queue, Delay
from TSP50_CTL import TSP_CTL
import logging
from Logger import Logger
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
    # filename = './setting/settings.json'
    def __init__(self, setting, arch=None):
        
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
        #assert arch != []
        self.logger  = logging.getLogger('Drive Through Infor')
        self.errorLogger  = logging.getLogger('Error Report')
        self.Transit_Param = [5, 1, 1] # parameters for transition queue [average wait time, wait time deviation, queue size]
        self.timer = 0 # in virtually seconds
        self.record = {}
        self.architect = []
        self.outInt = -1 #used to track if output intger is changed
        self.outBits = [] #output bits converted from output intger, 8 bits
        self.queues = [] #store each constructed queue in here

        if arch:
            for i, n in enumerate(arch): #translate arch into architect, add transition queues between each queue
                if n != 0:
                    self.architect.append([i+1]*n)
                    if i < len(arch)-1:
                        self.architect.append([0]*n) #adding transition queues between other queues
                        
            self.construct() #construct queues from translated "architect"
            
        else:
            self.set_up(setting)

        self.link() #link one queue tail to another queue's head
        #self.logger = logging.getLogger('Model')
        #logging.basicConfig(level=logging.DEBUG,
                    #format='%(asctime)s %(levelname)s %(message)s',
                    #filename='./log/example.log',
                    #filemode='w')
        
            

    ######################### Depreciated #########################
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
    ###############################################################
                

    def set_up(self, setting): #parse setup file and construct queues
        
        queues_parallel = []
        transit_number = 1
        entrance_queue_size = 4
        random_wait = True
        if setting['store']['random'] == 'n':
            random_wait = False
            #self.Transit_Param = [1, 1, 1]
    
        for detector in setting['detectors']:
            if detector['name'] and 'Greet' not in detector['name']:
                q = Queue(detector['wait_avg'], detector['wait_dev'], detector['qsize'], detector['name'], random_wait, detector['LED'])
                
                if not queues_parallel: #empty
                    queues_parallel.append(q)
                else:
                    assert len(q.name) >= 4
                    if q.name[0:4] == queues_parallel[0].name[0:4]: #check if they are same type of windows by checking name
                        queues_parallel.append(q)
                    else:
                        self.queues.append(queues_parallel)
                        transit_parallel = []
                        for i in range(len(queues_parallel)):
                            transit_queue = Queue(self.Transit_Param[0], self.Transit_Param[1], self.Transit_Param[2], 'Transit '+str(transit_number)) #3 seconds average, 1 second dev, queue size 1
                            transit_number += 1
                            transit_parallel.append(transit_queue)
                        self.queues.append(transit_parallel)
                        queues_parallel = [q]

        if queues_parallel:
            self.queues.append(queues_parallel)

        # fix the max queue size due to different implementation
        idx = len(self.queues)-1
        while(idx >= 0):
            if idx - 2 >= 0:
                for i, q in enumerate(self.queues[idx]): # assume the number of next queues is always smaller or equal, which is true in drive through
                    q.maxsize = self.queues[idx - 2][i].maxsize
            idx -= 2

        if self.queues[0]:
            for q in self.queues[0]:
                q.maxsize = entrance_queue_size
            

        self.logger.info('=================================== Displaying Model Setup ===================================')
        for arr in self.queues:
            for q in arr:
                q.display_settings()
                
                
            
        
                
    def push(self, car): # push in model will automatically decide which next queue the car will go, use the number of cars from each of next queue as score
        if self.queues and self.queues[0]:
            score = [0]*len(self.queues[0])
            idx = 0
            for qs in self.queues:
                for i in range(len(score)):
                    if i < len(qs):
                        score[i] += qs[i].score
            idx = score.index(min(score))
            self.queues[0][idx].push(car)
            self.queues[0][idx].push(Delay(-1))
                

    def link(self): #exp, link the menu queue tail to casher queue head
        n = len(self.queues)
        #link all the queques exp. menu queue link to a transition queue, transition queue link to casher queue
        if n >= 2:
            for i in range(0, n-1):
                if len(self.queues[i]) == len(self.queues[i+1]):
                    for j in range(0, len(self.queues[i])):
                        self.queues[i][j].qid = i
                        self.queues[i][j].nextqueue = self.queues[i+1][j]
                        self.logger.info(self.queues[i][j].name + ' is linking to '+ self.queues[i+1][j].name)
                else:
                    for j in range(0, len(self.queues[i])):
                        self.queues[i][j].nextqueue = self.queues[i+1][0]
                        self.logger.info(self.queues[i][j].name + ' is linking to ' + self.queues[i+1][0].name)
    
        
                        
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
    
    def lineUp(self, var, length, fillin): #line up the int string for print out
        newstr = str(var)
        assert len(newstr) <= length
        if len(newstr) < length:
            newstr = ''.join([fillin]*(length - len(newstr))) + newstr
        return newstr

    
    def secToHr(self, n):
        hr = int(n/3600)
        mi = int((n-hr*3600)/60)
        sec = n - hr*3600 - mi*60
        return self.lineUp(hr, 2, '0') + ':'+self.lineUp(mi, 2, '0') + ':' + self.lineUp(sec, 2, '0')

        
    def status(self): #call queue status
        self.logger.info('Processing Vitual Time: ' + str(self.secToHr(self.timer)) + ' | ' + str(self.timer) + ' seconds')
        for arr in self.queues:
            for q in arr:
                q.status()
        s = ''.join(list(map(str, self.outBits)))
        s = s[::-1]
        self.logger.info('Output Bits: ' + s) 
        self.logger.info('================================================================================================')
        #print ('================================================================================================')

    def getbits(self):
        bits = []
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

    def update(self):
        self.outBits = self.getbits()
        self.outInt = self.getint()

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


           

class Scheduler: #simulation per day
    
    def __init__(self, model, TSP_Controller, setting, offset = 0): #offset is the number of days from now on, when is this simulating in the future
        
    #def __init__(self, carPerHr = 50, start_time = "06:00", end_time = "22:00"): #st is the store day starting time, et is the day ending time
        self.model = model
        self.tsp_ctl = TSP_Controller
        self.wd = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'} #weekday dictionary
        self.weekday_int = (datetime.datetime.today().weekday()+offset)%7
        self.weekday = self.wd[self.weekday_int] #string of weekday
        self.wkday_type = None
        self.logger  = logging.getLogger('Drive Through Infor')
        self.error_logger  = logging.getLogger('Error Report')
        if self.weekday_int < 5:
            self.wkday_type = 'wkday'
        else:
            self.wkday_type = 'wkend'
        
        self.carPerHr = setting['store']['car_freq']
        
        self.totalCars = 0
        self.lastInt = -1
        
        self.now = datetime.datetime.now()

        if offset == 0:
            self.st = self.now.hour*60*60 + self.now.minute*60 + self.now.second #simulation start time in seconds
        else:
            self.st = 0
            
        self.et = 24*60*60
        self.car_queue_t = []
        self.sim_t = self.et - self.st #total simulation time in seconds in this day
        self.sim_t_hr = self.sim_t/60/60
        self.time_stamp = datetime.datetime.fromtimestamp(time.time()+self.et*offset).strftime('%Y-%m-%d %H:%M:%S')
        self.time_stamp_date = datetime.datetime.fromtimestamp(time.time()+self.et*offset).strftime('%Y-%m-%d')

        self.logger.info('========================= New Day Schedule on ' + self.time_stamp_date+' '+self.weekday+' Created =========================')
        self.logger.info(str(self.carPerHr)+' Cars per Hour')
        self.logger.info('Total Simulation Time is '+format(self.sim_t_hr , '.2f') + ' hours')

        self.car_seq_generate(self.time_segment(setting))
        
        self.logger.info('================================================================================================')

    def time_segment(self, setting):
        #check if open
        open_time = 0
        close_time = 0
        windows = []
        for store_hr in setting['store_hours']:
            if store_hr['day'] == self.weekday:
                if store_hr['open'] == 'y':
                    open_time = self.hrToSeconds(store_hr['open_time'])
                    self.logger.info('Store opens at '+store_hr['open_time'])
                    close_time = self.hrToSeconds(store_hr['close_time'])
                    self.logger.info('Store closes at '+store_hr['close_time'])
                else:
                    return [] #terminate this function and leave car_queue_t to be [] if it is a close day
        bst = max(open_time, self.st) #business start time
        bet = min(close_time, self.et) #business end time

        self.logger.info('Total business hours are '+format((bet - bst)/3600, '.2f'))
        
        #check if today has peak hours     
        for phr in setting['peak_hours']:
            if phr[self.wkday_type] == 'y':
                window = [self.hrToSeconds(phr['start']), self.hrToSeconds(phr['end']), (1+phr['percent_inc']/100)*self.carPerHr]
                windows.append(window)
                assert window[1] <= bet

        added = False
        peak_n = len(windows)
        segments = []
        
        for idx, w in enumerate(windows):
            if bst < w[0] and added == False:
                segments.append([bst, w[0], self.carPerHr])
                added = True
                #print ('added first')

            if bst >= w[0] and bst < w[1]:
                w[0] = bst
                segments.append(w)
                added = True
                #print ('added between')
                
                if idx + 1 == peak_n:
                    segments.append([w[1], bet, self.carPerHr])
                    #print ('added last')
                else:
                    segments.append([w[1], windows[idx+1][0], self.carPerHr])
                    #print ('added mid')
                    
            if w[0] > bst and w[1] > bst:
                segments.append(w)
                if idx + 1 == peak_n:
                    segments.append([w[1], bet, self.carPerHr])
                    #print ('added last')
                else:
                    segments.append([w[1], windows[idx+1][0], self.carPerHr])
                    #print ('added mid')
                    
        if not segments and bst < bet:
            segments.append([bst, bet, self.carPerHr])
        #print (segments)
        return segments
            


        
    def hrToSeconds(self, time):#input is a time string such as 06:00 means 6 am in the morning
                            # 06:00:00 is the same, return an int as number of seconds
        arr = list(map(int, time.split(':')))
        seconds = 0
        power = 2
        for n in arr:
            seconds += n*(60**power)
            power -= 1
        return seconds

    def car_seq_generate(self, segments):
        if not segments:
            return
        else:
            for seg in segments:
                self.car_queue_t += self.generate(seg[0], seg[1], seg[2])
        #print (self.car_queue_t)
        #print (len(self.car_queue_t))
                
            
    def generate(self, st, et, freq): # generate cars in a time manner in seconds, time is a priod in seconds
        n = int((et-st)/3600*freq)
        arr = sorted(random.sample(range(st, et), n))
        
        return arr
        

    def simulate(self, speedup = 1, display_queue = False, display_signal = False): # speedup = 1 means realtime
                                                                      # speedup = 0 means simulating the traffic and record the data into a csv immediately
        tic = self.st
        toc = self.et
        self.totalCars = len(self.car_queue_t)
        idx = 0
        self.logger.info('*********************************** Day ' + self.time_stamp + ' ***********************************')
        self.logger.info('Generated ' + str(len(self.car_queue_t)) + ' cars in simulation queue')
        if speedup == 1:
            self.logger.info('Simulation is in real time')
        elif speedup == 0:
            self.logger.info('Generating simulation data instantly')
        else:
            self.logger.info('Simulation is speeded up by ' + str(speedup) + ' times')

        if not display_queue:
            self.logger.info('Drive through traffic queue display are hidden')


        printToggle = True
        
        while (tic < toc):
            if speedup != 0:
                start_time_ms = int(round(time.time())*1000) #timer on computer, to track program execution time
                
            if idx < self.totalCars and tic == self.car_queue_t[idx]:
                if display_queue:
                    self.logger.info('One car in, Now generated total of |' + str(idx+1) + '| cars')
                self.model.push(Car(idx))
                idx += 1
                printToggle = True
            
            self.model.timer = tic
                
            self.model.timing()
            self.model.update()
        
            n = self.model.outInt
            
            if n != self.lastInt:
                self.lastInt = n
                if display_signal:
                    self.logger.info('Signal updated to '+str(n))
                if display_queue:
                    self.model.status()
                #model.record[tic] = n

            if printToggle and idx + 1 < self.totalCars:
                self.logger.info('Next car is coming in ' + str(self.car_queue_t[idx+1] - tic) + ' seconds')
                printToggle = False
                               
            if speedup != 0:
                past_time_ms = int(round(time.time())*1000) - start_time_ms
                sleep_time = 1000 - past_time_ms
                if sleep_time >= 0: #BUG running on raspberry pi2
                    self.tsp_ctl.update(n)
                    time.sleep(sleep_time/1000/speedup)
                else:
                    self.error_logger.error('1 Second Time Calibration ERROR')
            tic += 1    
        
        self.logger.info('::::::::::::::::::::::::::::::::: Day ' + self.time_stamp_date + ' End :::::::::::::::::::::::::::::::::')
        time.sleep(10*60)

        #model.writeCSV(timestamp = self.time_stamp)
        
                
            
def main():
    
    #st = "06:00"
    #et = "22:00"
    
    #model = Model([2, 1, 1])
    #print (m1.architect)
    #scheduler = Scheduler(90, st, et)
    #TSP_Controller = TSP_CTL()

    #scheduler.simulate(model, TSP_Controller, speedup = 1, display = True)

    filename = './setting/settings.json'
    setting = json.load(open(filename))
    
    model = Model(setting)
    TSP_Controller = TSP_CTL()
    schedule = Scheduler(model, TSP_Controller, setting, 0)

    

# test
if __name__ == '__main__':
    main()
    


























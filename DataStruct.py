from enum import Enum
import random
import sys
import copy
import logging

class Car:  #linked list node
    def __init__(self, ID):
        self.id = ID
        self.timer = 0 # time to transit to another queue
        self.next = None
        self.total_wait = 0
        
class Delay:  #linked list node
    def __init__(self, ID):
        self.id = ID
        self.timer = 0 # time to transit to another queue
        self.next = None
        self.total_wait = 0

#class QType depreciated
class QType(Enum):
    TRANSIT = 0 # transition queue
    MENU = 1    # menu queue
    CASH = 2    # casher queue
    PRESENT = 3 # presenter queue
    GREET = 4
    
class Queue:
    def __init__(self, wait_avg, wait_dev, maxsize, name, rand_wait = True, LED = None): #average wait time and deviation wait time
        #assert isinstance(qtype, QType)
        self.logger  = logging.getLogger('Drive Through Infor')
        self.maxsize = maxsize
        self.qid = None
        self.name = name
        self.LED = LED
        self.n = 0 #number of cars in the queue
        self.head = None
        self.tail = None
        self.nextqueue = None #should be only one queue
        self.rand_wait = rand_wait
        self.score = 0 # priority score that new car should come in this queue
                        # the lower the better
                        # later on, wait time would involve calculation

        self.wait_avg = None
        self.wait_dev = None
        
        if isinstance(wait_avg, int):
            self.wait_avg = wait_avg
        else:
            self.wait_avg = self.minToSeconds(wait_avg)
            
        if isinstance(wait_dev, int):
            self.wait_dev = wait_dev
        else:
            self.wait_dev = self.minToSeconds(wait_dev)
        

    def examine(self): #examine the queue and update what to do when car timer is 0
        if self.head:
            if self.head.id > 0:
                if self.nextqueue:
                    if self.nextqueue.n < self.nextqueue.maxsize:
                        self.nextqueue.push(self.head)
                        self.pop()
                    else:
                        self.head.timer += 1
                        
                else: #no next queues, so pop out without consequences
                    self.pop()
            else:
                if self.nextqueue:
                    self.nextqueue.push(self.head)
                    self.pop()
                else:
                    self.pop()


    def pop(self):
        if self.head: #extra step to check if queue has at least one car

            if self.head.id > 0:
                self.n -= 1
                self.score -= 1
                
            nextCar = self.head.next
            self.head.next = None
            self.head = nextCar
            if self.head:
                if self.head.id > 0:
                    if self.rand_wait:
                        self.head.timer = self.random_wait()
                    else:
                        self.head.timer = self.wait_avg
                else:
                    self.head.timer = 2 # 2 seconds delay
            else:
                self.tail = None

            #############check here if still pull in

                      
                
    def push(self, car):
        tmp_id = car.id
        if self.n < self.maxsize and tmp_id > 0:
            
            if self.head == None:
                self.head = car
                self.tail = car

                if tmp_id > 0:
                    if self.rand_wait:
                        self.head.timer = self.random_wait()
                    else:
                        self.head.timer = self.wait_avg
                else:
                    self.head.timer = 2

            else:
                self.tail.next = car
                self.tail = self.tail.next
            self.n += 1
            self.score += 1
            
        if tmp_id < 0:
            if self.head == None:
                self.head = car
                self.tail = car
                self.head.timer = 2
            else:
                self.tail.next = car
                self.tail = self.tail.next

            
            

    def count_down(self):
        if self.head:
            if self.head.timer <= 0:
                self.examine()
            else:
                self.head.timer -= 1

    def wait_time_count(self):
        current = self.head
        while (current):
            current.total_wait += 1
            current = current.next
            if (self.qid == 0):
                break
            
    def random_wait(self): #generate random wait time
        return round(random.normalvariate(self.wait_avg, self.wait_dev))

    def detect(self):
        if self.head:
            if self.head.id > 0: 
                return 1 #exist a car
            return 0 
        return 0
    
    def getname(self):
        return self.name

    def lineUp(self, var, length, fillin): #line up the int string for print out
        if var == 'N':
            newstr = 'N/A'
            while (len(newstr) < length):
                newstr = fillin + newstr
            return newstr
        newstr = str(var)
        assert len(newstr) <= length
        if len(newstr) < length:
            newstr = ''.join([fillin]*(length - len(newstr))) + newstr
        return newstr

    
    def minToSeconds(self, time):#input is a time string such as 06:00 means 6 minutes
        arr = list(map(int, time.split(':')))
        seconds = 0
        power = 1
        for n in arr:
            seconds += n*(60**power)
            power -= 1
        return seconds

    def secToMin(self, n):
        if n == 'N':
            return 'N/A'
        return self.lineUp(int(n/60), 2, '0') + ':' + self.lineUp(int(n%60), 2, '0')
        

    def status(self):
        wait_time = 0
        total_wait_time = 'N'
        ID = 'N'
        if self.head:              
            wait_time = self.head.timer
            ID = self.head.id
            total_wait_time = self.head.total_wait

                
        infor = 'Queue Event Name: '+ self.lineUp(str(self.name), 10, ' ') + "| VEH: " + self.lineUp(str(self.LED), 4,' ') + ' | cars: ' + str(self.n) + ' | cur_id: '+ self.lineUp(ID, 4, ' ') + ' | waits: '+ self.lineUp(wait_time, 3, ' ') + ' | total wait: ' + self.secToMin(total_wait_time)
        self.logger.info(infor)
        #print(infor)

    def display_settings(self):
        infor = 'Queue Event Name: '+ self.lineUp(str(self.name), 10, ' ') + "| VEH: " + self.lineUp(str(self.LED), 4, ' ') + ' | wait_avg: ' + self.secToMin(self.wait_avg) + ' | wait_dev: ' + self.secToMin(self.wait_dev) + ' | Queue Size: ' + str(self.maxsize)
        self.logger.info(infor)
        #print(infor)

        
# test
if __name__ == '__main__':
    q1 = Queue(30, 5, 1, 'Menu', False, '2')
    q2 = Queue(30, 5, 2, 'Cashier', False, '3')
    q1.nextqueue = q2
    q1.push(Car(1))
    q1.status()
    q2.status()
    q1.count_down()
    q2.count_down()
    q1.wait_time_count()
    q2.wait_time_count()
    q1.status()
    q2.status()
    while (q1.head):
        q1.count_down()
        q1.wait_time_count()
    q1.status()
    q2.status()

            
            


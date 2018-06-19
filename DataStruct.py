from enum import Enum
import random
import sys
import copy

class Car:  #doubly linked list node
    def __init__(self, ID):
        self.id = ID
        self.timer = 0 # time to transit to another queue
        self.next = None
        self.total_wait = 0

class QType(Enum):
    TRANSIT = 0 # transition queue
    MENU = 1    # menu queue
    CASH = 2    # casher queue
    PRESENT = 3 # presenter queue
    GREET = 4
    
class Queue:
    def __init__(self, qtype, wait_avg, wait_dev, maxsize, ID): #average wait time and deviation wait time
        assert isinstance(qtype, QType)
        self.maxsize = maxsize
        self.wait_avg = wait_avg
        self.wait_dev = wait_dev
        self.id = ID
        self.type = qtype
        self.n = 0 #number of cars in the queue
        self.head = None
        self.tail = None
        self.nextqs = [] #empty list of queues
        self.score = 0 # priority score that new car should come in this queue
                        # the lower the better
                        # later on, wait time would involve calculation
        self.lastCarID = -1

    def examine(self): #examine the queue and update what to do    
        if self.nextqs:
            idx = -1
            score = sys.maxsize
            extra_wait = sys.maxsize
            
            for i, q in enumerate(self.nextqs): #check which next queue is available
                if q.score < score and q.n < q.maxsize:
                    idx = i
                    score = q.score
                if q.head:
                    extra_wait = min(extra_wait, q.head.timer)
                    
            if idx != -1: #actually pop out a car to another queue
                self.nextqs[idx].push(self.head)
                self.pop()                 
            else: #not finding a pushable queue, adding extra wait time to current queue head car
                self.head.timer = extra_wait
                
        else: #no next queues, so pop out without consequences
            self.pop()

    def pop(self):
        if self.head: #extra step to check if queue has at least one car
            nextCar = self.head.next
            self.head.next = None
            self.head = nextCar
            if self.head:
                self.head.timer = self.random_wait()
            else:
                self.tail = None
            self.n -= 1
            self.score -= 1
                      
                
    def push(self, car):
        if self.n < self.maxsize:
            self.n += 1
            self.score += 1
            if self.head == None:
                self.head = car
                self.tail = car
                self.head.timer = self.random_wait()
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
            if (str(self.type)[6:] == 'MENU'):
                break
            
    def random_wait(self): #generate random wait time
        return round(random.normalvariate(self.wait_avg, self.wait_dev))

    def detect(self):
        if self.head:
            if self.head.id != self.lastCarID:
                self.lastCarID = self.head.id
                return 0
            return 1
        return 0
    
    def getname(self):
        return str(self.type)[6:] + str(self.id)

    def lineUp(self, var, length): #line up the int string for print out
        if var == 'N':
            return 'N/A'
        newstr = str(var)
        assert len(newstr) <= length
        if len(newstr) < length:
            newstr = ''.join(['0']*(length - len(newstr))) + newstr
        return newstr

    def secToMin(self, n):
        if n == 'N':
            return 'N/A'
        return self.lineUp(int(n/60), 2) + ':' + self.lineUp(int(n%60), 2)
        

    def status(self):
        wait_time = 0
        total_wait_time = 'N'
        ID = 'N'
        if self.head:
            wait_time = self.head.timer
            ID = self.head.id
            total_wait_time = self.head.total_wait
                
        if self.type == QType.MENU or self.type == QType.CASH:
            print ('Queue identity: '+ str(self.type) + str(self.id) + '    | cars: ' +
                   str(self.n) + ' | cur_id: '+ self.lineUp(ID, 3) + ' | waits: '+ self.lineUp(wait_time, 2) +
                   ' | total wait: ' + self.secToMin(total_wait_time))
        else:
            print ('Queue identity: '+ str(self.type) + str(self.id) + ' | cars: ' +
                   str(self.n) + ' | cur_id: '+ self.lineUp(ID, 3)  + ' | waits: '+ self.lineUp(wait_time, 2) +
                   ' | total wait: ' + self.secToMin(total_wait_time))

        #display next queue connection
##        if self.nextqs:
##            s = 'Next queues identities: '
##            for q in self.nextqs:
##                s += str(q.type) + str(q.id) + ' | '
##            print (s)
                


        
# test
if __name__ == '__main__':
    def printid(q):
        if q.head:
            print("head id = "+str(q.head.id))
            print("tail id = "+str(q.tail.id))
        else:
            print("empty")
        
    a = Car(1)
    b = Car(2)
    c = Car(3)
    d = Car(4)


    q1 = Queue(QType.MENU)
    q2 = Queue(QType.CASH)
    q3 = Queue(QType.PRESENT)

    q1.nextqs = [q2, q3]

    q1.push(a)
    q1.push(b)
    q1.push(c)

    q1.pop()

    printid(q2)
    printid(q3)

    q1.push(d)

    q1.pop()
    printid(q2)
    printid(q3)

    q1.pop()
    printid(q2)
    printid(q3)

    q1.pop()
    printid(q2)
    printid(q3)



            
            


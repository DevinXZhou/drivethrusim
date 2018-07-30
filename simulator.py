from model import Model, Scheduler
from TSP50_CTL import TSP_CTL
from Logger import Logger
import datetime
import time
import json
import argparse
import sys
import os

def parse():
    parser = argparse.ArgumentParser(description='Simulation Parameters')

    parser.add_argument('--viewq', type = int, help='display the information of all car queues in terminal')
    parser.add_argument('--viewn', type = int, help='display the intger that sending to TSP50')
    parser.add_argument('--spd', type = int, help='speed up the simulation process, 1 is real time, 0 means record the simulated data immediately, default=1')
    parser.add_argument('--file', type = str, help='confgure the setup for simulation, configure file are in json format and should be put in /setting folder')
    
    return parser.parse_args()


class Simulator:
    def __init__(self, filename = './setting/settings.json'):
        self.setting = json.load(open(filename))
        self.tsp_ctl = TSP_CTL(self.setting)
        self.infoLogDir = './log/record'
        self.errorLogDir = './log/error'
        self.extDir = '.log'

    def simulate(self, spd = 1, viewq = False, viewn = True):
        while (True):
            time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('<%Y-%m-%d>')

            logDir = self.infoLogDir + time_stamp + self.extDir
            errorLogDir = self.errorLogDir + time_stamp + self.extDir

            inforLog = Logger(logDir, 'msg').logger
            errorLog = Logger(errorLogDir, 'error').logger

            model = Model(self.setting)
            self.tsp_ctl.reset()
            new_schedule = Scheduler(model, self.tsp_ctl, self.setting)
            new_schedule.simulate(speedup = spd, display_queue = viewq, display_signal = viewn)
            self.tsp_ctl.reset()


def main():
    args = parse()

    
    #old_stdout = sys.stdout
    #log_file = open('./log/printout.log', 'w')
    #sys.stdout = log_file
    
 
    speedup = 1

    filename = './setting/settings.json'
    
    if args.file != None:
        filename = args.file

    view_queue = True
    view_signal = True

    if args.viewq == 0:
        view_queue = False

    if args.viewn == 0:
        view_signal = False
        
    if args.spd != None:
        speedup = args.spd
        
    sim = Simulator(filename)
    sim.simulate(speedup, view_queue, view_signal)

    #sys.stdout = old_stdout
    #log_file.close()
    
if __name__ == '__main__':
    main()

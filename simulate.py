import sys
from model import Model, Scheduler
from TSP50_CTL import TSP_CTL
import argparse

def parse():
    parser = argparse.ArgumentParser(description='Simulation Parameters')
    parser.add_argument('arch1', type = int, help='specify how many menus, assign to be 0 if none, at most 2')
    parser.add_argument('arch2', type = int, help='specify how many cashers, assign to be 0 if none, at most 2')
    parser.add_argument('arch3', type = int, help='specify how many presents, assign to be 0 if none, at most 2')
    parser.add_argument('--cars', type = int, help='specify how many cars per hour, default=90')
    parser.add_argument('--st', type = str, help='simulation start time, default=06:00')
    parser.add_argument('--et', type = str, help='simulation end time, default=22:00')
    parser.add_argument('--view', type = bool, help='display the drive through traffic of each queue, default=false')
    parser.add_argument('--spd', type = int, help='speed up the simulation process, 1 is real time, 0 means record the simulated data immediately, default=1')
    return parser.parse_args()

def main():
    st = "06:00"
    et = "22:00"
    cars_per_hr = 90
    view = False
    args = parse()
    spd = 1

    
    model = Model([args.arch1, args.arch2, args.arch3])
    if args.cars != None:
        cars_per_hr = args.cars
    if args.st != None:
        st = args.st
    if args.et != None:
        et = args.et
    if args.view != None:
        view = args.view
    if args.spd != None:
        spd = args.spd

    
    scheduler = Scheduler(cars_per_hr, st, et)
    CTL = TSP_CTL()
    scheduler.simulate(model, CTL, speedup = spd, display = view)


if __name__ == '__main__':
    main()
    

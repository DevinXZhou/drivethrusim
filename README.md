#Drive Through Detector Signals Simulator

To execute this program
Either run run.sh in terminal or run 'python3 simulate.py 2 1 1' in terminal

Required arguments parameters:
arch1 arch2 arch3 

Explaination:
These are the specification of drive through windows, the first stop is arch1 windows, second stop is arch2 windows and so on...
Each parameter should be a int from 0 to 2, min of 0 and max of 2


Optional arguments parameters:
--cars   --st   --et   --view   --spd

--cars 		specify how many cars per hour will be simulated
--st 		specify the start time of simulation which has to be format like this "06:00", which means 6 am in the morning
--et 		end time of simulation, exp "22:00" 22:00 pm in evening
--view 		if set to be true, it will display more details of each drive through lane queues
--spd		speed up the simulation, default is 1 which will simulate in realtime,if set to be 0, it will generate data instantly

All data sare saved in /data folder with a time stamp in its filename


# How to use?

python3 simulate.py 2 1 1	# means Y lane, 2 menu windows, 1 casher, 1 present
python3 simulate.py 2 1 1 --spd=0	#only generate a record of TSP LED signals
## Drive Through Detector Signals Simulator

resetTSP.sh 	# will reset all raspberry pi GIOP PINs to low

run_Dual.sh 	# will run a dual lane simulation continuously forever based on current time and the configuration settings in setting folder

run_Single.sh   # will run a single lane simulation

run_Y.sh	# will run a Y lane simulation

### Run the following command in terminal for a different json configuration file

### go to the downloaded folder directory
cd ~/Desktop/drivethrusim-master/

### update the raspberry pi timer, these is time drift after turning off the raspberry
sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

### run simulator using specific json configuration file
python3 simulator.py --file=./setting/<configuration_filename.json>

1. each detector name should be less or equals to 10 chars, 
otherwise it will cause a problem of logging. Because the program is trying to 
print out lines which are all lined up perfectly

2. Watch out capital letters, if the detector name first 4 chars are different, 
then the model will be treating it as totally different detectors,
then the model setup will be wrong

3. the queue size "qsize" is set up exactly as the setup in ZOOM, 
but it will be fixed in the model due to different model queue structure

4. There is 10 minutes sleep from 23:59 pm to 00:09 am, this is used to avoid program time drift
do not setup "open_time" "close_time" to be within 23:59 to 00:09.

5. Total simulated cars should be less than 10,000, otherwise the log print will cause error, 
it was trying to line up all print lines 

6. Be careful about the values of wait average time and wait deviation, 
if actual wait time is less than 5 seconds, it will discard

7. Queue max size >= 2
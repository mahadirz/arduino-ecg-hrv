# Arduino ECG & Heart Health Analysis

A beginner step to get started with AD8232 for ECG readings and perform processing and analysis in python

## Steps to follow
* Configure the arduino with AD8232 module. Here's a good website to help out setup https://www.how2electronics.com/ecg-monitoring-with-ad8232-ecg-sensor-arduino/
* Use the ecg.ino as the code to be compiled and uploaded into arduino controller, change the PIN number accordingly.
* Attach the sensor pads to your body, again follow the website above for placement area.
* Run ecg_plot_save.py. `python ecg_plot_save.py` to generate csv file of readings. Currently if both plot and saving enabled the iteration on my computer only up to 50 per second (it/s) while it able to go 120 it/s if plot `self.is_plot = False `. 120 it/s is expected since the delay configured in arduino.ino is 8ms
* Just wait a couple of minutes and close the program. By default the program save into `ecg_records.csv`
* Open **ECG & HRV.ipynb** Notebook and run all cells to get HRV information and produce a filtered ECG readings
* Open **DeepLearning Classification of atrial fibrillation.ipynb** to get the ECG classification for Atrial Fibrillation (AF)

Disclaimer: I'm not a medical practitioner

## The Circuit
![Alt text](arduino-circuit.JPG?raw=true "arduino circuit")


## Serial Plotter
![Alt text](ecg-serial-plotter.png?raw=true "serial plotter")

## Matplotlib Plotter
![Alt text](ecg-matplotlib.png?raw=true "Matplotlib circuit")

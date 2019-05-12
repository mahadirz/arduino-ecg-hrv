import pendulum
import serial.tools.list_ports
from serial import Serial
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import time
import multiprocessing as mp
import csv


class IterationRate:
    def __init__(self):
        self.start = None
        self.end = None
        self.count = 0
        self.average = 0

    def record(self):
        if self.start is None:
            self.start = time.time()

        self.end = time.time()
        self.count += 1

    def get_average_ps(self):
        diff = self.end - self.start
        if diff > 0:
            return self.count / diff
        return self.count


class ProcessPlotter(object):
    def __init__(self, buffer_size=100):
        self.y = []
        self.buffer_size = buffer_size
        self.line = None

    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if len(self.y) > self.buffer_size:
                # self.y = self.y[-self.buffer_size:]
                pass
            if command is None:
                print("Exiting plotter...")
                self.terminate()
                return False
            else:
                self.y.append(command)
                self.ax.clear()
                self.ax.plot(self.y, 'b')
                plt.pause(.000001)
                if len(self.y) > self.buffer_size:
                    self.y.pop(0)

        self.fig.canvas.draw()
        return True

    def __call__(self, pipe):
        print('starting plotter...')

        self.pipe = pipe
        self.fig, self.ax = plt.subplots()
        timer = self.fig.canvas.new_timer(interval=500)
        timer.add_callback(self.call_back)
        timer.start()
        style.use('fivethirtyeight')
        print('plotter initialized')
        # plt.title('Live ECG Streaming Sensor Data')  # Plot the title
        # plt.grid(True)  # Turn the grid on
        # plt.ylabel('Amplitude')  # Set ylabels
        # plt.legend(loc='upper left')  # plot the legend
        plt.show()


class Ecg:
    def __init__(self):
        self.port = "/dev/cu.usbmodem14301"  # chosen port that contains ECG readings
        self.baud_rate = 9600  # the port baud rate, must be the same as in Arduino setting
        self.exit_flag = False  # flag used to indicate exit command has been issued
        self.mock = False  # mocking serial reading
        self.device = None
        self.hz = 100  # Hertz: the number of ECG record per second the module is passing to serial

        self.file_name = "ecg_records{}.csv"  # the filename to save ecg data
        self.file = {'f': None, 'writer': None, 'counter': 0}

        self.is_plot = True
        self.is_save = True

        self.counter = 0

        self.plot_pipe, self.plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter()  # initialize ProcessPlotter
        self.plot_process = mp.Process(
            target=self.plotter, args=(self.plotter_pipe,), daemon=False)
        self.plot_process.start()

    def _plot(self, data):
        """
        :return:
        """
        send = self.plot_pipe.send
        try:
            send(data)
        except BrokenPipeError as e:
            print("Broken pipe, the plot window were closed!")
            self.exit_flag = True

    def _write(self, num):
        if self.file['f'] is None:
            # procedure if the file is first initialize
            if self.file['counter'] == 0:
                filename = self.file_name.format("")
            else:
                # append number to the filename postfix
                filename = self.file_name.format("_" + str(self.file['counter']))

            # open with write permission
            self.file['f'] = open(filename, "w")
            self.file['writer'] = csv.writer(self.file['f'], delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            self.file['writer'].writerow(['ts', 'val'])
        else:
            # existing file
            ts = int(time.time() * 1000.0)
            self.file['writer'].writerow([ts, num])
            self.file['f'].flush()

    def _read_write_cleanup(self):
        if self.file['f'] is not None:
            self.file['writer'].close()
            self.file['f'].close()

    def begin(self):
        """
        Read from ECG data and append into buffer
        and delegate writing procedure
        :return:
        """
        if self.mock:
            while True:
                if self.exit_flag:
                    self._read_write_cleanup()
                    break
                data = np.random.randint(300, 600)
                if self.is_save:
                    self._write(data)
                if self.is_plot:
                    self._plot(data)
                time.sleep(0.1)  # sleep for 100ms
        else:
            start = pendulum.now()
            if self.device is None:
                self.device = Serial(self.port, self.baud_rate)
                if not self.device.isOpen():
                    print("Serial port is busy!")
                    self.exit_flag = True
                    return
                ratesX = IterationRate()
                i = 0
                while True:
                    if self.exit_flag:
                        self._read_write_cleanup()
                        self.device.close()
                        break
                    while self.device.inWaiting() == 0:
                        pass
                    ratesX.record()
                    valueRead = self.device.readline(500)
                    # check if valid value can be casted
                    try:
                        valueInInt = int(valueRead)
                        # print(valueInInt)
                        if valueInInt > 5000:
                            "noise or not a real reading"
                            continue
                        if self.is_save:
                            self._write(valueInInt)
                        if self.is_plot:
                            self._plot(valueInInt)
                        if i % 1000 == 0:
                            diff = pendulum.now().diff(start).in_seconds()
                            print("elapsed in seconds", diff)
                            self.hz = ratesX.get_average_ps()
                            print("hz", self.hz)

                    except ValueError:
                        print("Invalid! cannot cast")

                    # time.sleep(0.1)
                    i += 1


if __name__ == '__main__':
    # @todo add argument parser and help for list of ports
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
    # uncomment the line below if you're on macOSX
    mp.set_start_method("forkserver")
    ecg = Ecg()
    ecg.begin()


from numpy.core.fromnumeric import choose
import pyaudio
import wave
import time
import sys
import struct


from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg

import numpy as np
from scipy.fft import fft, fftfreq, fftshift

from sklearn.preprocessing import normalize

class AudioObject:

    def __init__(self, 
                chunk,
                format,
                channels,
                rate,
                input,
                output,
                input_device,
                output_device
                ) -> None:
        self.chunk         = chunk
        self.format        = format
        self.channels      = channels
        self.rate          = rate
        self.input         = input
        self.output        = output
        self.input_device  = input_device
        self.output_device = output_device
        
        self.traces = dict()
        self.data_waveform = np.zeros(self.chunk)
        self.frames = []

        self.x = np.arange(0, self.chunk)
        self.xf = fftfreq(int(self.chunk), 1 / self.rate )[:self.chunk//2]

        pg.setConfigOptions(antialias=True)
        self.app = QtWidgets.QApplication(sys.argv)
        self.w = pg.GraphicsLayoutWidget(title='Audio Analizer')
        self.w.resize(1000,600)
        self.w.setWindowTitle('pyqtgraph example: Plotting')

        self.waveform = self.w.addPlot(title='Waveform', row=1, col=1)
        self.waveform.setXRange(0, chunk, padding=0)
        self.waveform.setYRange(0, 256, padding=0)

        self.spectrum = self.w.addPlot(title='Spectrum', row=2, col=1) 
        self.spectrum.setLogMode(x=True, y=True)
        self.spectrum.setYRange(-4, 0, padding=0)
        #self.spectrum.setXRange(np.log10(20), np.log10(self.rate / 2), padding=0.005)
        #self.spectrum.setXRange(0, self.rate/2, padding=0)
    
        
        self.w.show()

        self.p = pyaudio.PyAudio()
        self.stream = self._open_stream()
    
    def callback(self, in_data, frame_count, time_info, status) -> tuple():
        
        data_int = struct.unpack(str(2 * CHUNK) + 'B', in_data)
        data_wav = np.array(data_int, dtype='b')[::2] + 128
        self.data_waveform = data_wav
        self.frames.append(data_wav)
        
        return (in_data, pyaudio.paContinue)


    def _open_stream(self) -> pyaudio.Stream:
        stream = self.p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=self.input,
                        output=self.output,
                        frames_per_buffer=self.chunk,
                        input_device_index=self.input_device,
                        output_device_index=self.output_device,
                        stream_callback=self.callback)

        return stream

    def startstream(self) -> None:
        self.stream.start_stream()

    def stopstream(self) -> None:
        self.stream.stop_stream()

    def update(self) -> None:

        spectrum = fft(np.array(self.data_waveform, dtype='int8') - 128)
        spectrum = np.abs(spectrum[0:int(self.chunk / 2)]) * 2 / (128 * self.chunk)

        self.trace('Waveform', self.x, self.data_waveform)
        self.trace('Spectrum', self.xf, spectrum)
 

    def trace(self,name,dataset_x,dataset_y) -> None:
        if name in self.traces:
            self.traces[name].setData(dataset_x,dataset_y)
        else:
            if name == 'Waveform':
                self.traces[name] = self.waveform.plot(pen='y')
            if name == 'Spectrum':
                self.traces[name] = self.spectrum.plot(pen='b')
    
    def start(self) -> None:
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            sys.exit(self.app.exec())

    def animate(self) -> None:
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.start()


def set_devices() -> tuple:
    input_devices = []
    output_devices = []
    for i in range(pyaudio.PyAudio().get_device_count()):
        if pyaudio.PyAudio().get_device_info_by_index(i)['maxInputChannels'] > 0:
            input_devices.append(pyaudio.PyAudio().get_device_info_by_index(i))
        if pyaudio.PyAudio().get_device_info_by_index(i)['maxOutputChannels'] > 0:
            output_devices.append(pyaudio.PyAudio().get_device_info_by_index(i))

    print(f'Select an input device, choose the index number')
    print(f'-----------------------')
    print(f'index, name, channels')
    for i, device in enumerate(input_devices):
        print(f'{device["index"]}: {device["name"]} --- {device["maxInputChannels"]}')
    
    input_device = pyaudio.PyAudio().get_device_info_by_index(int(input()))['index']

    print(f'Select an output device, choose the index number')
    print(f'-----------------------')
    print(f'index, name, channels')
    for i, device in enumerate(output_devices):
        print(f'{device["index"]}: {device["name"]} --- {device["maxInputChannels"]}')
    
    output_device = pyaudio.PyAudio().get_device_info_by_index(int(input()))['index']

    return input_device, output_device


if __name__ == '__main__':

    input_device, output_device = (set_devices())

    CHUNK    = 4096
    FORMAT   = pyaudio.paInt16
    CHANNELS = 1
    RATE     = 44100

    audio = AudioObject(CHUNK, FORMAT, CHANNELS, RATE, True, True, input_device, output_device)
    audio.animate()



import pyaudio
import wave
import time
import sys
import struct


from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg

import numpy as np

class AudioRecord:

    def __init__(self, 
                chunk,
                format,
                channels,
                rate,
                input,
                output,
                ) -> None:
        self.chunk         = chunk
        self.format        = format
        self.channels      = channels
        self.rate          = rate
        self.input         = input
        self.output        = output
        
        self.output_file = 'output.wav'
        self.frames = []
        self.data_waveform = []
        
        self.app = QtWidgets.QApplication(sys.argv)

        self.w = pg.GraphicsLayoutWidget(title='Audio Analizer')
        self.w.resize(1000,600)
        self.w.setWindowTitle('pyqtgraph example: Plotting')

        self.waveform = self.w.addPlot(title='Waveform', row=1, col=1)
        self.waveform.plot(pen='y')

        self.w.show()
        self.recording = False

        self.p = pyaudio.PyAudio()
        self.stream = self._open_stream()

    def callback(self, in_data, frame_count, time_info, status) -> tuple():

        if self.recording == True:
            self.frames.append(in_data)
            #data_int = struct.unpack(str(2 * self.chunk) + 'B', in_data)
            #self.data_waveform.append(data_int[::2] + 128)
        

        return (in_data, pyaudio.paContinue)

    def _open_stream(self) -> pyaudio.Stream:
        stream = self.p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=self.input,
                        output=self.output,
                        frames_per_buffer=self.chunk,
                        stream_callback=self.callback)
        return stream
        

    def save_wav(self) -> None:

        wf = wave.open(self.output_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()


    def record(self) -> None:

        print('Type "start" to start recording and "stop" to stop recording')
        while input() != 'start':
            pass
        self.recording = True
        print("* recording")

        while self.stream.is_active():
            if input() == 'stop':
                
                break
            time.sleep(0.1)
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.save_wav()

    def plot_waveform(self) -> None:

        self.waveform.setData(len(np.array(self.data_waveform)),np.array(self.data_waveform))
        

    def update():
        pass

    def start(self) -> None:
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            sys.exit(self.app.exec())

    def animate(self) -> None:
        self.timer = QtCore.QTimer()
        self.timer.singleShot(1, self.record)
        self.timer.timeout.connect(self.plot_waveform)
        self.timer.start(50)

        self.start()


if __name__ == '__main__':

    CHUNK = 4096
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"

    record = AudioRecord(CHUNK, FORMAT, CHANNELS, RATE, True, False)
    record.animate()

   
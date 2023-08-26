# For embedding audio player
import IPython

# Plots
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (15, 6)
from mir_eval.sonify import pitch_contour

import numpy

import essentia.standard as es




class PianoCrafter:
    
    def __init__(self, audiopath) -> None:
        self.audiopath = audiopath
        self.sr = 44100
        # Load audio file.
        # It is recommended to apply equal-loudness filter for PredominantPitchMelodia.
        loader = es.EqloudLoader(filename=self.audiopath, sampleRate=self.sr)
        self.audio = loader()
        print("Duration of the audio sample [sec]:")
        print(len(self.audio)/self.sr)

    def extract_pitch(self):
        # Extract the pitch curve
        # PitchMelodia takes the entire audio signal as input (no frame-wise processing is required).

        pitch_extractor = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
        self.pitch_values, self.pitch_confidence = pitch_extractor(self.audio)

    def plot_descriptors(self):
        # Pitch is estimated on frames. Compute frame time positions.
        self.pitch_times = numpy.linspace(0.0,len(self.audio)/self.sr,len(self.pitch_values) )

        # Plot the estimated pitch contour and confidence over time.
        f, axarr = plt.subplots(2, sharex=True)
        axarr[0].plot(self.pitch_times, self.pitch_values)
        axarr[0].set_title('estimated pitch [Hz]')
        axarr[1].plot(self.pitch_times, self.pitch_confidence)
        axarr[1].set_title('pitch confidence')
        plt.savefig('/data/descriptors.png')
        plt.show()

    def synth_melody(self):
        return pitch_contour(self.pitch_times, self.pitch_values, 44100).astype(numpy.float32)[:len(self.audio)]



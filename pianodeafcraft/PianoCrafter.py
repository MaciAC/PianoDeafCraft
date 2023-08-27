from tempfile import TemporaryDirectory
import mido

import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (15, 6)
from mir_eval.sonify import pitch_contour
import numpy
from scipy.io.wavfile import read
import essentia.standard as es




class PianoCrafter:
    
    def __init__(self, audiopath) -> None:
        self.audiopath = audiopath
        self.temp_dir = TemporaryDirectory()
        #self.audio, self.sr = read(self.audiopath)
        self.sr = 44100
        # It is recommended to apply equal-loudness filter for PredominantPitchMelodia.
        loader = es.EqloudLoader(filename=self.audiopath, sampleRate=self.sr)
        self.audio = loader()
        print("Duration of the audio sample [sec]:")
        print(len(self.audio)/self.sr)

    def extract_pitch(self):
        # Extract the pitch curve
        # PitchMelodia takes the entire audio signal as input (no frame-wise processing is required).
        #pitch_extractor = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
        pitch_extractor = es.MultiPitchKlapuri()
        self.pitch_values = pitch_extractor(self.audio)

    def plot_descriptors(pc):
        # Pitch is estimated on frames. Compute frame time positions.
        pc.pitch_times = numpy.linspace(0.0,len(pc.audio)/pc.sr,len(pc.pitch_values) )
        mel1 = [p[0] for p in pc.pitch_values]
        mel2 = []
        for p in pc.pitch_values:
            try:
                mel2.append(p[1])
            except:
                mel2.append(0.0)
        # Plot the estimated pitch contour and confidence over time.
        f, axarr = plt.subplots(2, sharex=True)
        axarr[0].plot(pc.pitch_times, mel1)
        axarr[0].set_title('estimated pitch 1 [Hz]')
        axarr[1].plot(pc.pitch_times, mel2)
        axarr[1].set_title('estimated pitch 2 [Hz]')
        plt.savefig('/data/descriptors.png')
        plt.show()

    def synth_melody(self):
        return pitch_contour(self.pitch_times, self.pitch_values, 44100).astype(numpy.float32)[:len(self.audio)]

    def save_midi(self):
        onsets, durations, notes = es.PitchContourSegmentation(hopSize=128)(self.pitch_values, self.audio)

        PPQ = 96 # Pulses per quarter note.
        BPM = 120 # Assuming a default tempo in Ableton to build a MIDI clip.
        tempo = mido.bpm2tempo(BPM) # Microseconds per beat.

        # Compute onsets and offsets for all MIDI notes in ticks.
        # Relative tick positions start from time 0.
        offsets = onsets + durations
        silence_durations = list(onsets[1:] - offsets[:-1]) + [0]

        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)

        for note, onset, duration, silence_duration in zip(list(notes), list(onsets), list(durations), silence_durations):
            track.append(mido.Message('note_on', note=int(note), velocity=64,
                                    time=int(mido.second2tick(duration, PPQ, tempo))))
            track.append(mido.Message('note_off', note=int(note),
                                    time=int(mido.second2tick(silence_duration, PPQ, tempo))))

        midi_file = '/data/extracted_melody.mid'
        mid.save(midi_file)
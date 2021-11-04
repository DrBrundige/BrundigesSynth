import math
import random
import wave
import struct
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from main import average_waves
# from song import Note


class BrundigesSynth:
	combined_wave = []
	bit_depth = 0
	sample_rate = 0

	def __init__(self, sample_rate=44100, bit_depth_power=16):
		self.bit_depth = (pow(2, bit_depth_power) / 2) - 1
		self.sample_rate = sample_rate

	def append_to_wave(self, sample):
		self.combined_wave.append(sample)

	def export_combined_wave(self, filename="wave"):
		assert len(self.combined_wave) > 0, "ERROR! Combined Wave is empty!"
		filename = "wavs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
		num_channels = 1
		w = wave.open(filename, 'w')
		w.setparams((num_channels, 2, self.sample_rate, 2, 'NONE', 'not compressed'))

		for i in self.combined_wave:
			frames = struct.pack('h', i)
			w.writeframesraw(frames)
		print("Success! Wrote file " + filename)
		w.close()

	def plot_combined_wave(self):
		plt.plot(self.combined_wave)
		plt.show()


class Oscillator:
	Synth = BrundigesSynth()
	all_filters = []
	i = 0
	j = 0
	wave = []
	num_samples = 0

	def __iter__(self):
		self.i = self.i
		return self

	def __next__(self):
		pass

	def play(self):
		pass


class Beeper(Oscillator):
	# Synthesizer environment. Standardizes sample rate and bit depth
	Synth = BrundigesSynth()
	Note = None
	amplitude = 0.0
	phase = 0.0
	period = 0.0

	def __init__(self, note):
		self.j = 0
		self.Synth = note.Song.Synth
		self.Note = note
		self.recalculate_note()

		self.wave = []
		self.all_filters = []

	def recalculate_note(self):
		# Volume of note
		self.amplitude = (self.Note.amplitude * self.Synth.bit_depth) / 2
		# Number of samples needed for a single oscillation
		self.phase = int(self.Note.frequency * self.Note.phase / 2)
		# Not really sure how this works
		self.period = (2 * math.pi * self.Note.frequency) / self.Synth.sample_rate

	def get_sample(self):
		# print(self.i < self.end)
		r = self.j * self.period
		if r >= math.pi * 2:
			r = 0.0
			self.j = 1
		else:
			self.j += 1

		# r += self.phase
		sample = int(math.sin(r) * self.amplitude)
		for filter in self.all_filters:
			sample = filter.filter(sample)
		# Clip - if r is greater than bit depth, return bit depth
		# print(math.sin(r) + 1)
		return sample


class DoubleHarmonicBeeper(Oscillator):
	# Synthesizer environment. Standardizes sample rate and bit depth
	Synth = BrundigesSynth()
	Note = None
	amplitude = 0.0
	phase = 0.0
	period = 0.0

	def __init__(self, note):
		self.j = 0
		self.Synth = note.Song.Synth
		self.Note = note
		self.recalculate_note()

		self.wave = []
		self.all_filters = []

	def recalculate_note(self):
		# Volume of note
		self.amplitude = (self.Note.amplitude * self.Synth.bit_depth) / 2
		# Number of samples needed for a single oscillation
		self.phase = int(self.Note.frequency * self.Note.phase / 2)
		# Not really sure how this works
		self.period = (2 * math.pi * self.Note.frequency) / self.Synth.sample_rate

	def get_sample(self):
		# print(self.i < self.end)
		r = self.j * self.period
		if r >= math.pi * 2:
			r = 0.0
			self.j = 1
		else:
			self.j += 1

		sample = 0
		for h in range(2):
			r = self.i * (2 * math.pi * self.Note.frequency / (h + 1)) / self.Synth.sample_rate
			r += self.phase
			r = int(math.sin(r) * self.amplitude)
			sample += r

		sample = int(sample / 2)
		self.i += 1

		for filter in self.all_filters:
			sample = filter.filter(sample)
		# Clip - if r is greater than bit depth, return bit depth
		return sample


import math
import wave
import struct
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from main import average_waves

class BrundigesSynth:
	all_oscillators = []
	combined_wave = []
	bit_depth = 0
	sample_rate = 0

	def __init__(self, sample_rate=44100, bit_depth_power=16):
		self.bit_depth = (pow(2, bit_depth_power) / 2) - 1
		self.sample_rate = sample_rate
		self.all_oscillators = []

	def export_combined_wave(self, filename="wave"):
		assert len(self.combined_wave) > 0, "ERROR! Combined Wave is empty!"
		filename = "wavs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
		num_channels = 1
		w = wave.open(filename, 'w')
		w.setparams((num_channels, 2, self.sample_rate, 2, 'NONE', 'not compressed'))
		for i in self.combined_wave:
			frames = struct.pack('h', i)
			w.writeframesraw(frames)
		w.close()

	# Combines two or more waves into a single wave
	def combine_waves(self, algorithm):
		waves = []
		for oscillator in self.all_oscillators:
			waves.append(oscillator.wave)

		# Asserts that each given wave is the same length
		first_wave = waves[0]
		for wave in waves:
			assert len(first_wave) == len(wave)

		self.combined_wave = []
		# For each sample, combines into one sample using given algorithm
		for i in range(len(first_wave)):
			sample = algorithm(waves, i)
			self.combined_wave.append(sample)
		return True

	def play_all_oscillators(self):
		for oscillator in self.all_oscillators:
			oscillator.play()

	def plot_all_oscillators(self, plot_combined_wave=False):
		for oscillator in self.all_oscillators:
			plt.plot(oscillator.wave)
		if plot_combined_wave:
			plt.plot(self.combined_wave)
		plt.show()


class Oscillator:
	Synth = BrundigesSynth()
	i = 0
	wave = []

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
	num_samples = 0
	duration = 0
	amplitude = 0.0
	i = 0
	# Frequency of wave this beeper will produce
	frequency = 0
	# Phase of wave. 0.5 is reversed
	phase = 0

	def __init__(self, synth, duration, frequency, amplitude=1.0, sample_rate=44100, phase=1.0):
		self.i = 0
		self.Synth = synth
		self.frequency = frequency
		# Number of samples produced. Obtained by multiplying sample rate by duration in seconds
		self.num_samples = duration * sample_rate
		# Volume of note
		self.amplitude = (amplitude * self.Synth.bit_depth) / 2
		self.phase = int(self.frequency * phase / 2)
		self.wave = []

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			r = self.i * (2 * math.pi * self.frequency) / self.Synth.sample_rate
			r += self.phase
			self.i += 1
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return int(math.sin(r) * self.amplitude)
		else:
			raise StopIteration

	def play(self):
		for sample in self:
			self.wave.append(sample)


if __name__ == '__main__':
	brundiges_synth = BrundigesSynth()

	brundiges_synth.all_oscillators.append(Beeper(brundiges_synth, 3, 440))
	brundiges_synth.all_oscillators.append(Beeper(brundiges_synth, 3, 110, phase=.25))
	# brundiges_synth.all_oscillators.append(Beeper(brundiges_synth, 1, 660, amplitude=.25))

	brundiges_synth.play_all_oscillators()
	brundiges_synth.combine_waves(average_waves)

	# brundiges_synth.plot_all_oscillators()
	brundiges_synth.export_combined_wave()

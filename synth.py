import math
import random
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
		print("Success! Wrote file " + filename)
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

	def plot_oscillators(self, plot_oscillator_waves=True, plot_combined_wave=False):
		if plot_oscillator_waves:
			for oscillator in self.all_oscillators:
				plt.plot(oscillator.wave)

		if plot_combined_wave:
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


class Filter:
	oscillator = Oscillator()

	def filter(self, sample):
		pass


class Beeper(Oscillator):
	# Synthesizer environment. Standardizes sample rate and bit depth
	Synth = BrundigesSynth()
	duration = 0
	amplitude = 0.0
	# Frequency of wave this beeper will produce
	frequency = 0
	# Phase of wave. 0.5 is reversed
	phase = 0
	period = (2 * math.pi)

	def __init__(self, synth, duration, frequency, amplitude=1.0, phase=0.0):
		self.i = 0
		self.j = 0
		self.Synth = synth
		self.frequency = frequency
		# Number of samples produced. Obtained by multiplying sample rate by duration in seconds
		self.num_samples = duration * self.Synth.sample_rate
		# Volume of note
		self.amplitude = (amplitude * self.Synth.bit_depth) / 2
		self.phase = int(self.frequency * phase / 2)
		self.period = (2 * math.pi * self.frequency) / self.Synth.sample_rate
		self.wave = []
		self.all_filters = []

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			r = self.j * self.period
			self.i += 1
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
		else:
			raise StopIteration

	def play(self):
		for sample in self:
			self.wave.append(sample)


class InvertedBeeper(Beeper):
	k = 1

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			r = self.j * self.period
			self.i += 1
			if r >= math.pi:
				r = 0.0
				self.j = 1
				self.k = self.k * -1
			else:
				self.j += 1

			# r += self.phase
			sample = int((1 - math.sin(r)) * self.amplitude)
			for filter in self.all_filters:
				sample = filter.filter(sample)
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return sample
		else:
			raise StopIteration


class SawtoothBuzzer(Beeper):
	# Synthesizer environment. Standardizes sample rate and bit depth

	def __init__(self, synth, duration, frequency, amplitude=1.0, phase=0.0):

		super().__init__(synth, duration, frequency / 2, amplitude=1.0, phase=0.0)

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			r = self.j * self.period
			self.i += 1
			if r > math.pi:
				r = 0.0
				self.j = 1
			else:
				self.j += 1
			r += self.phase
			sample = int(math.sin(r) * self.amplitude)
			for filter in self.all_filters:
				sample = filter.filter(sample)
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return sample
		else:
			raise StopIteration


class TriangleBuzzer(Beeper):
	k = 1

	def __next__(self):
		if self.i < self.num_samples:
			self.i += 1
			r = self.j * self.period
			if r > math.pi:
				r = 0
				self.j = 1
				self.k = self.k * -1
			else:
				self.j += 1

			# r += self.phase
			# r -=  / 2
			sample = int((1 - (2 * r / math.pi)) * self.k * self.amplitude)

			for filter in self.all_filters:
				sample = filter.filter(sample)

			return sample
		else:
			raise StopIteration


class HarmonicBeeper(Beeper):
	# Synthesizer environment. Standardizes sample rate and bit depth

	harmonics = 3

	def __init__(self, synth, duration, frequency, harmonics=3, amplitude=1.0, phase=0.0):
		super().__init__(synth, duration, frequency, amplitude, phase)
		self.harmonics = harmonics
		assert harmonics > 0, "ERROR! Harmonics must be 1 or greater!"

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			sample = 0

			for h in range(self.harmonics):
				r = self.i * (2 * math.pi * self.frequency / (h + 1)) / self.Synth.sample_rate
				r += self.phase
				r = int(math.sin(r) * self.amplitude)
				sample += r

			self.i += 1
			sample = int(sample / self.harmonics)
			for filter in self.all_filters:
				sample = filter.filter(sample)
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return sample
		else:
			raise StopIteration


class Clicker(Beeper):
	# Number of clicks per minute
	click_frequency = 0
	# Frequency of wave this clicker will produce while it is clicking
	click_waves = 1
	waves_remaining = 1

	def __init__(self, synth, duration, bpm, frequency=110, click_waves=1, amplitude=1.0):
		super().__init__(synth, duration, frequency, amplitude)
		# Number of samples between clicks
		self.click_frequency = int((self.Synth.sample_rate / (bpm / 60)))

		# Number of waves in each click
		self.click_waves = click_waves
		self.waves_remaining = click_waves

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			sample = 0

			if self.i % self.click_frequency == 0:
				self.waves_remaining = self.click_waves
			self.i += 1

			if self.waves_remaining > 0:
				r = self.j * self.period
				if r >= math.pi * 2:
					self.j = 1
					self.waves_remaining -= 1
				else:
					self.j += 1
					sample = int(math.sin(r) * self.amplitude)
					for filter in self.all_filters:
						sample = filter.filter(sample)

			return sample
		else:
			raise StopIteration

	def play(self):
		for sample in self:
			self.wave.append(sample)


class NoiseMaker(Oscillator):
	# Synthesizer environment. Standardizes sample rate and bit depth
	Synth = BrundigesSynth()
	duration = 0
	amplitude = 0.0
	i = 0

	def __init__(self, synth, duration, amplitude=1.0):
		self.i = 0
		self.Synth = synth
		# Number of samples produced. Obtained by multiplying sample rate by duration in seconds
		self.num_samples = duration * self.Synth.sample_rate
		# Volume of note
		self.amplitude = (amplitude * self.Synth.bit_depth) / 2
		self.wave = []

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.num_samples:
			r = self.i
			self.i += 1
			# print(random.randrange(0, 2))
			x = 1
			if random.randrange(0, 2) == 0:
				x = -1
			return int(random.random() * self.amplitude * x)
		else:
			raise StopIteration

	def play(self):
		for sample in self:
			self.wave.append(sample)


# Rounds down samples, creating a blockier wave
class LofiModulus(Filter):
	# Integer to which samples will be rounded.
	# Modulo 1 rounds down to whole number. Mod 2 rounds to even number, etc.
	modulo = 1

	def __init__(self, modulo):
		self.modulo = modulo

	def filter(self, sample):
		# Divides sample by modulo, rounds it down, then multiplies it back
		# There is a way to do this that actually uses the modulus,
		#   but this is who it is done in Excel, so it's what I know
		sliced_sample = sample / self.modulo
		sliced_sample = math.floor(sliced_sample)
		sliced_sample = sliced_sample * self.modulo
		return sliced_sample


# Copies samples over each other, creating a blockier wave.
class LofiDesampler(Filter):
	# Number of samples to hold
	sample_copies = 1
	# Counter
	i = 0
	# Saves value of the last held sample
	last_sample = 0

	def __init__(self, sample_copies):
		assert sample_copies > 0, "Errant input! sample_copies must be greater than 0!"
		self.sample_copies = sample_copies
		self.i = 0
		self.last_sample = 0

	def filter(self, sample):
		if self.i > 0:
			self.i -= 1
		else:
			self.i = self.sample_copies
			self.last_sample = sample

		return self.last_sample


class Square(Filter):

	def __init__(self, oscillator):
		self.oscillator = oscillator

	def filter(self, sample):
		# print("Filtering Wave")
		if sample > 0:
			return self.oscillator.amplitude
		else:
			return self.oscillator.amplitude * -1


if __name__ == '__main__':
	print("Brundige's Synth!")
	brundiges_synth = BrundigesSynth()

	# brundiges_synth.all_oscillators.append(HarmonicBeeper(brundiges_synth, 4, 440, harmonics=2, phase=.12, amplitude=.5))
	brundiges_synth.all_oscillators.append(Clicker(brundiges_synth, 4, 120, frequency=110, click_waves=4))
	# desampler = LofiDesampler(4)
	# modulus = LofiModulus(100)
	# brundiges_synth.all_oscillators[0].all_filters.append(desampler)
	# brundiges_synth.all_oscillators[0].all_filters.append(modulus)
	# brundiges_synth.all_oscillators.append(InvertedBeeper(brundiges_synth, 3, 55))

	brundiges_synth.play_all_oscillators()
	brundiges_synth.combine_waves(average_waves)

	brundiges_synth.plot_oscillators(plot_oscillator_waves=False, plot_combined_wave=True)
	brundiges_synth.export_combined_wave()
	print("Complete!")

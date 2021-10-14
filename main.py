import math
import wave
import struct
from datetime import datetime, timedelta
from matplotlib import pyplot as plt


class Oscillator:
	def __init__(self, duration, frequency, amplitude=1.0, sample_rate=44100, bit_depth_power=16, phase=0.0):
		self.bit_depth = (pow(2, bit_depth_power) / 2) - 1
		self.i = 0
		self.frequency = frequency
		self.samples = duration * sample_rate
		self.amplitude = (amplitude * self.bit_depth) / 2
		self.phase = int(self.frequency * phase / 2)
		self.sample_rate = sample_rate

	def __iter__(self):
		self.i = self.i
		return self

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.samples:
			r = self.i * (2 * math.pi * self.frequency) / self.sample_rate
			r += self.phase
			self.i += 1
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return self.get_sin(r)
		else:
			raise StopIteration

	def get_sin(self, r):
		# return int((math.sin(r)+1) * self.amplitude)
		return int(math.sin(r) * self.amplitude)

	def export_wav(self, data, filename="wave"):
		filename = "wavs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
		num_channels = 1
		w = wave.open(filename, 'w')
		w.setparams((num_channels, 2, self.sample_rate, 2, 'NONE', 'not compressed'))
		for i in data:
			frames = struct.pack('h', i)
			w.writeframesraw(frames)
		w.close()


# Combines two or more waves into a single wave
def combine_waves(waves, algorithm):
	# Asserts that each given wave is the same length
	first_wave = waves[0]
	for wave in waves:
		assert len(first_wave) == len(wave)

	averaged_wave = []
	# For each sample, combines into one sample using given algorithm
	for i in range(len(first_wave)):
		sample = algorithm(waves, i)
		averaged_wave.append(sample)
	return averaged_wave


# Takes the average of given waves
def average_waves(waves, i):
	num_waves = len(waves)  # Gets the number of waves
	sample = 0
	for wave in waves:
		sample += wave[i]
	# print(wave)
	return int(sample / num_waves)


# Takes the max of given waves
def max_waves(waves, i):
	# num_waves = len(waves)  # Gets the number of waves
	max = waves[0][i]
	for wave in waves:
		if wave[i] > max:
			max = wave[i]
	# print(wave)
	return max


if __name__ == '__main__':
	print("Brundige's Synth!")
	snyth = Oscillator((1 / 440 * 8), 440)
	# snyth = iter(myclass)
	data_a4 = []
	for i in snyth:
		data_a4.append(i)

	data_a2 = []
	snyth = Oscillator((1 / 440 * 8), 110, phase=.5, amplitude=.5)
	for i in snyth:
		data_a2.append(i)

	# data_a8 = []
	# snyth = Oscillator(3, 440, amplitude=.1)
	# for i in snyth:
	# 	data_a8.append(i)

	print("Taking max wave")
	average = combine_waves([data_a4, data_a2], average_waves)
	print("Max wave found!")
	plt.plot(data_a4)
	plt.plot(data_a2)
	plt.plot(average)
	plt.show()
	# snyth.export_wav(average)
	print("Complete!")

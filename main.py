import math
import wave
import struct
from datetime import datetime, timedelta
from matplotlib import pyplot as plt


class Oscillator:
	def __init__(self, duration, frequency, amplitude=.8, sample_rate=44100, bit_depth_power=16):
		self.bit_depth = (pow(2, bit_depth_power) / 2) - 1
		self.i = 0
		self.frequency = frequency
		self.samples = duration * sample_rate
		self.amplitude = (amplitude * self.bit_depth)/2
		self.sample_rate = sample_rate

	def __iter__(self):
		self.i = self.i
		return self

	def __next__(self):
		# print(self.i < self.end)
		if self.i < self.samples:
			r = self.i * (2 * math.pi * self.frequency) / self.sample_rate
			self.i += 1
			# Clip - if r is greater than bit depth, return bit depth
			# print(math.sin(r) + 1)
			return int((math.sin(r) + 1) * self.amplitude)
		else:
			raise StopIteration

	def get_sin(self):
		pass

	def export_wav(self, data, filename="wave"):
		filename = "wavs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav"
		num_channels = 1
		w = wave.open(filename, 'w')
		w.setparams((num_channels, 2, self.sample_rate, 2, 'NONE', 'not compressed'))
		for i in data:
			frames = struct.pack('h', i)
			w.writeframesraw(frames)
		w.close()


if __name__ == '__main__':
	print("Brundige's Synth!")
	snyth = Oscillator(3, 880, amplitude=1)
	# snyth = iter(myclass)
	data = []
	for i in snyth:
		# print(i)
		data.append(i)
	# plt.plot(data)
	# plt.show()
	snyth.export_wav(data)

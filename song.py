from note_synth import BrundigesSynth
from enum import Enum
import note_synth
from datetime import datetime


class ATuning(Enum):
	C3 = 261.63 / 2
	Cs3Db3 = 277.18 / 2
	D3 = 293.66 / 2
	Ds3Eb3 = 311.13 / 2
	E3 = 329.63 / 2
	F3 = 349.23 / 2
	Fs3Gb3 = 369.99 / 2
	G3 = 392.00 / 2
	Gs3Ab3 = 415.30 / 2
	A3 = 440.00 / 2
	As3Bb3 = 466.16 / 2
	B3 = 493.88 / 2

	C4 = 261.63
	Cs4Db4 = 277.18
	D4 = 293.66
	Ds4Eb4 = 311.13
	E4 = 329.63
	F4 = 349.23
	Fs4Gb4 = 369.99
	G4 = 392.00
	Gs4Ab4 = 415.30
	A4 = 440.00
	As4Bb4 = 466.16
	B4 = 493.88
	C5 = 261.63 * 2
	Cs5Db5 = 277.18 * 2
	D5 = 293.66 * 2
	Ds5Eb5 = 311.13 * 2
	E5 = 329.63 * 2
	F5 = 349.23 * 2
	Fs5Gb5 = 369.99 * 2
	G5 = 392.00 * 2
	Gs5Ab5 = 415.30 * 2
	A5 = 440.00 * 2
	As5Bb5 = 466.16 * 2
	B5 = 493.88 * 2


class NoteLengths(Enum):
	EIGHTH = (1.0 / 8.0)
	QUARTER = (1.0 / 4.0)
	HALF = (1.0 / 2.0)
	FULL = 1.0


class Song:
	Synth = BrundigesSynth()
	Tuning = ATuning
	bpm = 120
	all_notes = []

	def add_note(self, note):
		self.all_notes.append(note)

	def play(self):
		active_notes = []
		waiting_notes = []
		# TODO: Order notes by starting sample

		for note in self.all_notes:
			waiting_notes.append(note)

		i = 0
		while len(active_notes) > 0 or len(waiting_notes) > 0:
			# print(i)
			# try:
			j = 0
			while j < len(waiting_notes):
				if i >= waiting_notes[0].starting_sample:
					active_notes.append(waiting_notes.pop(0))
				else:
					j = len(waiting_notes)
			# except Exception as E:
			# 	print("Bingus!")

			sample = 0
			for note in active_notes:
				if note.samples_remaining > 0:
					sample += note.__next__()
				else:
					active_notes.remove(note)

			if len(active_notes) > 0:
				self.Synth.combined_wave.append(int(sample / len(active_notes)))
			else:
				self.Synth.combined_wave.append(0)

			i += 1

		print("Success!")
		return True

	def play_one_note(self, note):
		samples = []
		while note.samples_remaining > 0:
			samples.append(note.__next__())
		return samples

	def __init__(self, synth, tuning, bpm=120):
		self.Synth = synth
		self.Tuning = tuning
		self.bpm = bpm
		self.all_notes = []


class Note:
	Song = None
	Beeper = None
	starting_sample = 0
	num_samples = 0
	samples_remaining = 0
	duration = .25
	frequency = 440.0
	amplitude = 1.0
	phase = 1.0

	def __next__(self):
		self.samples_remaining -= 1
		return self.Beeper.get_sample()

	def __init__(self, song, start_time, length, note, Beeper):
		self.Song = song
		self.starting_sample = int(start_time * (self.Song.bpm / 60) * self.Song.Synth.sample_rate)
		self.duration = length.value
		self.frequency = note.value

		self.Beeper = Beeper(self)

		# Number of samples produced. Obtained by multiplying sample rate by duration in seconds
		self.num_samples = int(self.duration * (self.Song.bpm / 60) * self.Song.Synth.sample_rate)
		self.samples_remaining = self.num_samples


class Rest(Note):
	pass


if __name__ == '__main__':
	print("Welcome to Brundige's Synth!")
	brundiges_synth = BrundigesSynth()
	nice_song = Song(brundiges_synth, ATuning, 120)
	nice_song.add_note(Note(nice_song, 0.0, NoteLengths.QUARTER, ATuning.C4, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 0.25, NoteLengths.QUARTER, ATuning.E4, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 0.50, NoteLengths.QUARTER, ATuning.G4, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 0.75, NoteLengths.QUARTER, ATuning.C5, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 1.0, NoteLengths.QUARTER, ATuning.G4, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 1.25, NoteLengths.QUARTER, ATuning.E4, note_synth.DoubleHarmonicBeeper))
	nice_song.add_note(Note(nice_song, 1.5, NoteLengths.FULL, ATuning.C4, note_synth.DoubleHarmonicBeeper))

	start = datetime.now()
	# nice_song.play_one_note(nice_song.all_notes[0])
	nice_song.play()
	end = datetime.now()
	print(end.timestamp() - start.timestamp())

	brundiges_synth.plot_combined_wave()
	brundiges_synth.export_combined_wave()

# this_note = Note()

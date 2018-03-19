from random import choice
from itertools import product
from enum import Enum
import json
import os

'''
GENERAL NOTE: In I Ching castings, lines are counted bottom-up, and that is
replicated here. A trigram of:

YANG
YANG
YIN

Will be stored as [YIN, YANG, YANG]. Everything will follow this order except
for printing the hexagram itself.
'''

class Line:
	"""The base element to a casting. Default lines set up in Lines 'enumerator.'"""
	def __init__(self, name, num, old, yin, probability):
		self.name = name
		self.num = num
		self.old = old
		self.yin = yin
		self.probability = probability

class Lines:
	"""Simulating an enumerator using class variables for the four possible lines"""
	OLDYIN = Line(name='Old Yin', num=6, old=True, yin=True, probability=1)
	YANG = Line(name='Yang', num=7, old=False, yin=False, probability=5)
	YIN = Line(name='Yin', num=8, old=False, yin=True, probability=7)
	OLDYANG = Line(name='Old Yang', num=9, old=True, yin=False, probability=3)

class Trigrams(Enum):
	"""Simulating an enumerator using class variables for all 8 trigrams"""
	HEAVEN = 1
	LAKE = 2
	FIRE = 3
	THUNDER = 4
	WIND = 5
	WATER = 6
	MOUNTAIN = 7
	EARTH = 8

class IChingService:
	def __init__(self):
		"""Sets up dictionaries for later methods"""

		# Trigrams
		yin = True
		yang = False
		self.trigrams = {
			(yang, yang, yang): Trigrams.HEAVEN,
			(yang, yang, yin): Trigrams.LAKE,
			(yang, yin, yang): Trigrams.FIRE,
			(yang, yin, yin): Trigrams.THUNDER,
			(yin, yang, yang): Trigrams.WIND,
			(yin, yang, yin): Trigrams.WATER,
			(yin, yin, yang): Trigrams.MOUNTAIN,
			(yin, yin, yin): Trigrams.EARTH
		}

		# Hexagrams
		trigram_pairs = product(Trigrams, repeat=2)

		# See https://goo.gl/DNsvds
		hexagram_ids = [
			1, 43, 14, 34, 9, 5, 26, 11,
			10, 58, 38, 54, 61, 60, 41, 19,
			13, 49, 30, 55, 37, 63, 22, 36,
			25, 17, 21, 51, 42, 3, 27, 24,
			44, 28, 50, 32, 57, 48, 18, 46,
			6, 47, 64, 40, 59, 29, 4, 7,
			33, 31, 56, 62, 53, 39, 52, 15,
			12, 45, 35, 16, 20, 8, 23, 2
		]

		# Make dict {trigram combination: id}
		self.hexagrams = dict(zip(trigram_pairs, hexagram_ids))

	def cast_lines(self):
		"""Return initial casting (a list of 6 random Lines)"""
		# Simulate weighted probabilities by multiplying each list item by its probability
		probabilities = [Lines.OLDYIN] * Lines.OLDYIN.probability
		probabilities += [Lines.YANG] * Lines.YANG.probability
		probabilities += [Lines.YIN] * Lines.YIN.probability
		probabilities += [Lines.OLDYANG] * Lines.OLDYANG.probability

		casting = [choice(probabilities) for _ in range(6)]
		return casting

	def get_trigrams(self, casting):
		"""Return tuple of bottom and top trigram for use as dictionary keys"""
		# Deal only with booleans if yin or not
		yin_bools = tuple([line.yin for line in casting])

		bottom_trigram = self.trigrams[yin_bools[:3]]
		top_trigram = self.trigrams[yin_bools[3:]]

		return bottom_trigram, top_trigram

	def get_hexagram_id(self, bottom_trigram, top_trigram):
		"""Return id (starting at 1) for hexagram based on bottom and top trigram"""
		hexagram_id = self.hexagrams[(bottom_trigram, top_trigram)]
		return hexagram_id

	def get_relating_casting(self, casting):
		"""Convert old lines to their opposite and return casting (list of 6 Lines)"""
		# Change old yang to yin
		casting = [Lines.YIN if line is Lines.OLDYANG else line for line in casting]

		# Change old yin to yang
		casting = [Lines.YANG if line is Lines.OLDYIN else line for line in casting]

		return casting

	def line_repr(self, line):
		"""Get string to display a Line on Discord"""
		if line is Lines.OLDYIN:
			return "~~　　　~~╳~~　　　~~"
		if line is Lines.YANG:
			return "~~　　　　　　　~~"
		if line is Lines.YIN:
			return "~~　　　~~　~~　　　~~"
		if line is Lines.OLDYANG:
			return "~~　　　◯　　　~~"

	def get_changing_line_numbers(self, casting):
		"""Get indexes where there is a changing line (starting at 1)"""
		return [i for i, line in enumerate(casting, start=1) if line in [Lines.OLDYIN, Lines.OLDYANG]]

	def load_data(self):
		"""Load JSON from data/i_ching.json into dict"""
		# Won't work if ever in distribution. Convert to use pkg_resources?
		this_directory, this_filename = os.path.split(__file__)
		data_filepath = os.path.join(this_directory, "data", "i_ching.json")

		with open(data_filepath, encoding='utf-8') as f:
			data = json.load(f)

		return data

	def response(self):
		# Make initial casting
		casting = self.cast_lines()
		hexagram_id = self.get_hexagram_id(*self.get_trigrams(casting))

		# Make relating casting
		relating_casting = self.get_relating_casting(casting)
		relating_hexagram_id = self.get_hexagram_id(*self.get_trigrams(relating_casting))

		# Load full I Ching dictionary
		data = self.load_data()

		# Build response
		response = ""

		# Add title
		response += '**HEXAGRAM {} — {}\n'.format(data[hexagram_id-1]['id'], data[hexagram_id-1]['character'])
		response += data[hexagram_id-1]['title'] + '**\n\n'

		# Add hexagram (reversed to be top-down)
		for line in casting[::-1]:
			response += self.line_repr(line) + '\n'
		response += '\n'

		# Add Judgement
		response += '**Judgement**\n'
		response += '```{}```\n'.format(data[hexagram_id-1]['judgement'])

		# Add Image
		response += '**Image**\n'
		response += '```{}```\n'.format(data[hexagram_id-1]['image'])

		# Make link text (don't add yet)
		link = 'For commentary and interpretation:\n'
		link += 'http://www.akirarabelais.com/i/i.html#{}'.format(hexagram_id)

		# Add changing lines and relating hexagram (if any changing lines)
		changing_line_numbers = self.get_changing_line_numbers(casting)
		if len(changing_line_numbers) > 0:
			response += '**Changing Lines**\n'
			number_list_str = ', '.join(str(num) for num in changing_line_numbers)
			response += 'There are changing lines in lines: {} (numbered from the bottom)\n\n'.format(number_list_str)

			for num in changing_line_numbers:
				response += "Line {}:\n".format(num)
				response += '```{}```\n'.format(data[hexagram_id-1]['lines'][num-1])

			# Add commentary link
			response += link + '\n\n'

			# Add relating hexagram
			response += '**RELATING HEXAGRAM: HEXAGRAM {} — {}\n'.format(data[relating_hexagram_id-1]['id'], data[relating_hexagram_id-1]['character'])
			response += data[relating_hexagram_id-1]['title'] + '**\n\n'

			# Add hexagram (reversed to be top-down)
			for line in relating_casting[::-1]:
				response += self.line_repr(line) + '\n'
			response += '\n'

			# Add Judgement
			response += '**Judgement**\n'
			response += '```{}```\n'.format(data[relating_hexagram_id-1]['judgement'])

			# Add Image
			response += '**Image**\n'
			response += '```{}```\n'.format(data[relating_hexagram_id-1]['image'])

			# Add relating hexagram link
			response += 'For commentary and interpretation:\n'
			response += 'http://www.akirarabelais.com/i/i.html#{}'.format(relating_hexagram_id)
		else:
			# Add commentary link for sole hexagram
			response += link

		return response

import re
from random import randint

# ERRORS

class Error(Exception):
	"""Generic error to extend"""
	pass

class ExcessiveQuantityError(Error):
	"""The user was having fun testing how high the numbers go."""
	pass

class MalformedInputError(Error):
	"""The user's string is no good."""
	pass


# CLASS

class DiceService:
	def expected_characters(self, s):
		"""Returns boolean if string has character that aren't digits, +, -, whitespace, or 'd'"""
		result = bool(re.search('^[0-9\+\- d]*$', s))
		return result

	def is_int(self, s):
		"""Returns boolean if string can be converted to an integer"""
		try:
			int(s)
			return True
		except ValueError:
			return False

	def is_die(self, s):
		"""Returns bool if string is 'd' surrounded by any positive number of digits"""
		result = bool(re.search('^\d+d\d+$', s))
		return result

	def calculate_die_rolls(self, die):
		"""Takes a correctly formatted string for die and returns list of random rolls"""
		d_index = die.find('d')
		multiplier, faces = die[:d_index], die[d_index+1:]
		multiplier, faces = int(multiplier), int(faces)

		# Raise ExcessiveQuantityError if numbers are ridiculous
		if multiplier >= 100 or faces >= 1000:
			raise ExcessiveQuantityError()

		# Raise MalformedInputError if faces < 1
		if faces < 1:
			raise MalformedInputError()

		rolls = [randint(1,faces) for roll in range(multiplier)]
		return rolls

	def convert_possible_negative(self, s):
		"""If die is negative, return positive die and -1 to multiply by. Otherwise returns 1 and original string."""
		if s[0] == '-':
			return -1, s[1:]
		else:
			return 1, s

	def process(self, s):
		"""Takes in string, returns result int and list of individual rolls"""

		total_rolls = []
		total = 0

		try:
			# Ignore case (convert all to lowercase)
			s = s.lower()

			# Raise MalformedInputError if unexpected characters
			if not self.expected_characters(s):
				raise MalformedInputError()

			# Remove all spaces
			s = s.replace(' ', '')

			# Replace -'s with +- for consistent addition and easy splitting
			s = s.replace('-', '+-')

			# Split string by +'s
			segments = s.split('+')

			# Raise MalformedInputError if any blank segments (+ at start/end, multiple +'s in row)
			if '' in segments:
				raise MalformedInputError()

			# Parse each segment and add to total
			for segment in segments:
				# Convert to positive with multiplier
				multiplier, positive_segment = self.convert_possible_negative(segment)

				# If int, add to total
				# (positive_segment not necessary because int() handles negatives)
				if self.is_int(segment):
					total += int(segment)
				# If die, calculate rolls list and add sum to total
				elif self.is_die(positive_segment):
					rolls = self.calculate_die_rolls(positive_segment)
					total_rolls += rolls
					total += multiplier * sum(rolls)
				# If not integer or die, raise error
				else:
					raise MalformedInputError()
		except MalformedInputError:
			return 'Could not parse input. For formatting help, use `!help dice`.'
		except ExcessiveQuantityError:
			return "Please use multipliers below 100 and die faces below 1000."

		# Build response
		response = ""

		# Add snark if someone testing maximums
		if s == '99d999':
			response += '*...fine...*\n\n'

		# Special scenarios for critical hits/misses on d20
		if s == '1d20' and total is 20:
			response += '**CRITICAL HIT!**\n'
		if s == '1d20' and total is 1:
			response += '**CRITICAL MISS!**\n'

		# Print total in bold
		response += 'Total: **' + str(total) + '**'

		# Add individual rolls if more than 1
		if len(total_rolls) > 1:
			response += '\nIndividual rolls: ' + ', '.join([str(roll) for roll in total_rolls])

		# Add snark if no dice
		if len(total_rolls) is 0:
			response += '\nAlways glad to help!'
		# Add 'nice' if dice total is cool number (and user didn't just type number in)
		elif total in [69, 420, 666]:
			response += "\n\nNice."

		return response

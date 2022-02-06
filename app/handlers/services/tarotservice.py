import os
from PIL import Image
import random
import json

# ERRORS

class Error(Exception):
	"""Generic error to extend"""
	pass

class DeckNotFoundError(Error):
	"""The deck name provided is not supported."""
	pass

class SpreadNotFoundError(Error):
	"""The spread name provided is not supported."""
	pass

class BadTypeError(Error):
	"""The provided argument is not the expected type. (Often a non-boolean instead of a boolean.)"""
	pass


# DECORATORS

def card_count(i):
	"""Sets amount of cards needed by each spread"""
	def decorator(func):
		func.card_count = i
		return func
	return decorator


# CLASSES

class ResponseModel:
	"""Holds a message and image (default=None) to return to the MessageHandler (instead of generic tuple)"""
	def __init__(self, message, image=None):
		self.message = message
		self.image = image

class Card:
	"""Holds a card's ID (0-77), reversed boolean, description, and PIL image."""
	def __init__(self, id, reversed, description, image):
		self.id = id
		self.reversed = reversed
		self.description = description
		self.image = image

class TarotService:
	def __init__(self):
		"""Lists available avaiable decks and spreads for later methods"""
		self.decks = [
			'rider-waite-smith',
			'cbd-marseille',
			'ancient-italian'
		]
		self.spreads = {
			'single': self.single,
			'three-card': self.three_card,
			'celtic-cross': self.celtic_cross
		}

	# SPREADS

	@card_count(1)
	def single(self, cards):
		"""Makes a ResponseModel with the PIL image and text for a single-card spread."""
		card = cards[0]
		return ResponseModel(card.description, card.image)

	@card_count(3)
	def three_card(self, cards):
		"""Makes a ResponseModel with the PIL image and text for a horizontal three-card spread."""
		# Get output image dimensions
		card_width, card_height = cards[0].image.size
		padding = card_width // 20

		output_width = card_width * len(cards) + padding * (len(cards) - 1)
		output_height = card_height
		output_img = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))

		# Generate top-left corner points to place cards
		x_points = [i * (card_width + padding) for i in range(len(cards))]

		# Place each card in its point
		for card, x in zip(cards, x_points):
			output_img.paste(card.image, (x, 0))

		# Combine descriptions
		message = "\n\n".join([card.description for card in cards])

		return ResponseModel(message, output_img)

	@card_count(10)
	def celtic_cross(self, cards):
		"""Makes a ResponseModel with the large PIL image and text for a complex celtic cross spread."""
		# Build output
		# Calculate dimensions and paddings
		card_width, card_height = cards[0].image.size
		column_padding = card_width // 20
		cross_padding = card_height - card_width + column_padding

		output_height = card_height * 4 + column_padding * 3
		output_width = card_width * 4 + cross_padding * 3
		output_img = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))

		# Build points to place cards
		points = []

		# Replace cross_ys with below for full-height cross (too much negative space, IMO)
		# cross_ys = [0, (output_height-card_height)//2, output_height-card_height]

		# Make three vertical Y coordinates
		cross_ys = [
			cross_padding // 2,
			(output_height - card_height) // 2,
			output_height - card_height - (cross_padding // 2)
		]

		# Make four horizontal X coordinates
		card_xs = [i * (card_width + cross_padding) for i in range(4)]

		# Make points for individual cards
		# Card 0 (Cross left)
		x = card_xs[0]
		y = cross_ys[1]
		points.append((x,y))

		# Cards 1-3 (Cross top/middle/bottom)
		x = card_xs[1]
		points += [(x, y) for y in cross_ys]

		# Card 4 (Turned center)
		# Rotate image
		cards[4].image = cards[4].image.rotate(270, expand=True)
		# Calculate coordinates from cross center coordinates
		x, y = points[2]
		dimension_difference = (card_height - card_width) // 2
		x -= dimension_difference
		y += dimension_difference
		points.append((x,y))

		# Card 5 (Cross right)
		x = card_xs[2]
		y = cross_ys[1]
		points.append((x,y))

		# Cards 6-9 (Column)
		x = card_xs[3]
		padded_height = card_height + column_padding
		points += [(x, padded_height*i) for i in range(4)]

		# Place each card in its point
		for card, point in zip(cards, points):
			output_img.paste(card.image, (point[0], point[1]))

		# Rearrange cards in more readable way
		indices = [2, 4, 1, 3, 0, 5, 9, 8, 7, 6]
		cards = [cards[i] for i in indices]

		# Add reading key
		message = "```"
		message += "   3      10\n\n"
		message += "          9\n"
		message += "5  1  6\n"
		message += "   2      8\n\n"
		message += "   4      7"
		message += "```\n\n"

		# Define slot descriptions
		slots = [
			"Current situation",
			"Opposing forces",
			"Querent's outlook and approach",
			"Underlying or subconscious factors",
			"Past",
			"Immediate future",
			"The querent",
			"Environment or external influences",
			"Hopes and fears",
			"Final outcome on current trajectory"
		]

		# Combine descriptions with "#X" in front of name and slot description before first '\n'
		descriptions = []
		for i, card in enumerate(cards):
			first_newline = card.description.index('\n')
			name, meaning = card.description[:first_newline], card.description[first_newline+1:]
			descriptions += ["#{} {} ({})\n{}".format(i+1, name, slots[i], meaning)]

		message += "\n\n".join(descriptions)

		return ResponseModel(message, output_img)

	# BUILDING RANDOM CARDS

	def draw_cards(self, amount, deck, reversals, pips):
		"""Build list of desired amount of random Cards with attached id, reversed boolean, description, and image (flipped if reversed)."""
		# Grab all 78 cards or first 21 if 'pips' are included
		upper_range = 79 if pips else 22

		# Select 'amount' of random non-repeated cards from desired range
		card_ids = random.sample(range(1, upper_range), amount)

		# Attach descriptions and PIL images and build list of cards
		cards = []
		data = self.load_data()

		for card_id in card_ids:
			# 25% reversed cards seems okay (always set to False if no reversals)
			reversed = random.randrange(100) < 25 if reversals else False

			# Build text description (subtract 1 because JSON 0-indexed)
			name = '**' + data[card_id-1]['name'] + '**'
			meaning = data[card_id-1]['meaning']

			# Add reversal notes
			if reversed:
				name += ' (REVERSED)'
				meaning += '\n(Note: Reversed card alters default interpretation)'

			description = name + '\n' + meaning

			# Get PIL image
			image = self.load_image(deck, card_id)

			# Flip 180 if reversed
			if reversed:
				image = image.rotate(180)

			# Add card to list
			cards.append(Card(card_id, reversed, description, image))

		return cards

	def load_image(self, deck, card_id):
		"""Load PIL image for {card_id}.jpg from data/tarot/decks/{deck}"""
		# Won't work if ever in distribution. Convert to use pkg_resources?
		this_directory, this_filename = os.path.split(__file__)
		filename = str(card_id) + ".jpg"
		img_filepath = os.path.join(this_directory, "data", "tarot", "decks", deck, filename)

		# TODO raise error if invalid path. Only possible if self.decks and filesystem unsynchronized
		img = Image.open(img_filepath, 'r')

		return img

	def load_data(self):
		"""Load JSON from data/tarot/tarot.json into dict"""
		# Won't work if ever in distribution. Convert to use pkg_resources?
		this_directory, this_filename = os.path.split(__file__)
		data_filepath = os.path.join(this_directory, "data", "tarot", "tarot.json")

		with open(data_filepath, encoding='utf-8') as f:
			data = json.load(f)

		return data

	def validate_arguments(self, deck, spread, definitions, reversals, pips):
		"""Raise error if unsupported deck or spread, or non-boolean received for definitions, reversals, or pips."""
		if deck not in self.decks:
			raise DeckNotFoundError()

		if spread not in self.spreads.keys():
			raise SpreadNotFoundError()

		# Make sure all booleans are booleans
		if not all(isinstance(b, bool) for b in [definitions, reversals, pips]):
			raise BadTypeError()

	# RUNNING

	def response(self, deck='rider-waite-smith', spread='three-card', definitions=True, reversals=False, pips=True):
		"""Build ResponseModel of message and generated PIL image for random cards based on arguments."""
		try:
			self.validate_arguments(deck, spread, definitions, reversals, pips)
		except DeckNotFoundError:
			return ResponseModel('Deck not found. For a list of available decks, use `))help tarot`.')
		except SpreadNotFoundError:
			return ResponseModel('Spread not found. For a list of available spreads, use `))help tarot`.')
		except BadTypeError:
			return ResponseModel('Received an unexpected argument value. For formatting help, use `!help tarot`.')

		# Get this spread's function (dict of functions defined in __init__)
		spread_func = self.spreads[spread]

		# Get list of randomized cards
		cards = self.draw_cards(spread_func.card_count, deck, reversals, pips)

		# Send cards to spread function for ResponseModel of message and PIL image
		result = spread_func(cards)

		# Remove definitions if undesired
		if not definitions:
			result.message = ''

		return result

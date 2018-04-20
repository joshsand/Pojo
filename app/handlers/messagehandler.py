import random
import re
import os
from io import BytesIO
from app.handlers.services import *

# ERRORS

class Error(Exception):
	"""Generic error to extend"""
	pass

class MalformedArgumentError(Error):
	"""The message has incorrectly formatted arguments."""
	pass


# CLASS

class MessageHandler:

	# DECORATORS

	def general_filter(func):
		"""Adds 'filter' attribute. Value irrelevant since only tested with hasattr()"""
		func.filter = True
		return func

	def command(func):
		"""Adds 'command' attribute. Value irrelevant since only tested with hasattr()"""
		func.command = True
		return func

	def secret(func):
		"""Adds 'secret' attribute. Value irrelevant since only tested with hasattr()"""
		func.secret = True
		return func

	def rename(new_name):
		"""Decorator to change __name__ on functions when !command doesn't match the function's name."""
		def decorator(func):
			func.__name__ = new_name
			return func
		return decorator


	# COMMANDS

	@command
	async def help(self, message):
		"""Use to read instructions for any command. Call with no command specified to see a list of available commands.

		Usage: `!help` or `!help 8ball`
		Returns: Help for individual command, or list of available commands
		Arguments: A command name (no exclamation point) or none
		"""
		name, remainder = self.split_by_command(message)
		# If there's a command name to look up
		if remainder is not None:
			command = remainder.split()[0]

			if command in self.commands:
				# Get function doc
				doc = self.commands[command].__doc__
				# Remove tabs and right whitespace
				doc = re.sub('[\t]', '', doc)
				doc = doc.rstrip()

				# Bold header
				response = '**' + command + '**\n'
				response += doc

				await self.client.send_message(message.channel, response)
			else:
				response = 'Command not recognized. Type `!help` to see a list of available commands.'
				await self.client.send_message(message.channel, response)
		else:
			response = "Available commands:"
			# All keys whose functions don't have attribute "secret"
			for command in [key for key in self.commands.keys() if not hasattr(self.commands[key], 'secret')]:
				response += '\n • `' + command + '`'
			await self.client.send_message(message.channel, response)

	@command
	async def sup(self, message):
		"""A simple debug method. Say 'sup' to Pojo, Pojo responds 'Hey'.

		Usage: `!sup`
		Returns: `Hey`
		Arguments: None
		"""
		response = 'Hey'
		await self.client.send_message(message.channel, response)

	@rename('8ball')
	@command
	async def eight_ball(self, message):
		"""Ask a yes/no question to Pojo's Magic 8-Ball. (You don't actually have to type a question.)

		Usage: `!8ball` or `!8ball Will I graduate on time?`
		Returns: Random Magic 8-Ball message
		Arguments: None (or, your yes/no question, though not actually necessary)
		"""
		responses = [
			'It is certain',
			'It is decidedly so',
			'Without a doubt',
			'Yes definitely',
			'You may rely on it',
			'As I see it, yes',
			'Most likely',
			'Outlook good',
			'Yes',
			'Signs point to yes',
			'Reply hazy try again',
			'Ask again later',
			'Better not tell you now',
			'Cannot predict now',
			'Concentrate and ask again',
			'Don\'t count on it',
			'My reply is no',
			'My sources say no',
			'Outlook not so good',
			'Very doubtful'
		]

		response = random.choice(responses)
		await self.client.send_message(message.channel, response)

	@command
	async def dice(self, message):
		"""Let Pojo roll your D&D dice for you based on your provided equation. Format dice as multiplier + 'd' + number of sides (e.g., `1d20`). Supports addition and subtraction.

		Usage: `!dice 1d20`, `!dice 3d10`, `!dice 2d20 - 1d6  + 10`
		Returns: Total, individual rolls (if more than one)
		Arguments: Equation to parse (see usage examples)
		"""
		service = diceservice.DiceService()
		command, remainder = self.split_by_command(message)
		response = service.process(remainder)
		await self.client.send_message(message.channel, response)

	@rename('secret')
	@secret
	@command
	async def secret_command(self, message):
		"""A simple secret debug method. Responds with 'Shhh'.

		Usage: `!secret`
		Returns: `Shhh`
		Arguments: None
		"""
		response = 'Shhh'
		await self.client.send_message(message.channel, response)

	@rename('iching')
	@command
	async def i_ching(self, message):
		"""Consult the ancient Chinese oracle! Ask an open-ended (NOT yes or no) question about a method of action you are considering, the forces at work in a situation, how they develop and change, and how you relate to them. (You don't actually have to type a question) Pojo shuffles the digital yarrow stalks and gives you a hexagram (six lines representing yin or yang) and its associated text and any changing lines.

		"Changing lines" refer to yin and yang lines in the hexagram that are subject to change. Each position contains specific directions and outcomes relevant to your situation. These changing lines flip to their opposite to create a "relating hexagram" containing further information about the context and outcome potential in your situation.

		Usage: `!iching` or `!iching What will happen if I drop CST-201?` or `!iching What should my attitude be toward learning MongoDB?`
		Returns: Your I Ching casting
		Arguments: None (or, your question, though not actually necessary)
		"""
		service = ichingservice.IChingService()
		response = service.response()
		await self.client.send_message(message.channel, response)

	@secret
	@command
	async def cat(self, message):
		"""A test command to send a picture to a channel.

		Usage: `!cat`
		Returns: A spooky picture of Josh's cat
		Arguments: None
		"""
		this_directory, this_filename = os.path.split(__file__)
		data_filepath = os.path.join(this_directory, "services", "data", "cat", "cat.jpg")

		with open(data_filepath, 'rb') as f:
			await self.client.send_file(message.channel, f)

	@command
	async def tarot(self, message):
		"""Let Pojo flip your tarot cards! Supports multiple decks and spreads, with options for definitions, reversed cards, and pip cards.

		Usage: `!tarot` or `!tarot spread=celtic-cross pips=false deck=cbd-marseille`
		Returns: An image of your tarot spread of choice, with optional definitions.
		Arguments:
		 • `deck`: The tarot deck to use. Options: `tarot-waite-smith` (the iconic deck) [default], `cbd-marseille` (clean restoration of classic 1700's European design), `ancient-italian` (detailed floral late-1800's deck)
		 • `spread`: The arrangement of cards. Options: `single` (a single card), `three-card` (three cards in a row...widely applicable) [default], `celtic-cross` (the elaborate and popular 10-card spread)
		 • `definitions`: Whether Pojo sends follow-up card definitions. Options: `true` [default], `false` (for pros)
		 • `reversals`: Whether reading includes reversed/inverted cards. Options: `true`, `false` [default]
		 • `pips`: Whether reading includes pips (standard numbered and face cards). Options `true` [default], `false`
		"""
		# Send "typing" because this one can take a few seconds
		await self.client.send_typing(message.channel)

		# Initialize responses
		command, remainder = self.split_by_command(message)
		kwargs = {}

		response = None
		response_message = ""
		response_image = None

		# Parse arguments
		try:
			if remainder is not None:
				kwargs = self.args_to_dict(remainder)
		except MalformedArgumentError:
			response_message = "Arguments could not be parsed. For formatting help, use `!help tarot`."
			kwargs = None

		# Attempt response
		if kwargs is not None:
			service = tarotservice.TarotService()
			try:
				response = service.response(**kwargs)
			except TypeError:
				response_message = "Received an unexpected argument. For all allowed arguments, use `!help tarot`."

			# Get message and image from response model
			if response is not None:
				response_message = response.message
				response_image = response.image

		# Send image (if received)
		if response_image is not None:
			# Convert to BytesIO file-like object (necessary to send through Discord.py's send_file())
			bytes = BytesIO()
			response_image.save(bytes, 'PNG')
			bytes.name = 'tarot.png'
			bytes.seek(0)

			await self.client.send_file(message.channel, bytes)

		# Send response text (if any)
		if response_message != '':
			await self.client.send_message(message.channel, response_message)

	# GENERAL FILTERS

	@general_filter
	async def someone_say_pojo(self, message):
		"""Responds with random message to variations of 'Pojo'."""
		# Lowercase
		msg = message.content.lower()

		# Quick rejection if no p or j
		if 'p' not in msg or 'j' not in msg:
			return None

		# Convert zeros to o's
		msg = msg.replace('0', 'o')

		# Convert ()'s to o's
		msg = msg.replace('()', 'o')

		# Remove non-alphabetic characters
		msg = re.sub('[^a-z]+', '', msg)

		# Keyword matches
		pojos = ["pojo", "plainoldjavaobject"]

		# If any of the pojo matches are in msg...
		if any(pojo in msg for pojo in pojos):
			responses = [
				'Pojo?',
				'Pooojooo',
				'POJO!',
				'...pojo',
				'Pojopojopojopojo',
				'POJO!!!!!',
				'Pojo...',
				'Pojo?',
				'Someone say "Pojo?"',
				'Pojo',
				'Oh...pojo.',
				'Pojo',
				'Pojo...pojo.',
				'Pojo? Pojo.',
				'Poooooooojoooo',
				'Po? Jo?',
				'ＰＯＪＯ',
				'Pojo! Pojo!!',
				'𝖕𝖔𝖏𝖔',
				'𝕡𝕠𝕛𝕠'
			]

			response = random.choice(responses)
			await self.client.send_message(message.channel, response)

	@general_filter
	async def greater_good(self, message):
		"""Respond to 'greater good' so I don't have to."""
		# Lowercase
		msg = message.content.lower()

		# If 'greater good' is found, respond in kind
		if 'greater good' in msg:
			response = '*The greater good*'
			await self.client.send_message(message.channel, response)

	# TOOLS

	def split_by_command(self, message):
		"""Return tuple of command (w/o '!') and remainder of message. (Either may be None.)"""
		s = message.content

		# If first letter isn't !, not a command
		if s[0] is not '!':
			return None, s
		else:
			# Split string by spaces
			words = s.split()

			# Get command name (no '!')
			command_name = words[0][1:]

			# If message has more than one word, get remainder of message
			if len(words) > 1:
				remainder = ' '.join(words[1:])
			else:
				remainder = None

			return command_name, remainder

	def args_to_dict(self, s):
		"""Convert "key1=value2 key2=value2"-style formatted arguments to dict"""
		args = {}

		# Split string by spaces
		for arg in s.split(' '):
			# Return error if no ='s (stray words) or too many
			if arg.count('=') is not 1:
				raise MalformedArgumentError()

			# Split by equal sign for key and value
			k, v = arg.split('=')

			# Return error if either side empty (i.e., = at begin/end)
			if k is '' or v is '':
				raise MalformedArgumentError()

			# Convert to boolean
			if v.lower() == 'true':
				v = True
			elif v.lower() == 'false':
				v = False
			# If not boolean, maybe int?
			else:
				try:
					v = int(v)
				except ValueError:
					pass

			# Add key/value to dict
			args[k] = v

		return args


	# RUNNING

	def __init__(self, client):
		self.client = client

		# Get all methods in class
		functions = [getattr(MessageHandler, func) for func in dir(MessageHandler)]

		# Store list of methods with 'filter' attribute (from @general_filter)
		self.filters = [func for func in functions if hasattr(func, 'filter')]

		# Set up dict of commands with methods with 'command' attribute (from @command)
		command_functions = [func for func in functions if hasattr(func, 'command')]
		command_names = [c.__name__ for c in command_functions]
		self.commands = dict(zip(command_names, command_functions))

	async def parse(self, message):
		# Run filters
		for func in self.filters:
			await func(self, message)

		name, remainder = self.split_by_command(message)
		if (name is not None and name in self.commands):
			await self.commands[name](self, message)

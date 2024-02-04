import random
import re
import os
from io import BytesIO
from discord import File
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
		"""Decorator to change __name__ on functions when ))command doesn't match the function's name."""
		def decorator(func):
			func.__name__ = new_name
			return func
		return decorator


	# COMMANDS

	@command
	async def help(self, message):
		"""Use to read instructions for any command. Call with no command specified to see a list of available commands.

		Usage: `))help` or `))help 8ball`
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

				await message.channel.send(response)
			else:
				response = 'Command not recognized. Type `))help` to see a list of available commands.'
				await message.channel.send(response)
		else:
			response = "Available commands:"
			# All keys whose functions don't have attribute "secret"
			for command in [key for key in self.commands.keys() if not hasattr(self.commands[key], 'secret')]:
				response += '\n • `' + command + '`'
			await message.channel.send(response)

	@command
	async def sup(self, message):
		"""A simple debug method. Say 'sup' to Pojo, Pojo responds 'Hey'.

		Usage: `))sup`
		Returns: `Hey`
		Arguments: None
		"""
		response = 'Hey'
		await message.channel.send(response)

	@rename('8ball')
	@command
	async def eight_ball(self, message):
		"""Ask a yes/no question to Pojo's Magic 8-Ball. (You don't actually have to type a question.)

		Usage: `))8ball` or `))8ball Will I graduate on time?`
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
		await message.channel.send(response)

	@command
	async def dice(self, message):
		"""Let Pojo roll your D&D dice for you based on your provided equation. Format dice as multiplier + 'd' + number of sides (e.g., `1d20`). Supports addition and subtraction.

		Usage: `))dice 1d20`, `))dice 3d10`, `))dice 2d20 - 1d6  + 10`
		Returns: Total, individual rolls (if more than one)
		Arguments: Equation to parse (see usage examples)
		"""
		service = diceservice.DiceService()
		command, remainder = self.split_by_command(message)
		response = service.process(remainder)
		await message.channel.send(response)

	@rename('secret')
	@secret
	@command
	async def secret_command(self, message):
		"""A simple secret debug method. Responds with 'Shhh'.

		Usage: `))secret`
		Returns: `Shhh`
		Arguments: None
		"""
		response = 'Shhh'
		await message.channel.send(response)

	@rename('iching')
	@command
	async def i_ching(self, message):
		"""Consult the ancient Chinese oracle! Ask an open-ended (NOT yes or no) question about a method of action you are considering, the forces at work in a situation, how they develop and change, and how you relate to them. (You don't actually have to type a question) Pojo shuffles the digital yarrow stalks and gives you a hexagram (six lines representing yin or yang) and its associated text and any changing lines.

		"Changing lines" refer to yin and yang lines in the hexagram that are subject to change. Each position contains specific directions and outcomes relevant to your situation. These changing lines flip to their opposite to create a "relating hexagram" containing further information about the context and outcome potential in your situation.

		Usage: `))iching` or `))iching What will happen if I drop CST-201?` or `))iching What should my attitude be toward learning MongoDB?`
		Returns: Your I Ching casting
		Arguments: None (or, your question, though not actually necessary)
		"""
		service = ichingservice.IChingService()
		response = service.response()
		await message.channel.send(response)

	@secret
	@command
	async def cat(self, message):
		"""A test command to send a picture to a channel.

		Usage: `))cat`
		Returns: A spooky picture of Josh's cat
		Arguments: None
		"""
		this_directory, this_filename = os.path.split(__file__)
		data_filepath = os.path.join(this_directory, "services", "data", "cat", "cat.jpg")

		with open(data_filepath, 'rb') as bytes:
			f = File(bytes, filename="cat.jpg")
			await message.channel.send(file=f)

	@command
	async def tarot(self, message):
		"""Let Pojo flip your tarot cards! Supports multiple decks and spreads, with options for definitions, reversed cards, and pip cards.

		Usage: `))tarot` or `))tarot spread=celtic-cross pips=false deck=cbd-marseille`
		Returns: An image of your tarot spread of choice, with optional definitions.
		Arguments:
		 • `deck`: The tarot deck to use. Options: `tarot-waite-smith` (the iconic deck) [default], `cbd-marseille` (clean restoration of classic 1700's European design), `ancient-italian` (detailed floral late-1800's deck)
		 • `spread`: The arrangement of cards. Options: `single` (a single card), `three-card` (three cards in a row...widely applicable) [default], `celtic-cross` (the elaborate and popular 10-card spread)
		 • `definitions`: Whether Pojo sends follow-up card definitions. Options: `true` [default], `false` (for pros)
		 • `reversals`: Whether reading includes reversed/inverted cards. Options: `true`, `false` [default]
		 • `pips`: Whether reading includes pips (standard numbered and face cards). Options `true` [default], `false`
		"""
		# Send "typing" because this one can take a few seconds
		await message.channel.typing()

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
			response_message = "Arguments could not be parsed. For formatting help, use `))help tarot`."
			kwargs = None

		# Attempt response
		if kwargs is not None:
			service = tarotservice.TarotService()
			try:
				response = service.response(**kwargs)
			except TypeError:
				response_message = "Received an unexpected argument. For all allowed arguments, use `))help tarot`."

			# Get message and image from response model
			if response is not None:
				response_message = response.message
				response_image = response.image

		# Send image (if received)
		if response_image is not None:
			# Convert to BytesIO file-like object (necessary to send through Discord.py's send())
			bytes = BytesIO()
			response_image.save(bytes, 'PNG')
			bytes.name = 'tarot.png'
			bytes.seek(0)

			f = File(bytes, filename="tarot.png")
			await message.channel.send(file=f)

		# Send response text (if any)
		if response_message != '':
			await message.channel.send(response_message)

	@command
	async def fact(self, message):
		pass

	@secret
	@rename('dark-iching')
	@command
	async def dark_i_ching(self, message):
		"""Joke method, returns text.

		Usage: `))dark-iching`
		Returns: A special message
		Arguments: None
		"""
		response = '# WHAT HAVE YOU DONE'
		await message.channel.send(response)

	@command
	async def oblique(self, message):
		"""Summon the wisdom of Brian Eno's Oblique Strategies in your creative endeavors.

		Usage: `))oblique`
		Returns: Random Oblique Strategies card message
		Arguments: None
		"""
		responses = [
			'Abandon normal instruments',
			'Accept advice',
			'Accretion',
			'A line has two sides',
			'Allow an easement (an easement is the abandonment of a stricture)',
			'Are there sections? Consider transitions',
			'Ask people to work against their better judgement',
			'Ask your body',
			'Assemble some of the instruments in a group and treat the group',
			'Balance the consistency principle with the inconsistency principle',
			'Be dirty',
			'Breathe more deeply',
			'Bridges -build -burn',
			'Cascades',
			'Change instrument roles',
			'Change nothing and continue with immaculate consistency',
			'Children\'s voices -speaking -singing',
			'Cluster analysis',
			'Consider different fading systems',
			'Consult other sources -promising -unpromising',
			'Convert a melodic element into a rhythmic element',
			'Courage!',
			'Cut a vital connection',
			'Decorate, decorate',
			'Define an area as `safe\' and use it as an anchor',
			'Destroy -nothing -the most important thing',
			'Discard an axiom',
			'Disconnect from desire',
			'Discover the recipes you are using and abandon them',
			'Distorting time',
			'Do nothing for as long as possible',
			'Don\'t be afraid of things because they\'re easy to do',
			'Don\'t be frightened of cliches',
			'Don\'t be frightened to display your talents',
			'Don\'t break the silence',
			'Don\'t stress one thing more than another',
			'Do something boring',
			'Do the washing up',
			'Do the words need changing?',
			'Do we need holes?',
			'Emphasize differences',
			'Emphasize repetitions',
			'Emphasize the flaws',
			'Faced with a choice, do both (given by Dieter Roth)',
			'Feedback recordings into an acoustic situation',
			'Fill every beat with something',
			'Get your neck massaged',
			'Ghost echoes',
			'Give the game away',
			'Give way to your worst impulse',
			'Go slowly all the way round the outside',
			'Honor thy error as a hidden intention',
			'How would you have done it?',
			'Humanize something free of error',
			'Imagine the music as a moving chain or caterpillar',
			'Imagine the music as a set of disconnected events',
			'Infinitesimal gradations',
			'Intentions -credibility of -nobility of -humility of',
			'Into the impossible',
			'Is it finished?',
			'Is there something missing?',
			'Is the tuning appropriate?',
			'Just carry on',
			'Left channel, right channel, centre channel',
			'Listen in total darkness, or in a very large room, very quietly',
			'Listen to the quiet voice',
			'Look at a very small object, look at its centre',
			'Look at the order in which you do things',
			'Look closely at the most embarrassing details and amplify them',
			'Lowest common denominator check -single beat -single note -single',
			'riff',
			'Make a blank valuable by putting it in an exquisite frame',
			'Make an exhaustive list of everything you might do and do the last thing on the list',
			'Make a sudden, destructive unpredictable action; incorporate',
			'Mechanicalize something idiosyncratic',
			'Mute and continue',
			'Only one element of each kind',
			'(Organic) machinery',
			'Overtly resist change',
			'Put in earplugs',
			'Remember those quiet evenings',
			'Remove ambiguities and convert to specifics',
			'Remove specifics and convert to ambiguities',
			'Repetition is a form of change',
			'Reverse',
			'Short circuit (example: a man eating peas with the idea that they will improve his virility shovels them straight into his lap)',
			'Shut the door and listen from outside',
			'Simple subtraction',
			'Spectrum analysis',
			'Take a break',
			'Take away the elements in order of apparent non-importance',
			'Tape your mouth (given by Ritva Saarikko)',
			'The inconsistency principle',
			'The tape is now the music',
			'Think of the radio',
			'Tidy up',
			'Trust in the you of now',
			'Turn it upside down',
			'Twist the spine',
			'Use an old idea',
			'Use an unacceptable color',
			'Use fewer notes',
			'Use filters',
			'Use "unqualified" people',
			'Water',
			'What are you really thinking about just now? Incorporate',
			'What is the reality of the situation?',
			'What mistakes did you make last time?',
			'What would your closest friend do?',
			'What wouldn\'t you do?',
			'Work at a different speed',
			'You are an engineer',
			'You can only make one dot at a time',
			'You don\'t have to be ashamed of using your own ideas',
			'​'
		]

		response = random.choice(responses)
		await message.channel.send(response)

	# GENERAL FILTERS

	@general_filter
	async def someone_say_pojo(self, message):
		"""Responds with random message to variations of 'Pojo'."""
		# Lowercase
		msg = message.content.lower()

		# Quick rejection if no p or j
		if 'p' not in msg or 'j' not in msg:
			return

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
			await message.channel.send(response)

	@general_filter
	async def greater_good(self, message):
		"""Respond to 'greater good' so I don't have to."""
		# Lowercase
		msg = message.content.lower()

		# If 'greater good' is found, respond in kind
		if 'greater good' in msg:
			response = '*The greater good*'
			await message.channel.send(response)

	# TOOLS

	def split_by_command(self, message):
		"""Return tuple of command (w/o prefix) and remainder of message. (Either may be None.)"""
		prefix = '))'

		s = message.content

		# If message doesn't start with prefix, not a command
		if not s.startswith(prefix):
			return None, s
		else:
			# Split string by spaces
			words = s.split()

			# Get command name (no prefix)
			command_name = words[0][len(prefix):]

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
			if arg.count('=') != 1:
				raise MalformedArgumentError()

			# Split by equal sign for key and value
			k, v = arg.split('=')

			# Return error if either side empty (i.e., = at begin/end)
			if k == '' or v == '':
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

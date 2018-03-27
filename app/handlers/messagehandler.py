import random
import re
from app.handlers.services import *

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
		# If a command name to look up is given
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

	@secret
	@command
	async def secret(self, message):
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

	# GENERAL FILTERS

	@general_filter
	async def someone_say_pojo(self, message):
		# Let's see Jerran get around this one
		pojos = ["pojo", "p_o_j_o", "p o j o", "p-o-j-o", "plain old java object", "p()j()"]

		# Lowercase
		msg = message.content.lower()

		# Remove double spaces
		msg = ' '.join(msg.split())

		# Convert zeros to o's
		msg = msg.replace('0', 'o')

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

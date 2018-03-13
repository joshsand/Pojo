import random, re

def rename(new_name):
	"""Decorator to change __name__ on functions when !command doesn't match the function's name."""
	def decorator(f):
		f.__name__ = new_name
		return f
	return decorator

class MessageHandler:
	# COMMANDS
	async def help(self, message):
		"""Use to read instructions for any command. Call with no command specified to see a list of available commands.
		
		Usage: `!help` or `!help 8ball`
		Returns: Help for individual command, or list of available commands
		Arguments: A command name (no exclamation point) or none
		"""
		name, remainder = self.get_command_name(message)
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
			for command in self.commands.keys():
				response += '\n • `' + command + '`'
			await self.client.send_message(message.channel, response)
	
	async def sup(self, message):
		"""A simple debug method. Say 'sup' to Pojo, Pojo responds 'Hey'.
		
		Usage: `!sup`
		Returns: `Hey`
		Arguments: None
		"""
		response = 'Hey'
		await self.client.send_message(message.channel, response)
		
	@rename('8ball')	
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
		
	# GENERAL FILTERS

	async def someone_say_pojo(self, message):
		# Let's see Jerran get around this one
		pojos = ["pojo", "p_o_j_o", "p o j o", "p-o-j-o", "plain old java object"]
	
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
	
	def get_command_name(self, message):
		"""Return tuple of command (w/o '!') and remainder of message. (Either may be None.)"""
		str = message.content
		
		# If first letter isn't !, not a command
		if str[0] is not '!':
			return None, str
		else:
			# Split str by spaces
			words = str.split()
			
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
		
		# Set up list of filters
		self.filters = [self.someone_say_pojo]
		
		# Set up dict of commands
		command_functions = [self.help, self.sup, self.eight_ball]
		command_names = [c.__name__ for c in command_functions]
		self.commands = dict(zip(command_names, command_functions))
		
	async def parse(self, message):
		# Run filters
		for f in self.filters:
			await f(message)
		
		name, remainder = self.get_command_name(message)
		if (name is not None and name in self.commands):
			await self.commands[name](message)
			
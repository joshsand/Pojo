import discord, random

client = discord.Client()

@client.event
async def on_message(message):
	# Ignore messages from self
	if message.author == client.user:
		return
		
	await someoneSayPojo(message)
	
async def someoneSayPojo(message):
	# Let's see Jerran get around this one
	pojos = ["POJO", "P_O_J_O", "P O J O", "P-O-J-O"]
	
	# Uppercase
	msg = message.content.upper()
	
	# Remove double spaces
	msg = ' '.join(msg.split())
	
	# Convert zeros to O's
	msg = msg.replace('0', 'O')
	
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
		await client.send_message(message.channel, response)
		
@client.event
async def on_ready():
	print('Pojo awakes')
	
client.run('NDE5NzYzMjY1NjMyMDc1Nzc3.DX02ww.vj2GObEpqMeZEYswpbNzhwW7Zkw')
import discord, random

client = discord.Client()

@client.event
async def on_message(message):
	# Ignore messages from self
	if message.author == client.user:
		return
		
	await someoneSayPojo(message)
	
async def someoneSayPojo(message):
	if "POJO" in message.content.upper():
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
	print('Pojopy is ready and rhymes with jalopy')
	print(client.user.name)
	print(client.user.id)
	print('-----')
	
client.run('NDE5NzYzMjY1NjMyMDc1Nzc3.DX02ww.vj2GObEpqMeZEYswpbNzhwW7Zkw')
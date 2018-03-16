import discord
import random
from app.handlers.messagehandler import MessageHandler

client = discord.Client()
handler = MessageHandler(client)

@client.event
async def on_message(message):
	# Ignore messages from self
	if message.author == client.user:
		return
		
	await handler.parse(message)
		
@client.event
async def on_ready():
	print('Pojo awakes')
	
client.run('NDE5NzYzMjY1NjMyMDc1Nzc3.DX02ww.vj2GObEpqMeZEYswpbNzhwW7Zkw')
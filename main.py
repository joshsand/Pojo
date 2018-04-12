import discord
import os
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

if 'BOT_TOKEN' in os.environ:
	client.run(os.environ['BOT_TOKEN'])
else:
	print("ERROR: Client did not start. 'BOT_TOKEN' not found in environment variables.")
	client.close()

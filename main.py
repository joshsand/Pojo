import discord
import os
from app.handlers.messagehandler import MessageHandler

class MyClient(discord.Client):
	async def on_ready(self):
		print('Pojo awakes')

	async def on_message(self, message):
		# If testing, ignore DMs and anything not from Testing Grounds server
		if os.environ['ENVIRONMENT'] == 'testing' and (message.guild is None or message.guild.id != 413758117264883722):
			return

		# Ignore messages from self
		if message.author == client.user:
			return

		# Ignore messages from testing and prod Pojos
		if message.author.id in (419763265632075777, 1132189951941955604):
			return

		await handler.parse(message)

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
handler = MessageHandler(client)

if 'BOT_TOKEN' in os.environ:
	client.run(os.environ['BOT_TOKEN'])
else:
	print("ERROR: Client did not start. 'BOT_TOKEN' not found in environment variables.")
	client.close()
import threading, random, asyncio
from os import environ
from flask import Flask
import discord
	
'''
POJO THREAD (Discord.py server)
'''

client = discord.Client()
loop = asyncio.new_event_loop()

def run_pojo(loop):
	asyncio.set_event_loop(loop)
	
	@client.event
	async def on_ready():
		print(' * Pojo awakes')
	
	@client.event
	async def on_message(message):
		# Ignore messages from self
		if message.author == client.user:
			return
		
		await someoneSayPojo(message)
	
	client.run('NDE5NzYzMjY1NjMyMDc1Nzc3.DX02ww.vj2GObEpqMeZEYswpbNzhwW7Zkw')
	
async def someoneSayPojo(message):
	# Let's see Jerran get around this one
	pojos = ["pojo", "p_o_j_o", "p o j o", "p-o-j-o", "plain old java object"]

	# Lowercase
	msg = message.content.lower()

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

'''
SERVER THREAD (Flask server)
'''
	
app = Flask(__name__)
	
def run_server():
	app.run(environ.get('PORT'))
	
@app.route('/')
def index():
	return "Pojo"
	
'''
MAIN
'''
	
if __name__=='__main__':
	server_thread = threading.Thread(target=run_server)
	pojo_thread = threading.Thread(target=run_pojo, args=(loop,))
	server_thread.start()
	pojo_thread.start()
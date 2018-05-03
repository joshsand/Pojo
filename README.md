# Pojo

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Discord bot written using [discord.py](https://github.com/Rapptz/discord.py).

Includes single-response commands (like `!8ball` and `!help 8ball`) and general filters (like responding to the word "Pojo").

![An exchange with the Pojo bot](img/exchange.png)

The functions so far have included standard chatbot functions (Magic 8-Ball responses, calculating die rolls), divination simulators (tarot, I Ching), and random in-jokes from the server it was made for. I intend this source code to be useful for anyone curious about setting up their own Python Discord bot and how to organize and structure their project.

## Project structure

  * **main.py**
  
    The entry point. Starts the client, listens for message events, and sends every message to the MessageHandler for a response.
  
  * **MessageHandler**
  
    Parses every message to respond if it matches a general filter (like if it has the word "Pojo" in it) or call a command. This class uses custom decorators `@command` and `@general_filter` to mark these. By doing so, the `__init__()` function is able to dynamically build a list of all accepted commands and their names and descriptions using `__name__` and `__doc__` values. Other decorators include `@secret`, to hide a command from the `!help` list, and `@rename(new_name)`, to give a command a different name than its Python function name.
  
    Example of these in action:
  
    ```Python
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
    ```

    Because of this structure, to add a new command or general filter, one only needs to add a function (that takes in `self` and `message`) to the MessageHandler class and give it the relevant decorators for the bot to be able to recognize the command, call it, and dynamically build the `!help` info. `help()`, `__init__()`, and `parse()` do not have to be modified.
  
  * **app/handlers/services/**
  
    While some commands are short enough to define in MessageHandler (like `!secret`, shown above), others (like `!dice` and `!tarot`) are big enough to merit separation. Commands like these are given services with one entry point that returns the content to be sent to the client.
  
    I don't have a tight design to these besides decoupling their input and output from discord.py classes. DiceService, for example, has an entry point `process()` that takes and returns a string, and doesn't have to know about the message or client objects.
  
    All the services are imported into MessageHandler with `from app.handlers.services import *`. For this to work, the filenames to import must be added to __init__.py in the services package.
  
  * **app/handlers/services/data/**
  
    A data folder for any images, JSON data, or any other resources needed by the service classes.

## Deployment

**Local**

To run the bot locally, run main.py with an environment variable for `BOT_TOKEN`. Example: `BOT_TOKEN=yourtokenhere python main.py`. The bot will run and listen to messages from all servers it is a member of until the process is quit.

**Heroku**

Use the [Git and the Heroku CLI](https://devcenter.heroku.com/articles/git) to deploy the bot. The presence of Procfile and requirements.txt will let Heroku detect you are running a Python app and download all necessary dependencies and start the bot.

To add `BOT_TOKEN` to Heroku, go to your app's page, Settings, and click on "Reveal Config Vars". Here you can add `BOT_TOKEN` as the key and your token (from [Discord](http://discordapp.com/developers/applications/me)) as the value.

## Requirements

  * Python 3.5+
  * `Pillow` package
  * `discord` package
  
Heroku will download these requirements automatically. For local deployment, they can be downloaded using `pip install`.

## License

Pojo is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) for details.
from os import environ
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	return "Pojo"

if __name__ == "__main__":
	app.run(environ.get('PORT'))
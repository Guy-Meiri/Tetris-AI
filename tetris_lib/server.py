import tetris_lib.agent_runner
from tetris_lib.game_param_extractor import GameParameterExtractor
import os
import flask

from flask import Flask, jsonify

app = Flask(__name__)
root_dir = os.path.abspath(os.path.dirname(__file__))

def shutdown_server():
	func = flask.request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()

@app.route("/ai", methods= ['POST'])
def getData():
	game = GameParameterExtractor.getInstance()
	game.fromJson(flask.request.get_json())
	actions = [tetris_lib.agent_runner.onStateUpdate(game)]
	return jsonify({"keys": actions})

@app.route("/config", methods=["POST", "GET"])
def config():
	print(f"received request: {flask.request.get_json()}")
	return flask.send_from_directory(root_dir, "config.json")

def start_server(port=8080, debug=True):
	import logging
	logger = logging.getLogger("werkzeug")
	logger.setLevel(logging.ERROR)
	#disabled reloader because it creates 2 processes and fucks up the emulator run
	app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

if __name__ == '__main__':
	start_server()

import sys
from os.path import dirname
sys.path.append(r'C:\Users\Guy\Desktop\CS\AI-workshop\tetris-java')
from datetime import datetime

import time
from tetris_lib.agent import Agent
import tetris_lib.server
import tetris_lib.emulator_manager
import json
import __main__
import os
import sqlite3
from tetris_lib.DB import DB

agent = None
record_session = True
record_frame_cap = 50000
next_buffer_index = 0
sessions_buffer = []
is_run_once = False
start_time = 0
java_process = None

def get_agent_dir():
	if not hasattr(__main__, "__file__"):
		return "."
	return os.path.dirname(os.path.abspath(__main__.__file__))

record_path = get_agent_dir()

def run_forever(*args, **kwargs):
	global is_run_once
	is_run_once = False
	__run_agent(*args, **kwargs)

def __run_agent(agent_impl,
		emulator_path=tetris_lib.emulator_manager.EMULATOR_PATH,
		tetris_path=tetris_lib.emulator_manager.TETRIS_PATH):
	global agent, java_process, start_time
	if not isinstance(agent_impl, Agent):
		raise Exception("received agent is not instance of tetris_lib.Agent")
	agent = agent_impl
	java_process = None
	start_time = time.time()
	try:
		java_process = tetris_lib.emulator_manager.start_emulator(emulator_path, tetris_path)
		tetris_lib.server.start_server()

	except KeyboardInterrupt:
		pass
	except Exception as e:
		raise e
	finally:
		__save_recording()
		if java_process != None:
			java_process.terminate()
			java_process = None

def run_once(*args, **kwargs):
	global is_run_once
	is_run_once = True
	__run_agent(*args, **kwargs)

def set_record_path(path):
	global record_path
	record_path = path

def __save_recording():
	if len(sessions_buffer) == 0:
		return
	with open(f"{record_path}\\{str(agent)}.rec", "w") as f:
		json.dump(sessions_buffer, f)

def set_record_session(bool):
	global record_session
	record_session = bool

def set_record_cap(frames):
	global record_frame_cap
	record_frame_cap = frames
	sessions_buffer.clear()

def __record_gamestate(gamestate):
	#cyclic buffer for gamestates
	global next_buffer_index
	global sessions_buffer
	if len(sessions_buffer) < record_frame_cap:
		sessions_buffer.append(None)
	sessions_buffer[next_buffer_index] = gamestate.intoJson()
	next_buffer_index = (next_buffer_index + 1) % record_frame_cap

def parse_action(action):
	if isinstance(action, int):
		action = tetris_lib.transition_model.ActionsEnum.into_str(action)
	if isinstance(action, str):
		return action.lower()
	if action == None:
		return tetris_lib.transition_model.ActionsEnum.NONE
	raise Exception(f"invalid action type {action} received")

def onStateUpdate(game_param_extractor):
	if record_session:
		__record_gamestate(game_param_extractor.gamestate)
	try:
		result = parse_action(agent.onStateUpdate(game_param_extractor))
	except Exception as e:
		print(f"exception occured: {e}")
		java_process.terminate()
		tetris_lib.server.shutdown_server()
		return parse_action(tetris_lib.transition_model.ActionsEnum.NONE)
	if game_param_extractor.gamestate.has_game_ended: #TODO: ask amit how to update this at the end of the game
		print("Game ended")
		db = DB.get_instance()
		gamestate = game_param_extractor.gamestate
		#db = DB(r"C:\Users\Guy\Desktop\CS\AI-workshop\tetris-java\agentResults.db")
		db.saveGameToDataBase(str(agent), gamestate.score, int(time.time() - start_time), gamestate.level, datetime.now())
		agent.onEpisodeEnded()

		if is_run_once:
			java_process.terminate()
			tetris_lib.server.shutdown_server()
	#return tetris_lib.transition_model.ActionsEnum.NONE
	return result


if __name__ == "__main__":
	pass



import tetris_lib.agent_runner
from tetris_lib.game_param_extractor import GameParameterExtractor
from tetris_lib.path_finder import get_required_actions
from tetris_lib.transition_model import ActionsEnum
from tetris_lib.agent import Agent
from copy import deepcopy
import operator

def lock_height(game_param_extractor, lock_location):
	# how far from the "ground" the current piece was locked
	#(tid, (row, col))
	return 19 - lock_location[1][0]

def well_cells(game_param_extractor, lock_location):
	# how many well cells are in the board (well x its size)
	return sum(game_param_extractor.calcWells().values())

def holes(game_param_extractor, lock_location):
	return game_param_extractor.calcNumberOfHoles()

def column_trainsitions(game_param_extractor, lock_location):
	#the number of transitions between empty and solid cell
	transitions = 0
	for column in zip(*list(game_param_extractor.gamestate.board.into_row_iter())):
		last_cell = column[0]
		for cell in column[1:]:
			if cell != last_cell:
				transitions +=1
			last_cell = cell
	return transitions

def row_transitions(game_param_extractor, lock_location):
	#same as the above - for rows
	transitions = 0
	for row in game_param_extractor.gamestate.board.into_row_iter():
		last_cell = row[0]
		for cell in row[1:]:
			if cell != last_cell:
				transitions +=1
			last_cell = cell
	return transitions

def evaluate(game_param_extractor, lock_location):
	functions = [lock_height, well_cells, holes, column_trainsitions, row_transitions]
	weights = [12.885008263218383,
		15.842707182438396,
		26.894496507795950,
		27.616914062397015,
		30.185110719279040]
	sum = 0
	tid, (y, x) = lock_location
	for func, weight in zip(functions, weights):
		transition_model = game_param_extractor.getTransitionModel()
		new_transition_model = transition_model.create_gamestate_from_location_lock(tid, y, x)
		new_manager = GameParameterExtractor()
		new_manager.gamestate = new_transition_model.gamestate
		sum += func(new_manager, lock_location) * weight
	return sum



class TestAgent(Agent):
	def __init__(self):
		self.actions = []
		self.actions_since_new_piece = 0
	def get_next_action(self, game_param_extractor):
		gamestate = game_param_extractor.gamestate 
		x, y = gamestate.tetrimino_x, gamestate.tetrimino_y
		if len(self.actions) == 0:
			return ActionsEnum.NONE
		next_action, x, y = self.actions[0]
		if gamestate.tetrimino_x == x and gamestate.tetrimino_y == y:
			print(f"at {gamestate.tetrimino_x}, {gamestate.tetrimino_y} taking action {ActionsEnum.into_str(next_action)}")
			self.actions.pop(0)
			return next_action
		else:
			print(f"current location (col, row): {gamestate.tetrimino_x}, {gamestate.tetrimino_y}")
			print(f"waiting for location: {x},{y}")
			return ActionsEnum.NONE
	def onStateUpdate(self, game_param_extractor):
		gamestate = game_param_extractor.gamestate 
		x, y = gamestate.tetrimino_x, gamestate.tetrimino_y
		if (x, y) != (5, 0) or self.actions_since_new_piece != 0:
			self.actions_since_new_piece = 0
			return self.get_next_action(game_param_extractor)
		self.actions_since_new_piece += 1
		print("new piece detected, computing optimal path")
		return self.propagate_actions_list(game_param_extractor)
		
	def propagate_actions_list(self, game_param_extractor):
		transition_model = game_param_extractor.getTransitionModel()
		locks = []
		for lock_location in transition_model.get_all_possible_lock_locations():
			score = evaluate(game_param_extractor, lock_location)
			locks.append((score, lock_location))
		locks.sort(key=operator.itemgetter(0))

		# #DEBUG
		# for score, lock_location in locks[:6]:
		#     tid, (y, x) = lock_location
		#     desired_state = transition_model.create_gamestate_from_location_lock(tid, y, x)
		#     print(f"board with score {score}:")
		#     print(desired_state)
		# #END OF DEBUG

		for _, lock_location in locks:
			tid, (y, x) = lock_location
			desired_state = transition_model.create_gamestate_from_location_lock(tid, y, x)
			print("going for desired state:")
			print(desired_state)
			actions = list(get_required_actions(transition_model, lock_location))
			if len(actions) == 0:
				print(f"couldnt find a path to desired location, skipping..")
				continue
			#filtering None actions
			current_action,x,y = actions[0]
			self.actions = list(filter(lambda x: x[0] != ActionsEnum.NONE, actions[1:]))
			print(f"sending action {ActionsEnum.into_str(current_action)}")
			return current_action
	def onEpisodeEnded(self):
		pass
	def __repr__(self):
		return "TestAgent"


agent = TestAgent()
tetris_lib.agent_runner.set_record_cap(200_000)
tetris_lib.agent_runner.run_once(agent)
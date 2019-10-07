from tetris_lib.gamestate import GameState
from tetris_lib.tetris_board import TeterisBoard
from tetris_lib.tetrimino import Tetrimino
from tetris_lib.game_param_extractor import GameParameterExtractor
from copy import deepcopy
import random

class ActionsEnum():
	LEFT = 0
	RIGHT = 1
	A = 2
	B = 3
	NONE = 4
	@staticmethod
	def into_str(action):
		return ["LEFT", "RIGHT", "A", "B", "NONE"][action]
	@staticmethod
	def into_iter():
		return range(5)

class TetrisTransitionModel():
	ACTIONS_TILL_DROP = 1 #every action there is a drop
	def __init__(self, gamestate=None, actions_count=0):
		self.actions_count = actions_count
		self.total_rows_cleared = 0
		self.has_game_ended = False
		self.last_generated_tid = 0
		self.last_rows_cleared = 0
		if gamestate:
			self.gamestate = gamestate
		else:
			self.gamestate = GameState()
			self.gamestate.tetrimino_y = 0
			self.gamestate.tetrimino_x = 5
			self.gamestate.tetrimino = self.__generate_tid()
			self.gamestate.next_tetrimino = self.__generate_tid()

	@staticmethod
	def fromJsonFile(filepath):
		return TetrisTransitionModel(GameState.fromJsonFile(filepath))
	
	def __hash__(self):
		return hash((self.gamestate, self.actions_count))
	def __eq__(self, other):
		return self.gamestate == other.gamestate and self.actions_count == other.actions_count
	def lock_tetrimino(self):
		tet_x, tet_y = self.gamestate.tetrimino_x, self.gamestate.tetrimino_y
		for x, y in self.gamestate.tetrimino.get_abs_pattern(tet_x, tet_y):
			self.gamestate.board.set_cell(x, y, 1)

	def get_level(self):
		return self.total_rows_cleared // 10

	def has_ended(self):
		return self.has_game_ended

	def make_drop_if_necesary(self):
		if self.is_drop():
			self.gamestate.tetrimino_y += 1

	def is_next_state_drop(self):
		new_action_count = (self.actions_count + 1) % self.ACTIONS_TILL_DROP
		return new_action_count == self.ACTIONS_TILL_DROP - 1

	def is_drop(self):
		return self.actions_count == self.ACTIONS_TILL_DROP - 1

	def generate_new_state(self, action):
		if self.has_game_ended:
			raise Exception("Game ended!")

		trans_model = deepcopy(self)
		trans_model.actions_count = (trans_model.actions_count + 1) % self.ACTIONS_TILL_DROP
		
		if not self.is_tetrimino_locked():
			if not self.__validate_tid_location(action):
				trans_model.make_drop_if_necesary()
				return trans_model
			trans_model.apply_non_score_action(action)
		else:
			trans_model.lock_tetrimino()
			rows_cleared = trans_model.__clear_rows()
			level = self.get_level()
			trans_model.gamestate.score += self.__get_added_score(rows_cleared, level)
			trans_model.last_rows_cleared = rows_cleared
			trans_model.total_rows_cleared += rows_cleared # to advance the level
			trans_model.gamestate.tetrimino = trans_model.gamestate.next_tetrimino
			trans_model.gamestate.next_tetrimino = self.__generate_tid()
			trans_model.gamestate.tetrimino_x = 5
			trans_model.gamestate.tetrimino_y = 0
			trans_model.has_game_ended = not trans_model.__validate_tid_location(None)
		return trans_model

	def is_tetrimino_locked(self):
		"""
			meaning if the next time drop will be invalid
		"""
		pattern = self.gamestate.tetrimino.get_pattern()
		#check if next action, drop will be invalid
		result = not self.__validate_pattern(pattern, self.is_next_state_drop())
		#print(f"tetrimino {'is' if result else 'isnt'} locked")
		return result

	def apply_non_score_action(self, action):
		
		self.gamestate.tetrimino = self.__rotate_if_needed(action)
		self.make_drop_if_necesary()
		self.gamestate.tetrimino_x += self.__action_to_newx(action)

	def __generate_tid(self):
		#				T    J 	  Z    O  S   L   I
		tetriminos = [0x2 , 0x7, 0x8, 0xa, 0xb, 0xe, 0x12]
		#return Tetrimino(0x12)
		index = random.randint(0,7)
		if index != 7:
			if self.last_generated_tid != tetriminos[index]:
				self.last_generated_tid = tetriminos[index]
				return Tetrimino(tetriminos[index])
		new_index = random.randint(0, 7)
		new_index += index
		self.last_generated_tid = tetriminos[new_index % 7]
		return Tetrimino(self.last_generated_tid)
	
	def get_valid_actions(self, is_shuffle=False):
		valid_actions = [ActionsEnum.NONE]
		for action in ActionsEnum.into_iter():
			if action == ActionsEnum.NONE:
				continue
			if not self.__validate_tid_location(action):
				continue
			valid_actions.append(action)
		if is_shuffle:
			random.shuffle(valid_actions)
		return valid_actions

	@staticmethod
	def __get_added_score(rows_cleared, level):
		score = [0, 40, 100, 300, 1200]
		return (level + 1) * score[rows_cleared]

	def __clear_rows(self):
		cleaned_rows_counter = 0
		for row_index, row in enumerate(self.gamestate.board.into_row_iter()):
			if row.count(TeterisBoard.EMPTY_CELL) != 0:
				continue
			self.gamestate.board.remove_row(row_index)
			cleaned_rows_counter += 1
		
		return cleaned_rows_counter

	def __validate_pattern(self, pattern, is_drop, action = None):
		x, y = self.gamestate.tetrimino_x, self.gamestate.tetrimino_y
		return self.__validate_pattern_by_location(x, y, pattern, is_drop, action=action)
	
	def __validate_pattern_by_location(self, x, y, pattern, is_drop, action = None):
		for relative_x, relative_y in pattern:
			abs_x = x + relative_x + self.__action_to_newx(action)
			abs_y = y + relative_y + is_drop
			if not self.gamestate.board.validate_empty_cell(abs_x, abs_y):
				return False
		return True

	def __rotate_if_needed(self, action):
		if action == ActionsEnum.A:
			return self.gamestate.tetrimino.rotate_clockwise()
		elif action == ActionsEnum.B:
			return self.gamestate.tetrimino.rotate_counterclockwise()
		return self.gamestate.tetrimino
		
	def __validate_tid_location(self, action):
		pattern = self.__rotate_if_needed(action).get_pattern()
		return self.__validate_pattern(pattern, self.is_next_state_drop(), action=action)

	@staticmethod
	def __action_to_newx(action):
		if action == ActionsEnum.LEFT:
			return -1
		elif action == ActionsEnum.RIGHT:
			return +1
		return 0
	
	def get_all_possible_lock_locations(self):
		''' 
		returns a list of tuples, each tuple is in the form (tid, x_coordinate, y_coordinate) where:
		-tid is the id of the locked tetrimino piece
		-x_coordinate and y_coordinate are the the coordinates of the relative (0,0) of the tetrimino can be locked 
		'''
		lock_coords = []
		for rotation in self.gamestate.tetrimino.get_possible_rotations_outcomes():
			for _, x , y in self.gamestate.board:
				pattern = rotation.get_pattern()
				#make sure the location is valid (without considering drop)
				if not self.__validate_pattern_by_location(x, y, pattern, False):
					continue
				#make sure we cant drop anymore from that location
				if self.__validate_pattern_by_location(x, y, pattern, True):
					continue
				lock_coords.append((rotation, (y, x)))
		
		return lock_coords
	
	def create_gamestate_from_location_lock(self, tid, y, x):
		new_transition_model_state = deepcopy(self)
		new_transition_model_state.gamestate.tetrimino = tid
		new_transition_model_state.gamestate.tetrimino_x = x
		new_transition_model_state.gamestate.tetrimino_y = y
		return new_transition_model_state.generate_new_state(ActionsEnum.NONE)
	
	def __lt__(self, other):
		return False
	
	def __repr__(self):
		x,y = self.gamestate.tetrimino_x, self.gamestate.tetrimino_y
		output = self.gamestate.board.to_string_with_tid(self.gamestate.tetrimino, x, y) + "\n"
		output += "  " + "".join(map(lambda x: f" {x} ", range(TeterisBoard.COLUMNS))) + "\n"
		output += f"Score: {self.gamestate.score}\n"
		output += f"Tetrimino location: ({self.gamestate.tetrimino_x}, {self.gamestate.tetrimino_y})\n"
		output += f"Tetrimino id: {self.gamestate.tetrimino.get_id()}"
		return output
	
	def getgame_param_extractor(self):
		return GameParameterExtractor(self.gamestate)
		

def main():
	# a little hack to add the tetris_lib package to the PATH env variable
	import sys
	import os
	full_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	print(full_path)
	sys.path.insert(0, full_path)
	#END OF TRICK xP

	transition = TetrisTransitionModel()

	action = ActionsEnum.NONE
	try:
		while action != 5:
			print("---------")
			lock_locations = transition.get_all_possible_lock_locations()
			for lock in lock_locations:
				print(transition.create_gamestate_from_location_lock(lock[0], *lock[1]))
			
			print(lock_locations)
			print("--------------")
			print("Current state:")
			print(transition)
			print("please choose an action:")
			print("1) Left")
			print("2) Right")
			print("3) A")
			print("4) B")
			print("5) None")
			print("6) Exit")
			#print(f"num of available actions: {len(transition.get_valid_actions())}")
			inp = input()
			if inp == "":
				action = ActionsEnum.NONE
			else:
				action = int(inp)-1
			transition = transition.generate_new_state(action)
	except KeyboardInterrupt as e:
		pass

if __name__ == '__main__':
	main()
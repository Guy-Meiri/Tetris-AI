import random
import json
from tetris_lib.tetris_board import TeterisBoard
from tetris_lib.tetrimino import Tetrimino
from datetime import datetime

class GameState(object):
	def __init__(self):
		self.board = TeterisBoard() 
		# place random pieces on the board for DEBUG perposess. 
		# self.board = [[random.randint(GameState.EMPTY_CELL,GameState.EMPTY_CELL+1) for i in range(GameState.COLUMNS )] for j in range(GameState.ROWS)]
		self.score = 0
		self.next_tetrimino = Tetrimino(0)
		self.tetrimino = Tetrimino(0)
		self.has_game_ended = False
		self.tetrimino_x = -1
		self.tetrimino_y = -1

	@staticmethod
	def fromJsonFile(file_path):
		import sys
		print(sys.path)
		with open(file_path, "r") as f:
			data = json.load(f)
			return GameState.fromJson(data)

	@staticmethod
	def fromJson(data):
		state = GameState()
		state.board = TeterisBoard.fromJson(data['board'])
		state.score = data['score']
		state.next_tetrimino = Tetrimino(data['next_tetrimino_id'])
		state.tetrimino = Tetrimino(data['tetrimino_id'])
		state.has_game_ended = data['has_game_ended']
		state.tetrimino_x = data['tetrimino_x']
		state.tetrimino_y = data['tetrimino_y']
		state.level = data.get("level", "0")
		return state

	def intoJson(self):
		return {
			"board" : self.board.intoJson(),
			"score" : self.score,
			"next_tetrimino_id" : self.next_tetrimino.get_id(),
			"tetrimino_id" : self.tetrimino.get_id(),
			"has_game_ended" : self.has_game_ended,
			"tetrimino_x" : self.tetrimino_x,
			"tetrimino_y" : self.tetrimino_y,
			"level" : self.level
		}
	def __hash__(self):
		data = ((tuple(tuple(row) for row in self.board.into_row_iter()),
		self.score,
		self.tetrimino_x,
		self.tetrimino_y,
		self.tetrimino.get_id()))
		return hash(data)

	def __eq__(self, other):
		my_board = (tuple(tuple(row) for row in self.board.into_row_iter()))
		other_board = (tuple(tuple(row) for row in other.board.into_row_iter()))
		return self.score == other.score \
			and self.tetrimino_x == other.tetrimino_x \
			and self.tetrimino_y == other.tetrimino_y \
			and self.tetrimino == other.tetrimino \
			and my_board == other_board
		
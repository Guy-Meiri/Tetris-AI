# from tetris_lib.gamestate import GameState
# from tetris_lib.gamemanager import ActionsEnum
# from tetris_lib.transition_model import TetrisTransitionModel


# class MoveFinder():

#     m_possible_moves = []

#     def __init__(self, gamestate=None, actions_count=0):
#         if gamestate:
#     	    self.gamestate = gamestate
# 	    else:
# 			self.gamestate = GameState()
# 			self.gamestate.tetrimino_y = 0
# 			self.gamestate.tetrimino_x = 5
#             self.gamestate.tetrimino_id = self.__generate_tid()
# 			self.gamestate.next_tetrimino_id = self.__generate_tid()
    
#     def get_possible_moves(self):
#         pass
# from pprint import pprint
ROWS= 10
COLUMNS = 20
board = [[0]*10 for i in range(20)]
EMPTY_CELL = 0

board[1][2] = 1



def _is_empty_cell( x, y):
	if x < 0 or x >= ROWS:
		return False
	elif y >= COLUMNS:
		return False
	elif board[x][y] != EMPTY_CELL:
		return False

	return True

print(_is_empty_cell(1,4))
print(_is_empty_cell(1,2))
# for i, row in enumerate(board):
#     for j, col in enumerate(row):
#         board[i][j] = i*10+ j

# pprint(board)
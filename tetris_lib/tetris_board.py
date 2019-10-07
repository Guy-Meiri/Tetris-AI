
class TeterisBoard():
	ROWS = 20
	COLUMNS = 10
	EMPTY_CELL = 239
	def __init__(self, board=None):
		if board == None:
			self.board = [[TeterisBoard.EMPTY_CELL]*TeterisBoard.COLUMNS for i in range(TeterisBoard.ROWS)] 
		else:
			self.board = board
	
	@staticmethod
	def fromJson(board):
		return TeterisBoard(board=board)
	def intoJson(self):
		return self.board
	def validate_empty_cell(self, x, y):
		if not self.is_valid_location(x, y):
			return False
		if self.get_cell(x, y) != TeterisBoard.EMPTY_CELL:
			return False
		return True
	def is_valid_location(self, x, y):
		if x >= TeterisBoard.COLUMNS or x < 0:
			return False
		elif y >= TeterisBoard.ROWS or y < -2:
			return False
		return True
	def get_cell(self, x, y):
		if self.is_valid_location(x, y):
			return self.board[y][x]
		return None
	def set_cell(self, x, y, value):
		if not self.is_valid_location(x, y):
			return
		self.board[y][x] = value
	def __iter__(self):
		return TeterisBoardIterator(self)
	def into_row_iter(self):
		return TeterisBoardRowIterator(self)
	def remove_row(self, index):
		self.board.pop(index)
		self.board = [([TeterisBoard.EMPTY_CELL] * TeterisBoard.COLUMNS)] + self.board
	
	def __eq__(self, other):
		for _, col, row in self:
			if self.board[row][col] != other.board[row][col]:
				return False
		return True
	def __repr__(self):
		return self.to_string_with_tid(None, 0, 0)
	
	def to_string_with_tid(self, tetrimino, x, y):
		output = []
		abs_pattern = []
		if tetrimino != None:
			abs_pattern = tetrimino.get_abs_pattern(x, y)
		for rowIndex, row in enumerate(self.board):
			for columnIndex, cell in enumerate(row):
				if (columnIndex, rowIndex) in abs_pattern:
					output.append(" + ")
				elif cell == TeterisBoard.EMPTY_CELL:
					output.append(" _ ")  # represents an empty cell
				else:
					output.append(" x ")  # represents an occupied cell
			output.append(f" Row: {rowIndex}")
			output.append(" \n")
		return "".join(output)

class TeterisBoardRowIterator():
	def __init__(self, tetris_board):
		self.current_row_index = 0
		self.board = tetris_board
	def __iter__(self):
		return self
	def __next__(self):
		current_row = self.current_row_index
		self.current_row_index += 1
		if not self.board.is_valid_location(0, current_row):
			raise StopIteration()
		return self.board.board[current_row]

class TeterisBoardIterator():
	def __init__(self, tetris_board):
		self.current_cell_index = 0
		self.board = tetris_board
	def __into_2d_index(self):
		return (self.current_cell_index % TeterisBoard.COLUMNS, self.current_cell_index // TeterisBoard.COLUMNS)
	def __next__(self):
		x, y = self.__into_2d_index()
		if not self.board.is_valid_location(x, y):
			raise StopIteration()
		self.current_cell_index += 1
		return self.board.get_cell(x, y), x, y

if __name__ == "__main__":
	pass
from tetris_lib.tetris_board import TeterisBoard
from tetris_lib.gamestate import GameState
import pygame

class StateDisplay(object):
	WHITE = (255, 255, 255)
	BLACK = (0,0,0)
	RED = (255, 0, 0)
	BLUE = (0, 0, 255)
	GREEN = (0, 255, 0)
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((400, 500))
		self.font = pygame.font.SysFont('segoeuiemoji', 30)
		self.screen.fill(StateDisplay.WHITE)
		self.last_score = -1
		self.last_render = None
		self.last_pattern = None

	def displayTextAt(self, text, location):
		render = self.font.render(text, True, StateDisplay.BLACK)
		self.screen.blit(render, location)

	def displayScore(self, score):
		self.displayTextAt(f"Score: {score}", (100, 460))

	def displayNextTid(self, next_tid):
		self.displayTextAt("Next tid", (265, 60))
		border = 5
		rect_size = (20*5 + border*2, 20*5 + border*2)
		rect_location = (270 - border, 100 - border)
		self.drawRect(rect_location, rect_size)
		tetrimino_id_y = rect_location[0] + border
		tetrimino_id_x = rect_location[1] + border
		current_pattern = next_tid.get_pattern()
		for row_id in range(5):
			for column_id in range(5):
				color = StateDisplay.WHITE
				if [column_id - 2, row_id - 2] in current_pattern:
					color = StateDisplay.GREEN
				rect = pygame.Rect(tetrimino_id_y + column_id*20, tetrimino_id_x+ row_id*20, 16, 16, width=4)
				pygame.draw.rect(self.screen, color, rect)

	def drawRect(self, location, size):
		pygame.draw.rect(self.screen, StateDisplay.BLACK, (*location, *size), 2)

	def displayBoard(self, state):
		OFFSET = 50
		self.drawRect((45, 45), (200 + 5, 400 + 5))
		current_pattern = state.tetrimino.get_pattern()
		if current_pattern == None:
			current_pattern = self.last_pattern
		self.last_pattern = current_pattern
		x, y = state.tetrimino_x, state.tetrimino_y
		current_pattern = list(map(lambda tup: [tup[0]+x, tup[1]+y], current_pattern))
		for cell, x_cord, y_cord in state.board:
				color = StateDisplay.RED if cell != TeterisBoard.EMPTY_CELL else StateDisplay.BLACK
				if [x_cord, y_cord] in current_pattern: #if the current cell is the falling tetrimino
						color = StateDisplay.BLUE
				pygame.draw.rect(self.screen,color,pygame.Rect(OFFSET + x_cord*20, OFFSET+ y_cord*20, 16, 16, width=4))

	def displayState(self, gamestate):
		self.screen.fill(StateDisplay.WHITE)
		self.displayScore(gamestate.score)
		self.displayBoard(gamestate)
		self.displayNextTid(gamestate.next_tetrimino)
		pygame.display.flip()
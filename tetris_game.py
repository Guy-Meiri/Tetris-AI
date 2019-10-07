import pygame
from tetris_lib.transition_model import TetrisTransitionModel, ActionsEnum
from tetris_lib.gamestate import GameState
from tetris_lib.state_display import StateDisplay

clock = pygame.time.Clock()

KEY_TO_ACTION = {
	pygame.K_LEFT : ActionsEnum.LEFT,
	pygame.K_RIGHT : ActionsEnum.RIGHT,
	pygame.K_x : ActionsEnum.A,
	pygame.K_z : ActionsEnum.B
}

def main():
	state = TetrisTransitionModel()
	states = [(state,ActionsEnum.NONE)]
	FPS = 15
	done = False
	display = StateDisplay()
	while not done:
		current_action = ActionsEnum.NONE
		keydown = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				keydown = True

		pressed = pygame.key.get_pressed()
		try:
			pressed = list(pressed).index(1)
		except ValueError as e:
			pressed = ActionsEnum.NONE

		current_action = KEY_TO_ACTION.get(pressed, ActionsEnum.NONE)
		if not keydown:
			current_action = ActionsEnum.NONE	
		state = state.generate_new_state(current_action)
		if state.has_ended():
			return
		states.append((state, current_action))
		display.displayState(state.gamestate)
		clock.tick(FPS)

if __name__ == '__main__':
	main()
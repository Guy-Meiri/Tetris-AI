from tetris_lib.state_display import StateDisplay
from tetris_lib.gamestate import GameState
import pygame
import json
import sys

def main(filePath):
	clock = pygame.time.Clock()
	FPS = 15
	with open(filePath, "r") as f:
		result = json.load(f)
	print("recording loaded!")

	display = StateDisplay()
	for state in result:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit(0)
		display.displayState(GameState.fromJson(state))
		clock.tick(FPS)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: simulator.py [recording file]")
		exit(-1)
	main(sys.argv[1])
	
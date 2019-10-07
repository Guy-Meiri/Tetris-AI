import sys
sys.path.insert(0, r"c:\Users\Guy\Desktop\CS\AI-workshop\tetris-java")
sys.path.insert(0, r"c:\Users\Guy\Desktop\CS\AI-workshop\tetris-java\tetris_lib")
import random
import tetris_lib.agent
import tetris_lib.agent_runner
import tetris_lib.game_param_extractor

IS_DUMB = False
class RandomAgent(tetris_lib.agent.Agent):
	def __init__(self):
		pass
	def onStateUpdate(self, gamemanager):
		actions = list(tetris_lib.gamemanager.ActionsEnum.into_iter())
		if IS_DUMB:
			return tetris_lib.game_param_extractor.ActionsEnum.NONE
		return random.choice(actions)
	def onEpisodeEnded(self):
		print("Episode Ended")
	def __repr__(self):
		return "RandomAgent"
		
agent = RandomAgent()
tetris_lib.agent_runner.run_forever(agent)
print("ended!!")

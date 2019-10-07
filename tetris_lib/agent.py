from abc import ABC, abstractmethod


class Agent(ABC):
	def __init__(self):
		pass
	@abstractmethod
	def onStateUpdate(self, game_param_extractor):
		"""
			receives a game_param_extractor Obj, and returns one of game_param_extractor.ACTIONS 
		"""
		raise Exception("Non implemented method onStateUpdate(self, game_param_extractor)")
	@abstractmethod
	def onEpisodeEnded(self):
		"""
			called when the current episode has ended
		"""
		raise Exception("Non implemented method onEpisodeEnded(self)")
	@abstractmethod
	def __repr__(self):
		raise Exception("Non implemented method __repr__")
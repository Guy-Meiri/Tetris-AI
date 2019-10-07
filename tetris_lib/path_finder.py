import random
import heapq
import time
import sys

import os
parentDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
os.chdir(parentDir)

#
from collections import namedtuple
from tetris_lib.transition_model import TetrisTransitionModel, ActionsEnum
from tetris_lib.tetrimino import Tetrimino
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
#from tetrimino import Tetrimino

Node = namedtuple("Node", ["transition_model_state", "actions"])
DEBUG = False

def manhatten_distance(point1, point2):
	y1, x1 = point1
	y2, x2 = point2
	return abs(y1 - y2) + abs(x1 - x2)

def rotation_distance(tid1, tid2):
	max_distance = len(tid1.get_possible_rotations_outcomes())
	tid1 = tid1.get_id() % max_distance
	tid2 = tid2.get_id() % max_distance
	first_distance = abs(tid1 - tid2)
	return min(first_distance, max_distance - first_distance)

def get_total_cost(node, lock_location, depth):
	tid, desired_point = lock_location
	current_tid = node.transition_model_state.gamestate.tetrimino
	current_point = node.transition_model_state.gamestate.tetrimino_y, node.transition_model_state.gamestate.tetrimino_x
	distance = manhatten_distance(desired_point, current_point)*TetrisTransitionModel.ACTIONS_TILL_DROP
	return depth + max(distance, 0) + rotation_distance(tid, current_tid)*2

##code copied from Stack overflow:
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):
	'''
	From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
	Licensed under Creative Commons Attribution-Share Alike 

	If the graph is a tree this will return the positions to plot this in a 
	hierarchical layout.

	G: the graph (must be a tree)

	root: the root node of current branch 
	- if the tree is directed and this is not given, 
	  the root will be found and used
	- if the tree is directed and this is given, then 
	  the positions will be just for the descendants of this node.
	- if the tree is undirected and not given, 
	  then a random choice will be used.

	width: horizontal space allocated for this branch - avoids overlap with other branches

	vert_gap: gap between levels of hierarchy

	vert_loc: vertical location of root

	xcenter: horizontal location of root
	'''
	if not nx.is_tree(G):
		raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

	if root is None:
		if isinstance(G, nx.DiGraph):
			root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
		else:
			root = random.choice(list(G.nodes))

	def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
		'''
		see hierarchy_pos docstring for most arguments

		pos: a dict saying where all nodes go if they have been assigned
		parent: parent of this branch. - only affects it if non-directed

		'''

		if pos is None:
			pos = {root:(xcenter,vert_loc)}
		else:
			pos[root] = (xcenter, vert_loc)
		children = list(G.neighbors(root))
		if not isinstance(G, nx.DiGraph) and parent is not None:
			children.remove(parent)  
		if len(children)!=0:
			dx = width/len(children) 
			nextx = xcenter - width/2 - dx/2
			for child in children:
				nextx += dx
				pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
									vert_loc = vert_loc-vert_gap, xcenter=nextx,
									pos=pos, parent = root)
		return pos


	return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
## end of copied code

def get_required_actions(transition_model_state, lock_location):
	searchGraph = nx.DiGraph()
	tid, (row, col) = lock_location
	desired_state = transition_model_state.create_gamestate_from_location_lock(tid, row, col)
	initial_state = Node(transition_model_state, tuple())
	searchGraph.add_node(initial_state)
	priority_queue = []
	heapq.heappush(priority_queue, (get_total_cost(initial_state, lock_location, 0), initial_state))
	if DEBUG:
		print(f"estimated cost: {get_total_cost(initial_state, lock_location, 0)}")
	closed_set = set()
	labels = {initial_state : 0}
	expanded = 0
	while len(priority_queue) != 0:
		_, current_node = heapq.heappop(priority_queue)
		current_transition_model_state = current_node.transition_model_state
		
		if current_transition_model_state in closed_set:
			continue
		
		closed_set.add(current_transition_model_state)
		board = current_node.transition_model_state.gamestate.board

		if current_transition_model_state.is_tetrimino_locked():
			board = current_transition_model_state.generate_new_state(ActionsEnum.NONE).gamestate.board
		
			if board == desired_state.gamestate.board:
				if not DEBUG:
					return current_node.actions
				
				from networkx.drawing.nx_agraph import write_dot, graphviz_layout
				print(f"expanded {expanded} nodes")
				plt.title('draw_networkx')
				pos = hierarchy_pos(searchGraph, initial_state)    
				nx.draw(searchGraph,labels=labels, pos=pos, font_size=6, node_size=10)
				print(f"method 2) total cost: {len(current_node.actions)}")
				plt.show()
				#return (*current_node.actions, ActionsEnum.NONE)
				return current_node.actions
			continue
		
		if expanded % 100 == 0 and DEBUG:
			print(f"expanded {expanded} nodes")
		
		for action in current_transition_model_state.get_valid_actions():
			gamestate = current_transition_model_state.gamestate
			x, y = gamestate.tetrimino_x, gamestate.tetrimino_y
			new_tansition_model_state = current_transition_model_state.generate_new_state(action)
			#new_actions_list = *current_node.actions, action
			new_actions_list = *current_node.actions, (action, x, y)
			new_node = Node(new_tansition_model_state, new_actions_list)
			expanded += 1
			labels[new_node] = expanded
			searchGraph.add_node(new_node)
			searchGraph.add_edge(current_node, new_node)
			cost = get_total_cost(new_node, lock_location, len(new_actions_list))
			heapq.heappush(priority_queue, (cost, new_node))
	return []

def log(data, isDebug=True):
	if isDebug:
		print(data)

def test_with_transition_model(current_state, desired_lock_location, isDebug=True):
	log("current state:", isDebug=isDebug)
	log(current_state, isDebug=isDebug)
	log("required state:", isDebug=isDebug)
	tid, (row, col) = desired_lock_location
	desired_state = current_state.create_gamestate_from_location_lock(tid, row, col)
	log(desired_state, isDebug=isDebug)
	actions = get_required_actions(current_state, desired_lock_location)
	for action, x, y in actions:
		current_x , current_y = current_state.gamestate.tetrimino_x, current_state.gamestate.tetrimino_y
		while (current_x, current_y) != (x,y): 
			current_state = current_state.generate_new_state(ActionsEnum.NONE)
			current_x , current_y = current_state.gamestate.tetrimino_x, current_state.gamestate.tetrimino_y

		log("taking action: " + ActionsEnum.into_str(action), isDebug=isDebug)
		current_state = current_state.generate_new_state(action)
		log(current_state, isDebug=isDebug)
		if isDebug:
			time.sleep(0.7)

	current_state = current_state.generate_new_state(ActionsEnum.NONE)
	log(desired_state, isDebug=isDebug)
	assert(desired_state.gamestate.board == current_state.gamestate.board)

def test1():
	#testing simple clean board path finding
	current_state = TetrisTransitionModel()
	desired_lock_location = random.choice(current_state.get_all_possible_lock_locations())
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)

def test2():
	#testing with need to move to the left and then to the right, and left again
	current_state = TetrisTransitionModel.fromJsonFile(r"tests\path_finder_tunnel1.json")
	from tetrimino import Tetrimino
	desired_lock_location = (Tetrimino(0xa), (16, 6))
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)

def test3():
	#moving into the top of the tower
	current_state = TetrisTransitionModel.fromJsonFile(r"tests\path_finder_tower1.json")
	from tetrimino import Tetrimino
	desired_lock_location = (Tetrimino(0xa), (2, 7))
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)

def test4():
	#testing with need to move to the left and then to the right, and left again
	current_state = TetrisTransitionModel.fromJsonFile(r"tests\path_finder_tunnel2.json")

	desired_lock_location = (Tetrimino(3), (16, 8))
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)

def test5():
	current_state = TetrisTransitionModel.fromJsonFile(r"tests\path_finder_failed1.json")
	desired_lock_location = (Tetrimino(2), (16, 5))
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)


def test6():
	current_state = TetrisTransitionModel.fromJsonFile(r"tests\shalom_ethan.json")
	desired_lock_location = (Tetrimino(0xa), (18, 9))
	return test_with_transition_model(current_state, desired_lock_location, isDebug=DEBUG)

if __name__ == "__main__":
	DEBUG = True
	tests = [test6, test1, test2, test3, test4, test5]
	for index, test in enumerate(tests):
		try:
			test()
			if DEBUG:
				pass
				#os.system("cls")
			print(f"test {index + 1} passed")
		except Exception as e:
			raise e
			print(f"test {index + 1} has failed: {e}")
	
		 



import pprint
import functools
import numpy as np 
from tetris_lib.gamestate import GameState
from tetris_lib.tetris_board import TeterisBoard
#import transition_model

class GameParameterExtractor(object):
	NO_WELLS = -1
	DEEP_WELL_THRESHOLD = 3

	__instance = None

	def __init__(self, gamestate=None):
		self.gamestate = GameState() if not gamestate else gamestate
		self.update_id = -1
		self.session_id = -1

	@staticmethod
	def getInstance():
		if not GameParameterExtractor.__instance:
			GameParameterExtractor.__instance = GameParameterExtractor()
		return GameParameterExtractor.__instance

	def fromJson(self, json):
		if self.session_id > json["session_id"]:
			return
		if self.session_id == json["session_id"] and self.update_id > json["update_id"]:
			return
		
		self.gamestate = GameState.fromJson(json)
		self.update_id = json["update_id"]
		self.session_id = json["session_id"]

	def __repr__(self):
		output = []
		output.append(repr(self.gamestate.board))
		output.append(f"wells: {self.calcWells()}\n")
		output.append(f"The height difference between the highest and lowest cells is: {self.calcHeightDifference()}\n")
		output.append(f"The variance in column height is: {self.calcColumnHeightVariance()}\n")
		output.append(f"The total number of well cells is: {self.totalNumberOfCellsInWells()}\n")
		output.append(f"The total number of wells deeper than 3 is: {self.numberOfWellsDeeperThan3()}\n")
		output.append(f"emtpy: {self.calcTotalNumberOfEmptyCells()}, empty but not holes: {self.calcNumberOfEmptyButNotHoleCells()}\
		, holes: {self.calcTotalNumberOfEmptyCells() - self.calcNumberOfEmptyButNotHoleCells()}")
		output = "".join(output)
		return output
	
	def calcNumberOfHoles(self):
		#print(f"empty: {calcTotalNumberOfEmptyCells()}, empty but not holes: {calcNumberOfEmptyButNotHoleCells()}\
		#, holes: {self.calcTotalNumberOfEmptyCells() - self.calcNumberOfEmptyButNotHoleCells()}")
		return self.calcTotalNumberOfEmptyCells() - self.calcNumberOfEmptyButNotHoleCells()

	def calcTotalNumberOfEmptyCells(self):
		result = list(map(lambda cell: int(cell[0] == TeterisBoard.EMPTY_CELL), self.gamestate.board))
		return sum(result)

	def calcNumberOfEmptyButNotHoleCells(self):
		highestFilledCellsForEachColumn = self.getColumnHeights()
		return TeterisBoard.COLUMNS * TeterisBoard.ROWS - sum(highestFilledCellsForEachColumn)

	def totalColumnHoles(self):
	# the number of empty cells with solid cells immediately above them. 
	# The playfield floor is not compared to the cell directly above it. Empty columns contain no holes
		numOfColumnHoles = 0

		for currColumn in range(TeterisBoard.COLUMNS):
			numOfColumnHoles += self._totalColumnHolesInSingleColumn(currColumn)

		return numOfColumnHoles
	
	def _totalColumnHolesInSingleColumn(self, columnInd):
		holesInColumn = 0
		if self.IsColumnEmpty(columnInd):
			return holesInColumn
		else:
			for rowInd in range(1,TeterisBoard.ROWS):
				isCurrCellEmpty = self.gamestate.board.get_cell(columnInd, rowInd ) == TeterisBoard.EMPTY_CELL
				isCellAboveEmpty = self.gamestate.board.get_cell(columnInd, rowInd - 1) == TeterisBoard.EMPTY_CELL
				if  isCurrCellEmpty and not isCellAboveEmpty:
					holesInColumn += 1
		
		return holesInColumn

	# @functools.lru_cache(maxsize= 2)
	# Guy:when I try to use functools.lru_cache the code doesn't calculate the correct number of wells.
	# I suspect the decorator just makes us not call the function even when we want to. maybe this happens because
	# the function calcWells doesn't receive input parameters, so it doesn't get called more than once.
	def calcWells(self):
		@functools.lru_cache(maxsize = 8)
		def calcWellsWithUpdate(update_id, sesion_id):
			columnWellDict = {}

			for currColoumn in range(TeterisBoard.COLUMNS):
				wellLengthInCurrentColumn = self.getWellsInSingleColoumn(currColoumn)
				# print(f"col: {currColoumn} well length: {wellLengthInCurrentColumn}")
				if wellLengthInCurrentColumn != GameParameterExtractor.NO_WELLS:
					columnWellDict[currColoumn] = wellLengthInCurrentColumn

			return columnWellDict
		return calcWellsWithUpdate(self.update_id, self.session_id)
		
	def getWellsInSingleColoumn(self, column):
		seenFirstWellCellInColumn = False
		wellDepth = 0
		for row in range(TeterisBoard.ROWS):
			if not seenFirstWellCellInColumn and self.isCellWell(row,column):
				seenFirstWellCellInColumn = True
				wellDepth +=1
			elif not seenFirstWellCellInColumn and self.gamestate.board.get_cell(column, row) != TeterisBoard.EMPTY_CELL:
				return GameParameterExtractor.NO_WELLS

			elif seenFirstWellCellInColumn:
				if self.gamestate.board.get_cell(column, row) != TeterisBoard.EMPTY_CELL:
					return wellDepth
				else:
					wellDepth +=1

		if seenFirstWellCellInColumn:
			return wellDepth
		else:
			return GameParameterExtractor.NO_WELLS

	def IsColumnEmpty(self, column):
		for row in self.gamestate.board.into_row_iter():
			if row[column] != TeterisBoard.EMPTY_CELL:
				return False
		return True
	
	def totalNumberOfCellsInWells(self):
		totalNumberOfWells = 0
		wellsDict = self.calcWells()
		for wellDepthInCurrentColumn in wellsDict.values():
			totalNumberOfWells += wellDepthInCurrentColumn

		return totalNumberOfWells

	def numberOfWellsDeeperThan3(self):
		NumberOfWellsDeeperThan3 = 0
		wellsDict = self.calcWells()
		
		for wellDepthInCurrentColumn in wellsDict.values():
			if wellDepthInCurrentColumn >= GameParameterExtractor.DEEP_WELL_THRESHOLD:
				NumberOfWellsDeeperThan3 += 1
		
		return NumberOfWellsDeeperThan3

	def getNumFilledInRaw(self, row):
		piecesCount = 0
		for i in range(TeterisBoard.COLUMNS):
			if self.gamestate.board.get_cell(i,row) != TeterisBoard.EMPTY_CELL:
				piecesCount += 1
		return piecesCount

	def calcColumnHeightVariance(self):
		highestFilledCellsForEachColumn = self.getColumnHeights()
		return self.calcVariance(highestFilledCellsForEachColumn)

	def totalWeightedColumnHoles(self):
		# the sum of the column hole row indices. In this case, the rows 
		# are indexed from top to bottom starting with 1. The idea is to
		#  penalize holes located deeper in the stack more than those closer
		#  to the surface since fewer lines needs to be cleared to fill them.
		weightedColumnHoles = 0

		for currColumn in range(TeterisBoard.COLUMNS):
			weightedColumnHoles += self._WeightedSingleColumnHoles(currColumn)

		return weightedColumnHoles

	def _WeightedSingleColumnHoles(self, columnInd):
		WeightOfholesInColumn = 0
		if self.IsColumnEmpty(columnInd):
			return WeightOfholesInColumn
		else:
			for rowInd in range(1,TeterisBoard.ROWS):
				isCurrCellEmpty = self.gamestate.board.get_cell(columnInd, rowInd ) == TeterisBoard.EMPTY_CELL
				isCellAboveEmpty = self.gamestate.board.get_cell(columnInd, rowInd - 1) == TeterisBoard.EMPTY_CELL
				if isCurrCellEmpty and not isCellAboveEmpty:
					WeightOfholesInColumn += rowInd +1 # the "+1" is for our function to match the documentation of the original function
		
		return WeightOfholesInColumn

	def totalColumnHeights(self):
		heights = self.getColumnHeights()
		return sum(heights)
	
	def columnHeightSpread(self):
		#the height difference between the tallest and the shortest columns.
		columnHeights = self.getColumnHeights()
		maxHeight = max(columnHeights) - min(columnHeights)
		return maxHeight

	def totalWeightedSolidCells(self):
		#the sum heights of all the solid cells. The row immediately above the playfield floor has a height of one.
		sumOfLockHeights = 0

		for rowIndex, row in enumerate(self.gamestate.board.into_row_iter()):
			for col in row:
				if col != TeterisBoard.EMPTY_CELL:
					sumOfLockHeights += TeterisBoard.ROWS - rowIndex
		
		return sumOfLockHeights

	def totalColumnHoleDepths(self):
		'''the sum of the vertical distances between each hole and the top of the column in which it resides.
		 The top is the uppermost solid cell within a column and the depth of the hole is the difference between
		  the row index of the hole and the row index of the top.'''
		totalHoleDepths = 0
		for columnInd in range(TeterisBoard.COLUMNS):
			totalHoleDepths += self._holeDepthForSingleColumn(columnInd)

		return totalHoleDepths

	def _holeDepthForSingleColumn(self, columnInd):
		totalHoleDepthInCurrColumn = 0
		rowOfHighestFilledCellInColumn = self.getHighestFilledCellInColumn(columnInd)

		if rowOfHighestFilledCellInColumn != 0: # if the current column is not empty
			for rowInd in range(1,TeterisBoard.ROWS):
				isCurrCellEmpty = self.gamestate.board.get_cell(columnInd, rowInd ) == TeterisBoard.EMPTY_CELL
				isCellAboveEmpty = self.gamestate.board.get_cell(columnInd, rowInd - 1) == TeterisBoard.EMPTY_CELL
				if isCurrCellEmpty and not isCellAboveEmpty:
					totalHoleDepthInCurrColumn += rowOfHighestFilledCellInColumn - (TeterisBoard.ROWS - rowInd)

		return totalHoleDepthInCurrColumn



	@staticmethod
	def calcVariance(lst):
		return np.var(lst)

	def calcHeightDifference(self):
		highestFilledCellsForEachColumn = self.getColumnHeights()
		heightDifference = max(highestFilledCellsForEachColumn)- min(highestFilledCellsForEachColumn)
		return heightDifference

	def getColumnHeights(self):
		highestFilledCellsForEachColumn = []

		for i in range(TeterisBoard.COLUMNS):
			highestFilledCellsForEachColumn.append(self.getHighestFilledCellInColumn(i))
		return highestFilledCellsForEachColumn


	def getHighestFilledCellInColumn(self, col):
		for rowIndex, row in enumerate(self.gamestate.board.into_row_iter()):
			if row[col] != TeterisBoard.EMPTY_CELL:
				return TeterisBoard.ROWS - rowIndex
		return 0

	def isCellWell(self, row, coloumn):
		#validate that the current cell is empty
		if self.gamestate.board.get_cell(coloumn, row) != TeterisBoard.EMPTY_CELL:
			return False
		
		#validate that cells along its sides are either occupied or a board edge
		if not self.gamestate.board.validate_empty_cell(coloumn - 1, row) and \
			not self.gamestate.board.validate_empty_cell(coloumn + 1, row):
			return True
		return False
	
	def getTransitionModel(self):
		from tetris_lib.transition_model import TetrisTransitionModel
		return TetrisTransitionModel(self.gamestate)

	#def GameParameterExtractor(self):
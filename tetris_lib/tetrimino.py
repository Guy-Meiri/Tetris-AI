from collections import namedtuple

TidConversionParams = namedtuple("TidConversionParams", ["bias", "modulo_bias", "modulo"])
T = [[[-1, 0], [0, 0], [1, 0], [0, -1], ],  # Tu : 0
	 [[0, -1], [0, 0], [1, 0], [0, 1], ],   # Tr : 1
	 [[-1, 0], [0, 0], [1, 0], [0, 1], ],    # Td :2 (spawn)
	 [[0, -1], [-1, 0], [0, 0], [0, 1], ],  # Tl :3
]  

J = [[[0, -1], [0, 0], [-1, 1], [0, 1], ],  # Jl : 4
	 [[-1, -1], [-1, 0], [0, 0], [1, 0], ],  # Ju : 5
	 [[0, -1], [1, -1], [0, 0], [0, 1], ],   # Jr : 6
	 [[-1, 0], [0, 0], [1, 0], [1, 1], ],  # Jd : 7(spawn)
]
Z =  [[[-1, 0], [0, 0], [0, 1], [1, 1], ],  # Zh : 8(spawn)
	 [[1, -1], [0, 0], [1, 0], [0, 1], ], ]  # Zv : 9
O =  [[[-1, 0], [0, 0], [-1, 1], [0, 1], ], ]  # O : 10 (spawn)
S =  [[[0, 0], [1, 0], [-1, 1], [0, 1], ],  # Sh :11 (spawn)
	 [[0, -1], [0, 0], [1, 0], [1, 1], ], ]  # Sv :12

L = [[[0, -1], [0, 0], [0, 1], [1, 1], ], 	# Lr : 13
	 [[-1, 0], [0, 0], [1, 0], [-1, 1], ],  # Ld :14 (spawn)
	 [[-1, -1], [0, -1], [0, 0], [0, 1], ],  # Ll :15
	 [[1, -1], [-1, 0], [0, 0], [1, 0], ],  # Lu : 16
]  
I = [[[0, -2], [0, -1], [0, 0], [0, 1], ],    # Iv :17
	[[-2, 0], [-1, 0], [0, 0], [1, 0], ],  		  # Ih :18(spawn)
]

TETRIMINO_ID_TO_INDEX = [TidConversionParams(0, 0, 4)] * 4 + \
						[TidConversionParams(4, 0, 4)] * 4 + \
						[TidConversionParams(8, 0, 2)] * 2 + \
						[TidConversionParams(10, 0, 1)] + \
						[TidConversionParams(11, 1, 2)] * 2 + \
						[TidConversionParams(13, 3, 4)] * 4 + \
						[TidConversionParams(17, 1, 2)] * 2

PATTERNS = [*T, *J, *Z, *O, *S, *L, *I]

class Tetrimino():
	CLOCKWISE = 1
	COUNTER_CLOCKWISE = -1
	def __init__(self, tid):
		self.tid = tid
	def rotate_clockwise(self):
		return self.___rotate(Tetrimino.CLOCKWISE)
	def rotate_counterclockwise(self):
		return self.___rotate(Tetrimino.COUNTER_CLOCKWISE)
	def ___rotate(self, direction):
		tid_conv_params = TETRIMINO_ID_TO_INDEX[self.tid]
		bias = tid_conv_params.bias
		modulo_bias = tid_conv_params.modulo_bias
		modulo = tid_conv_params.modulo
		new_tid = bias + (self.tid + 1*direction + modulo_bias) % modulo
		return Tetrimino(new_tid)
	def get_pattern(self):
		if self.tid > len(PATTERNS) - 1 or self.tid < 0:
			return None
		return PATTERNS[self.tid]
	def get_abs_pattern(self, x, y):
		def absolutify_tuple(tup):
			return (tup[0] + x, tup[1] + y)
		return list(map(absolutify_tuple, self.get_pattern()))
	def get_id(self):
		return self.tid
	def get_possible_rotations_outcomes(self):
		result = set()
		next_tetrimino = self
		for _ in range(4):
			result.add(next_tetrimino)
			next_tetrimino = next_tetrimino.rotate_clockwise()
		return list(result)
	def __repr__(self):
		return str(self.tid)
	def __hash__(self):
		return hash(self.tid)
	def __eq__(self, other):
		if not isinstance(other, Tetrimino):
			return False
		return self.tid == other.tid

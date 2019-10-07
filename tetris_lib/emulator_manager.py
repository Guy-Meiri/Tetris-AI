
import os
import win32api
import win32con
import win32gui
import win32process
import time
import subprocess

#relative path
TETRIS_PATH = r"..\binaries\Tetris.nes"
EMULATOR_PATH = r"..\binaries\Nintaco.jar"

class KEYS():
	ALT = win32con.VK_MENU
	T = 0x54
	R = 0x52
	L = 0x4C

def hold(key):
	win32api.keybd_event(key, 0,0,0)
def release(key):
	win32api.keybd_event(key,0, win32con.KEYEVENTF_KEYUP ,0)
def press(*args):
		'''
		one press, one release.
		accepts as many arguments as you want. e.g. press(KEYS.T, KEYS.R).
		'''
		for i in args:
				hold(i)
				time.sleep(.1)
				release(i)
def make_path_relative(path):
	current_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(current_dir, path)

def start_process(emulator, tetris):
	emulator = make_path_relative(emulator)
	tetris_game = make_path_relative(tetris)
	if not os.path.isfile(emulator):
		raise FileNotFoundError(f"Emulator file at '{emulator}' does not exist")
	if not os.path.isfile(tetris_game):
		raise FileNotFoundError(f"Tetris file at '{tetris_game}' does not exist")
	
	#start the tetris with the game
	#print("Running: " + rf"java -jar {emulator} {tetris_game}")
	process = subprocess.Popen(rf"java -jar {emulator} {tetris_game}".split(" "))
	#might want to add some sleep
	return process

def get_window_by_pid(pid, name):
	current_window = None
	number_of_windows = 0
	def window_enum_callback(hwnd, arg):
		nonlocal current_window, number_of_windows
		current_pid = win32process.GetWindowThreadProcessId(hwnd)[1]
		if pid != current_pid:
			return
		number_of_windows += 1
		if str(win32gui.GetWindowText(hwnd)) == name:
			current_window = hwnd
	win32gui.EnumWindows(window_enum_callback, None)
	return current_window, number_of_windows


def get_window_by_pid_block(pid, number_of_windows_needed=8,name="Nintaco"):
	#replaced the sleep with a check of how many windows the emulator
	#process has, after few checks it turns up, that once its fully loaded
	#there are 8 window objects to the process.
	#this way it is not computer-speed dependant code, but more deterministic
	window_handle, number_of_windows = None, 0
	while window_handle == None or number_of_windows != number_of_windows_needed:
		time.sleep(0.2)
		window_handle, number_of_windows = get_window_by_pid(pid, name)
		print(window_handle, number_of_windows)
	time.sleep(8) # a security measure
	return window_handle

def set_forground(window):
	win32gui.SetForegroundWindow(window)

def start_emulator(emulator=EMULATOR_PATH, tetris=TETRIS_PATH):
	process = start_process(emulator, tetris)
	window = get_window_by_pid_block(process.pid)
	
	set_forground(window)
	loadJavaAndRun()
	if process.poll() != None:
		#process exited
		raise RuntimeError("java process terminated for unknown reason")
	return process

def loadJavaAndRun():
	press(KEYS.ALT)
	time.sleep(.1)
	press(KEYS.T), 
	time.sleep(.1)
	press(KEYS.R)
	time.sleep(.1)
	hold(KEYS.ALT)
	time.sleep(.1)
	press(KEYS.L)
	release(KEYS.ALT)

	time.sleep(.5)
	hold(KEYS.ALT)
	time.sleep(.1)
	press(KEYS.R)
	release(KEYS.ALT)

if __name__ == "__main__":
	print("Startingggg")
	process = start_emulator()
	time.sleep(4)
	process.terminate()
	
all: Main redisbridge monitor

Main:
	pyinstaller -F Main.py

redisbridge:
	pyinstaller -F redisbridge.py

monitor:
	pyinstaller -F monitor.py


clear:
	rm -fr build dist

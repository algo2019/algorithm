root:=$(shell readlink -f ../..)
py_lib:=$(shell readlink -f ../../pylib)

daydatesaveoper:
	pyinstaller -p $(root) -p $(py_lib) daydatesaveoper.py

clear:
	rm -rf build dist
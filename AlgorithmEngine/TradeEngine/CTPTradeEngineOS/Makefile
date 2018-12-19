ROOT = $(shell readlink -f ../..)
DIR_OBJ = ./build
DIR_BIN = ./target

CFLAGS = -std=c++0x -O3

ctptradeengine.so: PER
	python setup.py build_ext --inplace
	mv ctptradeengine.cpp $(DIR_OBJ)
	mv ctptradeengine.so $(DIR_BIN)


PER:
	mkdir -p $(DIR_OBJ)
	mkdir -p $(DIR_BIN)

clean:
	rm -rf $(DIR_OBJ) $(DIR_BIN)

install:
	mv $(DIR_BIN)/*.so $(ROOT)/pylib

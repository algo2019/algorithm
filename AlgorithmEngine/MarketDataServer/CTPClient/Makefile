DIR_OBJ = ./build
DIR_BIN = ./target

CFLAGS = -std=c++0x -O3


CTPClientRun: CTPClientRun.c
	gcc `python-config --cflags` -o ./target/CTPClientRun  ./build/CTPClientRun.c  `python-config --ldflags`

CTPClientRun.c: client.so
	cython CTPClientRun.py --embed
	mv CTPClientRun.c $(DIR_OBJ)

client.so: PER
	python setup.py build_ext --inplace
	mv client.cpp $(DIR_OBJ)


PER:
	mkdir -p $(DIR_OBJ)
	mkdir -p $(DIR_BIN)
	mkdir -p $(ROOT)/bin

clean:
	rm -rf $(DIR_OBJ) $(DIR_BIN)

ROOT = $(shell readlink -f ../..)
INC_BASE = -I$(ROOT)/include -I$(shell readlink -f ./CSimpleHandler/) -I$(shell readlink -f ./InstrumnetGainer/)
LIB_PATH_BASE = -L$(ROOT)/lib
LIBS = -lthostmduserapi -lthosttraderapi -lhiredis
CC = g++


OBJ1 = $(DIR_OBJ)/InstrumnetGainer.o
SRC1 = ./InstrumnetGainer/InstrumnetGainer.cpp

OBJ2 = $(DIR_OBJ)/CSimpleHandler.o
SRC2 = ./CSimpleHandler/CSimpleHandler.cpp

OBJ3 = $(DIR_OBJ)/test.o
SRC3 = crun.cpp


$(OBJ1): $(SRC1) PER
	$(CC) $(INC_BASE) $(CFLAGS) -c $< -o $@

$(OBJ2): $(SRC2) PER
	$(CC) $(INC_BASE) $(CFLAGS) -c $< -o $@

$(OBJ3): $(SRC3)
	$(CC) $(INC_BASE) $(CFLAGS) -c $< -o $@

crun: $(OBJ1) $(OBJ2) $(OBJ3)
	$(CC) $^ $(LIB_PATH_BASE) $(CFLAGS) $(LIBS) -o $(DIR_BIN)/crun

install:
	mv $(DIR_BIN)/*.so $(ROOT)/pylib
	mv $(DIR_BIN)/* $(ROOT)/bin

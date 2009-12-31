CC=gcc
CFLAGS=-c
LFLAGS=

all: main.o
	$(CC) $(LFLAGS) main.o -o vmtest
main.o: main.c
	$(CC) $(CFLAGS) main.c -o main.o
clean:
	rm -rf *.o
	rm -rf vmtest

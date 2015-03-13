
all: libkano-logging.a

kano-log.o:
	gcc -std=c99 -D_BSD_SOURCE -gdwarf-2 -c kano-log.c -o kano-log.o

libkano-logging.a: kano-log.o
	ar -r $@ $^

